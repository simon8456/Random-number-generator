from b5geo import *


def live_figure(rot, gap, ratio):
    g = geo(rot=rot.get_value(), gap=gap.get_value(), a=2.4, b=2.4 * ratio.get_value())
    grp = VGroup(Polygon(g["A"], g["B"], g["C"], g["D"], color=C_PAR, stroke_width=3.2),
                 Line(g["A"], g["C"], color=GRAY, stroke_width=2), Line(g["B"], g["D"], color=GRAY, stroke_width=2),
                 Circle(radius=g["RW"], arc_center=g["W"], color=C_W, stroke_width=2).set_stroke(opacity=0.35),
                 Circle(radius=g["R1"], arc_center=g["K1"], color=C_K1, stroke_width=3),
                 Circle(radius=g["R2"], arc_center=g["K2"], color=C_K2, stroke_width=3))
    u = normalize(g["D"] - g["B"])
    grp.add(Line(g["B"] - u * 1.0, g["D"] + u * 1.0, color=C_T, stroke_width=4))
    for n in "ABCDSM":
        col = RED if n == "M" else (PEN if n == "S" else C_PAR)
        grp.add(Dot(g[n], radius=0.055, color=col))
        d = {"A": LEFT, "B": DR, "C": RIGHT, "D": UL, "S": RIGHT, "M": UL}[n]
        grp.add(Text(n, font=FONT, font_size=28, color=col).next_to(g[n], d, buff=0.08))
    return grp


class B5e(B5Scene):
    INDEX = 5
    SEED = 505

    def full_fig(self, with_w=True):
        g = G
        f = VGroup(hpoly(g["A"], g["B"], g["C"], g["D"], color=C_PAR, width=3.2),
                   seg("A", "C", GRAY, width=2.2), seg("B", "D", GRAY, width=2.2))
        if with_w:
            f.add(circle_w(width=2.4).set_stroke(opacity=0.35), tag_w())
        f.add(circle_k1(), tag_k1(), circle_k2(), tag_k2(), hline(g["B"], g["D"], ext=0.9, color=C_T, width=4),
              *[pt(n) for n in "ABCDSM"])
        return f

    def construct(self):
        self.quick_header(self.HEADER)
        self.show_roadmap(None, (0, 1, 2, 3),
                          "Celý důkaz ještě jednou, každý krok jednou větou. Jedna: přímka es bé je tečna, když es bé na druhou "
                          "se rovná mocnosti bodu es. Dva: z kružnice omega dostaneme es em krát es cé rovno es bé krát es dé. "
                          "Tři: úhlopříčky rovnoběžníku se půlí, takže es em krát es á je es bé na druhou. "
                          "Čtyři: obě kružnice ká jedna i ká dva procházejí body á a em, takže es em krát es á je mocnost "
                          "bodu es k oběma, a proto je bé dé tečnou obou.")

        # --- obecnost
        rot, gap, ratio = ValueTracker(25), ValueTracker(95), ValueTracker(0.45)
        lv = always_redraw(lambda: live_figure(rot, gap, ratio))
        note = VGroup(Tx("Mění se tvar rovnoběžníku …", 32, INK), Tx("… a BD je pořád tečnou k₁ i k₂.", 32, C_T)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([3.3, 0.6, 0])
        with self.say("Platí to opravdu vždycky, nebo jen na našem obrázku? Podívej se: měním tvar rovnoběžníku, jeho úhly i délky "
                      "úhlopříček. Bod em, kružnice omega, ká jedna i ká dva se pokaždé přepočítají. A červená přímka bé dé se "
                      "obou kružnic pořád jen dotýká."):
            self.add(lv)
            self.play(Write(note[0]), run_time=1.0)
            self.play(gap.animate.set_value(75), run_time=3)
            self.play(ratio.animate.set_value(0.55), rot.animate.set_value(20), gap.animate.set_value(88), run_time=3)
            self.play(Write(note[1]), run_time=1.0)
            self.play(gap.animate.set_value(112), ratio.animate.set_value(0.5), rot.animate.set_value(15), run_time=3)
            self.play(gap.animate.set_value(95), ratio.animate.set_value(0.45), rot.animate.set_value(25), run_time=2.5)
        self.remove(lv)
        self.play(FadeOut(note), run_time=0.4)
        self.clear_body()

        # --- kontrolní otázky
        fig = self.full_fig()
        lg = legend()
        self.play(FadeIn(fig), FadeIn(lg), run_time=0.8)
        with self.say("A teď si ověříme, že tomu opravdu rozumíš. Dám ti pět kontrolních otázek. U každé si video zastav "
                      "a odpověz nahlas nebo na papír, a teprve pak poslouchej odpověď."):
            self.board.write("Kontrolní otázky", color=RED, size=34)
        g = G
        qa = [
            ("1) Proč stačí dokázat |SB|² = m_{S}(k₁)?",
             "Otázka jedna: proč stačí dokázat, že es bé na druhou se rovná mocnosti bodu es ke ká jedna?",
             "Protože kdyby přímka es bé protínala ká jedna ještě v bodě bé s čárkou, byla by mocnost es bé krát es bé s čárkou, "
             "a z rovnosti by vyšlo, že es bé s čárkou je es bé. Body by splynuly, takže druhý průsečík není a přímka je tečna.",
             "|SB| · |SB′| = |SB|² ⇒ B′ = B", None),
            ("2) Kde v důkazu použiješ, že BCDM je tětivový?",
             "Otázka dvě: kde v důkazu použiješ, že čtyřúhelník bé cé dé em je tětivový?",
             "Díky tomu leží body bé, cé, dé, em na jedné kružnici omega. Bod es je průsečík jejích dvou tětiv em cé a bé dé, "
             "a z mocnosti bodu dostaneme es em krát es cé rovno es bé krát es dé.",
             "ω:  |SM| · |SC| = |SB| · |SD|", "w"),
            ("3) Kde použiješ, že ABCD je rovnoběžník?",
             "Otázka tři: kde použiješ, že á bé cé dé je rovnoběžník?",
             "Úhlopříčky rovnoběžníku se půlí. Proto es cé se rovná es á a es dé se rovná es bé, a ze vzorce z omegy se stane "
             "es em krát es á rovno es bé na druhou.",
             "|SC| = |SA|,  |SD| = |SB|", "par"),
            ("4) Proč má S ke k₁ i ke k₂ stejnou mocnost?",
             "Otázka čtyři: proč má bod es ke kružnici ká jedna i ke ká dva stejnou mocnost?",
             "Protože obě kružnice procházejí body á a em, a ty leží na přímce, která prochází bodem es. Pro obě kružnice je to tedy "
             "stejná sečna se stejnými průsečíky, a tak i stejný součin es em krát es á.",
             "m_{S}(k₁) = |SM| · |SA| = m_{S}(k₂)", "am"),
            ("5) Proč jsou SB a SD jedna přímka?",
             "Otázka pět: proč je přímka es bé a přímka es dé jedna a táž přímka?",
             "Protože es je průsečík úhlopříček, leží na úhlopříčce bé dé. Body bé, es a dé jsou tedy na jedné přímce, "
             "a to je bé dé.",
             "S ∈ BD  ⇒  SB = SD = BD", "bd"),
        ]
        for q, nq, ans, short, hl in qa:
            self.think(q, nq, pause=7)
            with self.say(ans):
                if hl == "w":
                    self.play(Indicate(fig[3], color=C_W, scale_factor=1.03), run_time=1.0)
                    self.hl((g["M"], g["C"]), (g["B"], g["D"]), color=C_W, run_time=1.4)
                elif hl == "par":
                    tk = VGroup(ticks(g["S"], g["A"], 1), ticks(g["S"], g["C"], 1), ticks(g["S"], g["B"], 2),
                                ticks(g["S"], g["D"], 2))
                    self.play(Create(tk), run_time=0.6)
                    self.play(Indicate(tk, scale_factor=1.3), run_time=1.0)
                    self.play(FadeOut(tk), run_time=0.4)
                elif hl == "am":
                    self.play(Flash(g["A"], color=RED, line_length=0.22), Flash(g["M"], color=RED, line_length=0.22),
                              Indicate(fig[5], color=C_K1, scale_factor=1.03), Indicate(fig[7], color=C_K2, scale_factor=1.03),
                              run_time=1.2)
                    self.hl((g["S"], g["A"]), color=RED, run_time=1.2)
                elif hl == "bd":
                    self.play(Indicate(fig[9], color=C_T, scale_factor=1.02), run_time=1.0)
                else:
                    self.wait(0.5)
                self.board.write(short, size=27, indent=0.45, color=GREEN)
        self.wait(0.5)

        # --- zápis
        sfig = self.full_fig(with_w=True)
        self.summary(sfig, [
            "[Dk.:  S = AC ∩ BD,  k₁ … opsaná △AMB,  k₂ … opsaná △AMD",
            "úhlopříčky rovnoběžníku se půlí:  |SA| = |SC|,  |SB| = |SD|",
            "mocnost S k ω (BCDM):  |SM| · |SC| = |SB| · |SD|",
            "⇒  |SM| · |SA| = |SB|² = |SD|²",
            "A, M ∈ k₁:  m_{S}(k₁) = |SM| · |SA| = |SB|²,  B ∈ k₁",
            "⇒  SB je tečna k₁  (obrácená V 13.2)",
            "A, M ∈ k₂:  m_{S}(k₂) = |SM| · |SA| = |SD|²,  D ∈ k₂",
            "⇒  SD je tečna k₂;   B, S, D ∈ BD  ⇒  BD společná tečna  ∎"],
            "A na závěr zápis do písemky. Es je průsečík úhlopříček, ká jedna a ká dva jsou opsané kružnice. Úhlopříčky se půlí. "
            "Mocnost es ke kružnici omega dá es em krát es cé rovno es bé krát es dé, a po dosazení es em krát es á rovno es bé "
            "na druhou a es dé na druhou. Body á a em leží na ká jedna i ká dva, takže es em krát es á je mocnost es k oběma. "
            "Podle obrácené věty třináct celá dva je es bé tečna ká jedna a es dé tečna ká dva, a protože bé, es, dé leží "
            "na jedné přímce, je bé dé společná tečna.",
            size=26, dy=0.55, fig_w=4.6, x_text=-1.9,
            final="Zastav si video a zkus si celý důkaz napsat sám. Kdyby ses zasekl, vrať se k mapě důkazu se čtyřmi kroky.")
