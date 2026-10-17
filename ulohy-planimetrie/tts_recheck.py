"""Znovu ověří klipy, které tts_gen označil jako LOW, přesnějším porovnáním (po znacích,
bez mezer, čísla převedená na slova). Klipy, které i tak vyjdou špatně, smaže,
aby je další běh tts_gen.py vygeneroval znovu.

    /opt/tts/bin/python tts_recheck.py          # jen vypíše
    /opt/tts/bin/python tts_recheck.py --delete # smaže špatné
"""
import difflib
import json
import os
import re
import sys

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

from tts_gen import ALIASES, LETTERS, num2words, strip_acc

ROOT = os.path.dirname(os.path.abspath(__file__))
LIMIT = 0.85


def chars(s, ref):
    s = s.lower().replace("°", " stupnu ")
    s = re.sub(r"\d+", lambda m: " " + num2words(int(m.group()), lang="cs") + " ", s)
    out = []
    for t in re.findall(r"[^\W\d_]+", s):
        if ref and t in LETTERS:
            t = LETTERS[t]
        t = strip_acc(t)
        t = ALIASES.get(t, t)
        if len(t) >= 2:
            out.append(t)
    return "".join(out).replace("y", "i")


def main():
    items = {i["key"]: i for i in json.load(open(os.path.join(ROOT, "texts.json"), encoding="utf-8"))}
    low = sorted(set(re.findall(r"\] LOW [\d.]+ try\d [\d.]+s \S+ (\w+)",
                                open(os.path.join(ROOT, "tts_log.txt"), encoding="utf-8").read())))
    low = [k for k in low if k in items and os.path.exists(os.path.join(ROOT, "audio", k + ".wav"))]
    asr = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    bad = []
    for k in low:
        x, sr = sf.read(os.path.join(ROOT, "audio", k + ".wav"), dtype="float32")
        x16 = np.interp(np.arange(0, len(x), sr / 16000), np.arange(len(x)), x).astype(np.float32)
        hyp = " ".join(s.text.strip() for s in asr.transcribe(x16, language="cs", beam_size=5)[0])
        a, b = chars(items[k]["text"], True), chars(hyp, False)
        sc = difflib.SequenceMatcher(None, a, b).ratio()
        flag = "ok " if sc >= LIMIT else "BAD"
        print(f"{flag} {sc:.2f} {k} {items[k]['scene']}\n   TXT: {items[k]['text']}\n   ASR: {hyp}", flush=True)
        if sc < LIMIT:
            bad.append(k)
    print(f"{len(bad)} špatných z {len(low)}")
    if "--delete" in sys.argv:
        for k in bad:
            os.remove(os.path.join(ROOT, "audio", k + ".wav"))


if __name__ == "__main__":
    main()
