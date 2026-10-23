"""Průzkum hlasů XTTS: srozumitelnost v češtině (Whisper CER) a výška hlasu."""
import os, sys, json, re, time
os.environ['COQUI_TOS_AGREED'] = '1'
import numpy as np, librosa, torch
from TTS.api import TTS
from transformers import pipeline

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
torch.set_num_threads(4)
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
asr = pipeline('automatic-speech-recognition', model='openai/whisper-small', device='cpu')
TEXT = 'Já myslím, že Matěj Brabec není v Anglii. Viděl jsem ho jít do garáže a už nevyšel.'

def norm(s):
    s = s.lower()
    s = re.sub(r'[^a-záčďéěíňóřšťúůýž ]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def cer(a, b):
    a, b = norm(a), norm(b)
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb))
    return d[len(b)] / max(1, len(a))

res = {}
for spk in tts.speakers:
    p = os.path.join(out, spk.replace(' ', '_') + '.wav')
    t = time.time()
    tts.tts_to_file(text=TEXT, speaker=spk, language='cs', file_path=p)
    y, sr = librosa.load(p, sr=16000)
    hyp = asr({'raw': y, 'sampling_rate': 16000}, generate_kwargs={'language': 'czech', 'task': 'transcribe'})['text']
    f0 = librosa.yin(y, fmin=60, fmax=400, sr=16000)
    rms = librosa.feature.rms(y=y)[0]
    voiced = f0[:len(rms)][rms[:len(f0)] > rms.max() * 0.15]
    res[spk] = dict(cer=round(cer(TEXT, hyp), 3), f0=float(np.median(voiced)), dur=len(y) / 16000, hyp=hyp)
    print(spk, res[spk], round(time.time() - t, 1), flush=True)
    json.dump(res, open(os.path.join(out, 'survey.json'), 'w'), ensure_ascii=False, indent=1)
