from b5geo import *

KC = np.array([-4.3, -0.55, 0])      # pomocná kružnice k
KR = 1.65
SP = np.array([-1.3, -2.5, 0])       # bod S vně
DIST = np.linalg.norm(SP - KC)
POW = DIST ** 2 - KR ** 2
BASE = np.arctan2(*(KC - SP)[1::-1])
TANG = np.degrees(np.arcsin(KR / DIST))   # úhel tečny od spojnice S–střed
_d = np.array([np.cos(BASE + np.radians(TANG)), np.sin(BASE + np.radians(TANG)), 0])
TPT = SP + _d * np.sqrt(POW)              # bod dotyku
TANG_C = np.arctan2(*(TPT - KC)[1::-1])   # jeho úhel měřený od středu k


class B5b(B5Scene):
    INDEX = 2
    SEED = 502

    def construct(self):
        self.quick_header(self.HEADER)
        self.show_roadmap(0, (), "Krok jedna: jak dokázat, že je přímka tečna.")
        k = hcircle(KC, KR, color=PEN, width=3)
        ktag = Tx("k", 30, PEN).move_to(KC + KR * np.array([-0.8, 0.8, 0]))
        pS = Pt(SP, "S", DR)
        with self.say("Na chvíli odložíme naši úlohu a vezmeme si jednu obyčejnou kružnici ká a bod es, který leží mimo ni. "
                      "Tohle je princip, na kterém celý důkaz stojí, tak ho chci mít úplně jasný."):
            self.draw(k, ktag, run_time=1.3)
            self.draw(pS, run_time=0.4)

        th = ValueTracker(-8)

        def secant():
            a = BASE + np.radians(th.get_value())
            d = np.array([np.cos(a), np.sin(a), 0])
            ints = line_circle(SP, d, KC, KR)
            g = VGroup(Line(SP, SP + d * (DIST + KR + 0.6), color=GRAY, stroke_width=2.6))
            if len(ints) == 2:
                X, Y = ints
                sx, sy = np.linalg.norm(X - SP), np.linalg.norm(Y - SP)
                g.add(Line(SP, X, color=GREEN, stroke_width=6), Line(X, Y, color=GRAY, stroke_width=2.6),
                      Dot(X, radius=0.07, color=GREEN), Dot(Y, radius=0.07, color=ORANGE))
                g.add(Text("X", font=FONT, font_size=28, color=GREEN).next_to(X, normalize(X - KC), buff=0.08),
                      Text("Y", font=FONT, font_size=28, color=ORANGE).next_to(Y, normalize(Y - KC), buff=0.08))
                g.add(Text(f"|SX| = {sx:.2f}", font=FONT, font_size=32, color=GREEN).move_to([3.6, 1.7, 0]),
                      Text(f"|SY| = {sy:.2f}", font=FONT, font_size=32, color=ORANGE).move_to([3.6, 1.1, 0]),
                      Text(f"|SX| · |SY| = {sx * sy:.2f}", font=FONT, font_size=38, color=RED).move_to([3.6, 0.3, 0]))
            return g

        lv = always_redraw(secant)
        with self.say("Vedeme bodem es sečnu. Ta protne kružnici ve dvou bodech, bližším iks a vzdálenějším ypsilon. "
                      "Podívej se na součin es iks krát es ypsilon. Teď sečnou otáčím. Úseky se mění, ale součin zůstává pořád stejný. "
                      "Tomu stálému číslu se říká mocnost bodu es ke kružnici ká."):
            self.add(lv)
            self.play(th.animate.set_value(18), run_time=3)
            self.play(th.animate.set_value(-20), run_time=3.5)
            self.play(th.animate.set_value(5), run_time=2)
        self.board = Board(self, x=-0.3, y=-0.8)
        with self.say("Zapíšeme to: mocnost es ke ká je es iks krát es ypsilon, pro libovolnou sečnu."):
            self.board.write(ctx("m_{S}(k) =", ("|SX|", GREEN), "·", ("|SY|", ORANGE), " (libovolná sečna)"))
        with self.say("A teď sleduj, co se stane, když sečnou otáčím dál, až se kružnice skoro přestane dotýkat. "
                      "Body iks a ypsilon se k sobě přibližují, a v jednu chvíli splynou v jediný bod. To je bod dotyku té, "
                      "a přímka je tečna."):
            self.play(th.animate.set_value(TANG - 3), run_time=3.5)
            self.play(th.animate.set_value(TANG - 0.15), run_time=2.5, rate_func=smooth)
        self.remove(lv)
        a = BASE + np.radians(TANG)
        d = np.array([np.cos(a), np.sin(a), 0])
        T = SP + d * np.sqrt(POW)
        tline = hseg(SP, SP + d * (np.sqrt(POW) + 1.4), color=C_T, width=4)
        pT = Pt(T, "T", normalize(T - KC), color=C_T)
        self.add(tline, pT, Line(SP, T, color=GREEN, stroke_width=6))
        with self.say("V té chvíli je es iks i es ypsilon totéž, je to es té. A součin, který byl pořád stejný, je teď es té krát es té, "
                      "tedy es té na druhou. Mocnost se rovná druhé mocnině délky tečny."):
            self.board.write("tečna:  X = Y = T")
            self.board.write(ctx("⇒  m_{S}(k) =", ("|ST|", GREEN), "·", ("|ST|", GREEN), "=", ("|ST|²", GREEN)), indent=0.45)
        self.wait(0.5)

        # --- obráceně
        self.clear_body()
        k = hcircle(KC, KR, color=PEN, width=3)
        self.play(FadeIn(k), FadeIn(Tx("k", 30, PEN).move_to(KC + KR * np.array([-0.8, 0.8, 0]))), FadeIn(Pt(SP, "S", DR)),
                  run_time=0.5)
        with self.say("V naší úloze ale potřebujeme opak. Máme bod na kružnici, říkejme mu bé, a chceme dokázat, že přímka es bé "
                      "je tečna. Pomůže tohle: když es bé na druhou vyjde přesně rovno mocnosti, pak je es bé tečna."):
            self.board = Board(self, x=-0.3, y=-0.8)
            self.board.write("Obráceně:  B ∈ k  ∧  |SB|² = m_{S}(k)", color=RED)
            self.board.write("⇒  SB je tečna ?", indent=1.4, color=RED)
        self.think("Proč by z |SB|² = m_{S}(k) mělo plynout, že je SB tečna?",
                   "Než to ukážu, zkus si rozmyslet, proč by to mělo platit.", pause=5)

        phi = ValueTracker(TANG_C - 1.3)

        def bpoint():
            # bod B na kružnici – parametrizace úhlem od středu
            return KC + KR * np.array([np.cos(phi.get_value()), np.sin(phi.get_value()), 0])

        def live():
            B = bpoint()
            sb2 = np.linalg.norm(B - SP) ** 2
            ok = abs(sb2 - POW) < 0.03
            col = GREEN if ok else RED
            d = normalize(B - SP)
            ints = line_circle(SP, d, KC, KR)
            g = VGroup(Line(SP, SP + d * (np.linalg.norm(B - SP) + 1.2), color=GRAY, stroke_width=2.4),
                       Line(SP, B, color=C_SB, stroke_width=6), Dot(B, radius=0.08, color=C_SB),
                       Text("B", font=FONT, font_size=30, color=C_SB).next_to(B, normalize(B - KC), buff=0.08))
            if len(ints) == 2:
                other = ints[0] if np.linalg.norm(ints[0] - B) > np.linalg.norm(ints[1] - B) else ints[1]
                if np.linalg.norm(other - B) > 0.05:
                    g.add(Dot(other, radius=0.07, color=GRAY),
                          Text("B′", font=FONT, font_size=28, color=GRAY).next_to(other, normalize(other - KC), buff=0.08))
            g.add(Text(f"|SB|² = {sb2:.2f}", font=FONT, font_size=34, color=C_SB).move_to([3.6, 1.7, 0]),
                  Text(f"mocnost = {POW:.2f}", font=FONT, font_size=34, color=INK).move_to([3.6, 1.1, 0]),
                  Text("rovnají se ⇒ tečna" if ok else "nerovnají se", font=FONT, font_size=34, color=col)
                  .move_to([3.6, 0.4, 0]))
            return g

        lv = always_redraw(live)
        with self.say("Nejdřív to uvidíme. Bod bé posouvám po kružnici a porovnávám dvě čísla: es bé na druhou a mocnost. "
                      "Pokud přímka es bé kružnici protíná ještě jinde, v bodě bé s čárkou, čísla se nerovnají. "
                      "Rovnají se jen v jediné poloze, a to tehdy, když je es bé tečna."):
            self.add(lv)
            self.play(phi.animate.set_value(TANG_C - 0.4), run_time=3)
            self.play(phi.animate.set_value(TANG_C - 1.6), run_time=2.5)
            self.play(phi.animate.set_value(TANG_C), run_time=3.5, rate_func=smooth)
        self.remove(lv)
        self.add(live())
        self.board.size = 28
        with self.say("A teď proč to platí vždycky. Kdyby přímka es bé nebyla tečna, protínala by kružnici ještě v druhém bodě "
                      "bé s čárkou. Mocnost by pak byla es bé krát es bé s čárkou. Ale my víme, že mocnost je es bé krát es bé. "
                      "Takže es bé s čárkou je stejně dlouhé jako es bé. Oba body leží na stejné polopřímce ze es ve stejné "
                      "vzdálenosti, takže splynou. Druhý průsečík neexistuje a přímka je tečna."):
            self.board.write("kdyby SB protínala k ještě v B′:")
            self.board.write(ctx(("|SB|", C_SB), "·", ("|SB′|", GRAY), "= m_{S}(k) =", ("|SB|", C_SB), "·", ("|SB|", C_SB), size=28),
                             indent=0.45)
            self.board.write("⇒  |SB′| = |SB|  ⇒  B′ = B  ⇒  tečna ✓", indent=0.45)
        self.wait(0.5)

        # --- recept
        self.clear_body()
        card = VGroup(Text("RECEPT", font=FONT, font_size=40, color=RED, weight=BOLD),
                      Tx("Chci dokázat, že SB je tečna kružnice k (a B ∈ k).", 32, INK),
                      ctx("Stačí ukázat:", ("|SB|²", C_SB), "=", ("m_{S}(k)", INK), size=36),
                      Tx("Mocnost m_{S}(k) spočítám z libovolné sečny bodu S.", 30, GRAY)).arrange(DOWN, buff=0.35)
        box = SurroundingRectangle(card, buff=0.35, color=RED, corner_radius=0.15, stroke_width=3)
        VGroup(card, box).move_to(UP * 0.6)
        with self.say("Tím máme recept, který budeme používat. Chci-li dokázat, že es bé je tečna, stačí ukázat, že es bé na druhou "
                      "se rovná mocnosti bodu es. A mocnost spočítám z jakékoli sečny, která bodem es prochází."):
            self.play(Create(box), run_time=0.8)
            for m in card:
                self.play(Write(m), run_time=1.2)
        goal = VGroup(ctx("Pro nás:  ", ("|SB|²", C_SB), "=", ("m_{S}(k₁)", C_K1), "   a   ", ("|SD|²", C_SB), "=",
                          ("m_{S}(k₂)", C_K2), size=32)).next_to(box, DOWN, buff=0.6)
        with self.say("V naší úloze tedy potřebujeme dvě rovnosti: es bé na druhou se rovná mocnosti es ke ká jedna, "
                      "a es dé na druhou se rovná mocnosti es ke ká dvě. Bod es je průsečík úhlopříček."):
            self.play(Write(goal), run_time=2.0)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in (card, box, goal)], run_time=0.6)
