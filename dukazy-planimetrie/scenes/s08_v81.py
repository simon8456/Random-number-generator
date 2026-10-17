import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


class V81(ProofScene):
    CODE = "V 8.1"
    NAME = "Součet vnitřních úhlů ve čtyřúhelníku"
    INDEX = 8
    SEED = 81

    def construct(self):
        self.intro(
            ["Součet vnitřních úhlů ve čtyřúhelníku je 360°:  α + β + γ + δ = 360°."],
            "Věta osm celá jedna. Součet vnitřních úhlů ve čtyřúhelníku je tři sta šedesát stupňů.")

        A, B, C, D = (np.array([-6.3, -2.6, 0]), np.array([-1.2, -2.2, 0]),
                      np.array([-1.8, 1.2, 0]), np.array([-5.2, 1.7, 0]))
        q = hpoly(A, B, C, D)
        pts = VGroup(Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UR), Pt(D, "D", UL))
        al = AngleMark(A, B, D, 0.6, RED, label="α")
        be = AngleMark(B, C, A, 0.85, GREEN, fill_opacity=0.12, label="β", label_r=1.1)
        ga = AngleMark(C, D, B, 0.6, PURPLE, label="γ")
        de = AngleMark(D, A, C, 0.85, ORANGE, fill_opacity=0.12, label="δ", label_r=1.1)
        with self.say("Máme čtyřúhelník á bé cé dé s vnitřními úhly alfa, beta, gama a delta."):
            self.draw(q, run_time=1.6)
            self.draw(pts, run_time=0.5)
            self.draw(al, be, ga, de, run_time=1.2)
        diag = hseg(B, D, color=INK, width=3.4)
        f1, f2 = hfill(A, B, D, ORANGE, 0.16), hfill(B, C, D, TEAL, 0.16)
        with self.say("Celý trik: vedeme úhlopříčku bé dé. Ta rozdělí čtyřúhelník na dva trojúhelníky, "
                      "á bé dé a bé cé dé. U nekonvexního čtyřúhelníku bychom zvolili tu úhlopříčku, která leží uvnitř."):
            self.play(FadeOut(be.label), FadeOut(de.label), run_time=0.3)
            self.draw(diag, run_time=1.0)
            self.play(FadeIn(f1), FadeIn(f2), run_time=0.8)
            self.board.write("[Dk.:  úhlopříčka BD rozdělí ABCD")
            self.board.write("na  △ABD  a  △BCD", indent=0.95)
        b1 = AngleMark(B, D, A, 0.5, GREEN, label="β₁", label_r=0.85, font_size=26)
        b2 = AngleMark(B, C, D, 0.5, GREEN, label="β₂", label_r=0.85, font_size=26)
        d1 = AngleMark(D, A, B, 0.5, ORANGE, label="δ₁", label_r=0.85, font_size=26)
        d2 = AngleMark(D, B, C, 0.5, ORANGE, label="δ₂", label_r=0.85, font_size=26)
        with self.say("Úhlopříčka rozdělí úhel beta na dvě části, beta jedna a beta dva. A stejně tak úhel delta "
                      "na delta jedna a delta dva."):
            self.play(FadeOut(be), FadeOut(de), run_time=0.4)
            self.draw(b1, b2, run_time=0.8)
            self.draw(d1, d2, run_time=0.8)
            self.board.write("β = β₁ + β₂,   δ = δ₁ + δ₂", indent=0.95)
        with self.say("V trojúhelníku á bé dé je součet úhlů sto osmdesát stupňů: alfa plus beta jedna plus delta jedna."):
            self.play(f1.animate.set_fill(opacity=0.35), run_time=0.6)
            self.board.write("α + β₁ + δ₁ = 180°   (△ABD)", indent=0.95)
            self.play(f1.animate.set_fill(opacity=0.16), run_time=0.4)
        with self.say("A v trojúhelníku bé cé dé: gama plus beta dva plus delta dva je také sto osmdesát stupňů."):
            self.play(f2.animate.set_fill(opacity=0.35), run_time=0.6)
            l2 = self.board.write("γ + β₂ + δ₂ = 180°   (△BCD)", indent=0.95)
            self.play(f2.animate.set_fill(opacity=0.16), run_time=0.4)
        with self.say("Obě rovnosti sečteme, jako při sčítání pod sebou. Beta jedna plus beta dva je beta "
                      "a delta jedna plus delta dva je delta. Vyjde alfa plus beta plus gama plus delta "
                      "rovná se tři sta šedesát stupňů."):
            bar = hseg([self.board.x + 0.9, l2.get_bottom()[1] - 0.12, 0],
                       [self.board.x + 5.2, l2.get_bottom()[1] - 0.12, 0], color=INK, width=2.4)
            self.draw(bar, run_time=0.5)
            self.board.skip(0.1)
            r = self.board.write("α + β + γ + δ = 360°   ]", indent=0.95)
            self.play(Create(hbox(r)), run_time=0.7)

        fig = VGroup(hpoly(A, B, C, D), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UR), Pt(D, "D", UL),
                     hseg(B, D, color=INK), AngleMark(A, B, D, 0.6, RED, label="α"),
                     AngleMark(C, D, B, 0.6, PURPLE, label="γ"),
                     AngleMark(B, D, A, 0.5, GREEN, label="β₁", label_r=0.85, font_size=26),
                     AngleMark(B, C, D, 0.5, GREEN, label="β₂", label_r=0.85, font_size=26),
                     AngleMark(D, A, B, 0.5, ORANGE, label="δ₁", label_r=0.85, font_size=26),
                     AngleMark(D, B, C, 0.5, ORANGE, label="δ₂", label_r=0.85, font_size=26))
        self.summary(fig, [
            "[Dk.:  α + β₁ + δ₁ = 180°",
            "γ + β₂ + δ₂ = 180°",
            "――――――――――――――",
            "α + β + γ + δ = 360°  ]"],
            "Shrnutí do písemky: nakresli úhlopříčku bé dé a označ části úhlů. Alfa plus beta jedna plus delta jedna "
            "je sto osmdesát stupňů, gama plus beta dva plus delta dva je sto osmdesát stupňů. "
            "Sečtením dostaneš alfa plus beta plus gama plus delta je tři sta šedesát stupňů.")
