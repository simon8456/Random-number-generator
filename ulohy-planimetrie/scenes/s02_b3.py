import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

U = 0.45                      # 1 cm na obrazovce
O = np.array([-3.8, -1.0, 0])
R = 5 * U
M = O + np.array([3 * U, 0, 0])


def chord_through(th):
    """Krajní body tětivy přímky M + t·(cos th, sin th)."""
    u = np.array([np.cos(th), np.sin(th), 0])
    f = M - O
    b = np.dot(f, u)
    disc = np.sqrt(b * b - (np.dot(f, f) - R * R))
    return M + (-b - disc) * u, M + (-b + disc) * u


class B3(ProofScene):
    CODE = "B3"
    NAME = "Bod uvnitř kružnice"
    INDEX = 2
    SEED = 203

    def base(self):
        return VGroup(hcircle(O, R), Pt(O, "S", DOWN, font_size=28), Pt(M, "M", DR, color=RED, buff=0.04),
                      hseg(O, M, color=GRAY, width=2.4),
                      Tx("3", 26, GRAY).move_to((O + M) / 2 + UP * 0.22))

    def construct(self):
        self.intro(
            ["Bod M leží uvnitř kružnice k(S; 5 cm), |SM| = 3 cm.",
             "a) Určete součin úseků, na které bod M dělí libovolnou tětivu procházející M.",
             "b) Určete délku nejkratší tětivy procházející bodem M a ověřte na ní výsledek z a)."],
            "Úloha bé tři. Bod em leží uvnitř kružnice o poloměru pět centimetrů a jeho vzdálenost od středu je "
            "tři centimetry. Máme určit součin úseků, na které em dělí libovolnou tětivu, a pak délku nejkratší tětivy "
            "procházející bodem em.")
        g = self.base()
        rr = hseg(O, on_circle(O, R, 125), color=GRAY, width=2.4)
        rl = Tx("5", 26, GRAY).move_to((O + on_circle(O, R, 125)) / 2 + LEFT * 0.2)
        with self.say("Nakreslíme kružnici se středem es a poloměrem pět centimetrů a bod em ve vzdálenosti tři od středu."):
            self.draw(g[0], g[1], run_time=1.2)
            self.draw(g[3], g[4], g[2], run_time=0.8)
            self.draw(rr, rl, run_time=0.6)

        with self.say("Všimni si nejdřív zvláštní věci v zadání: slovo libovolnou. Úloha tvrdí, že odpověď nezávisí na tom, "
                      "kterou tětivu přes em zvolíme. To je přesně věta o mocnosti bodu, kterou jsme dokazovali minule: "
                      "pro všechny přímky bodem em je součin em á krát em bé stejný."):
            self.board.write("a)  libovolná tětiva AB, M ∈ AB")
            self.board.write("V 13.1:  |MA| · |MB| je pro všechny stejný", indent=0.45)
        th = ValueTracker(np.radians(70))

        def live():
            A, B = chord_through(th.get_value())
            a, b = np.linalg.norm(A - M) / U, np.linalg.norm(B - M) / U
            return VGroup(Line(A, B, color=INK, stroke_width=3.4), Dot(A, radius=0.055, color=INK),
                          Dot(B, radius=0.055, color=INK),
                          Text("A", font=FONT, font_size=30, color=INK).move_to(O + (A - O) * 1.13),
                          Text("B", font=FONT, font_size=30, color=INK).move_to(O + (B - O) * 1.13),
                          Text(f"|MA| = {a:.2f}    |MB| = {b:.2f}", font=FONT, font_size=30, color=INK)
                          .move_to([3.3, 0.3, 0]),
                          Text(f"|MA| · |MB| = {a * b:.2f}", font=FONT, font_size=36, color=RED)
                          .move_to([3.3, -0.5, 0]))

        lv = always_redraw(live)
        with self.say("Podívej se sám. Otáčím tětivou kolem bodu em. Úseky se pořád mění, jeden se zkracuje, druhý prodlužuje, "
                      "ale jejich součin zůstává pořád šestnáct."):
            self.add(lv)
            self.play(th.animate.set_value(np.radians(160)), run_time=4)
            self.play(th.animate.set_value(np.radians(10)), run_time=4)
            self.play(th.animate.set_value(np.radians(70)), run_time=2)
        self.remove(lv)

        self.think("Součin je pro všechny tětivy stejný. Kterou bys vybral, aby se počítal co nejsnáz?",
                   "Když je součin pro všechny tětivy stejný, kterou tětivu by sis vybral, aby se spočítal co nejsnáz?")

        A0, B0 = O + np.array([-R, 0, 0]), O + np.array([R, 0, 0])
        dia = hseg(A0 + LEFT * 0.1, B0 + RIGHT * 0.1, color=INK, width=3.4)
        pa, pb = Pt(A0, "A", LEFT), Pt(B0, "B", RIGHT)
        bmb = BraceBetweenPoints(M, B0, direction=DOWN, color=ORANGE)
        bma = BraceBetweenPoints(A0, M, direction=DOWN, color=TEAL)
        with self.say("Nejšikovnější je tětiva, která prochází středem es, tedy průměr. Na něm vidíme délky úseků hned. "
                      "Kratší úsek je poloměr minus vzdálenost em od středu, pět minus tři, tedy dva. "
                      "Delší úsek je poloměr plus vzdálenost, pět plus tři, tedy osm."):
            self.draw(dia, run_time=0.8)
            self.draw(pa, pb, run_time=0.5)
            self.play(GrowFromCenter(bmb), run_time=0.6)
            self.draw(Tx("|MB| = 5 − 3 = 2", 26, ORANGE).next_to(bmb, DOWN, buff=0.08).shift(DOWN * 0.4 + RIGHT * 0.3), run_time=0.8)
            self.play(GrowFromCenter(bma), run_time=0.6)
            self.draw(Tx("|MA| = 5 + 3 = 8", 26, TEAL).next_to(bma, DOWN, buff=0.08), run_time=0.8)
            self.board.write("průměr (tětiva přes S):  2 · 8 = 16 cm²", indent=0.45)
        with self.say("Obecně je to poloměr minus dé krát poloměr plus dé, a to je podle vzorce er na druhou minus dé na druhou. "
                      "Tady dvacet pět minus devět, šestnáct."):
            self.board.write("(r − d)(r + d) = r² − d² = 25 − 9 = 16", indent=0.45)
        with self.say("Ve skriptech se to zapisuje jako mocnost bodu: vzdálenost od středu na druhou minus poloměr na druhou. "
                      "Pro bod uvnitř vyjde záporně, minus šestnáct. To znaménko jen říká, že bod leží uvnitř kružnice. "
                      "Součin úseků je jeho absolutní hodnota, šestnáct centimetrů čtverečních."):
            self.board.write("m_{M} = |SM|² − r² = 9 − 25 = −16 cm²", indent=0.45)
            r = self.board.write("⇒  |MA| · |MB| = |m_{M}| = 16 cm²", indent=0.45)
            self.box(r, run_time=0.6)

        # ---- b) nejkratší tětiva
        self.clear_body()
        g = self.base()
        self.play(FadeIn(g), run_time=0.6)
        th2 = ValueTracker(np.radians(40))

        def live2():
            t = th2.get_value()
            A, B = chord_through(t)
            F = foot(O, A, B)
            h = np.linalg.norm(F - O) / U
            L = np.linalg.norm(B - A) / U
            return VGroup(Line(A, B, color=INK, stroke_width=3.4), Dot(A, radius=0.055, color=INK),
                          Dot(B, radius=0.055, color=INK), DashedLine(O, F, color=PURPLE, stroke_width=3),
                          Dot(F, radius=0.045, color=PURPLE),
                          Text(f"vzdálenost od S:  h = {h:.2f}", font=FONT, font_size=30, color=PURPLE)
                          .move_to([3.3, 0.3, 0]),
                          Text(f"délka tětivy:  {L:.2f}", font=FONT, font_size=34, color=INK).move_to([3.3, -0.5, 0]))

        lv2 = always_redraw(live2)
        with self.say("Teď část bé, nejkratší tětiva přes em. Zase otáčím tětivou kolem em a sleduji dvě čísla: "
                      "jak daleko je tětiva od středu, to je fialová úsečka, a jak je tětiva dlouhá. "
                      "Vidíš, že čím je tětiva dál od středu, tím je kratší."):
            self.add(lv2)
            self.play(th2.animate.set_value(np.radians(0)), run_time=3)
            self.play(th2.animate.set_value(np.radians(90)), run_time=4)
            self.play(th2.animate.set_value(np.radians(130)), run_time=2.5)
            self.play(th2.animate.set_value(np.radians(90)), run_time=2)
        self.remove(lv2)
        A, B = chord_through(np.radians(90))
        ch = hseg(A, B, color=INK, width=3.4)
        self.add(ch, Pt(A, "C", DOWN), Pt(B, "D", UP))
        with self.say("Proč? Poloměr k jednomu konci tětivy, vzdálenost h a polovina tětivy tvoří pravoúhlý trojúhelník. "
                      "Podle Pythagorovy věty je polovina tětivy odmocnina z er na druhou minus h na druhou. "
                      "Poloměr je pořád stejný, takže čím větší h, tím kratší tětiva."):
            self.play(FadeIn(hfill(O, M, A, ORANGE, 0.25)), run_time=0.6)
            self.draw(hseg(O, A, color=ORANGE, width=3), run_time=0.6)
            self.board.write("½ · tětiva = √(r² − h²)   (Pythagoras)")
            self.board.write("⇒ nejkratší tětiva = největší h", indent=0.45)
        self.think("Jak velké může h nejvýš být, když tětiva musí procházet bodem M?",
                   "Zkus si rozmyslet, jak velké může být h nejvýš, když tětiva musí procházet bodem em.", pause=5)
        with self.say("Vzdálenost středu od přímky je délka kolmice. Úsečka es em je přepona pravoúhlého trojúhelníku, "
                      "a přepona je vždycky delší než odvěsna. Takže h je nejvýš tři, a tři je právě tehdy, "
                      "když pata kolmice padne do bodu em. Tedy když je tětiva kolmá na es em."):
            self.board.write("h ≤ |SM| = 3,  rovnost ⇔ tětiva ⊥ SM")
            self.draw(RightMark(M, O, A, r=0.3), run_time=0.5)
        with self.say("Polovina nejkratší tětivy je tedy odmocnina z dvaceti pěti minus devíti, tedy odmocnina ze šestnácti, "
                      "čtyři centimetry. Celá tětiva cé dé má osm centimetrů."):
            self.board.write("½|CD| = √(5² − 3²) = √16 = 4 cm", gap=0.1)
            r = self.board.write("⇒  |CD| = 8 cm", indent=0.45)
            self.box(r, run_time=0.6)
        with self.say("A ověření části á: kolmice ze středu půlí tětivu, takže em je její střed a oba úseky mají čtyři centimetry. "
                      "Čtyři krát čtyři je šestnáct. Přesně jako v části á."):
            self.board.write("M je středem CD:  4 · 4 = 16 ✓", indent=0.45)

        A, B = chord_through(np.radians(90))
        fig = VGroup(self.base(), hseg(A, B, color=INK), Pt(A, "C", DOWN), Pt(B, "D", UP), RightMark(M, O, A, r=0.3),
                     hseg(O, A, color=ORANGE), Tx("5", 26, ORANGE).move_to((O + A) / 2 + LEFT * 0.2),
                     Tx("4", 26, INK).move_to((M + A) / 2 + RIGHT * 0.2))
        self.summary(fig, [
            "a)  součin je pro všechny tětivy stejný (mocnost bodu)",
            "průměr:  (r − |SM|)(r + |SM|) = 2 · 8 = 16",
            "m_{M} = |SM|² − r² = 9 − 25 = −16  ⇒  |MA| · |MB| = 16 cm²",
            "b)  nejkratší je tětiva CD ⊥ SM  (h = |SM| je největší)",
            "½|CD| = √(5² − 3²) = 4  ⇒  |CD| = 8 cm",
            "ověření:  |MC| · |MD| = 4 · 4 = 16 ✓"],
            "Shrnutí. Část á: součin úseků je pro všechny tětivy stejný, takže ho spočítáme na průměru: dva krát osm, "
            "šestnáct centimetrů čtverečních. Ve skriptech mocnost minus šestnáct. Část bé: nejkratší je tětiva kolmá na es em, "
            "protože je nejdál od středu. Její polovina je odmocnina z dvaceti pěti minus devíti, čtyři, celá má osm "
            "a čtyři krát čtyři je zase šestnáct.",
            final="Zastav si video a zkus si to spočítat sám.")
