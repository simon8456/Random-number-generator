"""Namluvení replik přes XTTS v2 (česky) s automatickou kontrolou srozumitelnosti (Whisper).
Spouští se ve venv s coqui-tts:  python engine/voices.py BUILD_DIR"""
import json
import os
import re
import sys
import time

os.environ['COQUI_TOS_AGREED'] = '1'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import numpy as np  # noqa
import librosa  # noqa
import soundfile as sf  # noqa
import torch  # noqa

from engine.parse import parse  # noqa
from engine.timeline import line_key, FPS  # noqa

# postava -> (XTTS mluvčí, rychlost, posun výšky v půltónech)
VOICES = json.load(open(os.path.join(HERE, 'engine', 'casting.json'), encoding='utf8'))

# výslovnost pro TTS
SAY = [
    (r'\bMgr\.\s*', 'magistr '), (r'\bJ\. Š\.', 'Jé Eš'), (r'\bM\. B\. K\. M\.', 'Em Bé. Ká Em.'),
    (r'\bSPZ\b', 'Espézet'), (r'\bOK\b', 'okej'), (r'\bGPSku\b', 'gépéesku'), (r'\bTři P\.', 'Tři Pé.'),
    (r'…', '...'), (r'„|“', ''), (r'\bpaní profesorko\b', 'paní profesorko'),
]


def spoken(text):
    s = text
    for a, b in SAY:
        s = re.sub(a, b, s)
    return s


UNITS = ['nula', 'jedna', 'dva', 'tři', 'čtyři', 'pět', 'šest', 'sedm', 'osm', 'devět', 'deset', 'jedenáct',
         'dvanáct', 'třináct', 'čtrnáct', 'patnáct', 'šestnáct', 'sedmnáct', 'osmnáct', 'devatenáct']
TENS = ['', '', 'dvacet', 'třicet', 'čtyřicet', 'padesát', 'šedesát', 'sedmdesát', 'osmdesát', 'devadesát']


def num_cs(n):
    if n < 20:
        return UNITS[n]
    if n < 100:
        return TENS[n // 10] + ('' if n % 10 == 0 else ' ' + UNITS[n % 10])
    if n < 1000:
        h = ['', 'sto', 'dvě stě', 'tři sta', 'čtyři sta', 'pět set', 'šest set', 'sedm set', 'osm set',
             'devět set'][n // 100]
        return h + ('' if n % 100 == 0 else ' ' + num_cs(n % 100))
    if n < 10000:
        th = 'tisíc' if n // 1000 == 1 else num_cs(n // 1000) + ' tisíc'
        return th + ('' if n % 1000 == 0 else ' ' + num_cs(n % 1000))
    return str(n)


def norm(s):
    s = re.sub(r'(\d+)[.,:](\d+)', lambda m: num_cs(int(m.group(1))) + ' ' + num_cs(int(m.group(2))), s)
    s = re.sub(r'\d+', lambda m: num_cs(int(m.group(0))), s)
    s = s.lower()
    s = re.sub(r'[^a-záčďéěíňóřšťúůýž ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def cer(ref, hyp):
    a, b = norm(ref), norm(hyp)
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb))
    return d[len(b)] / max(1, len(a))


def split_sentences(s):
    parts = re.split(r'(?<=[.!?])\s+', s.strip())
    out = []
    for p in parts:
        if out and len(out[-1]) < 18:
            out[-1] += ' ' + p
        else:
            out.append(p)
    return [p for p in out if p]


def main():
    build = sys.argv[1]
    only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
    vdir = os.path.join(build, 'voice')
    os.makedirs(vdir, exist_ok=True)
    mpath = os.path.join(vdir, 'manifest.json')
    man = json.load(open(mpath)) if os.path.exists(mpath) else {}
    scenes = parse(os.path.join(HERE, 'scenar.txt'))
    todo = []
    for sc in scenes:
        for kind, who, info in sc.cmds:
            if kind != 'line':
                continue
            if only and who not in only:
                continue
            key = line_key(who, info['text'])
            if key in man and os.path.exists(os.path.join(vdir, man[key]['file'])):
                continue
            todo.append((key, who, info['text']))
    # výkřik ředitele (ruch ve scéně 23)
    if not os.path.exists(os.path.join(vdir, 'shout.wav')):
        todo.append(('shout', 'HRUBAN', 'Okamžitě odejděte z mé kanceláře! Okamžitě!'))
    print('k namluvení:', len(todo), flush=True)
    if not todo:
        return
    torch.set_num_threads(4)
    from TTS.api import TTS
    from transformers import pipeline
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
    model = tts.synthesizer.tts_model
    asr = pipeline('automatic-speech-recognition', model='openai/whisper-small', device='cpu')
    lat = {}

    def trim_tail(w, sent):
        """Odstraní halucinované slovo za koncem věty (častá vada XTTS) podle časových značek Whisperu."""
        import difflib
        ref = norm(sent).split()
        if not ref:
            return w, ''
        y16 = librosa.resample(w, orig_sr=24000, target_sr=16000)
        try:
            r = asr({'raw': y16, 'sampling_rate': 16000}, return_timestamps='word',
                    generate_kwargs={'language': 'czech', 'task': 'transcribe'})
        except Exception:  # noqa
            return w, ''
        chunks = r.get('chunks') or []
        words = [(norm(c['text']), c['timestamp']) for c in chunks if norm(c['text'])]
        hyp = ' '.join(wd for wd, _ in words)
        if len(words) < 2:
            return w, hyp
        last = ref[-1]
        for i in range(len(words) - 1, max(-1, len(words) - 4), -1):
            wd, ts = words[i]
            if difflib.SequenceMatcher(None, wd, last).ratio() >= 0.6:
                if i < len(words) - 1 and ts[1]:
                    cut = int((ts[1] + 0.12) * 24000)
                    if cut < len(w):
                        w = w[:cut].copy()
                        fl = min(len(w), 1200)
                        w[-fl:] *= np.linspace(1, 0, fl)
                        hyp = ' '.join(wd for wd, _ in words[:i + 1])
                break
        return w, hyp

    def synth(spk, text, speed, temp, seed):
        if spk not in lat:
            d = model.speaker_manager.speakers[spk]
            lat[spk] = (d['gpt_cond_latent'], d['speaker_embedding'])
        g, e = lat[spk]
        torch.manual_seed(seed)
        pieces = []
        hyps = []
        for sent in split_sentences(text):
            out = model.inference(sent, 'cs', g, e, temperature=temp, length_penalty=1.0, repetition_penalty=8.0,
                                  top_k=40, top_p=0.8, speed=speed, enable_text_splitting=False)
            w = np.asarray(out['wav'], np.float32)
            w, _ = librosa.effects.trim(w, top_db=38)
            w, h = trim_tail(w, sent)
            hyps.append(h)
            pieces.append(w)
            pieces.append(np.zeros(int(24000 * 0.22), np.float32))
        wav = np.concatenate(pieces[:-1]) if pieces else np.zeros(2400, np.float32)
        return wav, ' '.join(hyps)

    t_start = time.time()
    for idx, (key, who, text) in enumerate(todo):
        spk, speed, shift = VOICES.get(who, VOICES['_default'])
        say = spoken(text)
        best = None
        for attempt in range(3):
            temp = [0.5, 0.4, 0.62][attempt]
            try:
                w, hyp = synth(spk, say, speed, temp, 1000 + attempt * 17 + idx)
            except Exception as ex:  # noqa
                print('chyba', ex, flush=True)
                continue
            c = cer(say, hyp)
            # podezřele dlouhé = halucinace
            exp_dur = len(say) / 13.0
            if len(w) / 24000 > exp_dur * 2.2 + 1.5:
                c += 0.5
            if best is None or c < best[0]:
                best = (c, w, hyp)
            if c <= 0.15:
                break
        c, w, hyp = best
        if shift:
            w = librosa.effects.pitch_shift(w, sr=24000, n_steps=shift)
        w = np.concatenate([np.zeros(1200, np.float32), w, np.zeros(1200, np.float32)])
        pk = np.abs(w).max() + 1e-9
        w = w / pk * 0.89
        fname = f'{key}.wav'
        sf.write(os.path.join(vdir, fname), w, 24000)
        if key != 'shout':
            man[key] = dict(file=fname, dur=round(len(w) / 24000, 3), who=who, cer=round(c, 3), hyp=hyp)
        el = time.time() - t_start
        print(f'[{idx + 1}/{len(todo)}] {who:10} cer={c:.2f} {len(w) / 24000:5.1f}s  ({el / 60:.1f} min)  {text[:50]}',
              flush=True)
        if idx % 5 == 0 or idx == len(todo) - 1:
            json.dump(man, open(mpath, 'w'), ensure_ascii=False, indent=0)
    json.dump(man, open(mpath, 'w'), ensure_ascii=False, indent=0)
    make_env(vdir, man)


def make_env(vdir, man):
    env = {}
    for key, m in man.items():
        y, sr = sf.read(os.path.join(vdir, m['file']))
        hop = sr // FPS
        n = len(y) // hop + 1
        r = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(y) else 0 for i in range(n)])
        r = r / (np.percentile(r[r > 0.005], 90) + 1e-6) if (r > 0.005).any() else r
        env[key] = np.clip(r, 0, 1).astype(np.float32)
    np.savez_compressed(os.path.join(vdir, 'env.npz'), **env)
    print('env ok', len(env))


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'env':
        vd = os.path.join(sys.argv[1], 'voice')
        make_env(vd, json.load(open(os.path.join(vd, 'manifest.json'))))
    else:
        main()
