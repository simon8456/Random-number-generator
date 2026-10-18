from b5geo import *


class B5c(B5Scene):
    INDEX = 3
    SEED = 503

    def base_figure(self):
        g = G
        self.par = hpoly(g["A"], g["B"], g["C"], g["D"], color=C_PAR, width=3.2)
        self.diag = VGroup(seg("A", "C", GRAY, width=2.2), seg("B", "D", GRAY, width=2.2))
        self.w, self.wt = circle_w(), tag_w()
        self.k1, self.k1t = circle_k1(), tag_k1()
        self.k2, self.k2t = circle_k2(), tag_k2()
        self.pts = {n: pt(n) for n in "ABCDSM"}
        self.lg = legend()
        self.play(FadeIn(VGroup(self.par, self.diag, self.w, self.wt, self.k1, self.k1t, self.k2, self.k2t,
                                *self.pts.values(), self.lg)), run_time=0.8)

    def construct(self):
        self.quick_header(self.HEADER)
        self.show_roadmap(1, (0,), "Krok dva: odkud vezmeme součin úseků z bodu es.")
        g = G
        self.base_figure()
        with self.say("Zpátky k naší úloze. Abych měl obrázek přehledný, kružnice ká jedna a ká dvě teď ztlumím, zatím je "
                      "nepotřebujeme. Soustředíme se jen na fialovou kružnici omega a na bod es."):
            self.dim(self.k1, self.k1t, self.k2, self.k2t, to=0.12)
            self.play(Indicate(self.lg.rows[1], color=C_W, scale_factor=1.06), run_time=1.0)
            self.play(Flash(g["S"], color=PEN, line_length=0.22), run_time=0.7)
        self.think("Které dvě tětivy kružnice ω procházejí bodem S?",
                   "Zkus najít dvě tětivy kružnice omega, které procházejí bodem es.", pause=5)
        sm, sc = seg("S", "M", C_SM, width=8), seg("S", "C", C_SA, width=7)
        sm.set_z_index(5)
        sb, sd = seg("S", "B", C_SB, width=7), seg("S", "D", C_SB, width=7)
        with self.say("První tětiva leží na úhlopříčce á cé. Omegu protíná v bodech em a cé, takže tětiva je em cé "
                      "a bod es ji dělí na dva úseky: es em, červeně, a es cé, zeleně."):
            self.blink(self.pts["M"], self.pts["C"], color=C_W)
            self.draw(sm, sc, run_time=1.0)
        with self.say("Druhá tětiva leží na úhlopříčce bé dé. Omegu protíná v bodech bé a dé, a es ji dělí na úseky es bé a es dé, "
                      "oba růžově."):
            self.blink(self.pts["B"], self.pts["D"], color=C_W)
            self.draw(sb, sd, run_time=1.0)
        with self.say("Bod es leží uvnitř kružnice omega a obě tětivy jím procházejí. Podle věty o mocnosti bodu, která platí "
                      "i pro bod uvnitř kružnice, jsou součiny úseků na obou tětivách stejné."):
            r = self.board.write(ctx(("|SM|", C_SM), "·", ("|SC|", C_SA), "=", ("|SB|", C_SB), "·", ("|SD|", C_SB), size=34))
            self.board.write("(mocnost S ke kružnici ω, V 13.1)", indent=0.45, color=C_W, size=26)

        # živé ověření
        th = ValueTracker(np.degrees(np.arctan2(*(g["C"] - g["S"])[1::-1])))

        def live():
            a = np.radians(th.get_value())
            d = np.array([np.cos(a), np.sin(a), 0])
            X, Y = line_circle(g["S"], d, g["W"], g["RW"])
            p1, p2 = np.linalg.norm(X - g["S"]), np.linalg.norm(Y - g["S"])
            return VGroup(Line(X, Y, color=C_W, stroke_width=4), Dot(X, radius=0.06, color=C_W), Dot(Y, radius=0.06, color=C_W),
                          Text(f"{p1:.2f} · {p2:.2f} = {p1 * p2:.2f}", font=FONT, font_size=32, color=C_W)
                          .move_to([3.4, -2.0, 0]))

        lv = always_redraw(live)
        with self.say("Pro jistotu se podívej: otáčím libovolnou tětivou omegy kolem bodu es, a součin úseků je pořád stejný."):
            self.add(lv)
            self.play(th.animate.set_value(th.get_value() + 150), run_time=5, rate_func=smooth)
        self.remove(lv)

        self.think(["Ve vzorci máme |SC| a |SD|, ale C a D v cíli vůbec nejsou.",
                    "Jak se jich zbavit? Co víme o úhlopříčkách rovnoběžníku?"],
                   "Jenže ve vzorci jsou úseky es cé a es dé, a body cé a dé v našem cíli vůbec nevystupují. "
                   "Jak se jich zbavit? Vzpomeň si, co víme o úhlopříčkách rovnoběžníku.", pause=6)

        # ---- krok 3: rovnoběžník
        with self.say("Tím jsme u kroku tři. Úhlopříčky rovnoběžníku se navzájem půlí. Nejlíp to uvidíš, když rovnoběžník "
                      "otočím o sto osmdesát stupňů kolem bodu es. Padne sám na sebe: cé se dostane na místo á a dé na místo bé."):
            self.board.write("Krok 3 – rovnoběžník: úhlopříčky se půlí", color=RED, size=28, gap=0.1)
            ghost = VGroup(hpoly(g["A"], g["B"], g["C"], g["D"], color=C_PAR, width=4),
                           Dot(g["C"], radius=0.09, color=C_SA), Dot(g["D"], radius=0.09, color=C_SB))
            self.add(ghost)
            self.play(Rotate(ghost, PI, about_point=g["S"]), run_time=3.0)
            self.play(FadeOut(ghost), run_time=0.5)
        with self.say("Takže zelený úsek es cé má stejnou délku jako es á. Ukážu to tak, že ho otočím kolem es, a přesně "
                      "dopadne na es á."):
            cp = sc.copy()
            self.play(Rotate(cp, PI, about_point=g["S"]), run_time=2.0)
            self.board.write(ctx(("|SC|", C_SA), "=", ("|SA|", C_SA), size=32), indent=0.45)
        sa = cp
        with self.say("A stejně růžový úsek es dé otočím na es bé, takže es dé se rovná es bé."):
            cp2 = sd.copy()
            self.play(Rotate(cp2, PI, about_point=g["S"]), run_time=2.0)
            self.board.write(ctx(("|SD|", C_SB), "=", ("|SB|", C_SB), size=32), indent=0.45)
            self.play(FadeOut(cp2), run_time=0.3)
        with self.say("Teď to dosadíme do vzorce z omegy. Místo es cé napíšu es á a místo es dé napíšu es bé. "
                      "Vyjde es em krát es á se rovná es bé krát es bé, tedy es bé na druhou. A protože es bé je stejně dlouhé "
                      "jako es dé, je to zároveň es dé na druhou."):
            r2a = self.board.write(ctx("⇒", ("|SM|", C_SM), "·", ("|SA|", C_SA), "=", ("|SB|", C_SB), "·", ("|SB|", C_SB),
                                       size=34), gap=0.15)
            r2b = self.board.write(ctx("=", ("|SB|²", C_SB), "=", ("|SD|²", C_SB), size=34), indent=1.75)
            self.box(VGroup(r2a, r2b))
        with self.say("Podívej se, co ten levý součin znamená na obrázku. Úseky es em a es á leží oba na stejné polopřímce z bodu es, "
                      "směrem k bodu á. Červený kousek do em a zelený kousek až do á."):
            self.play(FadeOut(sc), FadeOut(sb), FadeOut(sd), run_time=0.5)
            self.play(Indicate(sm, color=C_SM, scale_factor=1.1), Indicate(sa, color=C_SA, scale_factor=1.1), run_time=1.4)
        with self.say("Tahle rovnost je srdce celého důkazu. Kružnice omega už svou práci udělala, takže ji schovám."):
            self.play(FadeOut(self.w), FadeOut(self.wt), FadeOut(sm), FadeOut(sa), run_time=0.8)
        self.wait(1.0)
