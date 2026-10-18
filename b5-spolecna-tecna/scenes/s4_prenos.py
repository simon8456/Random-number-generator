from b5geo import *


class B5d(B5Scene):
    INDEX = 4
    SEED = 504

    def construct(self):
        self.quick_header(self.HEADER)
        self.show_roadmap(3, (0, 1, 2), "Krok čtyři: přeneseme to na kružnice ká jedna a ká dvě.")
        g = G
        par = hpoly(g["A"], g["B"], g["C"], g["D"], color=C_PAR, width=3.2)
        diag = VGroup(seg("A", "C", GRAY, width=2.2), seg("B", "D", GRAY, width=2.2))
        k1, k1t, k2, k2t = circle_k1(), tag_k1(), circle_k2(), tag_k2()
        pts = {n: pt(n) for n in "ABCDSM"}
        lg = legend()
        self.play(FadeIn(VGroup(par, diag, k1, k1t, k2, k2t, *pts.values(), lg)), run_time=0.8)
        key = self.board.write(ctx(("|SM|", C_SM), "·", ("|SA|", C_SA), "=", ("|SB|²", C_SB), "=", ("|SD|²", C_SB), size=34))
        self.box(key)
        with self.say("Máme tuhle rovnost z minulého kroku, nahoře v rámečku. A připomeňme cíl: es bé na druhou se má rovnat "
                      "mocnosti bodu es ke kružnici ká jedna."):
            self.board.write(ctx("cíl: ", ("|SB|²", C_SB), "=", ("m_{S}(k₁)", C_K1), size=30), indent=0.45)

        # --- k1
        with self.say("Ztlumím teď ká dva a díváme se jen na oranžovou kružnici ká jedna."):
            self.dim(k2, k2t, to=0.12)
            self.play(Indicate(lg.rows[2], color=C_K1, scale_factor=1.06), run_time=0.8)
        self.think("Na k₁ leží body A a M. Co to znamená pro přímku AC, která prochází bodem S?",
                   "Na kružnici ká jedna leží body á a em. Co to znamená pro přímku á cé, která prochází i bodem es?", pause=6)
        sec = hline(g["S"], g["A"], ext=0.0, ext2=0.7, color=C_K1, width=5)
        sm, sa = seg("S", "M", C_SM, width=8), seg("S", "A", C_SA, width=7)
        sm.set_z_index(5)
        with self.say("Přímka á cé prochází bodem es a protíná kružnici ká jedna právě v bodech em a á. Je to tedy sečna "
                      "kružnice ká jedna vedená z bodu es. Bližší průsečík je em, vzdálenější je á."):
            self.blink(pts["A"], pts["M"], color=C_K1)
            self.draw(sec, run_time=1.0)
            self.draw(sa, run_time=0.6)
            self.draw(sm, run_time=0.6)
        with self.say("Bod es leží mimo kružnici ká jedna. Poznáš to tak, že oba průsečíky, em i á, leží od es na stejnou stranu."):
            self.play(Flash(g["S"], color=PEN, line_length=0.22), run_time=0.8)
        with self.say("Podle receptu z kroku jedna je mocnost bodu es ke ká jedna rovna součinu úseků na sečně: es em krát es á."):
            self.board.write(ctx("A, M ∈ k₁  ⇒ ", ("m_{S}(k₁)", C_K1), "=", ("|SM|", C_SM), "·", ("|SA|", C_SA), size=30),
                             gap=0.1)
        with self.say("A teď spojíme. Es em krát es á jsme spočítali v kroku tři, je to es bé na druhou. Takže mocnost es ke ká jedna "
                      "se rovná es bé na druhou. Přesně to jsme chtěli."):
            self.play(Indicate(key, color=RED, scale_factor=1.05), run_time=1.0)
            self.board.write(ctx("⇒ ", ("m_{S}(k₁)", C_K1), "=", ("|SB|²", C_SB), "  a  B ∈ k₁", size=30), indent=0.45)
        sbx = seg("S", "B", C_SB, width=7)
        with self.say("Bod bé leží na ká jedna, takže podle receptu je přímka es bé tečna kružnice ká jedna a bé je bod dotyku. "
                      "Podívej, oba průsečíky splynou přesně v bé."):
            self.draw(sbx, run_time=0.6)
            r = self.board.write("⇒  SB je tečna k₁ v bodě B ✓", indent=0.45, color=C_K1)
            wobble_line(self, g["B"], g["D"], g["K1"], g["R1"], color=C_K1, amp=14, run=3.6)
        self.wait(0.4)

        # --- k2
        self.play(self.board.clear_anim(), FadeOut(sbx), run_time=0.5)
        key = self.board.write(ctx(("|SM|", C_SM), "·", ("|SA|", C_SA), "=", ("|SB|²", C_SB), "=", ("|SD|²", C_SB), size=34))
        self.box(key)
        with self.say("A teď druhá kružnice. Ztlumím ká jedna a rozsvítím ká dva."):
            self.dim(k1, k1t, to=0.12)
            self.undim(k2, k2t)
            self.play(Indicate(lg.rows[3], color=C_K2, scale_factor=1.06), run_time=0.8)
        self.think("Jakou mocnost má bod S ke kružnici k₂? Musíš počítat znovu?",
                   "Jakou mocnost má bod es ke kružnici ká dva? Musíš něco počítat znovu?", pause=6)
        with self.say("Nemusíš! A tohle je ten hlavní trik celé úlohy. Kružnice ká dva prochází přesně stejnými body á a em "
                      "jako ká jedna. Takže přímka á cé je i její sečnou, se stejnými průsečíky em a á. A proto vyjde i stejný "
                      "součin: es em krát es á."):
            self.blink(pts["A"], pts["M"], color=C_K2)
            self.play(Indicate(sec, color=C_K2, scale_factor=1.02), run_time=1.0)
            self.board.write(ctx("A, M ∈ k₂  ⇒ ", ("m_{S}(k₂)", C_K2), "=", ("|SM|", C_SM), "·", ("|SA|", C_SA), size=30),
                             gap=0.1)
        sdx = seg("S", "D", C_SB, width=7)
        with self.say("Z rámečku víme, že es em krát es á je taky es dé na druhou. Bod dé leží na ká dva, a tedy es dé je tečna "
                      "kružnice ká dva v bodě dé."):
            self.play(Indicate(key, color=RED, scale_factor=1.05), run_time=0.8)
            self.board.write(ctx("=", ("|SD|²", C_SB), ",  D ∈ k₂", size=30), indent=1.4)
            self.draw(sdx, run_time=0.6)
            self.board.write("⇒  SD je tečna k₂ v bodě D ✓", indent=0.45, color=C_K2)
            wobble_line(self, g["D"], g["B"], g["K2"], g["R2"], color=C_K2, amp=12, run=3.4)

        # --- závěr
        bd = hline(g["B"], g["D"], ext=1.0, color=C_T, width=4.5)
        with self.say("A závěr. Body bé, es a dé leží na jedné přímce, na úhlopříčce bé dé. Takže přímka es bé a přímka es dé "
                      "jsou jedna a táž přímka, bé dé. Ta se dotýká kružnice ká jedna v bodě bé a kružnice ká dva v bodě dé. "
                      "Je to jejich společná tečna. Hotovo."):
            self.undim(k1, k1t)
            self.play(FadeOut(sec), FadeOut(sm), FadeOut(sa), FadeOut(sdx), run_time=0.4)
            self.draw(bd, run_time=1.0)
            self.board.write("B, S, D ∈ BD  ⇒  SB = SD = BD", gap=0.1)
            r = self.board.write("⇒  BD je společná tečna k₁ a k₂   ∎", color=C_T)
            self.box(r)
            self.play(Flash(g["B"], color=C_K1, line_length=0.3), Flash(g["D"], color=C_K2, line_length=0.3), run_time=1.0)
        self.wait(1.5)
