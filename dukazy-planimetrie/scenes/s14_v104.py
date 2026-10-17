import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

S0 = np.array([-3.7, -0.75, 0])
R = 2.3


def P(deg):
    t = np.radians(deg)
    return S0 + R * np.array([np.cos(t), np.sin(t), 0])


def out(deg, k=0.32):
    t = np.radians(deg)
    return np.array([np.cos(t), np.sin(t), 0]) * k


class V104(ProofScene):
    CODE = "V 10.4"
    NAME = "Středový a obvodový úhel"
    INDEX = 14
    SEED = 104

    def base(self, pts, s_dir=DOWN + LEFT * 0.4):
        """Kružnice se středem S a body {jméno: úhel}."""
        g = VGroup(hcircle(S0, R, color=PEN), Pt(S0, "S", s_dir, font_size=28))
        for name, deg in pts.items():
            d = P(deg)
            dot = Dot(d, radius=0.055, color=PEN)
            lab = Text(name, font=FONT, font_size=30, color=PEN).move_to(d + out(deg))
            g.add(VGroup(dot, lab))
        return g

    def construct(self):
        self.intro(
            ["Nechť k(S; r) je kružnice. Pak středový úhel je dvojnásobkem libovolného",
             "obvodového úhlu příslušného k témuž oblouku kružnice:  ω = 2φ."],
            "Věta deset celá čtyři. Středový úhel je dvojnásobkem libovolného obvodového úhlu příslušného "
            "k témuž oblouku kružnice. Krátce: omega se rovná dvakrát fí.")

        # ---- pojmy
        A, B = P(215), P(325)
        k = hcircle(S0, R)
        pS = Pt(S0, "S", DOWN + LEFT * 0.4, font_size=28)
        pA, pB = Pt(A, "A", DL), Pt(B, "B", DR)
        arc = harc(S0, R + 0.0, np.radians(215), np.radians(325), color=RED, width=6)
        om = AngleMark(S0, A, B, 0.55, ORANGE, label="ω", label_r=0.85)
        cA, cB = hseg(S0, A, color=ORANGE), hseg(S0, B, color=ORANGE)
        with self.say("Nejdřív pojmy. Na kružnici ká se středem es máme oblouk á bé, tady červeně. "
                      "Středový úhel příslušný k tomuto oblouku má vrchol ve středu es a ramena es á a es bé. Značíme ho omega."):
            self.draw(k, run_time=1.5)
            self.draw(pS, pA, pB, run_time=0.6)
            self.draw(arc, run_time=0.8)
            self.draw(cA, cB, run_time=0.8)
            self.draw(om, run_time=0.6)
        th = ValueTracker(70)

        def ins():
            X = P(th.get_value())
            g = VGroup(Line(X, A, color=INK, stroke_width=3), Line(X, B, color=INK, stroke_width=3),
                       Dot(X, radius=0.055, color=PEN),
                       Text("X", font=FONT, font_size=30, color=PEN).move_to(X + out(th.get_value())))
            a1, a2 = sorted([np.arctan2((A - X)[1], (A - X)[0]), np.arctan2((B - X)[1], (B - X)[0])])
            g.add(Arc(radius=0.5, start_angle=a1, angle=a2 - a1, arc_center=X, color=RED, stroke_width=3))
            mid = (a1 + a2) / 2
            ang = np.degrees(a2 - a1)
            g.add(Text(f"φ = {round(ang)}°", font=FONT, font_size=26, color=RED)
                  .move_to(X + 0.95 * np.array([np.cos(mid), np.sin(mid), 0])))
            return g

        insm = always_redraw(ins)
        omv = Text(f"ω = {round(325 - 215)}°", font=FONT, font_size=30, color=ORANGE).move_to([-1.0, -3.3, 0])
        with self.say("Obvodový úhel má vrchol iks přímo na kružnici, mimo oblouk á bé, a ramena prochází body á a bé. "
                      "Zkusme bodem iks pohybovat po kružnici. Obvodový úhel se vůbec nemění, a je přesně polovinou "
                      "středového úhlu. Středový úhel má tady sto deset stupňů a obvodový pětapadesát."):
            self.add(insm)
            self.draw(omv, run_time=0.6)
            self.play(th.animate.set_value(150), run_time=3.5)
            self.play(th.animate.set_value(20), run_time=4.0)
            self.play(th.animate.set_value(90), run_time=2.5)
        with self.say("Důkaz rozdělíme na čtyři případy podle toho, kde leží střed es vzhledem k obvodovému úhlu: "
                      "á, es leží na rameni, bé, es leží uvnitř úhlu, cé, es leží vně úhlu, a dé, es leží na úsečce á bé."):
            self.wait(self.left())
        self.remove(insm)
        self.clear_body()
        self.board.size = 29

        # ---- a) S na rameni
        X, A, B = P(115), P(295), P(205)
        g = self.base({"X": 115, "A": 295, "B": 205}, s_dir=RIGHT)
        XA, XB, SB = hseg(X, A, color=INK), hseg(X, B, color=INK), hseg(S0, B, color=ORANGE)
        with self.say("Případ á. Střed es leží na rameni obvodového úhlu, tedy na úsečce iks á."):
            self.play(FadeIn(g), run_time=0.8)
            self.draw(XA, XB, run_time=1.0)
            self.board.write("a)  S leží na rameni obvodového úhlu:")
        f = hfill(S0, X, B, TEAL, 0.2)
        tk = VGroup(ticks(S0, X, 1), ticks(S0, B, 1))
        phiX = AngleMark(X, A, B, 0.6, RED, label="φ", label_r=0.9)
        phiB = AngleMark(B, S0, X, 0.6, RED, label="φ", label_r=0.9)
        with self.say("Spojíme es s bodem bé. Trojúhelník es iks bé je rovnoramenný, protože es iks i es bé jsou poloměry. "
                      "Jeho základna je bé iks, takže úhly při základně jsou shodné: úhel es bé iks je také fí."):
            self.draw(SB, run_time=0.6)
            self.play(FadeIn(f), run_time=0.5)
            self.draw(tk, run_time=0.5)
            self.draw(phiX, run_time=0.6)
            self.board.write("△SXB – rovnoramenný se základnou BX", indent=0.45)
            self.board.write("(|SX| = |SB| = r)", indent=0.95)
            self.board.write("⇒  |∢SBX| = |∢SXB| = φ", indent=0.95)
            self.draw(phiB, run_time=0.6)
        omg = AngleMark(S0, A, B, 0.5, ORANGE, label="ω", label_r=0.78)
        with self.say("Středový úhel omega, tedy úhel á es bé, je vnější úhel trojúhelníku es iks bé při vrcholu es. "
                      "Podle věty o vnějším úhlu je roven součtu dvou vnitřních úhlů u zbývajících vrcholů. "
                      "Takže omega se rovná fí plus fí, tedy dvakrát fí."):
            self.draw(omg, run_time=0.8)
            self.board.write("ω … vnější úhel △SXB", indent=0.45)
            self.board.write("⇒  ω = φ + φ = 2φ", indent=0.95)
            self.blink(phiX, phiB, omg, run_time=1.0)
        self.clear_body()
        self.board.size = 29

        # ---- b) S uvnitř
        X, A, B, C = P(100), P(222), P(322), P(280)
        g = self.base({"X": 100, "A": 222, "B": 322, "C": 280})
        with self.say("Případ bé. Střed es leží uvnitř obvodového úhlu. Vedeme přímku iks es a její druhý průsečík "
                      "s kružnicí označíme cé. Tím rozdělíme oba úhly na dvě části."):
            self.play(FadeIn(g), run_time=0.8)
            self.draw(hseg(X, A, color=INK), hseg(X, B, color=INK), run_time=0.9)
            self.draw(hseg(X, C, color=PURPLE, width=3.0), run_time=0.8)
            self.board.write("b)  S leží uvnitř obvodového úhlu:")
            self.board.write("C ∈ ^{XS} ∩ k", indent=0.45)
        m = VGroup(AngleMark(X, A, C, 0.75, RED, label="φ₁", label_r=1.05, font_size=26),
                   AngleMark(X, C, B, 0.55, GREEN, label="φ₂", label_r=0.82, font_size=26),
                   hseg(S0, A, color=ORANGE), hseg(S0, B, color=ORANGE),
                   AngleMark(S0, A, C, 0.45, RED, label="ω₁", label_r=0.75, font_size=26),
                   AngleMark(S0, C, B, 0.45, GREEN, label="ω₂", label_r=0.75, font_size=26))
        with self.say("Obvodový úhel fí se rozdělí na fí jedna a fí dva, středový úhel omega na omega jedna a omega dva. "
                      "Pro každou dvojici už střed leží na rameni, takže podle případu á platí omega jedna je dvakrát fí jedna "
                      "a omega dva je dvakrát fí dva."):
            self.draw(m[0], m[1], run_time=0.9)
            self.draw(m[2], m[3], run_time=0.6)
            self.draw(m[4], m[5], run_time=0.9)
            self.board.write("ω₁ = 2φ₁,   ω₂ = 2φ₂   (podle a)", indent=0.45)
        with self.say("A protože omega je omega jedna plus omega dva a fí je fí jedna plus fí dva, sečteme: "
                      "omega jedna plus omega dva se rovná dvakrát fí jedna plus fí dva, tedy omega se rovná dvakrát fí."):
            self.board.write("ω = ω₁ + ω₂,   φ = φ₁ + φ₂", indent=0.45)
            self.board.write("ω₁ + ω₂ = 2(φ₁ + φ₂)  ⇒  ω = 2φ", indent=0.45)
        self.clear_body()
        self.board.size = 29

        # ---- c) S vně
        X, A, B, C = P(200), P(260), P(320), P(20)
        g = self.base({"X": 200, "A": 260, "B": 320, "C": 20}, s_dir=UP)
        with self.say("Případ cé. Střed es leží vně obvodového úhlu. Zase vedeme přímku iks es a druhý průsečík je cé."):
            self.play(FadeIn(g), run_time=0.8)
            self.draw(hseg(X, A, color=INK), hseg(X, B, color=INK), run_time=0.9)
            self.draw(hseg(X, C, color=PURPLE, width=3.0), run_time=0.8)
            self.board.write("c)  S leží vně obvodového úhlu:")
            self.board.write("C ∈ ^{XS} ∩ k", indent=0.45)
        m = VGroup(AngleMark(X, C, A, 1.1, RED, label="φ₁", label_r=1.4, font_size=26, fill_opacity=0.12, label_t=0.75),
                   AngleMark(X, C, B, 0.7, GREEN, label="φ₂", label_r=0.95, font_size=26, fill_opacity=0.25),
                   hseg(S0, A, color=ORANGE), hseg(S0, B, color=ORANGE),
                   AngleMark(S0, C, A, 0.42, RED, label="ω₁", label_r=0.72, font_size=26, fill_opacity=0.12, label_t=0.3),
                   AngleMark(S0, C, B, 0.62, GREEN, label="ω₂", label_r=0.92, font_size=26, fill_opacity=0.25))
        with self.say("Teď je to rozdíl místo součtu. Fí jedna je velký úhel cé iks á, fí dva je menší úhel cé iks bé "
                      "a náš obvodový úhel fí je jejich rozdíl. Stejně tak omega jedna je úhel cé es á, omega dva je cé es bé "
                      "a omega je rozdíl omega jedna minus omega dva."):
            self.draw(m[0], m[1], run_time=1.0)
            self.draw(m[2], m[3], run_time=0.6)
            self.draw(m[4], m[5], run_time=1.0)
            self.board.write("ω₁ = 2φ₁,   ω₂ = 2φ₂   (podle a)", indent=0.45)
            self.board.write("ω = ω₁ − ω₂,   φ = φ₁ − φ₂", indent=0.45)
        with self.say("Podle případu á zase platí omega jedna je dvakrát fí jedna a omega dva je dvakrát fí dva. "
                      "Odečteme a dostaneme omega se rovná dvakrát fí."):
            self.board.write("ω₁ − ω₂ = 2(φ₁ − φ₂)  ⇒  ω = 2φ", indent=0.45)
        self.clear_body()
        self.board.size = 29

        # ---- d) S na AB
        X, A, B = P(115), P(205), P(25)
        g = self.base({"X": 115, "A": 205, "B": 25}, s_dir=DOWN + RIGHT * 0.3)
        with self.say("Poslední případ dé. Střed es leží na úsečce á bé, takže á bé je průměr a středový úhel je přímý, "
                      "má sto osmdesát stupňů."):
            self.play(FadeIn(g), run_time=0.8)
            self.draw(hseg(X, A, color=INK), hseg(X, B, color=INK), hseg(A, B, color=ORANGE), run_time=1.2)
            self.draw(hseg(X, S0, color=PURPLE, width=3.0), run_time=0.6)
            self.board.write("d)  S leží na AB:")
        m = VGroup(AngleMark(X, A, S0, 0.65, RED, label="φ₁", label_r=0.95, font_size=26),
                   AngleMark(X, S0, B, 0.65, GREEN, label="φ₂", label_r=0.95, font_size=26),
                   AngleMark(A, S0, X, 0.6, RED, label="φ₁", label_r=0.9, font_size=26),
                   AngleMark(B, X, S0, 0.6, GREEN, label="φ₂", label_r=0.9, font_size=26),
                   AngleMark(S0, A, P(24.8), 0.4, ORANGE, label="ω", label_r=0.62, font_size=26, fill_opacity=0.12))
        with self.say("Spojíme iks se středem es. Trojúhelník á iks es je rovnoramenný se základnou á iks, "
                      "takže úhel iks á es je stejný jako úhel á iks es, označme ho fí jedna. Analogicky v trojúhelníku "
                      "bé iks es je úhel iks bé es roven fí dva."):
            self.draw(m[0], m[2], run_time=0.9)
            self.board.write("△AXS – rovnoramenný se základnou AX", indent=0.45)
            self.board.write("⇒  |∢XAS| = φ₁", indent=0.95)
            self.draw(m[1], m[3], run_time=0.9)
            self.board.write("analogicky  |∢XBS| = φ₂", indent=0.45)
        with self.say("V trojúhelníku á bé iks je součet úhlů sto osmdesát stupňů: dvakrát fí jedna plus dvakrát fí dva. "
                      "Takže fí jedna plus fí dva, což je náš obvodový úhel fí, je devadesát stupňů, a to je polovina "
                      "středového úhlu omega."):
            self.draw(m[4], run_time=0.6)
            self.board.write("△ABX:  2(φ₁ + φ₂) = 180°", indent=0.45)
            self.board.write("φ₁ + φ₂ = 90° = φ = ω/2   ]", indent=0.45)

        # ---- shrnutí (ve dvou částech)
        X, A, B = P(115), P(295), P(205)
        fa = VGroup(self.base({"X": 115, "A": 295, "B": 205}, s_dir=RIGHT), hseg(X, A, color=INK), hseg(X, B, color=INK),
                    hseg(S0, B, color=ORANGE), AngleMark(X, A, B, 0.6, RED, label="φ", label_r=0.9),
                    AngleMark(B, S0, X, 0.6, RED, label="φ", label_r=0.9),
                    AngleMark(S0, A, B, 0.5, ORANGE, label="ω", label_r=0.78))
        self.summary(fa, [
            "[Dk.:  a)  S leží na rameni obvodového úhlu:",
            "△SXB – rovnoramenný se základnou BX",
            "⇒  |∢SBX| = |∢SXB| = φ",
            "ω … vnější úhel △SXB  ⇒  ω = φ + φ = 2φ",
            "b)  S leží uvnitř obvodového úhlu:  C ∈ ^{XS} ∩ k",
            "ω₁ = 2φ₁,   ω₂ = 2φ₂   (podle a)",
            "ω = ω₁ + ω₂,   φ = φ₁ + φ₂",
            "⇒  ω₁ + ω₂ = 2(φ₁ + φ₂)  ⇒  ω = 2φ"],
            "Shrnutí do písemky, první polovina. Případ á: trojúhelník es iks bé je rovnoramenný se základnou bé iks, "
            "takže úhel es bé iks je fí, a omega je vnější úhel, tedy fí plus fí, dvakrát fí. Případ bé: cé je druhý "
            "průsečík přímky iks es s kružnicí. Podle případu á je omega jedna dvakrát fí jedna a omega dva dvakrát fí dva, "
            "a když to sečteme, omega je dvakrát fí.",
            size=27, dy=0.58, fig_w=4.8, fig_h=4.8, x_text=-1.2, final=None, outro=False)
        X, A, B = P(115), P(205), P(25)
        fd = VGroup(self.base({"X": 115, "A": 205, "B": 25}, s_dir=DOWN + RIGHT * 0.3), hseg(X, A, color=INK),
                    hseg(X, B, color=INK), hseg(A, B, color=ORANGE), hseg(X, S0, color=PURPLE),
                    AngleMark(X, A, S0, 0.65, RED, label="φ₁", label_r=0.95, font_size=26),
                    AngleMark(X, S0, B, 0.65, GREEN, label="φ₂", label_r=0.95, font_size=26),
                    AngleMark(A, S0, X, 0.6, RED, label="φ₁", label_r=0.9, font_size=26),
                    AngleMark(B, X, S0, 0.6, GREEN, label="φ₂", label_r=0.9, font_size=26))
        self.summary(fd, [
            "c)  S leží vně obvodového úhlu:  C ∈ ^{XS} ∩ k",
            "ω₁ = 2φ₁,   ω₂ = 2φ₂   (podle a)",
            "ω = ω₁ − ω₂,   φ = φ₁ − φ₂",
            "⇒  ω₁ − ω₂ = 2(φ₁ − φ₂)  ⇒  ω = 2φ",
            "d)  S leží na AB:",
            "△AXS – rovnoramenný se základnou AX",
            "⇒  |∢XAS| = φ₁,   analogicky  |∢XBS| = φ₂",
            "△ABX:  2(φ₁ + φ₂) = 180°",
            "⇒  φ₁ + φ₂ = 90° = φ = ω/2   ]"],
            "Druhá polovina. Případ cé je stejný jako bé, jen odečítáme: omega je omega jedna minus omega dva "
            "a fí je fí jedna minus fí dva. Případ dé: trojúhelníky á iks es a bé iks es jsou rovnoramenné, "
            "v trojúhelníku á bé iks je dvakrát fí jedna plus dvakrát fí dva sto osmdesát stupňů, "
            "takže fí je devadesát stupňů, tedy polovina omegy.",
            size=26, dy=0.53, fig_w=4.8, fig_h=4.8, x_text=-1.2)
