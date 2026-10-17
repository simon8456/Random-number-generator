import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


def ext_point(P, Q, L=1.4):
    """Bod na prodloužení úsečky PQ za Q."""
    u = (Q - P) / np.linalg.norm(Q - P)
    return Q + u * L


class V82(ProofScene):
    CODE = "V 8.2"
    NAME = "Vnější úhly konvexního čtyřúhelníku"
    INDEX = 9
    SEED = 82

    def construct(self):
        self.intro(
            ["Součet vnějších úhlů konvexního čtyřúhelníku je 360°, počítáme-li",
             "u každého vrcholu právě jeden:  α' + β' + γ' + δ' = 360°."],
            "Věta osm celá dva. Součet vnějších úhlů konvexního čtyřúhelníku je tři sta šedesát stupňů, "
            "pokud u každého vrcholu počítáme právě jeden vnější úhel.")

        A, B, C, D = (np.array([-5.6, -2.1, 0]), np.array([-2.3, -2.5, 0]),
                      np.array([-1.7, 0.5, 0]), np.array([-4.5, 1.0, 0]))
        q = hpoly(A, B, C, D)
        pts = VGroup(Pt(A, "A", LEFT), Pt(B, "B", DOWN), Pt(C, "C", RIGHT), Pt(D, "D", UP))
        Bx, Cx, Dx, Ax = ext_point(A, B), ext_point(B, C), ext_point(C, D), ext_point(D, A)
        exts = VGroup(*[hseg(P, Q, color=GRAY, width=2.6) for P, Q in ((B, Bx), (C, Cx), (D, Dx), (A, Ax))])
        al = AngleMark(A, B, D, 0.42, RED, label="α", label_r=0.68, font_size=26)
        be = AngleMark(B, C, A, 0.42, GREEN, label="β", label_r=0.68, font_size=26)
        ga = AngleMark(C, D, B, 0.42, PURPLE, label="γ", label_r=0.68, font_size=26)
        de = AngleMark(D, A, C, 0.42, ORANGE, label="δ", label_r=0.68, font_size=26)
        alx = AngleMark(A, Ax, B, 0.62, RED, label="α'", label_r=0.95, fill_opacity=0.32)
        bex = AngleMark(B, Bx, C, 0.62, GREEN, label="β'", label_r=0.95, fill_opacity=0.32)
        gax = AngleMark(C, Cx, D, 0.62, PURPLE, label="γ'", label_r=0.95, fill_opacity=0.32)
        dex = AngleMark(D, Dx, A, 0.62, ORANGE, label="δ'", label_r=0.95, fill_opacity=0.32)
        with self.say("Máme konvexní čtyřúhelník á bé cé dé s vnitřními úhly alfa, beta, gama, delta. "
                      "Vnější úhel u každého vrcholu dostaneme prodloužením jedné strany. "
                      "Je to úhel vedlejší k vnitřnímu úhlu."):
            self.draw(q, run_time=1.4)
            self.draw(pts, run_time=0.5)
            self.draw(al, be, ga, de, run_time=1.0)
            self.draw(exts, run_time=1.2)
            self.draw(alx, bex, gax, dex, run_time=1.4)

        with self.say("U každého vrcholu platí: vnější úhel plus vnitřní úhel je sto osmdesát stupňů, "
                      "protože jsou to vedlejší úhly."):
            self.board.write("[Dk.:  u každého vrcholu:")
            self.board.write("vnější + vnitřní = 180°  (úhly vedlejší)", indent=0.95)
            self.board.write("α' + α = 180°,   β' + β = 180°,  …", indent=0.95)
            self.blink(al, alx, run_time=0.9)
        with self.say("U každého ze čtyř vrcholů použijeme jen jeden vnější úhel. Když sečteme všechny vnější "
                      "a všechny vnitřní úhly dohromady, dostaneme čtyřikrát sto osmdesát, tedy sedm set dvacet stupňů."):
            self.board.write("⇒  (α'+β'+γ'+δ') + (α+β+γ+δ) =", indent=0.95)
            self.board.write("= 4 · 180° = 720°", indent=1.45)
        with self.say("Součet vnitřních úhlů čtyřúhelníku je ale tři sta šedesát stupňů, podle předchozí věty osm celá jedna."):
            self.board.write("α + β + γ + δ = 360°   (V 8.1)", indent=0.95)
        with self.say("Takže na vnější úhly zbývá sedm set dvacet minus tři sta šedesát, a to je tři sta šedesát stupňů."):
            self.board.write("⇒  α' + β' + γ' + δ' = 720° − 360°", indent=0.95)
            r = self.board.write("= 360°   ]", indent=1.45)
            self.play(Create(hbox(r)), run_time=0.7)

        P0 = np.array([-3.6, -0.7, 0])
        with self.say("A ještě hezká představa. Když všechny čtyři vnější úhly posuneme do jednoho bodu, "
                      "přesně na sebe navážou a vyplní celý kruh, tedy tři sta šedesát stupňů."):
            cps = []
            for m, V in ((alx, A), (bex, B), (gax, C), (dex, D)):
                c = VGroup(m.fill.copy().set_fill(opacity=0.6), m.arcs.copy())
                cps.append((c, P0 - V))
            self.play(*[c.animate.shift(s) for c, s in cps], run_time=2.5)
            self.wait(1.5)
            self.play(*[FadeOut(c) for c, _ in cps], run_time=0.6)

        fig = VGroup(hpoly(A, B, C, D), Pt(A, "A", LEFT), Pt(B, "B", DOWN), Pt(C, "C", RIGHT), Pt(D, "D", UP),
                     *[hseg(P, Q, color=GRAY, width=2.6) for P, Q in ((B, Bx), (C, Cx), (D, Dx), (A, Ax))],
                     AngleMark(A, Ax, B, 0.62, RED, label="α'", label_r=0.95, fill_opacity=0.32),
                     AngleMark(B, Bx, C, 0.62, GREEN, label="β'", label_r=0.95, fill_opacity=0.32),
                     AngleMark(C, Cx, D, 0.62, PURPLE, label="γ'", label_r=0.95, fill_opacity=0.32),
                     AngleMark(D, Dx, A, 0.62, ORANGE, label="δ'", label_r=0.95, fill_opacity=0.32))
        self.summary(fig, [
            "[Dk.:  vnější úhel = vedlejší k vnitřnímu",
            "⇒  vnější + vnitřní = 180°  (u každého vrcholu)",
            "součet vnějších a vnitřních:  4 · 180° = 720°",
            "součet vnitřních = 360°  (V 8.1)",
            "⇒  součet vnějších = 720° − 360° = 360°  ]"],
            "Shrnutí do písemky: vnější úhel je vedlejší k vnitřnímu, takže vnější plus vnitřní je sto osmdesát stupňů. "
            "U čtyř vrcholů je to dohromady sedm set dvacet stupňů. Vnitřní úhly mají tři sta šedesát, "
            "a proto vnější úhly mají sedm set dvacet minus tři sta šedesát, tedy tři sta šedesát stupňů.")
