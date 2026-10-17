import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

K = 0.42
X = {"A": 4, "B": 5, "C": 2, "D": 3}         # tečnové délky v cm
RC = np.sqrt(11)                              # poloměr vepsané kružnice (cm)
O0 = np.array([-3.5, -1.05, 0])
COL = {"A": RED, "B": ORANGE, "C": GREEN, "D": PURPLE}


def build():
    r = RC * K
    t = {}
    ang = -PI / 2                             # bod dotyku na AB je dole
    t["P"] = ang
    V = {}
    seq = [("B", "Q"), ("C", "R"), ("D", "T")]
    a = np.arctan(X["A"] / RC)
    V["A"] = O0 + np.hypot(r, X["A"] * K) * np.array([np.cos(ang - a), np.sin(ang - a), 0])
    cur = ang
    for v, nxt in seq:
        h = np.arctan(X[v] / RC)
        V[v] = O0 + np.hypot(r, X[v] * K) * np.array([np.cos(cur + h), np.sin(cur + h), 0])
        cur += 2 * h
        t[nxt] = cur
    T = {k: O0 + r * np.array([np.cos(v), np.sin(v), 0]) for k, v in t.items()}
    return r, V, T


R, V, T = build()
SIDES = [("A", "B", "P"), ("B", "C", "Q"), ("C", "D", "R"), ("D", "A", "T")]
VDIR = {"A": DL, "B": DR, "C": UR, "D": UL}


class D2(ProofScene):
    CODE = "D2"
    NAME = "Tečnový čtyřúhelník a body dotyku"
    INDEX = 5
    SEED = 402

    def quad(self, col=PEN):
        g = VGroup(hpoly(V["A"], V["B"], V["C"], V["D"], color=col), hcircle(O0, R, color=INK, width=2.6))
        g.add(*[Pt(V[n], n, VDIR[n]) for n in "ABCD"])
        return g

    def tangent_pieces(self, width=6):
        """Pro každý vrchol dvě barevné tečnové úsečky (stejná barva = stejná délka)."""
        g = VGroup()
        for v1, v2, t in SIDES:
            g.add(hseg(V[v1], T[t], color=COL[v1], width=width, amp=0.004, over=0.0),
                  hseg(T[t], V[v2], color=COL[v2], width=width, amp=0.004, over=0.0))
        return g

    def construct(self):
        self.intro(
            ["Tečnový čtyřúhelník ABCD má |AB| = 9 cm, |BC| = 7 cm, |CD| = 5 cm.",
             "a) Určete |AD| a obvod čtyřúhelníku.",
             "b) Kružnice vepsaná se dotýká strany AB v bodě P, |AP| = 4 cm. Určete vzdálenosti",
             "všech ostatních bodů dotyku od nejbližších vrcholů."],
            "Úloha dé dva. Tečnový čtyřúhelník á bé cé dé má strany á bé devět, bé cé sedm a cé dé pět centimetrů. "
            "Máme určit čtvrtou stranu a obvod, a pak, když víme, že bod dotyku pé je od á vzdálený čtyři centimetry, "
            "určit vzdálenosti všech bodů dotyku od vrcholů.")
        q = self.quad()
        with self.say("Tečnový čtyřúhelník je takový, do kterého se dá vepsat kružnice. Každá jeho strana se té kružnice "
                      "dotýká, je to tečna. Body dotyku označíme pé, kvé, er a té."):
            self.draw(q[0], run_time=1.4)
            self.draw(*q[2:], run_time=0.5)
            self.draw(q[1], run_time=1.2)
            self.draw(*[Pt(T[k], k, (T[k] - O0) / np.linalg.norm(T[k] - O0), color=INK, font_size=26)
                        for k in "PQRT"], run_time=0.6)
        self.think("Celá úloha stojí na jedné vlastnosti tečen. Napadne tě, na které?",
                   "Celá úloha stojí na jedné jednoduché vlastnosti tečen ke kružnici. Napadne tě, na které?", pause=5)

        # ---- stejně dlouhé tečny z jednoho bodu
        Bv = V["B"]
        OB = hseg(O0, Bv, color=GRAY, width=2.2)
        rp, rq = hseg(O0, T["P"], color=INK, width=2.6), hseg(O0, T["Q"], color=INK, width=2.6)
        t1 = hfill(O0, T["P"], Bv, ORANGE, 0.3)
        t2 = hfill(O0, T["Q"], Bv, ORANGE, 0.3)
        pO = Pt(O0, "O", LEFT, font_size=26)
        with self.say("Je to tato: dvě tečny vedené z jednoho bodu ke kružnici jsou stejně dlouhé. Podívej se na vrchol bé. "
                      "Z něj vedou dvě tečny, k bodům pé a kvé. Spojíme bé se středem ó a nakreslíme poloměry do bodů dotyku."):
            self.draw(pO, run_time=0.3)
            self.draw(OB, rp, rq, run_time=1.0)
            self.draw(RightMark(T["P"], O0, Bv, r=0.2), RightMark(T["Q"], O0, Bv, r=0.2), run_time=0.5)
        with self.say("Poloměr je kolmý na tečnu, takže vzniknou dva pravoúhlé trojúhelníky. Mají společnou přeponu ó bé "
                      "a stejně dlouhé odvěsny, oba poloměry. Podle věty es es u jsou shodné. Je to vlastně zrcadlení podle "
                      "přímky ó bé. A proto bé pé je stejně dlouhé jako bé kvé."):
            self.play(FadeIn(t1), run_time=0.5)
            cp = t1.copy()
            axis = (Bv - O0) / np.linalg.norm(Bv - O0)
            self.play(Rotate(cp, PI, axis=axis, about_point=O0), run_time=1.8)
            self.play(FadeOut(cp), FadeIn(t2), run_time=0.5)
            self.board.write("tečny z jednoho bodu jsou stejně dlouhé:")
            self.board.write("△OPB ≅ △OQB (Ssu)  ⇒  |BP| = |BQ|", indent=0.45)
        self.play(*[FadeOut(m) for m in (OB, rp, rq, t1, t2, pO)], run_time=0.5)
        self.play(*[FadeOut(m) for m in self.mobjects if isinstance(m, RightMark)], run_time=0.3)

        pieces = self.tangent_pieces()
        with self.say("Platí to pro každý vrchol. Obarvíme si u každého vrcholu obě jeho tečny stejnou barvou: u á červeně, "
                      "u bé oranžově, u cé zeleně a u dé fialově. Stejná barva znamená stejnou délku. Délce té úsečky říkáme "
                      "tečnová délka vrcholu a značíme ji iks á, iks bé, iks cé, iks dé."):
            for i in range(4):
                v = "ABCD"[i]
                idx = {"A": (0, 7), "B": (1, 2), "C": (3, 4), "D": (5, 6)}[v]
                self.draw(pieces[idx[0]], pieces[idx[1]], run_time=0.7)
            self.board.write("x_{A}, x_{B}, x_{C}, x_{D} … tečnové délky", indent=0.0)
        with self.say("A teď to hlavní. Každá strana se bodem dotyku rozdělí na dvě tečnové délky svých krajních vrcholů. "
                      "Strana á bé je iks á plus iks bé, strana bé cé je iks bé plus iks cé, a tak dál."):
            self.board.write("a = x_{A} + x_{B},   b = x_{B} + x_{C}", indent=0.45)
            self.board.write("c = x_{C} + x_{D},   d = x_{D} + x_{A}", indent=0.45)
        self.think("Co vyjde, když sečteš protější strany a + c? A co b + d?",
                   "Zkus sečíst protější strany á plus cé. A co vyjde pro bé plus dé?", pause=5)
        with self.say("Á plus cé obsahuje všechny čtyři tečnové délky, každou jednou. A bé plus dé taky. Proto se součty protějších "
                      "stran rovnají. Na obrázku: dolní a horní strana dohromady mají všechny čtyři barvy, stejně jako levá a pravá. "
                      "To je přesně věta dvanáct celá čtyři o tečnovém čtyřúhelníku."):
            self.play(Indicate(VGroup(pieces[0], pieces[1], pieces[4], pieces[5]), scale_factor=1.05), run_time=1.2)
            self.play(Indicate(VGroup(pieces[2], pieces[3], pieces[6], pieces[7]), scale_factor=1.05), run_time=1.2)
            r = self.board.write("a + c = x_{A} + x_{B} + x_{C} + x_{D} = b + d", indent=0.45)
            self.box(r, run_time=0.6)

        # ---- a)
        self.play(self.board.clear_anim(), run_time=0.5)
        with self.say("Část á je teď jednoduchá. Á bé plus cé dé se rovná bé cé plus á dé. Devět plus pět je sedm plus á dé, "
                      "takže á dé je sedm centimetrů. Obvod je devět plus sedm plus pět plus sedm, dvacet osm centimetrů."):
            self.board.write("a)  |AB| + |CD| = |BC| + |AD|")
            self.board.write("9 + 5 = 7 + |AD|  ⇒  |AD| = 7 cm", indent=0.45)
            self.board.write("o = 9 + 7 + 5 + 7 = 28 cm", indent=0.45)
        # ---- b)
        vals = {}

        def put(v, txt, t):
            P1, P2 = V[v], T[t]
            n = (P1 + P2) / 2 - O0
            n = n / np.linalg.norm(n)
            return Tx(txt, 26, COL[v]).move_to((P1 + P2) / 2 + n * 0.36)

        with self.say("Část bé. Víme, že á pé je čtyři. To je tečnová délka vrcholu á. Teď prostě obejdeme čtyřúhelník dokola."):
            self.board.write("b)  x_{A} = |AP| = 4", gap=0.15)
            self.draw(put("A", "4", "P"), put("A", "4", "T"), run_time=0.6)
        with self.say("Na straně á bé zbývá na vrchol bé devět minus čtyři, tedy pět. A protože obě tečny z bé jsou stejné, "
                      "je i bé kvé pět."):
            self.board.write("x_{B} = |AB| − x_{A} = 9 − 4 = 5", indent=0.45)
            self.draw(put("B", "5", "P"), put("B", "5", "Q"), run_time=0.6)
        with self.say("Na straně bé cé zbývá na vrchol cé sedm minus pět, tedy dva."):
            self.board.write("x_{C} = |BC| − x_{B} = 7 − 5 = 2", indent=0.45)
            self.draw(put("C", "2", "Q"), put("C", "2", "R"), run_time=0.6)
        with self.say("Na straně cé dé zbývá na vrchol dé pět minus dva, tedy tři."):
            self.board.write("x_{D} = |CD| − x_{C} = 5 − 2 = 3", indent=0.45)
            self.draw(put("D", "3", "R"), put("D", "3", "T"), run_time=0.6)
        with self.say("A kontrola na poslední straně: dé té plus té á je tři plus čtyři, sedm. Přesně tolik vyšlo v části á. "
                      "Kdyby to nesedělo, udělali jsme někde chybu."):
            r = self.board.write("kontrola:  x_{D} + x_{A} = 3 + 4 = 7 = |AD| ✓", indent=0.45, color=GREEN)
        with self.say("Pomůcka na závěr, aby sis nepletl tečnový a tětivový čtyřúhelník: do kosočtverce se dá vepsat kružnice, "
                      "a kosočtverec má stejné strany, proto je podmínka tečnového čtyřúhelníku o stranách. Obdélníku se dá "
                      "opsat kružnice, ten má pravé úhly, proto je podmínka tětivového o úhlech."):
            self.board.write("tečnový: vepsaná, kosočtverec → strany", indent=0.0, color=GRAY, size=28)
            self.board.write("tětivový: opsaná, obdélník → úhly", indent=0.0, color=GRAY, size=28)

        fig = VGroup(self.quad(), self.tangent_pieces(width=5))
        for v1, v2, t in SIDES:
            for v in (v1, v2):
                fig.add(put(v, str(X[v]), t))
        self.summary(fig, [
            "tečny z jednoho bodu jsou stejně dlouhé  ⇒  tečnové délky x_{A}, …, x_{D}",
            "a + c = (x_{A} + x_{B}) + (x_{C} + x_{D}) = (x_{B} + x_{C}) + (x_{D} + x_{A}) = b + d",
            "a)  9 + 5 = 7 + |AD|  ⇒  |AD| = 7 cm,   o = 28 cm",
            "b)  x_{A} = 4,  x_{B} = 9 − 4 = 5,  x_{C} = 7 − 5 = 2,  x_{D} = 5 − 2 = 3",
            "kontrola:  x_{D} + x_{A} = 7 = |AD| ✓"],
            "Shrnutí. Tečny z jednoho bodu ke kružnici jsou stejně dlouhé, takže každý vrchol má svou tečnovou délku "
            "a každá strana je součtem dvou z nich. Proto se součty protějších stran rovnají: devět plus pět je sedm plus á dé, "
            "á dé je sedm a obvod dvacet osm. V části bé obejdeme čtyřúhelník: čtyři, pět, dva, tři, a kontrola tři plus čtyři je sedm.",
            size=26, dy=0.6, fig_w=4.6, x_text=-1.9,
            final="Zastav si video a zkus si to spočítat sám.")
