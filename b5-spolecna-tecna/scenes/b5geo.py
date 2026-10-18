"""Geometrie úlohy B5 a společné kreslicí prvky (barvy, legenda, cestovní mapa důkazu)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

# barvy objektů – drží se celé video
C_PAR = INK          # rovnoběžník ABCD
C_W = PURPLE         # ω … kružnice B, C, D, M
C_K1 = ORANGE        # k₁ … opsaná △AMB
C_K2 = TEAL          # k₂ … opsaná △AMD
C_T = RED            # společná tečna BD
# barvy úseků ve vzorcích
C_SM = RED
C_SA = GREEN         # |SA| = |SC|
C_SB = "#d81b60"     # |SB| = |SD|  (růžová)

SCALE = 0.8
S_POS = np.array([-3.45, 0.82, 0])


def geo(rot=25, gap=95, a=2.4, b=1.08, S=S_POS, s=SCALE):
    """Vrátí všechny body a kružnice úlohy pro dané tvarové parametry rovnoběžníku."""
    u = np.array([np.cos(np.radians(rot)), np.sin(np.radians(rot)), 0])
    v = np.array([np.cos(np.radians(rot + gap)), np.sin(np.radians(rot + gap)), 0])
    a, b = a * s, b * s
    g = {"S": np.array(S, dtype=float)}
    g["A"], g["C"] = g["S"] - a * u, g["S"] + a * u
    g["B"], g["D"] = g["S"] - b * v, g["S"] + b * v
    g["M"] = g["S"] - (b * b / a) * u
    g["W"] = circumcenter(g["B"], g["C"], g["D"])
    g["RW"] = np.linalg.norm(g["B"] - g["W"])
    g["K1"] = circumcenter(g["A"], g["M"], g["B"])
    g["R1"] = np.linalg.norm(g["A"] - g["K1"])
    g["K2"] = circumcenter(g["A"], g["M"], g["D"])
    g["R2"] = np.linalg.norm(g["A"] - g["K2"])
    return g


G = geo()
LBL = {"A": LEFT, "B": DOWN + RIGHT * 0.25, "C": RIGHT, "D": UP + LEFT * 0.2}


def pt(name, g=G, color=None, d=None, size=30):
    col = color or (RED if name == "M" else (PEN if name == "S" else C_PAR))
    dd = d if d is not None else (RIGHT if name == "S" else (UL if name == "M" else LBL[name]))
    return Pt(g[name], name, dd, color=col, font_size=size)


def seg(p, q, color, g=G, width=5):
    return hseg(g[p], g[q], color=color, width=width, amp=0.004, over=0.0)


def circle_w(g=G, width=3):
    return hcircle(g["W"], g["RW"], color=C_W, width=width)


def circle_k1(g=G, width=3):
    return hcircle(g["K1"], g["R1"], color=C_K1, width=width)


def circle_k2(g=G, width=3):
    return hcircle(g["K2"], g["R2"], color=C_K2, width=width)


def name_tag(text, at, color, size=28):
    return Tx(text, size, color).move_to(at)


def tag_w(g=G):
    return name_tag("ω", g["W"] + g["RW"] * np.array([0.78, 0.72, 0]), C_W)


def tag_k1(g=G):
    return name_tag("k₁", g["K1"] + g["R1"] * np.array([0.25, -1.22, 0]), C_K1)


def tag_k2(g=G):
    return name_tag("k₂", g["K2"] + g["R2"] * np.array([-0.78, 0.78, 0]), C_K2)


def legend():
    """Legenda vlevo dole: co je co."""
    rows = [
        (C_PAR, "line", "ABCD … rovnoběžník,  S = AC ∩ BD"),
        (C_W, "line", "ω … kružnice přes B, C, D, M"),
        (C_K1, "line", "k₁ … kružnice přes A, M, B"),
        (C_K2, "line", "k₂ … kružnice přes A, M, D"),
    ]
    g = VGroup()
    for i, (col, kind, txt) in enumerate(rows):
        sw = Line(LEFT * 0.22, RIGHT * 0.22, color=col, stroke_width=6)
        t = Tx(txt, 22, col if col != C_PAR else INK)
        place(t, 0.35, 0)
        sw.move_to([0, t.axis_y + 0.08, 0])
        row = VGroup(sw, t)
        row.shift(DOWN * i * 0.34)
        g.add(row)
    box = SurroundingRectangle(g, buff=0.15, color=GRAY, stroke_width=1.5, corner_radius=0.08,
                               fill_color=PAPER, fill_opacity=0.9)
    lg = VGroup(box, g)
    lg.to_corner(DL, buff=0.25)
    lg.rows = g
    return lg


ROAD = ["Jak dokázat,\nže je přímka tečna", "Odkud vzít součin:\nkružnice ω", "Rovnoběžník:\núhlopříčky se půlí",
        "Přenos na\nk₁ a k₂"]


def roadmap(active=None, done=()):
    boxes = VGroup()
    for i, t in enumerate(ROAD):
        lines = VGroup(*[Tx(x, 26, INK) for x in t.split("\n")]).arrange(DOWN, buff=0.1)
        num = Text(str(i + 1), font=FONT, font_size=40, color=RED, weight=BOLD)
        content = VGroup(num, lines).arrange(DOWN, buff=0.15)
        col = RED if i == active else (GREEN if i in done else GRAY)
        bx = RoundedRectangle(width=3.0, height=2.0, corner_radius=0.15, color=col,
                              stroke_width=5 if i == active else 2.5,
                              fill_color=col, fill_opacity=0.08 if i == active else 0.0)
        content.move_to(bx)
        if i in done:
            content.add(Text("✓", font="DejaVu Sans", font_size=34, color=GREEN).move_to(bx.get_corner(UR) + DL * 0.3))
        boxes.add(VGroup(bx, content))
    boxes.arrange(RIGHT, buff=0.35)
    arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.05, color=GRAY,
                            stroke_width=3, max_tip_length_to_length_ratio=0.35) for i in range(3)])
    return VGroup(boxes, arrows)


class B5Scene(ProofScene):
    CODE = "B5"
    NAME = "Společná tečna dvou opsaných kružnic"
    TOTAL = 5
    HEADER = ["V rovnoběžníku ABCD (|AC| > |BD|) je BCDM tětivový, M ∈ AC.",
              "Dokaž: přímka BD je společnou tečnou kružnic opsaných △AMB a △AMD."]

    def show_roadmap(self, active, done=(), narration=None):
        rm = roadmap(active, done).move_to(DOWN * 0.4)
        title = Text("Mapa důkazu", font=FONT, font_size=36, color=RED).next_to(rm, UP, buff=0.45)
        if narration:
            with self.say(narration):
                self.play(FadeIn(title), FadeIn(rm, lag_ratio=0.1), run_time=1.0)
        else:
            self.play(FadeIn(title), FadeIn(rm, lag_ratio=0.1), run_time=1.0)
            self.wait(1.5)
        self.play(FadeOut(title), FadeOut(rm), run_time=0.6)


def line_circle(P, d, c, r):
    """Průsečíky přímky P + t·d s kružnicí (c, r), seřazené podle t."""
    d = d / np.linalg.norm(d)
    f = P - c
    b = np.dot(f, d)
    disc = b * b - (np.dot(f, f) - r * r)
    if disc < 0:
        return []
    sq = np.sqrt(disc)
    return [P + (-b - sq) * d, P + (-b + sq) * d]


def wobble_line(scene, P, other, c, r, color=C_T, amp=14, run=2.5):
    """Ukázka tečny: přímku bodem P (směr k bodu other) pootočí o ±amp° a ukazuje průsečíky s kružnicí."""
    base = np.arctan2(*(other - P)[1::-1])
    th = ValueTracker(0.0)

    def live():
        a = base + np.radians(th.get_value())
        d = np.array([np.cos(a), np.sin(a), 0])
        g = VGroup(Line(P - d * 2.2, P + d * 2.2, color=GRAY, stroke_width=3))
        for X in line_circle(P, d, c, r):
            g.add(Dot(X, radius=0.075, color=color))
        return g

    lv = always_redraw(live)
    scene.add(lv)
    scene.play(th.animate.set_value(amp), run_time=run / 3)
    scene.play(th.animate.set_value(-amp), run_time=run / 3)
    scene.play(th.animate.set_value(0), run_time=run / 3)
    scene.remove(lv)
