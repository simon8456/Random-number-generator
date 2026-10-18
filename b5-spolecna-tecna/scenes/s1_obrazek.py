from b5geo import *


class B5a(B5Scene):
    INDEX = 1
    SEED = 501

    def construct(self):
        self.intro(
            ["V rovnoběžníku ABCD platí |AC| > |BD|. Bod M leží na úhlopříčce AC tak,",
             "že čtyřúhelník BCDM je tětivový. Dokažte, že přímka BD je společnou tečnou",
             "kružnic opsaných trojúhelníkům AMB a AMD."],
            "Úloha bé pět, tentokrát úplně sama a pořádně. V rovnoběžníku á bé cé dé je úhlopříčka á cé delší než bé dé. "
            "Bod em leží na úhlopříčce á cé tak, že čtyřúhelník bé cé dé em je tětivový. Máme dokázat, že přímka bé dé "
            "je společnou tečnou kružnic opsaných trojúhelníkům á em bé a á em dé.",
            header=self.HEADER)
        g = G
        lg = legend()
        rows = lg.rows
        with self.say("V minulém videu bylo na obrázku najednou moc písmenek a kružnic. Teď ho postavíme po kouscích. "
                      "Každá věc dostane svou barvu, která se už nezmění, a vlevo dole bude legenda, kde si můžeš kdykoli "
                      "připomenout, co je co."):
            self.play(FadeIn(lg[0]), run_time=0.6)

        # --- rovnoběžník
        par = hpoly(g["A"], g["B"], g["C"], g["D"], color=C_PAR, width=3.4)
        pts = VGroup(*[pt(n) for n in "ABCD"])
        with self.say("Nejdřív rovnoběžník á bé cé dé, tmavě modře. Kreslíme obecný, šikmý, žádný obdélník ani kosočtverec."):
            self.draw(par, run_time=1.5)
            self.draw(pts, run_time=0.6)
            self.play(FadeIn(rows[0]), run_time=0.6)
        diag = VGroup(seg("A", "C", GRAY, width=2.4), seg("B", "D", GRAY, width=2.4))
        pS = pt("S")
        tk = VGroup(ticks(g["S"], g["A"], 1), ticks(g["S"], g["C"], 1), ticks(g["S"], g["B"], 2), ticks(g["S"], g["D"], 2))
        with self.say("Úhlopříčky á cé a bé dé se protínají v bodě es. A protože je to rovnoběžník, úhlopříčky se navzájem "
                      "půlí: es á je stejně dlouhé jako es cé a es bé stejně jako es dé. Označím to čárkami. "
                      "Tuhle vlastnost si zapamatuj, budeme ji potřebovat."):
            self.draw(diag, run_time=1.0)
            self.draw(pS, run_time=0.4)
            self.draw(tk, run_time=0.8)
            self.board.write("S = AC ∩ BD")
            self.board.write("|SA| = |SC|,   |SB| = |SD|", indent=0.45)

        # --- ω
        w = circle_w()
        pM = pt("M")
        bcdm = hfill(g["B"], g["C"], g["D"], g["M"], C_W, 0.13)
        with self.say("Teď to slovo tětivový. Čtyřúhelník je tětivový, když jeho čtyři vrcholy leží na jedné kružnici. "
                      "Bé cé dé em je tětivový, takže body bé, cé, dé a em leží na jedné kružnici. Říkejme jí omega a kresleme ji fialově."):
            self.blink(pts[1], pts[2], pts[3], color=C_W, run_time=1.0)
            self.board.write("BCDM tětivový  ⇔  B, C, D, M ∈ ω", color=C_W)
        with self.say("Kružnici omega dostaneme takhle: vedeme ji body bé, cé a dé. Ona pak protne úhlopříčku á cé ještě v jednom bodě. "
                      "A to je přesně náš bod em. Bod em tedy není nějaký náhodný bod, je to druhý průsečík omegy s úhlopříčkou á cé."):
            self.draw(w, run_time=2.0)
            self.draw(tag_w(), run_time=0.3)
            self.play(Flash(g["M"], color=RED, line_length=0.25, num_lines=10), run_time=0.8)
            self.draw(pM, run_time=0.4)
            self.play(FadeIn(bcdm), run_time=0.6)
            self.play(FadeIn(rows[1]), run_time=0.5)
        with self.say("A co ta podmínka, že á cé je delší než bé dé? Ta jen zaručuje, že bod em padne mezi body á a es, "
                      "tak jak to vidíš na obrázku. Pro samotný důkaz ji potřebovat nebudeme."):
            self.hl((g["A"], g["S"]), color=RED, run_time=1.2)
            self.board.write("(|AC| > |BD| jen zaručí, že M leží mezi A a S)", color=GRAY, size=26)
        self.play(FadeOut(bcdm), run_time=0.4)

        # --- k1, k2
        t1 = hfill(g["A"], g["M"], g["B"], C_K1, 0.28)
        k1 = circle_k1()
        with self.say("Teď první z kružnic ze zadání. Trojúhelník á em bé, oranžově. Kružnice opsaná trojúhelníku je ta, "
                      "která prochází všemi třemi jeho vrcholy. Říkejme jí ká jedna. Prochází tedy body á, em a bé."):
            self.play(FadeIn(t1), run_time=0.6)
            self.draw(k1, run_time=1.6)
            self.draw(tag_k1(), run_time=0.3)
            self.play(FadeIn(rows[2]), run_time=0.5)
            self.board.write("k₁ … opsaná △AMB:  A, M, B ∈ k₁", color=C_K1)
        self.play(FadeOut(t1), run_time=0.4)
        t2 = hfill(g["A"], g["M"], g["D"], C_K2, 0.28)
        k2 = circle_k2()
        with self.say("A druhá: trojúhelník á em dé, tyrkysově, a jeho opsaná kružnice ká dvě. Ta prochází body á, em a dé."):
            self.play(FadeIn(t2), run_time=0.6)
            self.draw(k2, run_time=1.6)
            self.draw(tag_k2(), run_time=0.3)
            self.play(FadeIn(rows[3]), run_time=0.5)
            self.board.write("k₂ … opsaná △AMD:  A, M, D ∈ k₂", color=C_K2)
        self.play(FadeOut(t2), run_time=0.4)
        with self.say("Všimni si jedné věci, která bude za chvíli klíčová. Obě kružnice, ká jedna i ká dvě, procházejí "
                      "stejnými dvěma body: á a em. Tam se protínají."):
            for _ in range(2):
                self.play(Flash(g["A"], color=RED, line_length=0.22), Flash(g["M"], color=RED, line_length=0.22),
                          Indicate(k1, color=C_K1, scale_factor=1.03), Indicate(k2, color=C_K2, scale_factor=1.03),
                          run_time=1.0)
            self.board.write("obě k₁ i k₂ procházejí body A a M !", color=RED)

        # --- cíl
        bd = hline(g["B"], g["D"], ext=1.0, color=C_T, width=4)
        with self.say("A teď, co máme dokázat. Přímka bé dé, červeně, má být tečnou obou kružnic. Tečna je přímka, "
                      "která se kružnice jen dotkne, má s ní jediný společný bod."):
            self.draw(bd, run_time=1.0)
        with self.say("Podívej se na bod bé. Kdybych přímku jen trochu pootočil, protne kružnici ká jedna ve dvou bodech. "
                      "Ale přesně v poloze bé dé oba průsečíky splynou do jediného bodu bé. To je dotyk."):
            self.dim(k2, w, run_time=0.4)
            wobble_line(self, g["B"], g["D"], g["K1"], g["R1"], color=C_K1, amp=16, run=4.5)
        with self.say("A u bodu dé je to stejné s kružnicí ká dvě."):
            self.undim(k2, run_time=0.3)
            self.dim(k1, run_time=0.3)
            wobble_line(self, g["D"], g["B"], g["K2"], g["R2"], color=C_K2, amp=12, run=4.0)
            self.undim(k1, w, run_time=0.4)
        with self.say("Takže cíl je: bé dé je tečna ká jedna v bodě bé, a zároveň bé dé je tečna ká dvě v bodě dé."):
            r1 = self.board.write("Cíl:  BD je tečna k₁ v bodě B", color=C_T, gap=0.1)
            r2 = self.board.write("∧  BD je tečna k₂ v bodě D", color=C_T, indent=0.75)
            self.box(VGroup(r1, r2))
        self.wait(1.0)

        # --- mapa
        self.clear_body()
        self.show_roadmap(None, (), "Než začneme, tady je mapa celého důkazu, ať víš, kam jdeme. Za prvé: zjistíme, jak se vůbec "
                          "dokazuje, že je přímka tečna. Vyjde z toho, že stačí ukázat jednu rovnost délek. Za druhé: tu rovnost "
                          "vyrobíme z kružnice omega. Za třetí: upravíme ji pomocí rovnoběžníku. A za čtvrté: přeneseme ji "
                          "na kružnice ká jedna a ká dvě.")
