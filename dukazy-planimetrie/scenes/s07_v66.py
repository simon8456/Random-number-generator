import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


class V66(ProofScene):
    CODE = "V 6.6"
    NAME = "Rovnoramenný trojúhelník"
    INDEX = 7
    SEED = 66

    def construct(self):
        self.intro(
            ["Pro každý △ABC platí:  △ABC je rovnoramenný se základnou AB  ⇔  |∢CAB| = |∢ABC|."],
            "Věta šest celá šest. Trojúhelník á bé cé je rovnoramenný se základnou á bé právě tehdy, "
            "když jsou úhly při základně stejně velké.")

        A, B, C = np.array([-5.7, -2.3, 0]), np.array([-1.7, -2.3, 0]), np.array([-3.7, 1.3, 0])
        tri = hpoly(A, B, C)
        pA, pB, pC = Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP)
        tk = VGroup(ticks(A, C, 1), ticks(B, C, 1))
        aA = AngleMark(A, B, C, 0.6, RED, label="α")
        aB = AngleMark(B, C, A, 0.6, RED, label="β")
        with self.say("Znak ekvivalence, šipka na obě strany, znamená dvě implikace. Musíme dokázat směr tam "
                      "i směr zpátky. Rovnoramenný se základnou á bé znamená, že ramena á cé a bé cé jsou stejně dlouhá."):
            self.draw(tri, run_time=1.5)
            self.draw(pA, pB, pC, run_time=0.5)
            self.draw(tk, run_time=0.6)

        with self.say("Nejdřív směr tam. Předpokládáme, že trojúhelník je rovnoramenný, tedy délka á cé se rovná délce bé cé."):
            self.board.write("1. „⇒“:  △ABC rovnoramenný, AB základna")
            self.board.write("⇒  |AC| = |BC|", indent=0.45)
        with self.say("A teď ten trik. Porovnáme trojúhelník á bé cé se stejným trojúhelníkem, ale přečteným v jiném "
                      "pořadí: bé á cé. Představ si, že trojúhelník zvedneme a překlopíme. Bod á se dostane na místo bodu bé, "
                      "bé na místo á a cé zůstane nahoře."):
            cp = VGroup(hfill(A, B, C, color=ORANGE, opacity=0.25), hpoly(A, B, C, color=ORANGE))
            lab = VGroup(label("B", A + np.array([-0.05, -0.75, 0]), ORANGE), label("A", B + np.array([0.05, -0.75, 0]), ORANGE),
                         label("C", C + np.array([0.5, 0.2, 0]), ORANGE))
            self.play(FadeIn(cp), run_time=0.5)
            self.play(Rotate(cp, PI, axis=UP, about_point=(A + B) / 2), run_time=2.0)
            self.play(FadeIn(lab), run_time=0.6)
            self.wait(1.0)
        with self.say("Podle věty es u es jsou trojúhelníky á bé cé a bé á cé shodné. Strana á cé odpovídá straně bé cé "
                      "a ty jsou stejně dlouhé. Úhel při vrcholu cé je v obou případech ten samý úhel. "
                      "A strana cé bé odpovídá straně cé á, i ty jsou stejné."):
            self.board.write("⇒  △ABC ≅ △BAC  (sus)", indent=0.45)
            self.play(Indicate(tk), run_time=0.9)
            gC = AngleMark(C, A, B, 0.55, PURPLE)
            self.draw(gC, run_time=0.6)
            self.play(Indicate(gC), run_time=0.8)
        with self.say("Ve shodných trojúhelnících jsou shodné i odpovídající si úhly. Úhlu při vrcholu á odpovídá "
                      "úhel při vrcholu bé. Takže úhel cé á bé je stejně velký jako úhel á bé cé."):
            self.draw(aA, aB, run_time=1.0)
            r = self.board.write("⇒  |∢CAB| = |∢ABC|", indent=0.45)
            self.play(FadeOut(cp), FadeOut(lab), run_time=0.6)

        with self.say("Teď směr zpátky. Předpokládáme, že úhly při základně jsou stejné, a chceme dokázat, "
                      "že ramena jsou stejně dlouhá."):
            self.play(FadeOut(tk), run_time=0.4)
            self.board.write("2. „⇐“:  |∢CAB| = |∢ABC|", gap=0.15)
        with self.say("Použijeme stejný trik, jen tentokrát větu u es u. Strana á bé odpovídá straně bé á, to je pořád "
                      "ta samá úsečka. A úhly k ní přilehlé si odpovídají: úhel při á úhlu při bé, a ty jsou podle "
                      "předpokladu stejné. Proto jsou trojúhelníky á bé cé a bé á cé shodné podle u es u."):
            self.hl((A, B), color=RED, run_time=0.9)
            self.blink(aA, aB, run_time=1.0)
            self.board.write("⇒  △ABC ≅ △BAC  (usu)", indent=0.45)
        with self.say("A ze shodnosti plyne, že strana á cé je stejně dlouhá jako strana bé cé. "
                      "Trojúhelník je tedy rovnoramenný."):
            self.draw(VGroup(ticks(A, C, 1), ticks(B, C, 1)), run_time=0.6)
            self.board.write("⇒  |AC| = |BC|", indent=0.45)
            self.board.write("⇒  △ABC je rovnoramenný  ]", indent=0.45)

        fig = VGroup(hpoly(A, B, C), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP), ticks(A, C, 1), ticks(B, C, 1),
                     AngleMark(A, B, C, 0.6, RED), AngleMark(B, C, A, 0.6, RED))
        self.summary(fig, [
            "[Dk.:  1. „⇒“:  △ABC rovnoramenný, AB – základna",
            "⇒  |AC| = |BC|  ⇒  △ABC ≅ △BAC (sus)",
            "⇒  |∢CAB| = |∢ABC|",
            "2. „⇐“:  |∢CAB| = |∢ABC|  ⇒  △ABC ≅ △BAC (usu)",
            "⇒  |AC| = |BC|  ⇒  △ABC je rovnoramenný  ]"],
            "Shrnutí do písemky. Směr tam: trojúhelník je rovnoramenný, takže á cé se rovná bé cé, a proto "
            "trojúhelník á bé cé je shodný s trojúhelníkem bé á cé podle es u es. Z toho úhel cé á bé se rovná úhlu á bé cé. "
            "Směr zpátky: úhly jsou stejné, takže á bé cé je shodný s bé á cé podle u es u, a proto á cé se rovná bé cé.")
