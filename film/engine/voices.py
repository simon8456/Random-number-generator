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
    only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] not in ('', 'all') and not sys.argv[2].startswith('redo') else None
    shard, nshards = (int(x) for x in sys.argv[3].split('/')) if len(sys.argv) > 3 else (0, 1)
    vdir = os.path.join(build, 'voice')
    os.makedirs(vdir, exist_ok=True)
    man = load_manifest(vdir)
    mpath = os.path.join(vdir, f'manifest_{shard}.json')
    redo = float(sys.argv[2].split(':')[1]) if len(sys.argv) > 2 and sys.argv[2].startswith('redo:') else None
    if redo is not None:
        only = None
        bad = {k for k, v in man.items() if v['cer'] > redo}
        print('k přegenerování:', len(bad), flush=True)
        for k in bad:
            man.pop(k)
        old_best = {k: v for k, v in load_manifest(vdir).items() if k in bad}
        mpath = os.path.join(vdir, 'manifest_redo.json')
    else:
        old_best = {}
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
    if redo is not None:
        todo = [x for x in todo if x[0] in bad]
    todo = [x for i, x in enumerate(todo) if i % nshards == shard]
    # výkřik ředitele (ruch ve scéně 23)
    if shard == 0 and not os.path.exists(os.path.join(vdir, 'shout.wav')):
        todo.append(('shout', 'HRUBAN', 'Okamžitě odejděte z mé kanceláře! Okamžitě!'))
    print('k namluvení:', len(todo), flush=True)
    if not todo:
        return
    torch.set_num_threads(int(os.environ.get('TTS_THREADS', '4')))
    from TTS.api import TTS
    from faster_whisper import WhisperModel
    tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
    model = tts.synthesizer.tts_model
    asr = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=int(os.environ.get('TTS_THREADS', '4')))
    lat = {}

    def synth(spk, text, speed, temp, seed):
        """Namluví repliku po větách, jedním průchodem Whisperu odstraní halucinované konce vět
        a vrátí (zvuk, přepis)."""
        import difflib
        if spk not in lat:
            d = model.speaker_manager.speakers[spk]
            lat[spk] = (d['gpt_cond_latent'], d['speaker_embedding'])
        g, e = lat[spk]
        torch.manual_seed(seed)
        sents = split_sentences(text)
        segs = []
        for sent in sents:
            out = model.inference(sent, 'cs', g, e, temperature=temp, length_penalty=1.0, repetition_penalty=8.0,
                                  top_k=40, top_p=0.8, speed=speed, enable_text_splitting=False)
            w = np.asarray(out['wav'], np.float32)
            w, _ = librosa.effects.trim(w, top_db=38)
            segs.append(w)
        gap = np.zeros(int(24000 * 0.22), np.float32)
        bounds, pos = [], 0
        for w in segs:
            bounds.append((pos, pos + len(w)))
            pos += len(w) + len(gap)
        full = np.concatenate([np.concatenate([w, gap]) for w in segs])
        y16 = librosa.resample(full, orig_sr=24000, target_sr=16000)
        res, _ = asr.transcribe(y16, language='cs', word_timestamps=True, beam_size=2, vad_filter=False,
                                condition_on_previous_text=False)
        words = [(norm(wd.word), wd.start, wd.end) for sg in res for wd in (sg.words or []) if norm(wd.word)]
        kept_audio, kept_words = [], []
        for (b0, b1), sent, w in zip(bounds, sents, segs):
            t0, t1 = b0 / 24000, (b1 + len(gap) * 0.5) / 24000
            ws = [x for x in words if t0 - 0.05 <= (x[1] + x[2]) / 2 < t1]
            ref = norm(sent).split()
            if ref and len(ws) >= 2:
                last = ref[-1]
                for i in range(len(ws) - 1, max(-1, len(ws) - 4), -1):
                    if difflib.SequenceMatcher(None, ws[i][0], last).ratio() >= 0.6:
                        if i < len(ws) - 1:
                            cut = int((ws[i][2] + 0.12 - t0) * 24000)
                            if 0 < cut < len(w):
                                w = w[:cut].copy()
                                fl = min(len(w), 1200)
                                w[-fl:] *= np.linspace(1, 0, fl)
                                ws = ws[:i + 1]
                        break
            kept_audio.append(w)
            kept_words += [x[0] for x in ws]
        wav = np.concatenate([np.concatenate([w, gap]) for w in kept_audio])[:-len(gap)]
        return wav, ' '.join(kept_words)

    t_start = time.time()
    for idx, (key, who, text) in enumerate(todo):
        spk, speed, shift = VOICES.get(who, VOICES['_default'])
        say = spoken(text)
        best = None
        n_att = 6 if key in old_best else 3
        for attempt in range(n_att):
            temp = [0.5, 0.4, 0.62, 0.3, 0.55, 0.7][attempt]
            try:
                w, hyp = synth(spk, say, speed, temp, 1000 + attempt * 17 + idx + (500 if key in old_best else 0))
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
        if key in old_best and old_best[key]['cer'] <= c:
            man[key] = old_best[key]   # starší verze byla lepší
            print(f'[{idx + 1}/{len(todo)}] {who:10} ponechána starší verze ({old_best[key]["cer"]:.2f} <= {c:.2f})',
                  flush=True)
            json.dump(man, open(mpath, 'w'), ensure_ascii=False, indent=0)
            continue
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
        if True:
            json.dump(man, open(mpath, 'w'), ensure_ascii=False, indent=0)
    json.dump(man, open(mpath, 'w'), ensure_ascii=False, indent=0)


def load_manifest(vdir):
    import glob
    man = {}
    for p in sorted(glob.glob(os.path.join(vdir, 'manifest*.json'))):
        try:
            man.update(json.load(open(p)))
        except Exception:  # noqa
            pass
    return man


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
        m = load_manifest(vd)
        json.dump(m, open(os.path.join(vd, 'manifest.json'), 'w'), ensure_ascii=False, indent=0)
        make_env(vd, m)
    else:
        main()
