import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

SH = np.array([0.02, 0.15, 0])
A = np.array([-2.88, -2.5, 0]) + SH
S1, R1 = np.array([-4.61, -0.12, 0]) + SH, 0.77
S2, R2 = np.array([-1.92, -0.53, 0]) + SH, 1.26
ROT = -PI / 3
S1p = rotate_about(S1, A, ROT)                 # R(A; −60°)(S1)
S1pp = rotate_about(S1, A, -ROT)               # R(A; +60°)(S1)
CS = circle_intersections(S1p, R1, S2, R2)
BS = [rotate_about(C, A, -ROT) for C in CS]


class I3(ProofScene):
    CODE = "I3"
    NAME = "Rovnostranný trojúhelník s vrcholy na kružnicích (otočení)"
    INDEX = 8
    SEED = 803

    def base(self):
        return VGroup(hcircle(S1, R1, color=INK, width=3), hcircle(S2, R2, color=GREEN, width=3),
                      Tx("k₁", 30, INK).move_to(S1 + R1 * np.array([-1.25, 0.55, 0])),
                      Tx("k₂", 30, GREEN).move_to(S2 + R2 * np.array([0.95, 0.85, 0])),
                      Pt(A, "A", DOWN, color=RED))

    def construct(self):
        self.intro(
            ["Jsou dány kružnice k₁, k₂ a bod A.",
             "Sestrojte rovnostranný trojúhelník ABC tak, aby B ∈ k₁ a C ∈ k₂."],
            "Úloha í tři. Jsou dány dvě kružnice ká jedna, ká dva a bod á. Máme sestrojit rovnostranný trojúhelník á bé cé "
            "tak, aby vrchol bé ležel na ká jedna a vrchol cé na ká dva.")
        g = self.base()
        with self.say("Nakreslíme obě kružnice a bod á."):
            self.draw(g[0], g[1], run_time=1.4)
            self.draw(g[2], g[3], g[4], run_time=0.5)
        with self.say("Zase stejný problém jako minule: dvě neznámé naráz. O bodu bé víme jen, že leží na ká jedna, o bodu cé jen, "
                      "že leží na ká dva. Zkusme naivní postup: vezmu nějaký bod bé na ká jedna a doplním rovnostranný trojúhelník."):
            self.board.write("B ∈ k₁,  C ∈ k₂  …  dvě neznámé naráz", color=GRAY)
        t = ValueTracker(40)

        def tri():
            Bp = on_circle(S1, R1, t.get_value())
            Cp = rotate_about(Bp, A, ROT)
            onk2 = abs(np.linalg.norm(Cp - S2) - R2) < 0.05
            col = RED if onk2 else ORANGE
            return VGroup(Polygon(A, Bp, Cp, color=col, stroke_width=3, fill_color=col, fill_opacity=0.15),
                          Dot(Bp, radius=0.065, color=INK), Dot(Cp, radius=0.065, color=col),
                          Text("B", font=FONT, font_size=28, color=INK).next_to(Bp, normalize(Bp - S1), buff=0.08),
                          Text("C", font=FONT, font_size=28, color=col).next_to(Cp, UP, buff=0.08))

        lv = always_redraw(tri)
        with self.say("Pro tenhle bod bé vrchol cé na kružnici ká dva neleží. Ani pro tenhle. Musel bych zkoušet donekonečna. "
                      "Potřebujeme chytřejší nápad."):
            self.add(lv)
            self.play(t.animate.set_value(100), run_time=2.5)
            self.play(t.animate.set_value(170), run_time=2.0)
        self.remove(lv)
        self.add(tri())
        self.think("V rovnostranném trojúhelníku: jak se dostaneš z bodu B do bodu C, když stojíš v A?",
                   "Zkus si rozmyslet: jak se v rovnostranném trojúhelníku dostaneš z bodu bé do bodu cé, když se díváš z bodu á?")
        with self.say("V rovnostranném trojúhelníku je á bé stejně dlouhé jako á cé a úhel u á má šedesát stupňů. Bod cé tedy "
                      "dostanu tak, že bod bé otočím kolem á o šedesát stupňů. Otočení zachová vzdálenost od á a pootočí o přesně "
                      "šedesát stupňů. Tady po směru hodinových ručiček, proto minus šedesát."):
            self.board.write("rovnostranný:  |AB| = |AC|,  |∢BAC| = 60°")
            r = self.board.write("⇒  C = R_{A; −60°}(B)", indent=0.45, color=RED)
        self.think("B běhá po celé kružnici k₁. Po čem pak běhá jeho otočený obraz C?",
                   "A teď: bod bé běhá po celé kružnici ká jedna. Po čem pak běhá jeho otočený obraz cé?", pause=5)

        self.clear_body()
        self.play(FadeIn(self.base()), run_time=0.4)
        dummy = Dot(rotate_about(on_circle(S1, R1, t.get_value()), A, ROT), radius=0.001)
        dummy.add_updater(lambda m: m.move_to(rotate_about(on_circle(S1, R1, t.get_value()), A, ROT)))
        trace = TracedPath(dummy.get_center, stroke_color=ORANGE, stroke_width=4)
        lv = always_redraw(tri)
        with self.say("Sleduj, kudy jde vrchol cé, když bé objede celou kružnici ká jedna. Cé opisuje také kružnici, oranžovou. "
                      "Je to obraz kružnice ká jedna v otočení kolem á o minus šedesát stupňů. Označíme ji ká jedna s čárkou."):
            self.add(dummy, trace, lv)
            self.play(t.animate.set_value(170 + 360), run_time=7, rate_func=linear)
        self.remove(lv)
        dummy.clear_updaters()
        k1p = hcircle(S1p, R1, color=ORANGE, width=3)
        with self.say("Kružnici neotáčíme bod po bodu. Stačí otočit její střed es jedna kolem á o šedesát stupňů, "
                      "kružítkem se středem á a úhloměrem, a poloměr opsat stejný."):
            self.add(k1p)
            self.remove(trace)
            self.draw(hseg(A, S1, color=GRAY, width=2.2), Pt(S1, "S₁", DOWN, font_size=26), run_time=0.6)
            self.draw(harc(A, np.linalg.norm(S1 - A), direction(A, S1), direction(A, S1) + ROT, color=GRAY, width=2.2),
                      run_time=0.8)
            self.draw(hseg(A, S1p, color=GRAY, width=2.2), Pt(S1p, "S₁′", DOWN + RIGHT * 0.3, font_size=26, color=ORANGE),
                      AngleMark(A, S1, S1p, 0.6, ORANGE, label="60°", label_r=0.9, font_size=22), run_time=0.8)
            self.draw(Tx("k₁′", 30, ORANGE).move_to(S1p + R1 * np.array([0.0, 1.3, 0])), run_time=0.3)
            self.board.write("B ∈ k₁  ⇒  C ∈ k₁′ = R_{A; −60°}(k₁)")
            self.board.write("k₁′(S₁′; r₁),   S₁′ = R_{A; −60°}(S₁)", indent=0.45)
        with self.say("A teď ta hlavní myšlenka. Cé musí ležet na ká jedna s čárkou, protože je to otočený bod z ká jedna. "
                      "A zároveň má podle zadání ležet na ká dva. Leží tedy v průsečíku ká jedna s čárkou a ká dva. "
                      "Ze dvou neznámých zbyla jedna a je určená průsečíkem."):
            self.play(Indicate(k1p, color=RED, scale_factor=1.03), run_time=1.0)
            self.board.write("zároveň  C ∈ k₂  ⇒  C ∈ k₁′ ∩ k₂", color=RED)
            self.draw(Pt(CS[0], "C₁", RIGHT, color=RED), Pt(CS[1], "C₂", UL, color=RED), run_time=0.6)
        tris = VGroup()
        with self.say("Bod bé pak dostaneme zpátky, otočením cé o plus šedesát stupňů. Máme dva průsečíky, a tedy dva trojúhelníky."):
            for C, Bp, col in zip(CS, BS, (RED, PURPLE)):
                tris.add(VGroup(hfill(A, Bp, C, col, 0.18), hpoly(A, Bp, C, color=col)))
                self.play(Create(tris[-1][1]), FadeIn(tris[-1][0]), run_time=1.0)
            self.draw(Pt(BS[0], "B₁", LEFT, color=RED), Pt(BS[1], "B₂", LEFT, color=PURPLE), run_time=0.5)
            self.board.write("B = R_{A; +60°}(C)", indent=0.45)
        self.think("Proč je sestrojený trojúhelník opravdu rovnostranný a B leží na k₁?",
                   "Zkus si sám zdůvodnit, proč je sestrojený trojúhelník opravdu rovnostranný a proč bé leží na ká jedna.", pause=5)
        with self.say("Cé leží na ká dva přímo z konstrukce. Cé leží na ká jedna s čárkou, takže když ho otočíme zpátky, "
                      "bé leží na ká jedna. Otočení je shodné zobrazení, takže á bé se rovná á cé, a úhel bé á cé má šedesát "
                      "stupňů. Rovnoramenný trojúhelník s úhlem šedesát stupňů u hlavního vrcholu je rovnostranný."):
            self.board.write("C ∈ k₂ ✓;  C ∈ k₁′ ⇒ B ∈ k₁ ✓", indent=0.0)
            self.board.write("|AB| = |AC|, 60° ⇒ rovnostranný (V 6.7) ✓", indent=0.0)

        # ---- druhý smysl
        k1pp = hcircle(S1pp, R1, color=TEAL, width=3)
        with self.say("A teď past, na které se nejčastěji ztrácejí body: druhý smysl otočení. Trojúhelník může být orientovaný "
                      "i obráceně, takže stejnou úvahu musíme udělat i s otočením o plus šedesát stupňů. Dostaneme další kružnici, "
                      "ká jedna se dvěma čárkami."):
            self.draw(hseg(A, S1pp, color=GRAY, width=2.2), Pt(S1pp, "S₁″", DOWN, font_size=26, color=TEAL), run_time=0.6)
            self.draw(k1pp, Tx("k₁″", 30, TEAL).move_to(S1pp + R1 * np.array([0.0, -1.35, 0])), run_time=1.0)
            self.board.write("+ druhý smysl:  R_{A; +60°}(k₁) = k₁″", color=TEAL)
        with self.say("Tady ká jedna se dvěma čárkami kružnici ká dva neprotíná, takže v tomhle obrázku další řešení nepřibudou. "
                      "Při jiné poloze kružnic by ale mohla přidat až dvě další řešení."):
            self.board.write("k₁″ ∩ k₂ = ∅  ⇒  zde nic navíc", indent=0.45, color=TEAL)

        # ---- diskuse
        with self.say("Diskuse tedy: pro každý smysl otočení počítáme společné body otočené kružnice s ká dva. Dva společné body, "
                      "dvě řešení. Dotyk, jedno řešení. Žádný společný bod, žádné řešení. Dohromady za oba smysly nejvýš čtyři řešení. "
                      "Tady jsou dvě."):
            self.board.write("Diskuse: |k₁′ ∩ k₂| + |k₁″ ∩ k₂| řešení  (0 až 4)", gap=0.1)

        fig = VGroup(self.base(), hcircle(S1p, R1, color=ORANGE, width=2.6), hcircle(S1pp, R1, color=TEAL, width=2.2),
                     Pt(S1, "S₁", DOWN, font_size=24), Pt(S1p, "S₁′", DOWN + RIGHT * 0.3, font_size=24, color=ORANGE),
                     hseg(A, S1, color=GRAY, width=1.8), hseg(A, S1p, color=GRAY, width=1.8),
                     AngleMark(A, S1, S1p, 0.6, ORANGE, label="60°", label_r=0.9, font_size=20),
                     *[VGroup(hfill(A, Bp, C, col, 0.18), hpoly(A, Bp, C, color=col)) for C, Bp, col in zip(CS, BS, (RED, PURPLE))])
        self.summary(fig, [
            "Rozbor: |AB| = |AC|, |∢BAC| = 60°  ⇒  C = R_{A; −60°}(B)",
            "B ∈ k₁ ⇒ C ∈ k₁′ = R_{A; −60°}(k₁);  zároveň C ∈ k₂",
            "1.  S₁′;  S₁′ = R_{A; −60°}(S₁)",
            "2.  k₁′;  k₁′(S₁′; r₁)",
            "3.  C;  C ∈ k₁′ ∩ k₂",
            "4.  B;  B = R_{A; +60°}(C)",
            "5.  △ABC      (totéž pro R_{A; +60°} → k₁″)",
            "Diskuse: každý smysl 0 / 1 / 2 řešení, celkem až 4"],
            "Shrnutí. Rozbor: v rovnostranném trojúhelníku je cé obraz bé v otočení kolem á o šedesát stupňů, takže cé leží "
            "na otočené kružnici ká jedna s čárkou a zároveň na ká dva. Postup: otoč střed es jedna, narýsuj ká jedna s čárkou, "
            "průsečík s ká dva je cé, a bé dostaneš otočením zpět. Nezapomeň na druhý smysl otočení. Diskuse: až čtyři řešení.",
            size=26, dy=0.58, fig_w=4.6, x_text=-1.9,
            final="Zastav si video a zkus si konstrukci narýsovat sám.")
