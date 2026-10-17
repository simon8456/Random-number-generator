import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

y0 = -1.4
A, B = np.array([-5.8, y0, 0]), np.array([-1.6, y0, 0])
S = (A + B) / 2


def fig_base():
    return VGroup(hseg(A + LEFT * 0.6, B + RIGHT * 0.6, color=GRAY, width=2.4), hseg(A, B),
                  Pt(A, "A", DL), Pt(B, "B", DR), Pt(S, "S", DR, font_size=28),
                  hseg(S + DOWN * 2.2, S + UP * 4.0, color=RED, width=3.2),
                  label("o", S + np.array([0.3, 3.8, 0]), RED), RightMark(S, B, S + UP, r=0.3, color=RED))


class V111(ProofScene):
    CODE = "V 11.1"
    NAME = "Osa úsečky jako množina bodů"
    INDEX = 15
    SEED = 111

    def construct(self):
        self.intro(
            ["Nechť AB je úsečka. Množinou všech bodů X ∈ E₂, pro něž |AX| = |BX|,",
             "je osa o úsečky AB."],
            "Věta jedenáct celá jedna. Množinou všech bodů iks, které mají stejnou vzdálenost od bodů á a bé, "
            "je osa úsečky á bé.")

        g = fig_base()
        with self.say("Osa úsečky je přímka, která prochází středem es úsečky á bé a je na ni kolmá."):
            self.draw(g[0], g[1], run_time=1.0)
            self.draw(g[2], g[3], g[4], run_time=0.6)
            self.draw(g[5], g[6], g[7], run_time=1.2)
        with self.say("Označíme u množinu všech bodů, které mají od á a bé stejnou vzdálenost. Máme dokázat, že u je "
                      "přesně osa ó. U množin bodů vždycky dokazujeme dvě věci. Za prvé, že každý bod osy patří do u, "
                      "tedy ó je podmnožina u. A za druhé, že každý bod z u leží na ose, tedy u je podmnožina ó. "
                      "Jen tak víme, že jsou to stejné množiny."):
            self.board.write("U = {X ∈ E₂:  |AX| = |BX|}")
            self.board.write("chceme:  o ⊆ U  ∧  U ⊆ o", color=GRAY, size=29)

        X = S + UP * 2.6
        pX = Pt(X, "X", RIGHT)
        with self.say("Část jedna: ó je podmnožina u. Vezmeme libovolný bod iks na ose. Může nastat, že iks leží "
                      "přímo na přímce á bé. Pak je to střed es, a ten má od á i bé stejnou vzdálenost, takže patří do u."):
            self.board.write("1.  o ⊆ U:   X ∈ o lib.  ⇒", gap=0.1)
            self.board.write("X ∈ AB  ⇒  X = S", indent=0.45)
            self.board.write("⇒  |AS| = |BS|  ⇒  X ∈ U", indent=0.95)
            self.play(Indicate(g[4], color=RED), run_time=0.8)
        XA, XB = hseg(X, A, color=INK), hseg(X, B, color=INK)
        f1, f2 = hfill(A, S, X, ORANGE, 0.2), hfill(B, S, X, TEAL, 0.2)
        with self.say("Jinak iks na přímce á bé neleží. Porovnáme trojúhelníky á es iks a bé es iks. "
                      "Jsou shodné podle es u es: á es se rovná bé es, protože es je střed. Úhly u vrcholu es jsou "
                      "oba pravé, protože osa je kolmá. A strana es iks je společná."):
            self.draw(pX, run_time=0.4)
            self.draw(XA, XB, run_time=0.8)
            self.play(FadeIn(f1), FadeIn(f2), run_time=0.6)
            self.draw(VGroup(ticks(A, S, 1), ticks(S, B, 1)), RightMark(S, A, X, r=0.3, color=RED), run_time=0.6)
            self.board.write("X ∉ AB  ⇒  △ASX ≅ △BSX (sus)", indent=0.45)
            self.board.write("⇒  |AX| = |BX|  ⇒  X ∈ U", indent=0.95)
        with self.say("Ze shodnosti je á iks rovno bé iks, takže iks patří do u. První část je hotová."):
            self.draw(VGroup(ticks(X, A, 2), ticks(X, B, 2)), run_time=0.6)
            self.wait(0.5)

        self.clear_body()
        g2 = fig_base()
        X2 = np.array([S[0], 1.5, 0])
        with self.say("Část dva: u je podmnožina ó. Teď vezmeme libovolný bod iks, o kterém víme jen to, že má od á a bé "
                      "stejnou vzdálenost. Chceme ukázat, že leží na ose."):
            self.play(FadeIn(g2[:5]), run_time=0.6)
            self.board.write("2.  U ⊆ o:   X ∈ U lib.")
            self.board.write("⇒  |AX| = |BX|  ⇒", indent=0.95)
        with self.say("Když iks leží na přímce á bé, musí to být střed es, a ten na ose leží."):
            self.board.write("X ∈ AB  ⇒  X = S ∈ o", indent=0.45)
        pX2 = Pt(X2, "X", UP)
        with self.say("Když iks na přímce á bé neleží, je trojúhelník á bé iks rovnoramenný se základnou á bé, "
                      "protože ramena á iks a bé iks jsou stejně dlouhá."):
            self.draw(pX2, run_time=0.4)
            self.draw(hseg(X2, A, color=INK), hseg(X2, B, color=INK), run_time=0.8)
            self.draw(VGroup(ticks(X2, A, 2), ticks(X2, B, 2)), run_time=0.5)
            self.board.write("X ∉ AB  ⇒  ∃ △ABX – rovnoramenný", indent=0.45)
            self.board.write("se základnou AB,", indent=0.95)
        with self.say("V rovnoramenném trojúhelníku je těžnice na základnu zároveň výškou, to je věta šest celá dvanáct. "
                      "Úsečka iks es je těžnice, protože es je střed á bé, a tedy je i výška. "
                      "Takže iks es je kolmá na á bé, a přímka iks es je právě osa ó. Bod iks tedy na ose leží."):
            self.draw(hseg(X2, S, color=PURPLE, width=3.4), run_time=0.8)
            self.draw(RightMark(S, B, X2, r=0.3, color=PURPLE), run_time=0.5)
            self.board.write("XS je těžnice, ale i výška  (V 6.12)", indent=0.95)
            self.board.write("⇒  XS ⊥ AB  ⇒  X ∈ o   ]", indent=0.95)
            self.draw(g2[5], g2[6], run_time=0.8)

        X = S + UP * 2.6
        fig = VGroup(fig_base(), Pt(X, "X", RIGHT), hseg(X, A, color=INK), hseg(X, B, color=INK),
                     ticks(A, S, 1), ticks(S, B, 1), ticks(X, A, 2), ticks(X, B, 2))
        self.summary(fig, [
            "[Dk.:  U = {X ∈ E₂: |AX| = |BX|}",
            "1.  o ⊆ U:  X ∈ o lib.:",
            "X ∈ AB ⇒ X = S ⇒ |AS| = |BS| ⇒ X ∈ U",
            "X ∉ AB ⇒ △ASX ≅ △BSX (sus) ⇒ |AX| = |BX| ⇒ X ∈ U",
            "2.  U ⊆ o:  X ∈ U lib. ⇒ |AX| = |BX|:",
            "X ∈ AB ⇒ X = S ∈ o",
            "X ∉ AB ⇒ △ABX rovnoramenný se základnou AB,",
            "XS je těžnice i výška ⇒ XS ⊥ AB ⇒ X ∈ o  ]"],
            "Shrnutí do písemky. Označíme u množinu bodů se stejnou vzdáleností od á a bé. Jedna: ó je podmnožina u. "
            "Bod osy na přímce á bé je střed. Jinak jsou trojúhelníky á es iks a bé es iks shodné podle es u es, "
            "takže á iks se rovná bé iks. Dva: u je podmnožina ó. Bod na přímce á bé je střed. Jinak je trojúhelník "
            "á bé iks rovnoramenný, těžnice iks es je i výška, takže iks leží na ose.",
            size=27, dy=0.56, x_text=-1.0)
