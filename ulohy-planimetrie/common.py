"""Sdílené nástroje pro ručně kreslená videa s úlohami z planimetrie.

- ručně kreslené (lehce roztřesené) úsečky, přímky, kružnice, oblouky úhlů
- text v ručním písmu Kalam se značkami ^{AB} (polopřímka), ={AB} (přímka), @{AB} (oblouk)
- synchronizace animací s namluveným komentářem: with self.say("..."):
"""
import hashlib
import json
import os
import re
import wave
from contextlib import contextmanager

import numpy as np
from manim import *

ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(ROOT, "audio")

PAPER = "#f7f2e4"
GRID = "#dfe5ec"
INK = "#1b2a6b"      # modrý inkoust – text
PEN = "#2b2b2b"      # tužka – obrázky
RED = "#c62828"
GREEN = "#2e7d32"
ORANGE = "#e06a00"
PURPLE = "#7b1fa2"
TEAL = "#00838f"
GRAY = "#8a8a8a"
FONT = "Kalam"
CODE_FONT = "Shantell Sans"     # čitelné velké I (Kalam ho kreslí jako 1)

config.background_color = PAPER

TOTAL_CHAPTERS = 8


# ---------------------------------------------------------------- audio ---

def norm_text(text):
    return " ".join(text.split())


def audio_key(text):
    return hashlib.sha1(norm_text(text).encode("utf-8")).hexdigest()[:16]


def audio_for(text):
    """Vrátí (cesta, délka v s). Pokud audio ještě neexistuje, délku odhadne."""
    path = os.path.join(AUDIO_DIR, audio_key(text) + ".wav")
    if os.path.exists(path):
        with wave.open(path) as w:
            return path, w.getnframes() / w.getframerate()
    return None, max(1.2, len(norm_text(text)) / 14.0)


# ---------------------------------------------------- ručně kreslené čáry ---

_rng = np.random.default_rng(1)


def reseed(seed):
    global _rng
    _rng = np.random.default_rng(seed)


def _noise(n, amp, waves=3):
    t = np.linspace(0, 1, n)
    out = np.zeros(n)
    for k in range(1, waves + 1):
        out += _rng.normal() / k * np.sin(np.pi * k * t + _rng.uniform(0, 2 * np.pi))
    return amp * out / 1.5


def _p(P):
    P = np.array(P, dtype=float)
    if P.shape[0] == 2:
        P = np.array([P[0], P[1], 0.0])
    return P


def hseg(A, B, color=PEN, width=3.2, amp=0.012, over=0.05):
    """Ručně kreslená úsečka AB (lehce zvlněná, konce mírně přetažené)."""
    A, B = _p(A), _p(B)
    d = B - A
    L = np.linalg.norm(d)
    u = d / L
    nrm = np.array([-u[1], u[0], 0.0])
    a0 = -_rng.uniform(0, over)
    a1 = L + _rng.uniform(0, over)
    n = max(10, int(L * 8))
    s = np.linspace(a0, a1, n)
    off = _noise(n, amp * min(1.0, 0.4 + L / 6))
    pts = [A + u * si + nrm * oi for si, oi in zip(s, off)]
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly(pts)


def hline(A, B, ext=1.0, color=PEN, width=3.0, ext2=None):
    """Přímka AB – úsečka prodloužená o ext za A a ext2 za B."""
    A, B = _p(A), _p(B)
    u = (B - A) / np.linalg.norm(B - A)
    e2 = ext if ext2 is None else ext2
    return hseg(A - u * ext, B + u * e2, color=color, width=width, over=0.0)


def hpoly(*pts, color=PEN, width=3.2):
    """Uzavřený mnohoúhelník jako skupina ručně kreslených stran."""
    pts = [_p(P) for P in pts]
    return VGroup(*[hseg(pts[i], pts[(i + 1) % len(pts)], color=color, width=width)
                    for i in range(len(pts))])


def hfill(*pts, color=ORANGE, opacity=0.18):
    pts = list(pts)
    if pts and isinstance(pts[-1], (int, float)):
        opacity = pts.pop()
    if pts and isinstance(pts[-1], str):
        color = pts.pop()
    return Polygon(*[_p(P) for P in pts], stroke_width=0, fill_color=color,
                   fill_opacity=opacity)


def hcircle(c, r, color=PEN, width=3.0):
    c = _p(c)
    th0 = _rng.uniform(0, 2 * np.pi)
    n = 180
    th = np.linspace(th0, th0 + 2 * np.pi + 0.09, n)
    rr = r * (1 + _noise(n, 0.005)) + np.linspace(0, r * 0.006, n)
    pts = [c + np.array([np.cos(t) * q, np.sin(t) * q, 0]) for t, q in zip(th, rr)]
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly(pts)


def harc(c, r, a0, a1, color=PEN, width=3.0, amp=0.004):
    c = _p(c)
    n = max(8, int(abs(a1 - a0) * r * 14) + 6)
    th = np.linspace(a0, a1, n)
    rr = r * (1 + _noise(n, amp))
    pts = [c + np.array([np.cos(t) * q, np.sin(t) * q, 0]) for t, q in zip(th, rr)]
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly(pts)


def direction(V, P):
    d = _p(P) - _p(V)
    return np.arctan2(d[1], d[0])


def _sweep(V, P1, P2, reflex=False):
    a1, a2 = direction(V, P1), direction(V, P2)
    d = (a2 - a1) % (2 * np.pi)
    if (d > np.pi) != reflex:
        a1, d = a2, 2 * np.pi - d
    return a1, d


def lerp(A, B, t):
    return _p(A) + (_p(B) - _p(A)) * t


def line_intersection(A, B, C, D):
    A, B, C, D = map(_p, (A, B, C, D))
    M = np.array([[B[0] - A[0], C[0] - D[0]], [B[1] - A[1], C[1] - D[1]]])
    t, _ = np.linalg.solve(M, (C - A)[:2])
    return A + (B - A) * t


def circumcenter(A, B, C):
    A, B, C = map(_p, (A, B, C))
    d = 2 * (A[0] * (B[1] - C[1]) + B[0] * (C[1] - A[1]) + C[0] * (A[1] - B[1]))
    ux = ((A @ A) * (B[1] - C[1]) + (B @ B) * (C[1] - A[1]) + (C @ C) * (A[1] - B[1])) / d
    uy = ((A @ A) * (C[0] - B[0]) + (B @ B) * (A[0] - C[0]) + (C @ C) * (B[0] - A[0])) / d
    return np.array([ux, uy, 0.0])


def on_circle(c, r, deg):
    t = np.radians(deg)
    return _p(c) + r * np.array([np.cos(t), np.sin(t), 0])


def angle_deg(V, P1, P2):
    """Velikost (konvexního) úhlu P1 V P2 ve stupních."""
    a, b = _p(P1) - _p(V), _p(P2) - _p(V)
    c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def circle_intersections(c1, r1, c2, r2):
    c1, c2 = _p(c1), _p(c2)
    d = np.linalg.norm(c2 - c1)
    if d < 1e-9 or d > r1 + r2 or d < abs(r1 - r2):
        return []
    a = (r1 ** 2 - r2 ** 2 + d ** 2) / (2 * d)
    h = np.sqrt(max(0.0, r1 ** 2 - a ** 2))
    u = (c2 - c1) / d
    n = np.array([-u[1], u[0], 0])
    m = c1 + a * u
    return [m + h * n, m - h * n]


def foot(P, A, B):
    """Pata kolmice z P na přímku AB."""
    P, A, B = map(_p, (P, A, B))
    u = (B - A) / np.linalg.norm(B - A)
    return A + u * np.dot(P - A, u)


def rotate_about(P, C, ang):
    P, C = _p(P), _p(C)
    d = P - C
    return C + np.array([d[0] * np.cos(ang) - d[1] * np.sin(ang),
                         d[0] * np.sin(ang) + d[1] * np.cos(ang), 0])


class AngleMark(VGroup):
    """Oblouček úhlu ∢P1 V P2 (konvexní), volitelně vyplněná výseč a popisek."""

    def __init__(self, V, P1, P2, r=0.5, color=RED, n=1, label=None, fill=True,
                 fill_opacity=0.22, label_r=None, font_size=30, width=2.8,
                 reflex=False, label_color=None, ccw=False, label_t=0.5):
        super().__init__()
        V = _p(V)
        if ccw:   # vždy proti směru hodinových ručiček od P1 k P2 (např. přímý úhel)
            a0 = direction(V, P1)
            d = (direction(V, P2) - a0) % (2 * np.pi)
        else:
            a0, d = _sweep(V, P1, P2, reflex)
        self.vertex, self.a0, self.d, self.r = V, a0, d, r
        self.fill = VMobject()
        if fill:
            th = np.linspace(a0, a0 + d, 30)
            pts = [V] + [V + r * np.array([np.cos(t), np.sin(t), 0]) for t in th]
            self.fill = Polygon(*pts, stroke_width=0, fill_color=color,
                                fill_opacity=fill_opacity)
        self.arcs = VGroup(*[harc(V, r + 0.075 * k, a0, a0 + d, color=color, width=width)
                             for k in range(n)])
        self.add(self.fill, self.arcs)
        self.label = VMobject()
        if label:
            lr = label_r if label_r is not None else r + 0.27
            mid = a0 + d * label_t
            self.label = Text(label, font=FONT, font_size=font_size,
                              color=label_color or color)
            self.label.move_to(V + lr * np.array([np.cos(mid), np.sin(mid), 0]))
            self.add(self.label)


class RightMark(VGroup):
    """Značka pravého úhlu (oblouček s tečkou – jak se kreslí ve škole)."""

    def __init__(self, V, P1, P2, r=0.38, color=PEN, width=2.6):
        super().__init__()
        V = _p(V)
        a0, d = _sweep(V, P1, P2)
        self.add(harc(V, r, a0, a0 + d, color=color, width=width))
        mid = a0 + d / 2
        self.add(Dot(V + 0.45 * r * np.array([np.cos(mid), np.sin(mid), 0]),
                     radius=0.035, color=color))


def ticks(A, B, n=1, color=PEN, size=0.13, t=0.5):
    A, B = _p(A), _p(B)
    u = (B - A) / np.linalg.norm(B - A)
    nrm = np.array([-u[1], u[0], 0])
    M = A + (B - A) * t
    g = VGroup()
    for k in range(n):
        c = M + u * (k - (n - 1) / 2) * 0.08
        g.add(Line(c - nrm * size, c + nrm * size, color=color, stroke_width=2.6))
    return g


class Pt(VGroup):
    """Bod s popiskem."""

    def __init__(self, P, name="", d=UL, color=PEN, label_color=None, font_size=32,
                 buff=0.08, radius=0.055):
        super().__init__()
        self.P = _p(P)
        self.dot = Dot(self.P, radius=radius, color=color)
        self.add(self.dot)
        self.label = VMobject()
        if name:
            self.label = Text(name, font=FONT, font_size=font_size,
                              color=label_color or color)
            self.label.next_to(self.dot, d, buff=buff)
            self.add(self.label)


def label(text, pos, color=PEN, font_size=32):
    return Text(text, font=FONT, font_size=font_size, color=color).move_to(_p(pos))


# ---------------------------------------------------------- text / vzorce ---

_SUBDIGITS = {c: str(i) for i, c in enumerate("₀₁₂₃₄₅₆₇₈₉")}


def _parse_marks(s):
    """Rozparsuje značky ^{..} ={..} @{..} _{..} (i vnořené); ₀-₉ převede na _{0}..."""
    clean, marks, stack, i = "", [], [], 0
    while i < len(s):
        ch = s[i]
        if ch in "^=@_" and i + 1 < len(s) and s[i + 1] == "{":
            stack.append((ch, len(clean)))
            i += 2
            continue
        if ch == "}" and stack:
            kind, st = stack.pop()
            marks.append((kind, st, len(clean)))
            i += 1
            continue
        if ch in _SUBDIGITS:
            marks.append(("_", len(clean), len(clean) + 1))
            clean += _SUBDIGITS[ch]
        else:
            clean += ch
        i += 1
    return clean, marks


class Tx(VGroup):
    """Řádek textu v ručním písmu.

    Značky: ^{AB} šipka nad (polopřímka/polorovina), ={AB} oboustranná šipka (přímka),
    @{AB} oblouček nad (oblouk kružnice), _{c} dolní index (₀–₉ se převádí samo).
    self.find("sus") vrátí glyfy daného podřetězce (pro zvýraznění).
    """

    def __init__(self, s, size=32, color=INK, **kw):
        super().__init__()
        clean, marks = _parse_marks(s)
        self.clean = clean
        t = Text("|" + clean + "|", font=FONT, font_size=size, color=color,
                 disable_ligatures=True, **kw)
        axis_y = t[0].get_center()[1]
        t.submobjects = t.submobjects[1:-1]
        self.text = t
        # dolní indexy: zmenšit, posunout dolů, dorovnat mezeru
        for kind, a, b in sorted([m for m in marks if m[0] == "_"], key=lambda m: m[1]):
            g = VGroup(*t[a:b])
            nxt = [c for c in t[b:] if len(c.points) > 0]
            x_next = nxt[0].get_left()[0] if nxt else None
            g.scale(0.62, about_point=[g.get_left()[0], axis_y - 0.16 * size / 32, 0])
            g.shift(DOWN * 0.07 * size / 32)
            if x_next is not None:
                spaced = any(len(c.points) == 0 for c in t[b:b + 1])
                dx = (x_next - g.get_right()[0]) - (0.1 if spaced else 0.03) * size / 32
                if dx > 0:
                    for c in t[b:]:
                        c.shift(LEFT * dx)
        self.axis_pt = VectorizedPoint([t.get_left()[0], axis_y, 0])
        self.add(t, self.axis_pt)
        self.decos = VGroup()
        h = size / 32 * 0.1
        for kind, a, b in marks:
            if kind == "_":
                continue
            g = VGroup(*[c for c in t[a:b]])
            top = g.get_top()[1] + 0.07 * size / 32
            L, R = g.get_left()[0] + 0.02, g.get_right()[0] - 0.02
            sw = 2.2 * size / 32
            if kind == "^":
                d = VGroup(Line([L, top, 0], [R, top, 0], stroke_width=sw, color=color),
                           Line([R, top, 0], [R - h, top + h * 0.6, 0], stroke_width=sw, color=color),
                           Line([R, top, 0], [R - h, top - h * 0.6, 0], stroke_width=sw, color=color))
            elif kind == "=":
                d = VGroup(Line([L, top, 0], [R, top, 0], stroke_width=sw, color=color))
                for X, s_ in ((R, -1), (L, 1)):
                    d.add(Line([X, top, 0], [X + s_ * h, top + h * 0.6, 0], stroke_width=sw, color=color),
                          Line([X, top, 0], [X + s_ * h, top - h * 0.6, 0], stroke_width=sw, color=color))
            else:
                d = ArcBetweenPoints([L, top, 0], [R, top, 0], angle=-PI / 2.2,
                                     stroke_width=sw, color=color)
            self.decos.add(d)
        self.add(self.decos)

    def find(self, sub, nth=0):
        i = -1
        for _ in range(nth + 1):
            i = self.clean.index(sub, i + 1)
        return VGroup(*self.text[i:i + len(sub)])

    @property
    def axis_y(self):
        return self.axis_pt.get_center()[1]


class Frac(VGroup):
    def __init__(self, num, den, size=32, color=INK):
        super().__init__()
        n = num if isinstance(num, Mobject) else Tx(num, size, color)
        d = den if isinstance(den, Mobject) else Tx(den, size, color)
        w = max(n.width, d.width) + 0.12
        bar = Line(LEFT * w / 2, RIGHT * w / 2, color=color, stroke_width=2.4 * size / 32)
        n.next_to(bar, UP, buff=0.08)
        d.next_to(bar, DOWN, buff=0.08)
        self.add(n, bar, d)
        self.axis_pt = VectorizedPoint(bar.get_center() + DOWN * 0.02 * size / 32)
        self.add(self.axis_pt)

    @property
    def axis_y(self):
        return self.axis_pt.get_center()[1]


class Row(VGroup):
    """Vodorovné složení Tx/Frac zarovnaných na osu (např. zlomky v řádku)."""

    def __init__(self, *parts, buff=0.14, size=32, color=INK):
        super().__init__()
        parts = [Tx(p, size, color) if isinstance(p, str) else p for p in parts]
        x = 0
        for p in parts:
            p.shift([x - p.get_left()[0], -p.axis_y, 0])
            x = p.get_right()[0] + buff
        self.add(*parts)
        self.parts = parts
        self.axis_pt = VectorizedPoint([parts[0].get_left()[0], 0, 0])
        self.add(self.axis_pt)

    @property
    def axis_y(self):
        return self.axis_pt.get_center()[1]


def place(mob, x, y):
    """Umístí řádek levým okrajem na x a osou na y."""
    ay = mob.axis_y if hasattr(mob, "axis_y") else mob.get_center()[1]
    mob.shift([x - mob.get_left()[0], y - ay, 0])
    return mob


def wavy_underline(mob, color=RED, width=2.6, buff=0.1):
    L = mob.get_corner(DL) + DOWN * buff
    R = mob.get_corner(DR) + DOWN * buff
    return hseg(L, R, color=color, width=width, amp=0.02)


def hbox(mob, color=RED, buff=0.15, width=2.6):
    c = [mob.get_corner(d) + d * buff for d in (UL, UR, DR, DL)]
    return hpoly(*c, color=color, width=width)


# ------------------------------------------------------------- scéna ---

class Board:
    """Pravá polovina obrazovky – sem se řádek po řádku píše důkaz."""

    def __init__(self, scene, x=0.15, y=2.35, dy=0.64, ymin=-3.5, xmax=6.95, autoscroll=True):
        self.scene, self.x, self.y0, self.y, self.dy, self.ymin = scene, x, y, y, dy, ymin
        self.xmax = xmax
        self.autoscroll = autoscroll
        self.size = 31
        self.lines = VGroup()

    def _scroll(self, need):
        """Posune napsané řádky nahoru o need; co by vyjelo nad horní okraj, zmizí."""
        anims, keep = [], VGroup()
        for m in self.lines:
            if m.get_top()[1] + need > self.y0 + 0.4:
                anims.append(FadeOut(m, shift=UP * need))
            else:
                anims.append(m.animate.shift(UP * need))
                keep.add(m)
        if anims:
            self.scene.play(*anims, run_time=0.7)
        self.lines = keep
        self.y += need

    def make(self, s, size=None, color=INK, indent=0.0, gap=0.0):
        mob = s if isinstance(s, Mobject) else Tx(s, size or self.size, color)
        self.y -= gap
        h_extra = 0.0
        if isinstance(mob, (Row, Frac)):
            h_extra = 0.28
            self.y -= h_extra
        if self.autoscroll and self.y - 0.3 < self.ymin:
            self._scroll(self.ymin - (self.y - 0.3) + 0.05)
        place(mob, self.x + indent, self.y)
        maxw = self.xmax - self.x - indent
        if mob.width > maxw:
            mob.scale(maxw / mob.width, about_point=[mob.get_left()[0], self.y, 0])
        self.y -= self.dy + h_extra
        self.lines.add(mob)
        return mob

    def skip(self, h=0.3):
        self.y -= h

    def write(self, s, run_time=None, **kw):
        mob = self.make(s, **kw)
        self.scene.write(mob, run_time)
        return mob

    def clear_anim(self):
        anim = FadeOut(self.lines)
        self.lines = VGroup()
        self.y = self.y0
        return anim


class ProofScene(Scene):
    CODE = "V ?"
    NAME = ""
    INDEX = 0
    SEED = 1
    TOTAL = TOTAL_CHAPTERS

    def setup(self):
        reseed(self.SEED)
        grid = VGroup()
        for x in np.arange(-7.5, 7.6, 0.5):
            grid.add(Line([x, -4.2, 0], [x, 4.2, 0], stroke_width=1.0, color=GRID))
        for y in np.arange(-4.0, 4.1, 0.5):
            grid.add(Line([-7.3, y, 0], [7.3, y, 0], stroke_width=1.0, color=GRID))
        grid.set_z_index(-100)
        self.add(grid)
        self._say_end = 0.0
        self.board = Board(self)
        self.header = VGroup()

    # --- synchronizace s komentářem
    @contextmanager
    def say(self, text, pad=0.3):
        path, dur = audio_for(text)
        t0 = self.renderer.time
        if path:
            self.add_sound(path)
        self._say_end = t0 + dur
        yield dur
        rest = t0 + dur + pad - self.renderer.time
        if rest > 0.02:
            self.wait(rest)

    def left(self, minimum=0.5):
        return max(minimum, self._say_end - self.renderer.time)

    # --- kreslení
    def _anim(self, m, run_time):
        if isinstance(m, (Tx, Row, Frac, Text)):
            return Write(m, run_time=run_time)
        if isinstance(m, Pt):
            return FadeIn(m, scale=0.6, run_time=run_time)
        return Create(m, run_time=run_time, rate_func=smooth)

    def draw(self, *mobs, run_time=1.0, lag=0.0):
        anims = [self._anim(m, run_time) for m in mobs]
        if lag:
            self.play(LaggedStart(*anims, lag_ratio=lag), run_time=run_time)
        else:
            self.play(*anims, run_time=run_time)

    def write(self, mob, run_time=None):
        if run_time is None:
            n = len(mob.clean) if isinstance(mob, Tx) else 14
            run_time = float(np.clip(0.06 * n, 0.8, 2.6))
        self.play(Write(mob), run_time=run_time)
        return mob

    def box(self, mob, run_time=0.6, color=RED):
        """Rámeček kolem řádku na tabuli (posouvá se s tabulí)."""
        b = hbox(mob, color=color)
        self.play(Create(b), run_time=run_time)
        self.board.lines.add(b)
        return b

    def hl(self, *pairs, color=RED, width=6, run_time=1.0):
        """Krátce zvýrazní úsečky (nakreslí silnou barevnou čáru a zase ji schová)."""
        segs = VGroup(*[hseg(a, b, color=color, width=width, amp=0.006, over=0.0) for a, b in pairs])
        self.play(Create(segs), run_time=run_time * 0.5)
        self.play(FadeOut(segs), run_time=run_time * 0.5)

    def flash(self, mob, color=RED, run_time=1.0):
        self.play(Circumscribe(mob, color=color, buff=0.06, run_time=run_time))

    def blink(self, *mobs, color=RED, run_time=0.9):
        self.play(*[Indicate(m, color=color, scale_factor=1.12) for m in mobs],
                  run_time=run_time)

    # --- úvod věty
    def intro(self, statement, narration, extra_lines=()):
        """Úvodní karta: číslo a název věty, znění. Pak se přesune nahoru do záhlaví."""
        code = Text(self.CODE, font=CODE_FONT, font_size=72, color=RED, weight=BOLD)
        name = Text(self.NAME, font=FONT, font_size=40, color=INK)
        prog = Text(f"{self.INDEX} / {self.TOTAL}", font=FONT, font_size=24, color=GRAY)
        prog.to_corner(DR, buff=0.3)
        top = VGroup(code, name).arrange(DOWN, buff=0.25).move_to(UP * 2.2)
        ul = wavy_underline(name, color=RED)
        st = VGroup(*[Tx(s, 34, PEN) for s in statement])
        st.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        if st.width > 13:
            st.scale_to_fit_width(13)
        st.next_to(ul, DOWN, buff=0.7)
        with self.say(narration):
            self.play(Write(code), FadeIn(prog), run_time=0.9)
            self.play(Write(name), Create(ul), run_time=1.2)
            for s in st:
                self.write(s, run_time=min(2.4, self.left() / max(1, len(st))))
        # zmenšit do záhlaví
        hcode = Text(self.CODE, font=CODE_FONT, font_size=34, color=RED, weight=BOLD)
        hst = VGroup(*[Tx(s, 25, PEN) for s in statement]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        hcode.to_corner(UL, buff=0.32)
        hst.next_to(hcode, RIGHT, buff=0.35, aligned_edge=UP).shift(UP * 0.04)
        maxw = 14.2 - 0.32 - hcode.width - 0.35 - 0.3
        if hst.width > maxw:
            hst.scale_to_fit_width(maxw)
            hst.next_to(hcode, RIGHT, buff=0.35, aligned_edge=UP).shift(UP * 0.04)
        bottom = min(hst.get_bottom()[1], hcode.get_bottom()[1]) - 0.14
        rule = hseg([-6.95, bottom, 0], [6.95, bottom, 0], color=RED, width=2.2, amp=0.01)
        self.play(FadeOut(name), FadeOut(ul), ReplacementTransform(code, hcode),
                  ReplacementTransform(st, hst), run_time=1.2)
        self.play(Create(rule), run_time=0.5)
        self.header = VGroup(hcode, hst, rule, prog)
        self.header_bottom = bottom
        self.board = Board(self, y=bottom - 0.5)

    def clear_body(self, run_time=0.8):
        rest = [m for m in self.mobjects if m not in self.header and m.z_index > -100]
        if rest:
            self.play(*[FadeOut(m) for m in rest], run_time=run_time)
        self.board = Board(self, y=self.header_bottom - 0.5)

    def think(self, question, narration, pause=6.0, pos=None, lines=None):
        """Chvilka na přemýšlení: kartička s otázkou, komentář, pak tichá pauza s ubývajícím proužkem."""
        title = Text("Zastav se a zkus si to sám", font=FONT, font_size=28, color=RED)
        qs = [question] if isinstance(question, str) else list(question)
        q = VGroup(*[Tx(x, 30, INK) for x in qs]).arrange(DOWN, buff=0.12)
        content = VGroup(title, q).arrange(DOWN, buff=0.2)
        if content.width > 12.5:
            content.scale_to_fit_width(12.5)
        bg = RoundedRectangle(width=content.width + 0.9, height=content.height + 0.75, corner_radius=0.18,
                              fill_color=PAPER, fill_opacity=0.97, stroke_color=RED, stroke_width=2.6)
        bg.move_to(content).shift(DOWN * 0.08)
        bar = Line(bg.get_corner(DL) + RIGHT * 0.35 + UP * 0.2, bg.get_corner(DR) + LEFT * 0.35 + UP * 0.2,
                   color=RED, stroke_width=5)
        card = VGroup(bg, content, bar)
        card.move_to(pos if pos is not None else DOWN * (3.95 - card.height / 2 - 0.05))
        card.set_z_index(60)
        with self.say(narration):
            self.play(FadeIn(card, shift=UP * 0.2), run_time=0.6)
        self.play(bar.animate.stretch(0.002, 0, about_edge=LEFT), run_time=pause, rate_func=linear)
        self.play(FadeOut(card), run_time=0.5)

    def summary_title(self):
        t = Text("Zápis do písemky", font=FONT, font_size=36, color=RED)
        t.move_to([3.4, self.header_bottom - 0.42, 0])
        return t

    def summary(self, fig, lines, narration, size=29, dy=0.62, fig_w=5.6, fig_h=5.0, x_text=-0.75,
                final="Zastav si video a zkus si celý důkaz napsat bez koukání.", outro=True):
        """Závěrečný zápis důkazu: obrázek vlevo, kompletní zápis vpravo."""
        self.clear_body()
        title = Text("Zápis do písemky", font=FONT, font_size=36, color=RED)
        title.move_to([3.1, self.header_bottom - 0.45, 0])
        top = self.header_bottom - 1.0
        if fig is not None:
            fig.scale(min(fig_w / fig.width, fig_h / fig.height, 1.0))
            fig.move_to([-6.85 + fig.width / 2, (top - 3.85) / 2, 0])
        b = Board(self, x=x_text, y=top - 0.3, dy=dy, autoscroll=False)
        mobs = [b.make(s, size=size) if isinstance(s, str) else b.make(s) for s in lines]
        with self.say(narration):
            self.play(Write(title), run_time=0.8)
            if fig is not None:
                self.play(FadeIn(fig), run_time=0.8)
            per = max(0.8, (self.left() - 0.3) / max(1, len(mobs)))
            for m in mobs:
                self.write(m, run_time=min(per, 3.0))
                rest = per - min(per, 3.0)
                if rest > 0.05:
                    self.wait(rest)
        if final:
            with self.say(final):
                pass
        if outro:
            self.outro_pause()
        else:
            self.wait(2.0)

    def outro_pause(self, sec=2.5):
        self.wait(sec)
        self.play(*[FadeOut(m) for m in self.mobjects if m.z_index > -100], run_time=0.8)
