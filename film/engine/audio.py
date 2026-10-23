"""Zvuk: syntéza hudby, ruchů a atmosfér + finální mix s hlasy."""
import math
import os
import wave

import numpy as np
from scipy import signal

SR = 32000
RNG = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tarr(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2, total=None):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    e = np.ones(n) * s
    a_n = min(a_n, n)
    e[:a_n] = np.linspace(0, 1, a_n, endpoint=False) if a_n else e[:a_n]
    dd = min(d_n, max(0, n - a_n))
    e[a_n:a_n + dd] = np.linspace(1, s, dd, endpoint=False)
    if r_n and n > r_n:
        e[-r_n:] *= np.linspace(1, 0, r_n)
    return e


def lowpass(x, fc, order=2):
    b, a = signal.butter(order, min(0.99, fc / (SR / 2)), 'low')
    return signal.lfilter(b, a, x)


def highpass(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high')
    return signal.lfilter(b, a, x)


def bandpass(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), min(0.99, f2 / (SR / 2))], 'band')
    return signal.lfilter(b, a, x)


_IR = {}


def reverb(x, rt=2.2, wet=0.3, seed=1):
    key = (rt, seed)
    if key not in _IR:
        r = np.random.default_rng(seed)
        n = int(rt * SR)
        t = np.arange(n) / SR
        ir = r.normal(0, 1, (n, 2)) * np.exp(-6.9 * t / rt)[:, None]
        ir[:, 0] = lowpass(ir[:, 0], 6000)
        ir[:, 1] = lowpass(ir[:, 1], 6000)
        ir[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))[:, None]
        ir /= np.sqrt((ir ** 2).sum(axis=0))
        _IR[key] = ir
    ir = _IR[key]
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    out = np.zeros((len(x) + len(ir) - 1, 2), np.float32)
    for c in range(2):
        out[:, c] = signal.fftconvolve(x[:, c], ir[:, c])
    res = out[:len(x)] * wet
    res += x * (1 - wet * 0.5)
    return res


def pan(x, p):
    """p: -1 vlevo, +1 vpravo"""
    l = math.cos((p + 1) * math.pi / 4)
    r = math.sin((p + 1) * math.pi / 4)
    return np.stack([x * l, x * r], 1)


# ------------------------------------------------------------- nástroje

def inst_piano(f, d, vel=0.8):
    n = int((d + 1.5) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k, amp in enumerate((1.0, 0.5, 0.28, 0.16, 0.09, 0.05), 1):
        fk = f * k * (1 + 0.0004 * k * k)
        dec = 2.8 / (1 + 0.6 * k) * (220 / max(f, 80)) ** 0.3
        y += amp * np.sin(2 * np.pi * fk * t) * np.exp(-t / dec)
    y *= np.minimum(1, t / 0.004)
    rel = np.ones(n)
    off = int(d * SR)
    if off < n:
        rel[off:] = np.exp(-(np.arange(n - off) / SR) / 0.25)
    return y * rel * vel * 0.35


def inst_pad(f, d, bright=0.5, detune=0.004):
    t = tarr(d)
    y = np.zeros(len(t))
    for dt in (-detune, 0, detune):
        ff = f * (1 + dt)
        for k in range(1, 8):
            y += np.sin(2 * np.pi * ff * k * t + RNG.uniform(0, 6.28)) / k * (bright ** (k - 1))
    y *= env_adsr(len(t), a=min(1.2, d * 0.3), d=0.5, s=0.85, r=min(1.5, d * 0.4))
    return y * 0.08


def inst_pluck(f, d, damp=0.996):
    n = int((d + 0.5) * SR)
    N = max(2, int(SR / f))
    buf = RNG.uniform(-1, 1, N)
    out = np.zeros(n)
    # Karplus-Strong (vektorizovaně po blocích periody)
    prev = buf.copy()
    pos = 0
    while pos < n:
        m = min(N, n - pos)
        out[pos:pos + m] = prev[:m]
        nxt = damp * 0.5 * (prev + np.roll(prev, -1))
        prev = nxt
        pos += N
    return lowpass(out, 5000) * 0.3


def inst_bell(f, d, vel=0.6):
    n = int((d + 2.5) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for ratio, amp, dec in ((1, 1, 2.2), (2.76, 0.45, 1.2), (5.4, 0.25, 0.6), (8.9, 0.1, 0.3)):
        y += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t / dec)
    return y * np.minimum(1, t / 0.002) * vel * 0.18


def inst_bass(f, d, vel=0.8):
    t = tarr(d + 0.1)
    y = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sign(np.sin(2 * np.pi * f * t))
    y = lowpass(y, 700)
    return y * env_adsr(len(t), 0.005, 0.15, 0.6, 0.08) * vel * 0.28


def inst_string(f, d, vel=0.7):
    t = tarr(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.6)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    y = np.zeros(len(t))
    for k in range(1, 10):
        y += np.sin(k * ph) / k * (0.75 ** k)
    y = lowpass(y, 4500)
    return y * env_adsr(len(t), min(0.4, d * 0.3), 0.2, 0.8, min(0.6, d * 0.3)) * vel * 0.12


def inst_whistle(f, d, vel=0.7):
    t = tarr(d)
    vib = 1 + 0.012 * np.sin(2 * np.pi * 5.8 * t) * np.minimum(1, t / 0.25)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    y = np.sin(ph) + 0.05 * np.sin(2 * ph)
    breath = bandpass(RNG.normal(0, 1, len(t)), f * 0.8, min(f * 1.4, 14000)) * 0.12
    return (y + breath) * env_adsr(len(t), 0.05, 0.05, 0.9, 0.08) * vel * 0.22


def kick(vel=1.0):
    t = tarr(0.5)
    f = 110 * np.exp(-t * 18) + 42
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return y * vel * 0.7


def snare(vel=1.0):
    t = tarr(0.3)
    y = RNG.normal(0, 1, len(t)) * np.exp(-t * 20) * 0.5 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.4
    return bandpass(y, 150, 8000) * vel * 0.5


def tom(f=90, vel=1.0):
    t = tarr(0.6)
    ff = f * (1 + 0.5 * np.exp(-t * 12))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 5) * vel * 0.6


def hat(vel=1.0):
    t = tarr(0.08)
    return highpass(RNG.normal(0, 1, len(t)), 7000) * np.exp(-t * 60) * vel * 0.15


def boom(vel=1.0):
    t = tarr(4.0)
    f = 60 * np.exp(-t * 1.5) + 28
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.1)
    y += lowpass(RNG.normal(0, 1, len(t)), 300) * np.exp(-t * 2.5) * 0.6
    return y * vel * 0.9


def add(buf, x, at, gain=1.0, p=0.0):
    i = int(at * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    if x.ndim == 1:
        x = pan(x, p)
    j = min(len(buf), i + len(x))
    s = max(0, -i)
    buf[i + s:j] += x[s:j - i] * gain


# ------------------------------------------------------------- hudební skladba

NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def chord(name, octave=4):
    """'Am', 'F', 'C', 'G', 'Dm7', 'E', 'Bdim', 'Fmaj7', 'Asus2'"""
    root = name[0] + (name[1] if len(name) > 1 and name[1] in '#b' else '')
    rest = name[len(root):]
    r = 12 * (octave + 1) + NOTE[root]
    if rest.startswith('m') and not rest.startswith('maj'):
        iv = [0, 3, 7]
        rest = rest[1:]
    elif rest.startswith('dim'):
        iv = [0, 3, 6]
        rest = rest[3:]
    elif rest.startswith('sus2'):
        iv = [0, 2, 7]
        rest = rest[4:]
    elif rest.startswith('sus4'):
        iv = [0, 5, 7]
        rest = rest[4:]
    else:
        iv = [0, 4, 7]
    if rest == '7':
        iv.append(10)
    elif rest == 'maj7':
        iv.append(11)
    elif rest == 'add9':
        iv.append(14)
    return [r + i for i in iv]


# leitmotiv vraha (pískaná melodie): (midi, délka v dobách)
MOTIF = [(69, 1), (72, 1), (76, 2), (74, 1), (72, 1), (71, 2), (69, 1), (71, 0.5), (72, 0.5), (74, 1), (76, 1),
         (77, 1.5), (76, 0.5), (74, 1), (71, 1), (69, 3)]


def motif_notes(transpose=0, beat=0.5):
    t = 0
    for n, b in MOTIF:
        yield t, n + transpose, b * beat
        t += b * beat


class Cue:
    def __init__(self, dur):
        self.dur = dur
        self.buf = np.zeros((int((dur + 4) * SR), 2), np.float32)

    def note(self, fn, f, at, d, gain=1.0, p=0.0, **kw):
        if at > self.dur:
            return
        add(self.buf, fn(f, d, **kw), at, gain, p)

    def hit(self, x, at, gain=1.0, p=0.0):
        if at > self.dur:
            return
        add(self.buf, x, at, gain, p)


def prog_loop(prog, bar, dur):
    t = 0.0
    i = 0
    while t < dur:
        yield t, prog[i % len(prog)], i
        t += bar
        i += 1


def drone(c, freqs, gain=1.0, bright=0.3):
    for f in freqs:
        seg = 8.0
        t = 0
        while t < c.dur:
            c.note(inst_pad, f, t, seg + 2, gain, RNG.uniform(-0.5, 0.5), bright=bright)
            t += seg


def cue_prolog(d):
    c = Cue(d)
    drone(c, [midi(33), midi(40), midi(45.3)], 1.4, 0.25)
    t = 4.0
    while t < d - 6:
        for at, n, ln in motif_notes(12, 0.42):
            c.note(inst_bell, midi(n), t + at, ln, 0.9, 0.3)
        t += 16
    for i in range(int(d / 3)):
        c.note(inst_string, midi(RNG.choice([81, 82, 88])), i * 3 + 1, 3, 0.25, RNG.uniform(-0.8, 0.8))
    return c


def cue_home(d):
    c = Cue(d)
    prog = ['C', 'Am', 'F', 'G', 'C', 'Em', 'F', 'G']
    bar = 2.4
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 4)
        c.note(inst_bass, midi(notes[0] - 24), t, bar * 0.9, 0.8)
        for k, n in enumerate([notes[0], notes[1], notes[2], notes[1] + 12, notes[2], notes[1]]):
            c.note(inst_piano, midi(n), t + k * bar / 6, bar / 6, 0.55, -0.2 + 0.1 * k)
        if i % 2 == 0:
            mel = [notes[2] + 12, notes[1] + 12, notes[0] + 12, notes[1] + 12]
            for k, n in enumerate(mel):
                c.note(inst_piano, midi(n), t + k * bar / 4 + 0.05, bar / 4, 0.4, 0.3)
    return c


def cue_window(d):
    c = Cue(d)
    prog = ['Dm', 'Dm', 'G', 'Am']
    bar = 2.0
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 3)
        c.note(inst_pad, midi(notes[0]), t, bar + 0.5, 0.6, -0.3, bright=0.3)
        c.note(inst_pad, midi(notes[2]), t, bar + 0.5, 0.5, 0.3, bright=0.3)
        pat = [0, 2, 1, 2, 0, 2, 1, 2]
        for k in range(8):
            if RNG.random() < 0.85:
                c.note(inst_pluck, midi(notes[pat[k]] + 12), t + k * bar / 8, 0.3, 0.6, RNG.uniform(-0.6, 0.6))
        c.note(inst_bass, midi(notes[0] - 12), t, 0.4, 0.7)
        c.note(inst_bass, midi(notes[0] - 12), t + bar / 2, 0.3, 0.5)
    return c


def cue_suspense(d, dark=False):
    c = Cue(d)
    base = 38 if not dark else 33
    drone(c, [midi(base), midi(base + 1), midi(base + 7)], 1.3, 0.35)
    beat = 0.5
    n = int(d / beat)
    for i in range(n):
        t = i * beat
        if dark:
            if i % 4 == 0:
                c.hit(kick(0.5), t, 0.8)
                c.hit(kick(0.35), t + 0.25, 0.8)
        else:
            c.note(inst_bass, midi(base + (0 if (i // 8) % 2 == 0 else 1)), t, 0.25, 0.55)
        if i % 16 == 8:
            c.note(inst_string, midi(base + 36 + RNG.choice([0, 1, 6])), t, 4, 0.35, RNG.uniform(-0.7, 0.7))
    # postupné crescendo
    k = np.linspace(0.5, 1.0, len(c.buf))[:, None]
    c.buf *= k
    return c


def cue_school(d):
    c = Cue(d)
    prog = ['F', 'C', 'Dm', 'Bb']
    bar = 2.0
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 4)
        for k in range(4):
            c.note(inst_pluck, midi(notes[k % 3]), t + k * 0.5, 0.4, 0.5, -0.4 + 0.25 * k)
            c.note(inst_bass, midi(notes[0] - 24), t + k * 0.5, 0.2, 0.45)
        c.note(inst_string, midi(notes[1] + 12), t, bar, 0.25, 0.2)
    return c


def cue_tension_soft(d):
    c = Cue(d)
    prog = ['Am', 'Fmaj7', 'Dm', 'E']
    bar = 4.0
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 3)
        for k, n in enumerate(notes):
            c.note(inst_pad, midi(n), t, bar + 1, 0.55, -0.4 + 0.4 * k, bright=0.25)
        for k in range(3):
            if RNG.random() < 0.7:
                c.note(inst_piano, midi(RNG.choice(notes) + 12), t + 0.4 + k * 1.3, 1.2, 0.35, RNG.uniform(-0.5, 0.5))
    return c


def cue_garage(d):
    c = Cue(d)
    drone(c, [midi(31), midi(43), midi(44)], 1.4, 0.4)
    beat = 0.375
    for i in range(int(d / beat)):
        t = i * beat
        c.hit(hat(0.8 if i % 2 == 0 else 0.4), t, 1.0, 0.3)
        if i % 8 == 0:
            c.hit(kick(0.4), t, 0.8)
    # stoupající cluster
    for k in range(int(d / 6)):
        c.note(inst_string, midi(67 + k % 6), k * 6, 6.5, 0.3 + 0.03 * k, RNG.uniform(-0.6, 0.6))
    c.buf *= np.linspace(0.6, 1.0, len(c.buf))[:, None]
    return c


def cue_chase(d):
    c = Cue(d)
    bpm = 150
    beat = 60 / bpm
    prog = [45, 45, 46, 43]
    for i in range(int(d / beat * 4)):
        t = i * beat / 4
        root = prog[(i // 16) % 4]
        c.note(inst_bass, midi(root - 12 + (12 if i % 4 == 2 else 0)), t, beat / 4, 0.6)
        if i % 4 == 0:
            c.hit(kick(0.9 if i % 16 == 0 else 0.6), t)
        if i % 8 == 4:
            c.hit(snare(0.8), t)
        c.hit(hat(0.5), t, 1, 0.4)
        if i % 16 == 0:
            for n in chord('Am' if root == 45 else ('Bb' if root == 46 else 'G'), 4):
                c.note(inst_string, midi(n), t, beat * 4, 0.4, RNG.uniform(-0.6, 0.6))
    return c


def cue_dream(d):
    c = Cue(d)
    for i in range(int(d / 3)):
        f = midi(RNG.choice([57, 60, 63, 66, 69])) * (1 + 0.03 * math.sin(i))
        c.note(inst_pad, f, i * 3, 6, 0.9, RNG.uniform(-1, 1), bright=0.5, detune=0.02)
    t = 2
    while t < d:
        for at, n, ln in motif_notes(12, 0.6):
            c.note(inst_bell, midi(n) * (1 + 0.02 * math.sin(at * 3)), t + at, ln, 0.6, math.sin(at))
        t += 14
    return c


def cue_hospital(d):
    c = Cue(d)
    drone(c, [midi(64), midi(71), midi(76)], 0.6, 0.15)
    for i in range(int(d / 2)):
        c.note(inst_bell, midi(RNG.choice([76, 79, 83])), i * 2 + 0.5, 1, 0.25, RNG.uniform(-0.7, 0.7))
    return c


def cue_drama(d):
    c = Cue(d)
    prog = ['Am', 'F', 'C', 'G', 'Am', 'F', 'E', 'E']
    bar = 3.2
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 3)
        for k, n in enumerate(notes):
            c.note(inst_string, midi(n), t, bar + 0.3, 0.6, -0.5 + 0.5 * k)
        c.note(inst_string, midi(notes[0] - 12), t, bar + 0.3, 0.6)
        for k in range(4):
            c.note(inst_piano, midi(notes[(k * 2) % 3] + 12), t + k * bar / 4, bar / 4, 0.4, 0.2)
    return c


def cue_sad(d):
    c = Cue(d)
    prog = ['Am', 'Em', 'F', 'C', 'Dm', 'Am', 'E', 'Am']
    bar = 3.0
    mel = [76, 74, 72, 71, 72, 69, 68, 69]
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 3)
        for k in range(6):
            c.note(inst_piano, midi(notes[k % 3] + (12 if k > 2 else 0)), t + k * bar / 6, bar / 6, 0.4, -0.3)
        c.note(inst_piano, midi(mel[i % len(mel)]), t, bar * 0.8, 0.6, 0.2)
    return c


def cue_hope(d):
    c = Cue(d)
    prog = ['F', 'C', 'Dm', 'Bb', 'F', 'C', 'Bb', 'C']
    bar = 3.0
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 3)
        for k, n in enumerate(notes):
            c.note(inst_string, midi(n + 12), t, bar + 0.4, 0.45, -0.5 + 0.5 * k)
        for k in range(8):
            c.note(inst_piano, midi(notes[k % 3] + 12 * (k // 3 % 2) + 12), t + k * bar / 8, bar / 8, 0.32,
                   -0.3 + 0.08 * k)
        c.note(inst_bass, midi(notes[0] - 12), t, bar * 0.9, 0.5)
    return c


def cue_investigation(d):
    c = Cue(d)
    prog = ['Dm', 'Dm', 'Bb', 'A']
    bar = 2.4
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 3)
        for k in range(8):
            c.note(inst_pluck, midi(notes[[0, 1, 2, 1][k % 4]] + 12), t + k * bar / 8, 0.25, 0.5,
                   -0.5 if k % 2 else 0.5)
        c.note(inst_bass, midi(notes[0] - 12), t, bar * 0.45, 0.6)
        c.note(inst_bass, midi(notes[0] - 12), t + bar * 0.75, bar * 0.2, 0.5)
        c.note(inst_pad, midi(notes[1]), t, bar + 0.5, 0.35, 0, bright=0.2)
        c.hit(hat(0.6), t + bar * 0.5, 1, 0.3)
    return c


def cue_race(d):
    c = Cue(d)
    bpm = 120
    beat = 60 / bpm
    prog = ['Em', 'C', 'D', 'Bm']
    for i in range(int(d / beat * 2)):
        t = i * beat / 2
        ch = chord(prog[(i // 8) % 4], 3)
        c.note(inst_bass, midi(ch[0] - 12), t, beat / 2 * 0.8, 0.6)
        if i % 2 == 0:
            c.hit(kick(0.5), t)
        c.hit(hat(0.4), t + beat / 4, 1, -0.3)
        if i % 8 == 0:
            for n in ch:
                c.note(inst_pad, midi(n + 12), t, beat * 4, 0.5, RNG.uniform(-0.5, 0.5), bright=0.4)
    for at, n, ln in motif_notes(-12, 0.75):
        c.note(inst_string, midi(n), 8 + at, ln, 0.4, 0)
    return c


def cue_bunker(d):
    c = Cue(d)
    drone(c, [midi(29), midi(35), midi(41)], 1.5, 0.3)
    for i in range(int(d / 4)):
        c.note(inst_bell, midi(RNG.choice([30, 31, 37])), i * 4 + RNG.uniform(0, 2), 3, 0.7, RNG.uniform(-1, 1))
        if i % 3 == 0:
            c.hit(boom(0.4), i * 4)
    return c


def cue_climax(d):
    c = Cue(d)
    bpm = 160
    beat = 60 / bpm
    prog = ['Am', 'F', 'G', 'E']
    for i in range(int(d / beat * 2)):
        t = i * beat / 2
        ch = chord(prog[(i // 8) % 4], 3)
        c.note(inst_bass, midi(ch[0] - 12), t, beat / 2 * 0.9, 0.75)
        c.note(inst_string, midi(ch[i % 3] + 12), t, beat / 2, 0.35, 0.4 * (-1) ** i)
        if i % 4 == 0:
            c.hit(tom(80, 1.0), t)
        if i % 4 == 2:
            c.hit(snare(0.9), t)
        if i % 16 == 0:
            for n in ch:
                c.note(inst_pad, midi(n - 12), t, beat * 8, 1.0, 0, bright=0.8)
                c.note(inst_string, midi(n + 12), t, beat * 8, 0.5, RNG.uniform(-0.5, 0.5))
    return c


def cue_finale(d):
    c = Cue(d)
    prog = ['C', 'G', 'Am', 'F']
    bar = 2.8
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 3)
        for k, n in enumerate(notes):
            c.note(inst_string, midi(n + 12), t, bar + 0.4, 0.4, -0.5 + 0.5 * k)
        c.note(inst_bass, midi(notes[0] - 12), t, bar, 0.5)
    t = 4
    while t < d:
        for at, n, ln in motif_notes(3, 0.7):   # motiv v dur
            c.note(inst_piano, midi(n + 12), t + at, ln, 0.5, 0.2)
        t += 20
    return c


def cue_epilog(d):
    c = Cue(d)
    t = 1
    k = 0
    while t < d:
        det = 1 + 0.004 * k * k
        for at, n, ln in motif_notes(15, 0.55):
            c.note(inst_bell, midi(n) * det, t + at, ln, 0.6, 0.2)
        t += 12
        k += 1
    drone(c, [midi(48), midi(55)], 0.5, 0.2)
    return c


def cue_credits(d):
    c = Cue(d)
    prog = ['Am', 'F', 'C', 'G', 'Am', 'F', 'E', 'E']
    bar = 2.4
    for t, ch, i in prog_loop(prog, bar, d):
        notes = chord(ch, 3)
        c.note(inst_bass, midi(notes[0] - 12), t, bar * 0.9, 0.6)
        for k in range(8):
            c.note(inst_piano, midi(notes[k % 3] + 12), t + k * bar / 8, bar / 8, 0.3, -0.3 + 0.08 * k)
        for k, n in enumerate(notes):
            c.note(inst_string, midi(n + 12), t, bar + 0.3, 0.35, -0.5 + 0.5 * k)
        if i % 2 == 0:
            c.hit(kick(0.5), t)
            c.hit(kick(0.4), t + bar / 2)
    t = 2.4
    while t < d - 8:
        for at, n, ln in motif_notes(0, 0.6):
            c.note(inst_whistle, midi(n + 12), t + at, ln * 0.95, 0.9, 0)
        t += 19.2
    return c


CUES = {
    'prolog': cue_prolog, 'home': cue_home, 'window': cue_window, 'suspense1': cue_suspense,
    'suspense2': lambda d: cue_suspense(d, True), 'school': cue_school, 'tension_soft': cue_tension_soft,
    'garage': cue_garage, 'chase': cue_chase, 'dream': cue_dream, 'hospital': cue_hospital, 'drama': cue_drama,
    'sad': cue_sad, 'hope': cue_hope, 'investigation': cue_investigation, 'race': cue_race, 'bunker': cue_bunker,
    'climax': cue_climax, 'finale': cue_finale, 'epilog': cue_epilog, 'credits': cue_credits,
}
CUE_GAIN = {'home': 0.8, 'school': 0.8, 'window': 0.8, 'hope': 0.85, 'sad': 0.9, 'credits': 1.1, 'chase': 0.8,
            'climax': 0.85}


def render_cue(name, dur):
    c = CUES[name](dur)
    out = reverb(c.buf, 2.4, 0.35, seed=3)
    pk = np.abs(out).max() + 1e-9
    return out / pk * 0.5 * CUE_GAIN.get(name, 1.0)


# ------------------------------------------------------------- ruchy

def noise(d, color='white'):
    x = RNG.normal(0, 1, int(d * SR))
    if color == 'pink':
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        x = signal.lfilter(b, a, x) * 4
    elif color == 'brown':
        x = np.cumsum(x)
        x = highpass(x, 20)
        x /= np.abs(x).max() + 1e-9
    return x


def fade(x, a=0.005, r=0.02):
    n = len(x)
    ai, ri = int(a * SR), int(r * SR)
    if ai:
        x[:ai] *= np.linspace(0, 1, ai)
    if ri and ri < n:
        x[-ri:] *= np.linspace(1, 0, ri)
    return x


def sfx_door():
    t = tarr(0.9)
    creak = np.sin(2 * np.pi * (300 + 80 * np.sin(t * 9)) * t) * np.exp(-t * 3) * 0.15
    thud = lowpass(noise(0.9), 200) * np.exp(-np.maximum(0, t - 0.55) * 20) * (t > 0.55) * 0.9
    return fade(creak * (t < 0.55) + thud)


def sfx_door_creak():
    t = tarr(1.6)
    f = 220 + 140 * np.sin(t * 3.0) + 30 * np.sin(t * 37)
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.08
    return fade(bandpass(y, 300, 3000) * np.minimum(1, t * 4) * np.exp(-t * 0.8))


def sfx_doorbell():
    out = np.zeros(int(1.6 * SR))
    for at, f in ((0, 880), (0.45, 698)):
        add2(out, inst_bell(f, 0.8, 1.0) * 1.5, at)
    return out


def add2(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(x))
    buf[i:j] += x[:j - i] * g


def sfx_knock():
    out = np.zeros(int(1.4 * SR))
    for k in range(3):
        t = tarr(0.15)
        add2(out, lowpass(noise(0.15), 600) * np.exp(-t * 40), 0.1 + k * 0.28, 1.0)
    return out


def sfx_footsteps(n=8, gap=0.45):
    out = np.zeros(int((n * gap + 0.5) * SR))
    for k in range(n):
        t = tarr(0.2)
        add2(out, lowpass(noise(0.2), 900) * np.exp(-t * 30), k * gap + RNG.uniform(0, 0.04), 0.6)
    return out


def sfx_pin():
    t = tarr(0.4)
    y = lowpass(noise(0.4), 2500) * np.exp(-t * 40) * 0.6 + np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 30) * 0.1
    return y


def sfx_whistle():
    out = np.zeros(int(8 * SR))
    for at, n, ln in motif_notes(12, 0.42):
        add2(out, inst_whistle(midi(n), ln * 0.95, 1.0) * 2.5, at)
    return out


def sfx_whistle_ref():
    t = tarr(1.2)
    f = 2900 + 150 * np.sign(np.sin(2 * np.pi * 30 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    return fade(y * env_adsr(len(t), 0.02, 0.1, 0.9, 0.1))


def sfx_thermometer():
    out = np.zeros(int(1.2 * SR))
    for k in range(3):
        add2(out, np.sin(2 * np.pi * 3200 * tarr(0.12)) * 0.2, k * 0.25)
    return out


def sfx_sip():
    t = tarr(0.8)
    return bandpass(noise(0.8), 800, 4000) * (np.sin(t * 25) ** 2) * np.exp(-t * 3) * 0.3


def sfx_garage(open_=True):
    t = tarr(3.0)
    y = bandpass(noise(3.0), 80, 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)) * 0.5
    clunk = lowpass(noise(3.0), 300) * np.exp(-np.abs(t - 2.8) * 30) * 1.2
    return fade(y * env_adsr(len(t), 0.1, 0.1, 1, 0.3) + clunk)


def sfx_clock_tick():
    out = np.zeros(int(4 * SR))
    for k in range(4):
        add2(out, highpass(noise(0.03), 2000) * np.exp(-tarr(0.03) * 150) * 0.6, k)
    return out


def sfx_coffee():
    t = tarr(3.0)
    y = bandpass(noise(3.0), 200, 3000) * (0.5 + 0.5 * np.sin(t * 40) ** 2) * 0.25
    return fade(y * env_adsr(len(t), 0.2, 0.1, 1, 0.5))


def sfx_fire():
    t = tarr(6.0)
    y = lowpass(noise(6.0, 'brown'), 800) * 0.5
    for k in range(60):
        add2(y, highpass(noise(0.02), 1500) * RNG.uniform(0.2, 0.8), RNG.uniform(0, 5.9))
    return fade(y * env_adsr(len(t), 1.0, 0.1, 1, 1.0))


def sfx_car_start():
    t = tarr(4.0)
    f = 35 + 15 * np.minimum(1, t / 1.5) + 4 * np.sin(t * 3)
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3
    y = lowpass(y, 400) + lowpass(noise(4.0), 300) * 0.2
    return fade(y * env_adsr(len(t), 0.3, 0.2, 0.8, 1.5))


def sfx_car_door():
    t = tarr(0.6)
    return lowpass(noise(0.6), 500) * np.exp(-t * 18) + highpass(noise(0.6), 3000) * np.exp(-t * 60) * 0.3


def sfx_owl():
    out = np.zeros(int(2.5 * SR))
    for at, d_ in ((0, 0.35), (0.6, 0.25), (0.95, 0.6)):
        t = tarr(d_)
        f = 420 - 40 * t / d_
        add2(out, np.sin(2 * np.pi * np.cumsum(f) / SR) * env_adsr(len(t), 0.05, 0.05, 0.8, 0.15) * 0.25, at)
    return out


def sfx_notify():
    out = np.zeros(int(0.8 * SR))
    add2(out, inst_bell(1318, 0.2, 1.0), 0)
    add2(out, inst_bell(1760, 0.3, 1.0), 0.12)
    return out


def sfx_focus():
    t = tarr(0.25)
    return highpass(noise(0.25), 1500) * np.exp(-t * 50) * 0.3 + np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 80) * 0.1


def sfx_hit():
    y = boom(1.0)
    t = tarr(4.0)
    y += highpass(noise(4.0), 2000) * np.exp(-t * 6) * 0.25
    return y


def sfx_camera():
    t = tarr(0.3)
    y = highpass(noise(0.3), 2000) * (np.exp(-t * 60) + 0.6 * np.exp(-np.maximum(0, t - 0.12) * 60) * (t > 0.12))
    return y * 0.5


def sfx_freezer():
    t = tarr(4.0)
    y = (np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 200 * t) + 0.3 * np.sin(2 * np.pi * 300 * t)) * 0.12
    return fade(y * env_adsr(len(t), 0.5, 0.1, 1, 0.8))


def sfx_freezer_open():
    t = tarr(1.0)
    return fade(lowpass(noise(1.0), 1500) * np.exp(-t * 6) * 0.5 + sfx_freezer()[:len(t)] * 0.3)


def sfx_freezer_close():
    t = tarr(0.6)
    return lowpass(noise(0.6), 400) * np.exp(-t * 20)


def sfx_dog():
    out = np.zeros(int(1.0 * SR))
    for at in (0, 0.35):
        t = tarr(0.22)
        f = 500 * np.exp(-t * 4) + 300
        y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + noise(0.22) * 0.3
        y = bandpass(y, 300, 2500) * env_adsr(len(t), 0.01, 0.05, 0.7, 0.08)
        add2(out, y * 0.6, at)
    return out


def sfx_key():
    out = np.zeros(int(1.0 * SR))
    for k in range(6):
        add2(out, inst_bell(RNG.uniform(3000, 6000), 0.05, 0.6) * 0.6, RNG.uniform(0, 0.6))
    return out


def sfx_paper():
    t = tarr(1.2)
    return fade(highpass(noise(1.2), 2500) * (RNG.random(len(t)) > 0.7) * 0.3 * np.sin(np.pi * t / 1.2))


def sfx_bubble():
    out = np.zeros(int(3 * SR))
    for k in range(25):
        t = tarr(0.08)
        f = RNG.uniform(400, 1200) * (1 + t * 8)
        add2(out, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.15, RNG.uniform(0, 2.9))
    return out


def sfx_phone():
    out = np.zeros(int(3 * SR))
    for r in range(2):
        for k in range(10):
            add2(out, np.sin(2 * np.pi * 1400 * tarr(0.05)) * 0.2, r * 1.4 + k * 0.06)
    return out


def sfx_phone_send():
    t = tarr(0.5)
    f = 400 + 1600 * t / 0.5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.5) * 0.15


def sfx_call_end():
    out = np.zeros(int(0.8 * SR))
    for k, f in enumerate((660, 440)):
        add2(out, np.sin(2 * np.pi * f * tarr(0.15)) * 0.2, k * 0.2)
    return out


def sfx_heartbeat():
    out = np.zeros(int(4 * SR))
    for k in range(4):
        add2(out, kick(0.8), k * 0.9)
        add2(out, kick(0.5), k * 0.9 + 0.25)
    return lowpass(out, 150) * 1.5


def sfx_sirens():
    t = tarr(10.0)
    f = 700 + 300 * np.sign(np.sin(2 * np.pi * 0.7 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15
    return fade(y * np.minimum(1, t / 4) * 0.8, 0.01, 1.0)


def sfx_splash():
    t = tarr(2.5)
    y = lowpass(noise(2.5), 3000) * np.exp(-t * 2.5) * 0.8 + lowpass(noise(2.5), 200) * np.exp(-t * 8) * 1.0
    return y


def sfx_crack():
    t = tarr(1.5)
    y = highpass(noise(1.5), 500) * np.exp(-t * 8) * 0.5
    for k in range(10):
        add2(y, lowpass(noise(0.1), 800) * np.exp(-tarr(0.1) * 30) * 0.6, RNG.uniform(0, 1.3))
    return y


def sfx_struggle():
    out = np.zeros(int(2.5 * SR))
    for k in range(7):
        add2(out, lowpass(noise(0.25), 400) * np.exp(-tarr(0.25) * 15) * RNG.uniform(0.4, 1.0), RNG.uniform(0, 2.2))
    return out


def sfx_handcuffs():
    out = np.zeros(int(1.0 * SR))
    for k in range(5):
        add2(out, highpass(noise(0.03), 3000) * 0.5, 0.1 + k * 0.05)
        add2(out, inst_bell(4200, 0.03, 0.3)[:int(0.5 * SR)], 0.1 + k * 0.05)
    return out


SFX = {
    'door': sfx_door, 'door_creak': sfx_door_creak, 'doorbell': sfx_doorbell, 'knock': sfx_knock,
    'footsteps': sfx_footsteps, 'pin': sfx_pin, 'whistle': sfx_whistle, 'whistle_ref': sfx_whistle_ref,
    'thermometer': sfx_thermometer, 'sip': sfx_sip, 'garage_close': lambda: sfx_garage(False),
    'garage_open': sfx_garage, 'clock_tick': sfx_clock_tick, 'coffee': sfx_coffee, 'fire': sfx_fire,
    'car_start': sfx_car_start, 'car_door': sfx_car_door, 'owl': sfx_owl, 'notify': sfx_notify,
    'focus': sfx_focus, 'hit': sfx_hit, 'camera': sfx_camera, 'freezer': sfx_freezer,
    'freezer_open': sfx_freezer_open, 'freezer_close': sfx_freezer_close, 'dog': sfx_dog, 'key': sfx_key,
    'paper': sfx_paper, 'bubble': sfx_bubble, 'phone': sfx_phone, 'phone_send': sfx_phone_send,
    'call_end': sfx_call_end, 'heartbeat': sfx_heartbeat, 'sirens': sfx_sirens, 'splash': sfx_splash,
    'crack': sfx_crack, 'struggle': sfx_struggle, 'handcuffs': sfx_handcuffs,
}
SFX_GAIN = {'whistle': 0.8, 'hit': 0.9, 'sirens': 0.7, 'heartbeat': 1.0, 'car_start': 0.7, 'fire': 0.6,
            'freezer': 0.5, 'footsteps': 0.8}


# ------------------------------------------------------------- atmosféry

def amb(name, d):
    n = int(d * SR)
    if name == 'none' or d <= 0:
        return np.zeros(n)
    if name == 'day':
        y = lowpass(noise(d, 'pink'), 500) * 0.05
        for k in range(int(d / 2.5)):
            at = RNG.uniform(0, d - 0.5)
            t = tarr(0.15)
            f = RNG.uniform(2500, 4500) * (1 + 0.3 * np.sin(t * 60))
            add2(y, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 15) * 0.05, at)
        return y
    if name == 'night':
        y = lowpass(noise(d, 'brown'), 300) * 0.12 + lowpass(noise(d, 'pink'), 1500) * 0.015
        for k in range(int(d / 20)):
            add2(y, sfx_dog() * 0.08, RNG.uniform(0, max(0.1, d - 1.5)))
        return y
    if name == 'rain':
        y = bandpass(noise(d, 'pink'), 400, 9000) * 0.12
        for k in range(int(d * 12)):
            add2(y, highpass(noise(0.01), 3000) * 0.08, RNG.uniform(0, d - 0.02))
        return y
    if name == 'clock':
        y = np.zeros(n)
        for k in range(int(d)):
            add2(y, highpass(noise(0.03), 2000) * np.exp(-tarr(0.03) * 150) * (0.25 if k % 2 else 0.18), k + 0.01)
        return y
    if name == 'room':
        return lowpass(noise(d, 'pink'), 400) * 0.03
    if name == 'hospital':
        y = lowpass(noise(d, 'pink'), 600) * 0.03 + np.sin(2 * np.pi * 120 * tarr(d)) * 0.01
        for k in range(int(d / 1.1)):
            add2(y, np.sin(2 * np.pi * 1000 * tarr(0.09)) * 0.04, k * 1.1)
        return y
    if name == 'forest':
        t = tarr(d)
        y = bandpass(noise(d, 'pink'), 200, 2000) * (0.06 + 0.04 * np.sin(2 * np.pi * 0.07 * t))
        for k in range(int(d / 25)):
            add2(y, sfx_owl() * 0.3, RNG.uniform(0, max(0.1, d - 3)))
        return y
    if name == 'bunker':
        y = lowpass(noise(d, 'brown'), 120) * 0.15
        for k in range(int(d / 1.7)):
            add2(y, inst_bell(RNG.uniform(1500, 2500), 0.05, 0.5) * 0.5, RNG.uniform(0, d - 0.5))
        return y
    if name == 'garage':
        t = tarr(d)
        return (np.sin(2 * np.pi * 100 * t) * 0.02 + np.sin(2 * np.pi * 200 * t) * 0.01 +
                lowpass(noise(d, 'pink'), 300) * 0.03)
    if name == 'school':
        y = bandpass(noise(d, 'pink'), 300, 2500) * 0.03
        t = tarr(d)
        y *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.4 * t) * np.sin(2 * np.pi * 0.13 * t)
        return y
    return np.zeros(n)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    data = (x * 32767).astype('<i2')
    ch = 1 if x.ndim == 1 else x.shape[1]
    with wave.open(path, 'wb') as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def read_wav(path):
    with wave.open(path, 'rb') as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(1)
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    return x


# ------------------------------------------------------------- voice FX

PHONE = {'13': {'BEATA'}, '14': {'VIKTOR', 'BEATA'}, '25': {'PAZDERA'}, '26': {'BURES'}}
MUFFLED = {'29': {'SEBESTOVA'}}
ECHO = {'17': None, '24': {'SEBESTOVA', 'SIMON', 'KUNESOVA'}}


def voice_fx(x, scene_id, L):
    who, vo = L['who'], L['vo']
    if who == 'RADIO':
        y = bandpass(x, 350, 3200, 3)
        y = np.tanh(y * 3) * 0.5 + noise(len(y) / SR) * 0.01
        return pan(y, 0)
    if vo and who in PHONE.get(scene_id, ()):
        y = bandpass(x, 400, 3400, 3)
        return pan(np.tanh(y * 2) * 0.7, 0)
    if vo and who in MUFFLED.get(scene_id, ()):
        return pan(lowpass(x, 900) * 1.3, 0.2)
    if scene_id in ECHO and (ECHO[scene_id] is None or who in ECHO[scene_id]) and vo:
        return reverb(x, 3.0, 0.55, seed=9)
    if vo:
        return pan(x, 0)
    return reverb(x, 0.6, 0.12, seed=5)


def mix(tl, voice_dir, out_path, total):
    n = int((total + 2) * SR)
    voice = np.zeros((n, 2), np.float32)
    import json
    man = json.load(open(os.path.join(voice_dir, 'manifest.json')))
    for S in tl:
        for L in S.lines:
            m = man.get(L['key'])
            if not m:
                continue
            x = read_wav(os.path.join(voice_dir, m['file']))
            add(voice, voice_fx(x, S.id, L), L['start'], 1.0)
    # „shout“ ze scény 23
    shout_p = os.path.join(voice_dir, 'shout.wav')
    # obálka hlasu pro ducking
    venv = np.abs(voice).mean(1)
    venv = signal.lfilter([1], [1, -0.9995], venv) * 0.0005
    venv = np.convolve(venv, np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
    duck = 1.0 - np.clip(venv / (np.percentile(venv[venv > 1e-4], 50) + 1e-6), 0, 1) * 0.6
    print('voice ok', flush=True)

    music = np.zeros((n, 2), np.float32)
    runs = []
    cur = None
    for S in tl:
        for t, cue in S.music:
            if cur:
                runs.append((cur[0], cur[1], t))
            cur = None if cue == 'off' else (cue, t)
    if cur:
        runs.append((cur[0], cur[1], total))
    for cue, t0, t1 in runs:
        d = t1 - t0
        y = render_cue(cue, d + 2.5)
        # fade in/out
        fi = int(1.0 * SR)
        y[:fi] *= np.linspace(0, 1, fi)[:, None]
        e0 = int((d + 0.0) * SR)
        fo = int(2.5 * SR)
        y[e0:e0 + fo] *= np.linspace(1, 0, min(fo, len(y) - e0))[:, None] if e0 < len(y) else 1
        y[e0 + fo:] = 0
        add(music, y, t0, 1.0)
        print('music', cue, round(d, 1), flush=True)
    music *= duck[:, None]

    fx = np.zeros((n, 2), np.float32)
    for S in tl:
        for t, name in S.sfx:
            if name == 'shout' and os.path.exists(shout_p):
                x = lowpass(read_wav(shout_p), 1200) * 0.8
                add(fx, reverb(x, 1.5, 0.5), t, 0.7)
                continue
            fn = SFX.get(name)
            if fn:
                add(fx, fn(), t, SFX_GAIN.get(name, 0.8), RNG.uniform(-0.3, 0.3))
        # atmosféra — po scénách, persistentní
    amb_runs = []
    cur = None
    for S in tl:
        for t, a in S.amb:
            if cur:
                amb_runs.append((cur[0], cur[1], t))
            cur = (a, t)
    if cur:
        amb_runs.append((cur[0], cur[1], total))
    for a, t0, t1 in amb_runs:
        y = amb(a, t1 - t0 + 1.0)
        if len(y) > 2:
            fi = min(len(y), int(0.8 * SR))
            y[:fi] *= np.linspace(0, 1, fi)
            y[-fi:] *= np.linspace(1, 0, fi)
            add(fx, np.stack([y, np.roll(y, 300)], 1), t0, 1.0)
    print('fx ok', flush=True)
    master = voice * 1.0 + music * 0.55 + fx * 0.9
    # jemná limitace
    pk = np.percentile(np.abs(master), 99.95)
    master = master / max(pk, 1e-6) * 0.85
    master = np.tanh(master * 1.1) / np.tanh(1.1)
    write_wav(out_path, master[:int(total * SR)])
    print('mix', out_path)
