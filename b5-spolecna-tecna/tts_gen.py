"""Vygeneruje chybějící audio (OmniVoice, klon hlasu z voice_ref.wav) a ověří ho přes Whisper.

Spouštět v prostředí s torch + omnivoice + faster-whisper:
    /opt/tts/bin/python tts_gen.py
Každý klip se přepíše Whisperem a porovná s textem; když se moc liší
(zkomolené slovo, useknutý konec), vygeneruje se znovu (max. 4 pokusy, bere se nejlepší).
"""
import difflib
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

import numpy as np
import soundfile as sf
import torch
from faster_whisper import WhisperModel
from num2words import num2words
from omnivoice import OmniVoice

ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(ROOT, "audio")
REF_TEXT = "Nakreslíme si libovolný trojúhelník á bé cé. Bodem cé vedeme přímku pé rovnoběžnou se stranou á bé."
SR = 24000
SPEED = 0.9
TRIES = 3
THRESH = 0.8

LETTERS = {"á": "a", "bé": "b", "cé": "c", "dé": "d", "ef": "f", "gé": "g", "há": "h", "jé": "j",
           "ká": "k", "el": "l", "em": "m", "en": "n", "pé": "p", "kvé": "q", "er": "r", "es": "s",
           "té": "t", "vé": "v", "iks": "x", "zet": "z", "í": "i", "ó": "o", "ú": "u", "é": "e"}


def strip_acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def tokens(s, ref=False):
    s = s.lower().replace("°", " stupnu ")
    s = re.sub(r"\d+", lambda m: " " + num2words(int(m.group()), lang="cs") + " ", s)
    toks = re.findall(r"[^\W\d_]+", s)
    out = []
    for t in toks:
        if ref and t in LETTERS:
            out.extend(LETTERS[t])
            continue
        out.append(strip_acc(t))
    # písmena zkratek (ABC -> a b c) i jednopísmenné tokeny ignorujeme – porovnáváme jen slova
    return [t for t in out if len(t) >= 3]


ALIASES = {"bot": "bod", "gamma": "gama", "alpha": "alfa", "zhrnuti": "shrnuti", "trick": "trik"}


def score(text, hyp):
    a, b = tokens(text, ref=True), [ALIASES.get(t, t) for t in tokens(hyp)]
    if not a:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def postprocess(x):
    x = np.asarray(x, dtype=np.float32)
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    x = x * (10 ** (-20 / 20) / rms)
    peak = np.abs(x).max()
    if peak > 0.95:
        x = x * 0.95 / peak
    return x


def main():
    items = json.load(open(os.path.join(ROOT, "texts.json"), encoding="utf-8"))
    todo = [i for i in items if not os.path.exists(os.path.join(AUDIO, i["key"] + ".wav"))]
    if len(sys.argv) > 1:
        todo = [i for i in todo if any(a in i["scene"] for a in sys.argv[1:])]
    print(f"generuji {len(todo)} klipů", flush=True)
    if not todo:
        return
    torch.set_num_threads(os.cpu_count())
    model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.bfloat16)
    ref = model.create_voice_clone_prompt(ref_audio=os.path.join(ROOT, "voice_ref.wav"), ref_text=REF_TEXT)
    asr = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    log = open(os.path.join(ROOT, "tts_log.txt"), "a", encoding="utf-8")
    t_start = time.time()
    for n, it in enumerate(todo):
        best = None
        for k in range(TRIES):
            torch.manual_seed(1000 * k + n)
            x = model.generate(text=it["text"], language="cs", voice_clone_prompt=ref,
                               num_step=12, speed=SPEED)[0]
            x16 = np.interp(np.arange(0, len(x), SR / 16000), np.arange(len(x)), x).astype(np.float32)
            segs, _ = asr.transcribe(x16, language="cs", beam_size=1)
            hyp = " ".join(s.text.strip() for s in segs)
            sc = score(it["text"], hyp)
            dur = len(x) / SR
            cps = len(it["text"]) / dur
            if not (9 <= cps <= 21):
                sc -= 0.3
            if best is None or sc > best[0]:
                best = (sc, x, hyp, k)
            if sc >= THRESH:
                break
        sc, x, hyp, k = best
        sf.write(os.path.join(AUDIO, it["key"] + ".wav"), postprocess(x), SR, subtype="PCM_16")
        flag = "OK " if sc >= THRESH else "LOW"
        msg = (f"[{n + 1}/{len(todo)}] {flag} {sc:.2f} try{k} {len(x) / SR:.1f}s {it['scene']} {it['key']}\n"
               f"   TXT: {it['text']}\n   ASR: {hyp}\n")
        log.write(msg)
        log.flush()
        el = time.time() - t_start
        print(msg.splitlines()[0] + f"  (elapsed {el / 60:.1f} min)", flush=True)


if __name__ == "__main__":
    main()
