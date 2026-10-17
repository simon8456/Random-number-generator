import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

O = np.array([-4.3, -1.05, 0])
R = 1.85
M = O + np.array([0.75, 0.38, 0])
S2 = 2 * M - O
Y1, Y2 = circle_intersections(O, R, S2, R)


def refl(P):
    return 2 * M - P


class I4(ProofScene):
    CODE = "I4"
    NAME = "Tětiva se zadaným středem (středová souměrnost)"
    INDEX = 7
    SEED = 704

    def base(self):
        return VGroup(hcircle(O, R), Pt(O, "S", DOWN + LEFT * 0.3, font_size=28), Tx("k", 30, PEN).move_to(O + R * np.array([-0.8, 0.75, 0])),
                      Pt(M, "M", DOWN + RIGHT * 0.3, color=RED))

    def construct(self):
        self.intro(
            ["Je dána kružnice k a bod M ležící uvnitř k, M ≠ S.",
             "Sestrojte tětivu kružnice k, jejímž středem je bod M."],
            "Úloha í čtyři. Je dána kružnice ká a bod em uvnitř ní, různý od středu. Máme sestrojit tětivu, jejímž "
            "středem je bod em.")
        g = self.base()
        with self.say("Nakreslíme kružnici ká se středem es a bod em uvnitř."):
            self.draw(g[0], g[2], run_time=1.2)
            self.draw(g[1], g[3], run_time=0.5)
        with self.say("Hledáme dva body, iks a ypsilon, oba na kružnici, a bod em má být přesně uprostřed mezi nimi. "
                      "Potíž je, že neznáme ani jeden z nich. Máme dvě neznámé naráz a o každé víme jen to, že leží na kružnici. "
                      "Takhle se to přímo sestrojit nedá."):
            self.board.write("hledám X, Y ∈ k,  M je střed XY")
            self.board.write("dvě neznámé naráz  ⇒  přímo to nejde", indent=0.45, color=GRAY)
        with self.say("Tady přichází hlavní myšlenka všech úloh se zobrazením: vyjádřit jednu neznámou pomocí druhé. "
                      "Co znamená, že em je střed úsečky iks ypsilon? Že ypsilon dostanu z iks tak, že projdu bodem em "
                      "a pokračuju stejně daleko na druhou stranu. To je přesně středová souměrnost se středem em."):
            X0 = on_circle(O, R, 150)
            Y0 = refl(X0)
            self.draw(Pt(X0, "X", LEFT, color=INK), run_time=0.4)
            self.play(Create(DashedLine(X0, Y0, color=INK, stroke_width=2.4)), run_time=1.2)
            self.draw(Pt(Y0, "Y", RIGHT, color=INK), VGroup(ticks(X0, M, 1), ticks(M, Y0, 1)), run_time=0.6)
            self.board.write("M je střed XY  ⇔  Y = S_{M}(X)", indent=0.0, color=RED)
        self.wait(0.3)
        self.think("X běhá po celé kružnici k. Kde všude se pak může objevit Y = S_{M}(X)?",
                   "Teď si představ, že iks běhá po celé kružnici ká. Kde všude se pak může objevit ypsilon?")

        self.clear_body()
        g = self.base()
        self.play(FadeIn(g), run_time=0.5)
        t = ValueTracker(150)

        def Xp():
            return on_circle(O, R, t.get_value())

        def live():
            X = Xp()
            Y = refl(X)
            return VGroup(DashedLine(X, Y, color=INK, stroke_width=2.2), Dot(X, radius=0.07, color=INK),
                          Dot(Y, radius=0.07, color=TEAL),
                          Text("X", font=FONT, font_size=30, color=INK).next_to(X, normalize(X - O), buff=0.1),
                          Text("Y", font=FONT, font_size=30, color=TEAL).next_to(Y, normalize(Y - S2), buff=0.1))

        dummy = Dot(refl(Xp()), radius=0.001)
        dummy.add_updater(lambda m: m.move_to(refl(Xp())))
        trace = TracedPath(dummy.get_center, stroke_color=TEAL, stroke_width=4)
        lv = always_redraw(live)
        with self.say("Podívej se. Bod iks objede celou kružnici ká a jeho obraz ypsilon objede taky kružnici, tyrkysovou. "
                      "Je to obraz kružnice ká ve středové souměrnosti, označíme ji ká s čárkou. Má stejný poloměr a její střed "
                      "es s čárkou je obraz středu es."):
            self.add(dummy, trace, lv)
            self.play(t.animate.set_value(150 + 360), run_time=7, rate_func=linear)
        self.remove(lv)
        dummy.clear_updaters()
        k2 = hcircle(S2, R, color=TEAL, width=3)
        with self.say("Celou kružnici tedy nemusím zobrazovat bod po bodu. Stačí zobrazit střed: es s čárkou je takový bod, "
                      "aby em byl středem úsečky es es s čárkou. A poloměr opíšu stejný."):
            self.add(k2)
            self.remove(trace)
            self.draw(hseg(O, S2, color=GRAY, width=2.2), VGroup(ticks(O, M, 2), ticks(M, S2, 2)), run_time=0.8)
            self.draw(Pt(S2, "S′", UR, font_size=28, color=TEAL), Tx("k′", 30, TEAL).move_to(S2 + R * np.array([0.8, 0.75, 0])),
                      run_time=0.5)
            self.board.write("X ∈ k  ⇒  Y ∈ S_{M}(k) = k′")
            self.board.write("k′(S′; r),   S′ = S_{M}(S)", indent=0.45)
        with self.say("A teď to klíčové. Bod ypsilon musí ležet na kružnici ká s čárkou, protože je obrazem bodu z ká. "
                      "Ale podle zadání má ležet i na původní kružnici ká, protože je to konec tětivy. Leží tedy v průsečíku "
                      "obou kružnic. Ze dvou neznámých nám zbyla jediná, a ta je určená průsečíkem."):
            self.play(Indicate(g[0], color=RED, scale_factor=1.02), Indicate(k2, color=RED, scale_factor=1.02), run_time=1.2)
            self.draw(Pt(Y1, "Y", UP, color=RED), run_time=0.5)
            self.board.write("zároveň  Y ∈ k  ⇒  Y ∈ k ∩ k′", indent=0.0, color=RED)
        with self.say("Kružnice se protínají ve dvou bodech. Kde je druhý konec tětivy? Zobrazíme ypsilon zpátky přes em. "
                      "A ejhle, padne přesně do druhého průsečíku. Oba průsečíky jsou tedy konce jedné a téže tětivy."):
            self.play(Create(DashedLine(Y1, Y2, color=RED, stroke_width=3)), run_time=1.2)
            self.draw(Pt(Y2, "X", DOWN, color=RED), run_time=0.5)
            self.draw(hseg(Y1, Y2, color=RED, width=4.5), run_time=0.8)
        self.think("Proč je i druhý konec X = S_{M}(Y) na kružnici k?",
                   "Zkus si rozmyslet, proč i druhý konec iks leží na kružnici ká.", pause=5)
        with self.say("Protože ypsilon leží na ká s čárkou, a když ká s čárkou zobrazíme zpátky přes em, dostaneme zase ká. "
                      "Středová souměrnost provedená dvakrát vrátí všechno na místo. Proto iks leží na ká, em je střed iks ypsilon, "
                      "a iks ypsilon je hledaná tětiva."):
            self.board.write("X = S_{M}(Y) ∈ S_{M}(k′) = k   (S_{M} ∘ S_{M} = I)", indent=0.0)
            self.board.write("⇒ M je střed XY, X, Y ∈ k  ⇒  XY je tětiva ✓", indent=0.45)
        with self.say("Mimochodem, hotovou tětivu si můžeš zkontrolovat: přímka ze středu kružnice do středu tětivy je na tětivu "
                      "kolmá. Tětiva musí být kolmá na es em. Do písemky ale piš konstrukci přes zobrazení, ta se dá zobecnit "
                      "i na jiný poměr než půlku."):
            self.draw(hseg(O, M, color=PURPLE, width=2.6), RightMark(M, O, Y1, r=0.22, color=PURPLE), run_time=0.8)
            self.board.write("kontrola: XY ⊥ SM", indent=0.0, color=GRAY, size=28)

        # ---- diskuse
        self.clear_body()
        dd = ValueTracker(0.85)

        def live2():
            Mm = O + dd.get_value() * np.array([0.97, 0.24, 0])
            Sp = 2 * Mm - O
            g = VGroup(Circle(radius=R, arc_center=O, color=PEN, stroke_width=3),
                       Circle(radius=R, arc_center=Sp, color=TEAL, stroke_width=2.6),
                       Dot(O, radius=0.05, color=PEN), Dot(Mm, radius=0.07, color=RED), Dot(Sp, radius=0.05, color=TEAL))
            ints = circle_intersections(O, R, Sp, R)
            if len(ints) == 2:
                g.add(Line(ints[0], ints[1], color=RED, stroke_width=5))
                txt = "1 řešení" if dd.get_value() > 0.02 else ""
            else:
                txt = "žádné řešení"
            if dd.get_value() < 0.02:
                txt = "M = S: každý průměr"
            g.add(Text(f"|SM| = {dd.get_value() / R:.2f} r", font=FONT, font_size=34, color=INK).move_to([3.3, 0.7, 0]),
                  Text(txt, font=FONT, font_size=36, color=RED).move_to([3.3, -0.1, 0]))
            return g

        lv2 = always_redraw(live2)
        with self.say("Diskuse. Kružnice ká a ká s čárkou mají stejný poloměr er a jejich středy jsou od sebe dvakrát es em. "
                      "Když je em uvnitř kružnice, je to méně než dvě er, a kružnice se protnou ve dvou bodech. Ty dva body ale "
                      "dávají jedinou tětivu, takže řešení je právě jedno."):
            self.add(lv2)
            self.play(dd.animate.set_value(1.4), run_time=2.5)
            self.play(dd.animate.set_value(0.6), run_time=2.0)
        with self.say("Když em splyne se středem, ká s čárkou splyne s ká a řešením je každý průměr, nekonečně mnoho řešení. "
                      "A když em leží na kružnici nebo vně, kružnice se neprotnou a řešení není."):
            self.play(dd.animate.set_value(0.0), run_time=2.0)
            self.wait(1.0)
            self.play(dd.animate.set_value(2.0), run_time=2.5)
            self.wait(0.5)
            self.play(dd.animate.set_value(0.85), run_time=1.5)
        self.remove(lv2)

        fig = VGroup(self.base(), hcircle(S2, R, color=TEAL, width=2.6), Pt(S2, "S′", UR, font_size=26, color=TEAL),
                     hseg(O, S2, color=GRAY, width=2.0), VGroup(ticks(O, M, 2), ticks(M, S2, 2)),
                     hseg(Y1, Y2, color=RED, width=4.5), Pt(Y1, "Y", UP, color=RED), Pt(Y2, "X", DOWN, color=RED),
                     Tx("k′", 28, TEAL).move_to(S2 + R * np.array([0.8, 0.75, 0])))
        self.summary(fig, [
            "Rozbor: M je střed XY  ⇔  Y = S_{M}(X)",
            "X ∈ k  ⇒  Y ∈ k′ = S_{M}(k)",
            "zároveň Y ∈ k  ⇒  Y ∈ k ∩ k′",
            "1.  S′;  S′ = S_{M}(S)   (M je střed SS′)",
            "2.  k′;  k′(S′; r)",
            "3.  X, Y;  {X, Y} = k ∩ k′",
            "4.  XY",
            "Diskuse:  |SS′| = 2|SM| < 2r  ⇒  právě 1 řešení;",
            "M = S ⇒ nekonečně mnoho (průměry);  M na k nebo vně ⇒ 0"],
            "Shrnutí. Rozbor: em je střed tětivy, právě když ypsilon je obraz iks ve středové souměrnosti se středem em. "
            "Iks leží na ká, takže ypsilon leží na obrazu ká s čárkou, a zároveň na ká. Postup: zobraz střed es, narýsuj ká s čárkou "
            "se stejným poloměrem, průsečíky jsou konce tětivy. Diskuse: pro em uvnitř, různé od es, je řešení právě jedno.",
            size=26, dy=0.58, fig_w=4.6, x_text=-1.9,
            final="Zastav si video a zkus si konstrukci narýsovat sám.")
