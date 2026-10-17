import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


class V64(ProofScene):
    CODE = "V 6.4"
    NAME = "Vnější úhel trojúhelníku"
    INDEX = 6
    SEED = 64

    def construct(self):
        self.intro(
            ["V každém trojúhelníku je velikost vnějšího úhlu při jednom vrcholu rovna",
             "součtu velikostí vnitřních úhlů u zbývajících dvou vrcholů:  α' = β + γ."],
            "Věta šest celá čtyři. V každém trojúhelníku je velikost vnějšího úhlu při jednom vrcholu "
            "rovna součtu velikostí vnitřních úhlů u zbývajících dvou vrcholů.")

        A, B, C = np.array([-4.5, -2.4, 0]), np.array([-0.9, -2.4, 0]), np.array([-3.4, 1.2, 0])
        D = np.array([-6.8, -2.4, 0])
        tri = hpoly(A, B, C)
        ext = hseg(A, D, color=PEN)
        pA, pB, pC, pD = Pt(A, "A", DOWN), Pt(B, "B", DR), Pt(C, "C", UP), Pt(D, "D", DOWN)
        al = AngleMark(A, B, C, 0.55, ORANGE, label="α")
        be = AngleMark(B, C, A, 0.65, GREEN, label="β")
        ga = AngleMark(C, A, B, 0.6, PURPLE, label="γ")
        alx = AngleMark(A, C, D, 0.8, RED, label="α'", label_r=1.15, fill_opacity=0.15)
        with self.say("Nakreslíme trojúhelník á bé cé s vnitřními úhly alfa, beta, gama."):
            self.draw(tri, run_time=1.5)
            self.draw(pA, pB, pC, run_time=0.5)
            self.draw(al, be, ga, run_time=1.0)
        with self.say("Vnější úhel při vrcholu á je úhel vedlejší k vnitřnímu úhlu alfa. "
                      "Dostaneme ho tak, že prodloužíme stranu bé á za bod á. Označíme ho alfa s čárkou."):
            self.draw(ext, pD, run_time=1.0)
            self.draw(alx, run_time=1.0)
        with self.say("Důkaz je krátký. Alfa a alfa s čárkou jsou vedlejší úhly, takže dohromady mají sto osmdesát stupňů."):
            self.board.write("[Dk.:  α + α' = 180°   (úhly vedlejší)")
            self.blink(al, alx, run_time=1.0)
        with self.say("A součet vnitřních úhlů v trojúhelníku je taky sto osmdesát stupňů, to je věta šest celá dva."):
            self.board.write("α + β + γ = 180°   (V 6.2)", indent=0.95)
            self.blink(al, be, ga, run_time=1.0)
        with self.say("V obou rovnostech je alfa a obě dávají sto osmdesát. Takže alfa s čárkou musí být "
                      "to samé co beta plus gama. Formálně: alfa s čárkou se rovná sto osmdesát minus alfa, "
                      "a to je beta plus gama."):
            self.board.write("⇒  α' = 180° − α = β + γ   ]", gap=0.1)
            r = self.board.lines[-1]
            self.play(Create(hbox(r)), run_time=0.7)
        with self.say("Hezky je to vidět i na obrázku. Úhel beta posuneme do vrcholu á a úhel gama otočíme "
                      "kolem středu strany á cé. Společně přesně vyplní vnější úhel alfa s čárkou."):
            cb = VGroup(be.fill.copy(), be.arcs.copy())
            self.play(cb.animate.shift(A - B), run_time=1.6)
            cg = VGroup(ga.fill.copy(), ga.arcs.copy())
            self.play(Rotate(cg, PI, about_point=(A + C) / 2), run_time=1.6)
            self.wait(0.5)
            self.play(FadeOut(cb), FadeOut(cg), run_time=0.5)

        fig = VGroup(hpoly(A, B, C), hseg(A, D), Pt(A, "A", DOWN), Pt(B, "B", DR), Pt(C, "C", UP), Pt(D, "D", DOWN),
                     AngleMark(A, B, C, 0.55, ORANGE, label="α"), AngleMark(B, C, A, 0.65, GREEN, label="β"),
                     AngleMark(C, A, B, 0.6, PURPLE, label="γ"),
                     AngleMark(A, C, D, 0.8, RED, label="α'", label_r=1.15, fill_opacity=0.15))
        self.summary(fig, [
            "[Dk.:  α + α' = 180°   (úhly vedlejší)",
            "α + β + γ = 180°",
            "⇒  α' = β + γ  ]"],
            "Shrnutí do písemky: alfa plus alfa s čárkou je sto osmdesát stupňů, protože jsou to vedlejší úhly. "
            "Alfa plus beta plus gama je sto osmdesát stupňů. Z toho alfa s čárkou se rovná beta plus gama.")
