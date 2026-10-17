import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

CB, CA = 1.3, 4.1
V = np.sqrt(CB * CA)


def tri_pts(origin, s=1.0):
    """Pravoúhlý △ABC s přeponou AB vodorovně; origin = pata výšky C₀."""
    o = np.array(origin, dtype=float)
    A = o + s * np.array([-CB, 0, 0])
    B = o + s * np.array([CA, 0, 0])
    C = o + s * np.array([0, V, 0])
    return A, B, C, o


class V73(ProofScene):
    CODE = "V 7.3"
    NAME = "Eukleidova věta o výšce"
    INDEX = 12
    SEED = 73

    def construct(self):
        self.intro(
            ["Nechť je dán pravoúhlý △ABC s přeponou AB, pak platí:  v_{c}² = c_{b} · c_{a}"],
            "Věta sedm celá tři, Eukleidova věta o výšce. V pravoúhlém trojúhelníku á bé cé s přeponou á bé "
            "platí: vé cé na druhou se rovná cé bé krát cé á.")

        # --- co věta říká
        A, B, C, C0 = tri_pts([-1.4, -1.1, 0])
        tri = hpoly(A, B, C)
        h = hseg(C, C0, color=INK, width=3.2)
        lab = VGroup(Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP), Pt(C0, "C₀", DOWN + RIGHT * 0.4, font_size=28))
        rC = RightMark(C, A, B)
        r0 = RightMark(C0, B, C, r=0.3)
        with self.say("Nejdřív co věta říká. Máme pravoúhlý trojúhelník s pravým úhlem u vrcholu cé. "
                      "Z vrcholu cé spustíme výšku na přeponu, její patu označíme cé nula. Délku výšky značíme vé cé."):
            self.draw(tri, run_time=1.5)
            self.draw(lab[:3], rC, run_time=0.6)
            self.draw(h, run_time=0.8)
            self.draw(lab[3], r0, run_time=0.5)
            vl = Tx("v_{c}", 30, INK).move_to((C + C0) / 2 + LEFT * 0.38)
            self.draw(vl, run_time=0.5)
        cbl = Tx("c_{b}", 30, ORANGE).move_to((A + C0) / 2 + DOWN * 0.38)
        cal = Tx("c_{a}", 30, TEAL).move_to((B + C0) / 2 + DOWN * 0.38)
        with self.say("Výška rozdělí přeponu na dva úseky. Úsek u vrcholu á se jmenuje cé bé, "
                      "protože leží u odvěsny bé. Úsek u vrcholu bé se jmenuje cé á."):
            self.hl((A, C0), color=ORANGE, run_time=0.8)
            self.draw(cbl, run_time=0.5)
            self.hl((C0, B), color=TEAL, run_time=0.8)
            self.draw(cal, run_time=0.5)
        sq = VGroup(hfill(C0, C0 + RIGHT * V, C0 + RIGHT * V + UP * V, C, color=INK, opacity=0.15),
                    hpoly(C0, C0 + RIGHT * V, C0 + RIGHT * V + UP * V, C, color=INK, width=2.6))
        rect = VGroup(hfill(C0, B, B + DOWN * CB, C0 + DOWN * CB, color=TEAL, opacity=0.2),
                      hpoly(C0, B, B + DOWN * CB, C0 + DOWN * CB, color=TEAL, width=2.6))
        with self.say("Věta říká, že obsah čtverce nad výškou je stejný jako obsah obdélníku, jehož strany jsou "
                      "oba úseky přepony. Čtverec má obsah vé cé na druhou, obdélník cé bé krát cé á."):
            self.play(FadeOut(cbl), FadeOut(cal), run_time=0.3)
            self.draw(sq, run_time=1.2)
            self.draw(rect, run_time=1.2)
            s1 = Tx("v_{c}²", 34, INK).move_to(C0 + np.array([V / 2 + 0.1, V / 2 + 0.25, 0]))
            s2 = Tx("c_{b} · c_{a}", 30, TEAL).move_to(C0 + np.array([CA / 2, -CB / 2, 0]))
            self.draw(s1, s2, run_time=0.8)
            self.wait(1.0)

        # --- důkaz
        self.clear_body()
        A, B, C, C0 = tri_pts([-5.2, -1.6, 0], 1.0)
        f1 = hfill(A, C0, C, ORANGE, 0.22)
        f2 = hfill(C0, B, C, TEAL, 0.22)
        fig = VGroup(hpoly(A, B, C), hseg(C, C0, color=INK), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP),
                     Pt(C0, "C₀", DOWN, font_size=28), RightMark(C, A, B), RightMark(C0, B, C, r=0.3),
                     RightMark(C0, A, C, r=0.3))
        with self.say("Teď důkaz. Výška rozdělí trojúhelník na dva menší pravoúhlé trojúhelníky: "
                      "á cé cé nula a cé bé cé nula. Ukážeme, že jsou si podobné."):
            self.play(FadeIn(fig), run_time=0.8)
            self.play(FadeIn(f1), FadeIn(f2), run_time=0.8)
            self.board.write("[Dk.:  △ACC₀ ∼ △CBC₀  (uu):")
        with self.say("Oba mají pravý úhel u vrcholu cé nula."):
            self.board.write("|∢AC₀C| = |∢CC₀B| = 90°", indent=0.95)
        aA = AngleMark(A, B, C, 0.55, RED, label="α")
        aC1 = AngleMark(C, A, C0, 0.75, ORANGE, fill_opacity=0.1)
        aC2 = AngleMark(C, C0, B, 0.6, RED, label="α", label_r=0.85)
        with self.say("Označme alfa úhel při vrcholu á. V trojúhelníku á cé cé nula je součet úhlů sto osmdesát, "
                      "takže úhel u vrcholu cé je devadesát minus alfa. Celý úhel u cé je pravý, takže na úhel cé nula cé bé "
                      "zbude devadesát minus devadesát minus alfa, a to je zase alfa."):
            self.draw(aA, run_time=0.6)
            self.draw(aC1, run_time=0.8)
            self.board.write("|∢ACC₀| = 90° − α", indent=0.95)
            self.draw(aC2, run_time=0.8)
            self.board.write("⇒  |∢C₀CB| = 90° − (90° − α) = α", indent=0.95)
        with self.say("V sešitě je to napsané stručně: úhel cé nula cé bé je otočením úhlu cé nula á cé o devadesát stupňů, "
                      "jejich ramena jsou na sebe kolmá. Podívej: když menší trojúhelník otočíme o devadesát stupňů "
                      "kolem bodu cé nula a zvětšíme ho, přesně padne na ten druhý."):
            self.board.write("(∢C₀CB je otočením ∢C₀AC)", indent=0.95, color=GRAY, size=27)
            cp = VGroup(f1.copy().set_fill(opacity=0.4), hpoly(A, C0, C, color=ORANGE))
            self.play(Rotate(cp, -PI / 2, about_point=C0), run_time=1.8)
            self.play(cp.animate.scale(V / CB, about_point=C0), run_time=1.5)
            self.wait(0.5)
            self.play(FadeOut(cp), run_time=0.5)
        with self.say("U podobných trojúhelníků je poměr odpovídajících si stran stejný. Strana cé cé nula leží proti "
                      "úhlu alfa v prvním trojúhelníku a odpovídá jí strana bé cé nula, která leží proti úhlu alfa ve druhém. "
                      "Strana á cé nula odpovídá straně cé cé nula. Takže cé cé nula ku á cé nula se rovná bé cé nula ku cé cé nula."):
            self.board.write(Row("⇒", Frac("|CC₀|", "|AC₀|", 30), "=", Frac("|BC₀|", "|CC₀|", 30), size=30), )
        with self.say("A teď jen přepíšeme na obvyklé značení: vé cé ku cé bé se rovná cé á ku vé cé. "
                      "Vynásobíme obě strany a dostaneme vé cé na druhou se rovná cé bé krát cé á."):
            self.board.write(Row(Frac("v_{c}", "c_{b}", 30), "=", Frac("c_{a}", "v_{c}", 30), size=30))
            r = self.board.write("⇒   v_{c}² = c_{b} · c_{a}   ]")
            self.play(Create(hbox(r)), run_time=0.7)

        A, B, C, C0 = tri_pts([-4.6, -1.0, 0], 1.0)
        sfig = VGroup(hpoly(A, B, C), hseg(C, C0, color=INK), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UP),
                      Pt(C0, "C₀", DOWN, font_size=28), RightMark(C, A, B), RightMark(C0, B, C, r=0.3),
                      AngleMark(A, B, C, 0.55, RED, label="α"), AngleMark(C, C0, B, 0.6, RED, label="α", label_r=0.85),
                      Tx("v_{c}", 28, INK).move_to((C + C0) / 2 + LEFT * 0.35),
                      Tx("c_{b}", 28, ORANGE).move_to((A + C0) / 2 + DOWN * 0.35),
                      Tx("c_{a}", 28, TEAL).move_to((B + C0) / 2 + DOWN * 0.35))
        self.summary(sfig, [
            "[Dk.:  △ACC₀ ∼ △CBC₀ (uu), neboť ∢C₀CB je",
            "otočením ∢C₀AC  (oba pravé úhly u C₀)",
            Row(Frac("|CC₀|", "|AC₀|", 29), "=", Frac("|BC₀|", "|CC₀|", 29), size=29),
            Row(Frac("v_{c}", "c_{b}", 29), "=", Frac("c_{a}", "v_{c}", 29), "⇒   v_{c}² = c_{b} · c_{a}   ]", size=29)],
            "Shrnutí do písemky: trojúhelník á cé cé nula je podobný trojúhelníku cé bé cé nula podle věty u u, "
            "protože oba mají pravý úhel u cé nula a úhel cé nula cé bé je otočením úhlu cé nula á cé. "
            "Proto cé cé nula ku á cé nula se rovná bé cé nula ku cé cé nula, tedy vé cé ku cé bé se rovná cé á ku vé cé, "
            "a z toho vé cé na druhou se rovná cé bé krát cé á.",
            x_text=-0.4)
