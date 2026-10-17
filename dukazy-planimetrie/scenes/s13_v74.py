import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

CB, CA = 1.3, 4.1
V = np.sqrt(CB * CA)
Bleg = np.sqrt(CB ** 2 + V ** 2)


def tri_pts(origin, s=1.0):
    o = np.array(origin, dtype=float)
    return o + s * np.array([-CB, 0, 0]), o + s * np.array([CA, 0, 0]), o + s * np.array([0, V, 0]), o


class V74(ProofScene):
    CODE = "V 7.4"
    NAME = "Eukleidova věta o odvěsně"
    INDEX = 13
    SEED = 74

    def construct(self):
        self.intro(
            ["Nechť je dán pravoúhlý △ABC s přeponou AB, pak platí:",
             "b² = c · c_{b},   a² = c · c_{a}"],
            "Věta sedm celá čtyři, Eukleidovy věty o odvěsnách. V pravoúhlém trojúhelníku s přeponou á bé platí: "
            "bé na druhou se rovná cé krát cé bé a á na druhou se rovná cé krát cé á.")

        A, B, C, C0 = tri_pts([-1.4, -1.5, 0])
        lab = VGroup(Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UR), Pt(C0, "C₀", DOWN + RIGHT * 0.4, font_size=28))
        fig = VGroup(hpoly(A, B, C), hseg(C, C0, color=INK), RightMark(C, A, B), RightMark(C0, B, C, r=0.3))
        sides = VGroup(Tx("b", 30, PEN).move_to((A + C) / 2 + np.array([0.3, -0.12, 0])),
                       Tx("a", 30, PEN).move_to((B + C) / 2 + np.array([0.2, 0.25, 0])),
                       Tx("c_{b}", 28, ORANGE).move_to((A + C0) / 2 + DOWN * 0.35))
        with self.say("Co věta říká? Odvěsny značíme jako obvykle á a bé, přeponu cé. Úsek přepony u vrcholu á, "
                      "tedy přilehlý k odvěsně bé, je cé bé. Úsek u vrcholu bé je cé á."):
            self.draw(fig, run_time=1.6)
            self.draw(lab, sides, run_time=0.8)
        n = np.array([-V, CB, 0])
        sq = VGroup(hfill(A, C, C + n, A + n, color=ORANGE, opacity=0.2), hpoly(A, C, C + n, A + n, color=ORANGE, width=2.6))
        rect = VGroup(hfill(A, B, B + DOWN * CB, A + DOWN * CB, color=ORANGE, opacity=0.2),
                      hpoly(A, B, B + DOWN * CB, A + DOWN * CB, color=ORANGE, width=2.6))
        with self.say("Obsah čtverce nad odvěsnou bé je stejný jako obsah obdélníku se stranami cé a cé bé, "
                      "tedy celá přepona krát přilehlý úsek. Pro odvěsnu á to platí stejně s úsekem cé á."):
            self.draw(sq, run_time=1.2)
            self.draw(rect, run_time=1.2)
            self.draw(Tx("b²", 34, ORANGE).move_to(A + (C - A) / 2 + n / 2),
                      Tx("c · c_{b}", 30, ORANGE).move_to((A + B) / 2 + DOWN * CB / 2), run_time=0.8)
            self.wait(1.0)

        self.clear_body()
        A, B, C, C0 = tri_pts([-5.1, -1.5, 0])
        base = VGroup(hpoly(A, B, C), hseg(C, C0, color=INK), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP),
                      Pt(C0, "C₀", DOWN, font_size=28), RightMark(C, A, B), RightMark(C0, B, C, r=0.3),
                      Tx("b", 28, PEN).move_to((A + C) / 2 + np.array([-0.3, 0.12, 0])),
                      Tx("a", 28, PEN).move_to((B + C) / 2 + np.array([0.2, 0.25, 0])),
                      Tx("c_{b}", 26, ORANGE).move_to((A + C0) / 2 + DOWN * 0.33))
        small = hfill(A, C0, C, ORANGE, 0.3)
        big = hfill(A, B, C, TEAL, 0.12)
        with self.say("Důkaz. Porovnáme malý trojúhelník á cé nula cé s celým trojúhelníkem á cé bé."):
            self.play(FadeIn(base), run_time=0.8)
            self.play(FadeIn(big), FadeIn(small), run_time=0.8)
            self.board.write("[Dk.:  △AC₀C ∼ △ACB  (uu):")
        aA = AngleMark(A, B, C, 0.55, RED, label="α")
        with self.say("Oba mají u vrcholu á stejný úhel alfa, je společný."):
            self.draw(aA, run_time=0.7)
            self.board.write("úhel α při vrcholu A je společný", indent=0.95)
        with self.say("A oba mají pravý úhel: malý trojúhelník u vrcholu cé nula, velký u vrcholu cé. "
                      "Shodují se ve dvou úhlech, takže jsou podobné podle věty u u."):
            self.play(Indicate(base[7]), Indicate(base[6]), run_time=1.0)
            self.board.write("|∢AC₀C| = |∢ACB| = 90°", indent=0.95)
        bis = (B - A) / np.linalg.norm(B - A) + (C - A) / np.linalg.norm(C - A)
        with self.say("Odpovídající si vrcholy jsou: á odpovídá á, cé nula odpovídá cé, a cé odpovídá bé. "
                      "Na obrázku: malý trojúhelník překlopíme podle osy úhlu alfa a zvětšíme, a padne na velký."):
            cp = VGroup(small.copy(), hpoly(A, C0, C, color=ORANGE))
            self.play(Rotate(cp, PI, axis=bis, about_point=A), run_time=1.8)
            self.play(cp.animate.scale(Bleg / CB, about_point=A), run_time=1.5)
            self.wait(0.4)
            self.play(FadeOut(cp), run_time=0.5)
        with self.say("Poměry odpovídajících si stran jsou stejné. Strana á cé nula odpovídá straně á cé, "
                      "a strana á cé odpovídá straně á bé. Takže á cé nula ku á cé se rovná á cé ku á bé."):
            self.board.write(Row("⇒", Frac("|AC₀|", "|AC|", 30), "=", Frac("|AC|", "|AB|", 30), size=30))
        with self.say("V obvyklém značení: cé bé ku bé se rovná bé ku cé. Roznásobíme a máme bé na druhou "
                      "se rovná cé krát cé bé."):
            self.board.write(Row(Frac("c_{b}", "b", 30), "=", Frac("b", "c", 30), size=30))
            r = self.board.write("⇒   b² = c · c_{b}")
            self.play(Create(hbox(r)), run_time=0.6)
        with self.say("Pro odvěsnu á je to úplně stejné, jen použijeme trojúhelník bé cé nula cé, který je podobný "
                      "trojúhelníku bé cé á, se společným úhlem beta. Dostaneme cé á ku á se rovná á ku cé, "
                      "tedy á na druhou se rovná cé krát cé á."):
            self.play(FadeOut(small), FadeIn(hfill(C0, B, C, PURPLE, 0.25)), run_time=0.6)
            self.draw(AngleMark(B, C, A, 0.6, GREEN, label="β"), run_time=0.6)
            self.board.write("analogicky △BC₀C ∼ △BCA (uu):")
            self.board.write(Row(Frac("c_{a}", "a", 30), "=", Frac("a", "c", 30), "⇒   a² = c · c_{a}   ]", size=30))

        A, B, C, C0 = tri_pts([-4.6, -1.2, 0])
        sfig = VGroup(hpoly(A, B, C), hseg(C, C0, color=INK), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP),
                      Pt(C0, "C₀", DOWN, font_size=28), RightMark(C, A, B), RightMark(C0, B, C, r=0.3),
                      AngleMark(A, B, C, 0.55, RED, label="α"), AngleMark(B, C, A, 0.6, GREEN, label="β"),
                      Tx("b", 28, PEN).move_to((A + C) / 2 + np.array([-0.3, 0.12, 0])),
                      Tx("a", 28, PEN).move_to((B + C) / 2 + np.array([0.2, 0.25, 0])),
                      Tx("c_{b}", 26, ORANGE).move_to((A + C0) / 2 + DOWN * 0.33),
                      Tx("c_{a}", 26, TEAL).move_to((B + C0) / 2 + DOWN * 0.33))
        self.summary(sfig, [
            "[Dk.:  △AC₀C ∼ △ACB (uu)",
            "(společný úhel α, pravé úhly u C₀ a C)",
            Row(Frac("|AC₀|", "|AC|", 28), "=", Frac("|AC|", "|AB|", 28), size=28),
            Row(Frac("c_{b}", "b", 28), "=", Frac("b", "c", 28), "⇒   b² = c · c_{b}", size=28),
            "△BC₀C ∼ △BCA (uu)   (společný úhel β)",
            Row(Frac("c_{a}", "a", 28), "=", Frac("a", "c", 28), "⇒   a² = c · c_{a}   ]", size=28)],
            "Shrnutí do písemky: trojúhelník á cé nula cé je podobný trojúhelníku á cé bé podle u u, mají společný úhel "
            "alfa a pravý úhel. Proto cé bé ku bé se rovná bé ku cé, tedy bé na druhou je cé krát cé bé. "
            "Analogicky trojúhelník bé cé nula cé je podobný trojúhelníku bé cé á, a vyjde á na druhou je cé krát cé á.",
            x_text=-0.6)
