import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


class V62(ProofScene):
    CODE = "V 6.2"
    NAME = "Součet vnitřních úhlů v trojúhelníku"
    INDEX = 4
    SEED = 62

    def construct(self):
        self.intro(
            ["Součet všech vnitřních úhlů v trojúhelníku je 180°:  α + β + γ = 180°."],
            "Věta šest celá dva. Součet všech vnitřních úhlů v trojúhelníku je sto osmdesát stupňů. "
            "Tedy v každém trojúhelníku á bé cé platí: alfa plus beta plus gama se rovná sto osmdesát stupňů.")

        A, B, C = np.array([-6.0, -2.6, 0]), np.array([-1.2, -2.6, 0]), np.array([-4.2, 0.9, 0])
        tri = hpoly(A, B, C)
        pA, pB, pC = Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP, buff=0.15)
        al = AngleMark(A, B, C, 0.6, RED, label="α")
        be = AngleMark(B, C, A, 0.6, GREEN, label="β")
        ga = AngleMark(C, A, B, 0.55, PURPLE, label="γ")
        with self.say("Nakreslíme si libovolný trojúhelník á bé cé. Vnitřní úhly označíme jako obvykle: "
                      "alfa u vrcholu á, beta u vrcholu bé a gama u vrcholu cé."):
            self.draw(tri, run_time=2)
            self.draw(pA, pB, pC, run_time=0.6)
            self.draw(al, run_time=0.7)
            self.draw(be, run_time=0.7)
            self.draw(ga, run_time=0.7)

        Lp, Rp = np.array([-6.9, C[1], 0]), np.array([-0.5, C[1], 0])
        p = hseg(Lp, Rp, color=INK, width=3.2)
        plab = label("p", Rp + np.array([-0.15, 0.3, 0]), INK)
        with self.say("A teď hlavní trik celého důkazu. Bodem cé vedeme přímku pé, "
                      "která je rovnoběžná se stranou á bé."):
            self.draw(p, run_time=1.5)
            self.draw(plab, run_time=0.4)
            self.board.write("Sestrojme  p ∥ AB,  C ∈ p.")

        de = AngleMark(C, Lp, A, 0.75, RED, label="δ", label_r=1.05)
        ep = AngleMark(C, B, Rp, 0.75, GREEN, label="ε", label_r=1.05)
        with self.say("U vrcholu cé tak vzniknou na přímce pé dva nové úhly: vlevo úhel delta "
                      "a vpravo úhel epsilon."):
            self.draw(de, run_time=0.9)
            self.draw(ep, run_time=0.9)

        tAC = hline(A, C, ext=0.6, color=ORANGE, width=4)
        mAC = (A + C) / 2
        with self.say("Podívej se na úhly alfa a delta. Přímka á cé protíná obě rovnoběžky, "
                      "přímku á bé i přímku pé. Alfa a delta leží na opačných stranách této příčky "
                      "a mezi rovnoběžkami, jsou to tedy střídavé úhly. A střídavé úhly u rovnoběžek jsou shodné. "
                      "Vidíš to i na obrázku: když úhel alfa otočíme o sto osmdesát stupňů kolem středu úsečky á cé, "
                      "přesně padne na úhel delta."):
            self.draw(tAC, run_time=1.0)
            self.blink(al, de, run_time=1.0)
            self.wait(max(0.1, self.left() - 4.2))
            cp = VGroup(al.fill.copy(), al.arcs.copy())
            self.play(Rotate(cp, PI, about_point=mAC), run_time=2.2)
            self.play(FadeOut(cp), run_time=0.4)
            self.board.write("α = δ   (střídavé úhly)")
        self.play(FadeOut(tAC), run_time=0.4)

        tBC = hline(B, C, ext=0.6, color=ORANGE, width=4)
        mBC = (B + C) / 2
        with self.say("Úplně stejně to funguje u úhlů beta a epsilon. Tentokrát je příčkou přímka bé cé. "
                      "Beta a epsilon jsou střídavé úhly, a proto se beta rovná epsilon."):
            self.draw(tBC, run_time=0.9)
            cp = VGroup(be.fill.copy(), be.arcs.copy())
            self.play(Rotate(cp, PI, about_point=mBC), run_time=2.0)
            self.play(FadeOut(cp), run_time=0.4)
            self.board.write("β = ε   (střídavé úhly)")
        self.play(FadeOut(tBC), run_time=0.4)

        with self.say("Teď si všimni, že úhly delta, gama a epsilon leží u bodu cé hezky vedle sebe "
                      "a dohromady vyplní celý přímý úhel na přímce pé. Přímý úhel má sto osmdesát stupňů, "
                      "takže delta plus gama plus epsilon je sto osmdesát stupňů."):
            self.play(de.fill.animate.set_fill(opacity=0.45), ga.fill.animate.set_fill(opacity=0.45),
                      ep.fill.animate.set_fill(opacity=0.45), run_time=1.0)
            self.play(Indicate(p, color=RED), run_time=1.0)
            self.board.write("δ + γ + ε = 180°", gap=0.15)
            self.play(de.fill.animate.set_fill(opacity=0.22), ga.fill.animate.set_fill(opacity=0.22),
                      ep.fill.animate.set_fill(opacity=0.22), run_time=0.6)

        with self.say("A teď už jen dosadíme. Místo delta napíšeme alfa a místo epsilon napíšeme beta. "
                      "Dostaneme alfa plus beta plus gama se rovná sto osmdesát stupňů. A to jsme chtěli dokázat."):
            res = self.board.make("⇒  α + β + γ = 180°", gap=0.15)
            self.write(res)
            self.play(Create(hbox(res)), run_time=0.8)

        # ---- zápis do písemky
        fig = VGroup(hpoly(A, B, C), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP, buff=0.15),
                     hseg(Lp, Rp, color=INK), label("p", Rp + np.array([-0.15, 0.3, 0]), INK),
                     AngleMark(A, B, C, 0.6, RED, label="α"), AngleMark(B, C, A, 0.6, GREEN, label="β"),
                     AngleMark(C, A, B, 0.55, PURPLE, label="γ"),
                     AngleMark(C, Lp, A, 0.75, RED, label="δ", label_r=1.05),
                     AngleMark(C, B, Rp, 0.75, GREEN, label="ε", label_r=1.05))
        self.summary(fig, [
            "[Dk.:  Sestrojme  p ∥ AB,  C ∈ p.",
            "α = δ  (střídavé úhly)",
            "β = ε  (střídavé úhly)",
            "δ + γ + ε = 180°",
            "⇒  α + β + γ = 180°  ]"],
            "Shrnutí, jak to napíšeš do písemky. Nakresli obrázek s rovnoběžkou pé. "
            "Pak napiš: sestrojme pé rovnoběžnou s á bé, cé leží na pé. "
            "Alfa se rovná delta a beta se rovná epsilon, protože jsou to střídavé úhly. "
            "Delta plus gama plus epsilon je sto osmdesát stupňů, a proto alfa plus beta plus gama "
            "je sto osmdesát stupňů.")
