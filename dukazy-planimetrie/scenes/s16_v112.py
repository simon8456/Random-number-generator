import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

y0 = -1.9
A, B = np.array([-5.6, y0, 0]), np.array([-1.8, y0, 0])
S = (A + B) / 2
X = np.array([-5.2, 1.0, 0])
Y = line_intersection(B, X, S, S + UP)


class V112(ProofScene):
    CODE = "V 11.2"
    NAME = "Poloroviny určené osou úsečky"
    INDEX = 16
    SEED = 112

    def construct(self):
        self.intro(
            ["Nechť AB je úsečka, o její osa. Pak platí:",
             "a)  ^{oA} = {X ∈ E₂:  |AX| ≤ |BX|}     b)  ^{oB} = {X ∈ E₂:  |AX| ≥ |BX|}"],
            "Věta jedenáct celá dva. Osa ó úsečky á bé rozdělí rovinu na dvě poloroviny. Polorovina ó á, "
            "ve které leží bod á, je přesně množina bodů, které mají k bodu á blíž nebo stejně daleko jako k bodu bé. "
            "A polorovina ó bé obráceně.")

        half = Polygon([-6.95, -3.9, 0], [S[0], -3.9, 0], [S[0], self.header_bottom - 0.05, 0],
                       [-6.95, self.header_bottom - 0.05, 0], stroke_width=0, fill_color=ORANGE, fill_opacity=0.12)
        o = hseg([S[0], -3.8, 0], [S[0], self.header_bottom - 0.2, 0], color=RED, width=3.2)
        g = VGroup(hseg(A, B), Pt(A, "A", DL), Pt(B, "B", DR), Pt(S, "S", DR, font_size=26))
        ol = label("o", [S[0] + 0.3, self.header_bottom - 0.45, 0], RED)
        hl = Tx("^{oA}", 32, ORANGE).move_to([-6.3, self.header_bottom - 0.5, 0])
        with self.say("Polorovina ó á je uzavřená polorovina s hraniční přímkou ó, ve které leží bod á. "
                      "Patří do ní i samotná osa. Dokážeme část á, část bé je úplně stejná. "
                      "Zase dokazujeme dvě inkluze."):
            self.draw(g, run_time=1.0)
            self.draw(o, ol, run_time=0.8)
            self.play(FadeIn(half), run_time=0.6)
            self.draw(hl, run_time=0.5)
            self.board.write("U = {X ∈ E₂:  |AX| ≤ |BX|}")

        with self.say("Jedna: každý bod poloroviny ó á splňuje vlastnost. Vezmeme bod iks z poloroviny. "
                      "Pokud leží na ose, platí á iks se rovná bé iks podle předchozí věty, takže nerovnost platí."):
            self.board.write("1.  Nechť X ∈ ^{oA}.", gap=0.1)
            self.board.write("X ∈ o  ⇒  |AX| = |BX|  (V 11.1)", indent=0.45)
        with self.say("Pokud iks neleží na ose, ale leží na přímce á bé, je to zřejmé: leží na straně bodu á, "
                      "a tak má k á blíž."):
            self.board.write("X ∉ o,  X ∈ AB  ⇒  zřejmé", indent=0.45)
        pX = Pt(X, "X", UL)
        with self.say("Zajímavý je poslední případ: iks neleží na ose ani na přímce á bé. Spojíme iks s bodem bé. "
                      "Bé leží v opačné polorovině, takže úsečka bé iks protne osu. Průsečík označíme ypsilon."):
            self.draw(pX, run_time=0.4)
            self.draw(hseg(B, X, color=INK), run_time=0.9)
            self.draw(Pt(Y, "Y", UR), run_time=0.4)
            self.board.write("X ∉ o,  X ∉ AB:", indent=0.45)
            self.board.write("označme  Y ∈ o ∩ BX", indent=0.95)
        with self.say("Bod ypsilon leží na ose, takže je od á a bé stejně daleko: bé ypsilon se rovná á ypsilon."):
            self.draw(hseg(A, Y, color=TEAL), run_time=0.7)
            self.draw(VGroup(ticks(A, Y, 1), ticks(B, Y, 1)), run_time=0.5)
        with self.say("Teď počítáme. Bé iks je bé ypsilon plus ypsilon iks. Bé ypsilon nahradíme á ypsilon. "
                      "A á ypsilon plus ypsilon iks je větší než á iks, to je trojúhelníková nerovnost v trojúhelníku á ypsilon iks: "
                      "cesta oklikou přes ypsilon je vždycky delší než přímá cesta."):
            self.board.write("|BX| = |BY| + |YX| =", indent=0.45)
            self.board.write("= |AY| + |YX| > |AX|", indent=0.95)
            self.play(FadeIn(hfill(A, Y, X, TEAL, 0.2)), run_time=0.5)
            self.draw(hseg(A, X, color=RED, width=4), run_time=0.7)
            self.board.write("(trojúhelníková nerovnost v △AYX)", indent=0.95, color=GRAY, size=27)
        with self.say("Vyšlo bé iks větší než á iks, takže vlastnost platí."):
            self.board.write("⇒  |BX| > |AX|  ⇒  platí vlastnost", indent=0.45)

        self.clear_body()
        X2 = np.array([-2.2, 0.8, 0])
        g2 = VGroup(hseg(A, B), Pt(A, "A", DL), Pt(B, "B", DR), Pt(S, "S", DR, font_size=26),
                    hseg([S[0], -3.8, 0], [S[0], self.header_bottom - 0.2, 0], color=RED, width=3.2),
                    label("o", [S[0] + 0.3, self.header_bottom - 0.45, 0], RED))
        half2 = Polygon([S[0], -3.9, 0], [-0.3, -3.9, 0], [-0.3, self.header_bottom - 0.05, 0],
                        [S[0], self.header_bottom - 0.05, 0], stroke_width=0, fill_color=TEAL, fill_opacity=0.12)
        with self.say("Dva: obrácená inkluze. Tu dokážeme obměnou. Místo každý bod s vlastností leží v polorovině "
                      "dokážeme ekvivalentní tvrzení: každý bod, který v polorovině neleží, vlastnost nemá."):
            self.play(FadeIn(g2), run_time=0.6)
            self.board.write("2.  obměna:  Nechť X ∉ ^{oA}.")
        with self.say("Bod iks mimo polorovinu ó á leží v opačné polorovině ó bé a na ose neleží. "
                      "Podle části jedna, jen s prohozenými body á a bé, platí bé iks menší než á iks."):
            self.play(FadeIn(half2), run_time=0.5)
            self.draw(Pt(X2, "X", UR), hseg(X2, A, color=INK), hseg(X2, B, color=INK), run_time=0.8)
            self.board.write("X ∉ o  ⇒  X ∈ ^{oB}", indent=0.45)
            self.board.write("⇒  |BX| < |AX|   (podle 1.)", indent=0.95)
        with self.say("Takže iks nesplňuje vlastnost á iks menší nebo rovno bé iks, a do množiny u nepatří. "
                      "Tím je část á dokázaná a část bé se dokáže analogicky."):
            self.board.write("⇒  neplatí vlastnost  |AX| ≤ |BX|", indent=0.45)
            self.board.write("b) analogicky   ]", indent=0.0, gap=0.1)

        fig = VGroup(Polygon([-6.95, -3.9, 0], [S[0], -3.9, 0], [S[0], 2.0, 0], [-6.95, 2.0, 0], stroke_width=0,
                             fill_color=ORANGE, fill_opacity=0.12),
                     hseg(A, B), Pt(A, "A", DL), Pt(B, "B", DR), hseg([S[0], -3.8, 0], [S[0], 2.0, 0], color=RED),
                     label("o", [S[0] + 0.3, 1.7, 0], RED), Pt(X, "X", UL), hseg(B, X, color=INK),
                     Pt(Y, "Y", UR), hseg(A, Y, color=TEAL), hseg(A, X, color=RED), ticks(A, Y, 1), ticks(B, Y, 1))
        self.summary(fig, [
            "[Dk.:  1.  Nechť X ∈ ^{oA}.",
            "X ∈ o  ⇒  platí podle V 11.1",
            "X ∉ o:  X ∈ AB – zřejmé;",
            "X ∉ AB:  označme  Y ∈ o ∩ BX",
            "|BX| = |BY| + |YX| = |AY| + |YX| > |AX|",
            "⇒  |BX| > |AX|  ⇒  platí vlastnost",
            "2.  Nechť X ∉ ^{oA}.  X ∉ o  ⇒  X ∈ ^{oB}",
            "⇒  |BX| < |AX|",
            "⇒  neplatí vlastnost pro polorovinu ^{oA}  ]"],
            "Shrnutí do písemky. Jedna: bod iks z poloroviny ó á. Na ose platí rovnost podle věty jedenáct celá jedna. "
            "Mimo osu a mimo přímku á bé označíme ypsilon průsečík osy s úsečkou bé iks. Pak bé iks je bé ypsilon plus "
            "ypsilon iks, to je á ypsilon plus ypsilon iks, a to je víc než á iks. Dva, obměnou: bod mimo polorovinu "
            "ó á leží v ó bé, takže bé iks je menší než á iks a vlastnost neplatí.",
            size=27, dy=0.57, x_text=-1.3)
