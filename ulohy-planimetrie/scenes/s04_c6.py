import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

K = 0.5                                   # 1 cm
A = np.array([-5.7, -2.7, 0])
B = A + np.array([8 * K, 0, 0])
D = A + np.array([0, 4 * K, 0])
C = B + (D - A)
E = foot(A, B, D)


def rot_pts(pts, center, ang):
    return [rotate_about(P, center, ang) for P in pts]


class C6(ProofScene):
    CODE = "C6"
    NAME = "Obdélník a výška na úhlopříčku"
    INDEX = 4
    SEED = 306

    def construct(self):
        self.intro(
            ["V obdélníku ABCD je |AB| = 2a a |AD| = a. Bod E je patou kolmice vedené z vrcholu A",
             "na úhlopříčku BD.   a) Dokažte, že |DE| · |DB| = a².",
             "b) Pro a = 4 cm určete |BD|, |DE| a |AE|."],
            "Úloha cé šest. V obdélníku á bé cé dé je strana á bé dvakrát á a strana á dé á. Bod é je pata kolmice "
            "z vrcholu á na úhlopříčku bé dé. Máme dokázat, že dé é krát dé bé je á na druhou, a pak pro á rovno čtyři "
            "spočítat délky bé dé, dé é a á é.")
        rect = hpoly(A, B, C, D)
        lab = VGroup(Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UR), Pt(D, "D", UL))
        bd = hseg(B, D, color=PEN)
        ae = hseg(A, E, color=RED, width=3.4)
        pE = Pt(E, "E", UP + RIGHT * 0.3, color=RED)
        dims = VGroup(Tx("2a", 28, GRAY).move_to((A + B) / 2 + DOWN * 0.35),
                      Tx("a", 28, GRAY).move_to((A + D) / 2 + LEFT * 0.3))
        with self.say("Nakreslíme obdélník, dlouhá strana á bé je dvakrát á, krátká strana á dé je á. Vedeme úhlopříčku bé dé "
                      "a z vrcholu á na ni spustíme kolmici. Její pata je bod é."):
            self.draw(rect, run_time=1.4)
            self.draw(lab, dims, run_time=0.6)
            self.draw(bd, run_time=0.8)
            self.draw(ae, run_time=0.8)
            self.draw(pE, RightMark(E, B, A, r=0.25), run_time=0.5)
        with self.say("Výraz dé é krát dé bé se rovná á na druhou nápadně připomíná Eukleidovu větu o odvěsně: "
                      "odvěsna na druhou se rovná přeponě krát přilehlému úseku. Jenže kde je tu pravoúhlý trojúhelník?"):
            self.board.write("|DE| · |DB| = a²  …  připomíná Eukleida", color=GRAY, size=29)
            self.board.write("(odvěsna² = přepona · přilehlý úsek)", indent=0.45, color=GRAY, size=29)
        self.think("Najdi v obdélníku pravoúhlý trojúhelník, ve kterém je AE výškou na přeponu.",
                   "Zkus najít v obrázku pravoúhlý trojúhelník, ve kterém je úsečka á é výškou na přeponu.")
        tri = hfill(A, B, D, ORANGE, 0.25)
        with self.say("Je to trojúhelník á bé dé. Má pravý úhel u vrcholu á, protože je to roh obdélníku. Jeho přepona je "
                      "úhlopříčka bé dé, ta leží naproti pravému úhlu. Odvěsny jsou á bé a á dé. A úsečka á é vychází z vrcholu "
                      "pravého úhlu kolmo na přeponu, je to tedy přesně výška na přeponu."):
            self.play(FadeIn(tri), run_time=0.7)
            self.draw(RightMark(A, B, D, r=0.35, color=ORANGE), run_time=0.5)
            self.board.write("[a)  △ABD:  pravý úhel při A  (roh obdélníku)")
            self.board.write("přepona BD,  odvěsny AB, AD", indent=0.95)
            self.board.write("AE ⊥ BD  ⇒  AE je výška na přeponu", indent=0.95)

        # otočení do klasické polohy
        cen = (A + B + D) / 3
        ang = PI - np.arctan2(*(B - D)[1::-1])
        A2, B2, D2, E2 = rot_pts([A, B, D, E], cen, ang)
        sh = np.array([-3.7, -0.9, 0]) - (B2 + D2) / 2 + np.array([0, -0.3, 0])
        A2, B2, D2, E2 = A2 + sh, B2 + sh, D2 + sh, E2 + sh
        geo = VGroup(tri, hpoly(A, B, D, color=PEN), ae)
        with self.say("Trojúhelník je ale v obrázku natočený. Proto ho Eukleides neprozradí na první pohled. "
                      "Vyjmeme ho z obdélníku a otočíme tak, aby přepona ležela dole vodorovně, jak jsme zvyklí z učebnice."):
            self.play(*[FadeOut(m) for m in self.mobjects if m not in self.header and m.z_index > -100
                        and m not in (tri,) and m not in self.board.lines], FadeIn(geo), run_time=0.8)
            self.play(Rotate(geo, ang, about_point=cen), run_time=2.2)
            self.play(geo.animate.shift(sh), run_time=1.0)
        lab2 = VGroup(Pt(A2, "A", UP), Pt(B2, "B", DR if B2[0] > D2[0] else DL), Pt(D2, "D", DL if B2[0] > D2[0] else DR),
                      Pt(E2, "E", DOWN, color=RED), RightMark(A2, B2, D2, r=0.3, color=ORANGE),
                      RightMark(E2, B2, A2, r=0.22))
        self.draw(lab2, run_time=0.6)
        de_lbl = Tx("|DE|", 26, TEAL).move_to((D2 + E2) / 2 + DOWN * 0.38)
        eb_lbl = Tx("|EB|", 26, GRAY).move_to((E2 + B2) / 2 + DOWN * 0.38)
        with self.say("Teď je to klasický obrázek. Přepona bé dé dole, výška á é na ni. Výška rozdělí přeponu na dva úseky: "
                      "dé é a é bé. Úsek dé é leží u vrcholu dé, tedy u odvěsny á dé. Je to úsek přilehlý k odvěsně á dé."):
            self.hl((D2, E2), color=TEAL, run_time=1.0)
            self.draw(de_lbl, eb_lbl, run_time=0.6)
            self.hl((A2, D2), color=TEAL, run_time=1.0)
        with self.say("Eukleidova věta o odvěsně pro odvěsnu á dé tedy říká: á dé na druhou se rovná dé bé krát dé é. "
                      "A protože á dé je á, dostáváme přesně to, co jsme měli dokázat."):
            self.board.write("Eukleidova v. o odvěsně (odvěsna AD):", indent=0.45)
            self.board.write("|AD|² = |DB| · |DE|", indent=0.95)
            r = self.board.write("⇒  |DE| · |DB| = a²   ∎", indent=0.95)
            self.box(r, run_time=0.6)
        sm = hfill(D2, E2, A2, TEAL, 0.3)
        with self.say("A proč Eukleides vůbec platí? Malý trojúhelník dé é á a velký dé á bé mají společný úhel u dé "
                      "a oba mají pravý úhel. Jsou tedy podobné podle věty u u. Poměr odpovídajících si stran: dé é ku dé á "
                      "se rovná dé á ku dé bé. Vynásobením do kříže dostaneme dé á na druhou rovno dé é krát dé bé."):
            self.play(FadeIn(sm), run_time=0.6)
            self.draw(AngleMark(D2, E2, A2, 0.5, PURPLE), run_time=0.5)
            self.board.write("(proč: △DEA ∼ △DAB (uu)  ⇒", indent=0.45, color=GRAY, size=28)
            self.board.write(Row(Frac("|DE|", "|DA|", 28, GRAY), "=", Frac("|DA|", "|DB|", 28, GRAY), ")", size=28, color=GRAY),
                             indent=1.2)
        self.wait(0.6)

        # ---- b) výpočet
        self.clear_body()
        geo2 = VGroup(hfill(A2, B2, D2, ORANGE, 0.18), hpoly(A2, B2, D2), hseg(A2, E2, color=RED, width=3.2),
                      Pt(A2, "A", UP), Pt(B2, "B", DR if B2[0] > D2[0] else DL), Pt(D2, "D", DL if B2[0] > D2[0] else DR),
                      Pt(E2, "E", DOWN, color=RED), RightMark(A2, B2, D2, r=0.3, color=ORANGE),
                      Tx("8", 28, PEN).move_to((A2 + B2) / 2 + unit_out(A2, B2, D2) * 0.32),
                      Tx("4", 28, PEN).move_to((A2 + D2) / 2 + unit_out(A2, D2, B2) * 0.32))
        self.play(FadeIn(geo2), run_time=0.6)
        with self.say("Část bé, pro á rovno čtyři. Odvěsny jsou tedy osm a čtyři. Přeponu bé dé spočítáme Pythagorovou větou: "
                      "odmocnina z osmi na druhou plus čtyř na druhou, to je odmocnina z osmdesáti, a to je čtyři odmocniny z pěti, "
                      "přibližně osm celých devadesát čtyři centimetru."):
            self.board.write("b)  a = 4:  |AB| = 8,  |AD| = 4")
            self.board.write("|BD| = √(8² + 4²) = √80 = 4√5 ≐ 8,94 cm", indent=0.45)
        with self.say("Úsek dé é dostaneme rovnou z části á: dé é je á na druhou děleno dé bé. Šestnáct děleno čtyřmi odmocninami "
                      "z pěti je čtyři lomeno odmocninou z pěti. Usměrníme, tedy rozšíříme odmocninou z pěti, a máme čtyři odmocniny "
                      "z pěti lomeno pěti, asi jedna celá sedmdesát devět centimetru."):
            self.board.write(Row("|DE| =", Frac("a²", "|BD|", 28), "=", Frac("16", "4√5", 28), "=", Frac("4", "√5", 28), "=",
                                 Frac("4√5", "5", 28), "≐ 1,79 cm", size=29), indent=0.45)
        self.think("Jak spočítat výšku AE, když znáš obě odvěsny i přeponu?",
                   "A teď výška á é. Zkus si rozmyslet, jak ji spočítat, když znáš obě odvěsny i přeponu.", pause=5)
        with self.say("Trik je obsah trojúhelníku spočítaný dvakrát. Jednou vezmu za základnu odvěsnu á bé a výška k ní je "
                      "druhá odvěsna á dé. Podruhé vezmu za základnu přeponu bé dé a výška k ní je právě á é. "
                      "Obsah je pořád stejný, takže polovina á bé krát á dé se rovná polovině bé dé krát á é."):
            self.hl((A2, B2), (A2, D2), color=ORANGE, run_time=1.2)
            self.hl((B2, D2), (A2, E2), color=RED, run_time=1.2)
            self.board.write("obsah dvakrát:", indent=0.45)
            self.board.write("½ · |AB| · |AD| = ½ · |BD| · |AE|", indent=0.95)
        with self.say("Vyjádříme á é: osm krát čtyři děleno čtyřmi odmocninami z pěti, to je osm lomeno odmocninou z pěti, "
                      "po usměrnění osm odmocnin z pěti lomeno pěti, přibližně tři celé padesát osm centimetru."):
            self.board.write(Row("|AE| =", Frac("8 · 4", "4√5", 28), "=", Frac("8", "√5", 28), "=", Frac("8√5", "5", 28),
                                 "≐ 3,58 cm", size=29), indent=0.45)
        with self.say("A kontrola větou o výšce: é bé je osm celých devadesát čtyři minus jedna celá sedmdesát devět, "
                      "tedy sedm celých patnáct. Jedna celá sedmdesát devět krát sedm celých patnáct je dvanáct celých osm, "
                      "a to je přesně tři celé padesát osm na druhou. Sedí to."):
            self.board.write("kontrola:  |AE|² = |DE| · |EB| = 1,79 · 7,15 ≐ 12,8 ✓", indent=0.45, color=GREEN)

        fig = VGroup(hpoly(A, B, C, D), hseg(B, D), hseg(A, E, color=RED), Pt(A, "A", DL), Pt(B, "B", DR),
                     Pt(C, "C", UR), Pt(D, "D", UL), Pt(E, "E", UP + RIGHT * 0.3, color=RED), RightMark(E, B, A, r=0.25),
                     hfill(A, B, D, ORANGE, 0.2), Tx("2a", 26, GRAY).move_to((A + B) / 2 + DOWN * 0.35),
                     Tx("a", 26, GRAY).move_to((A + D) / 2 + LEFT * 0.3))
        self.summary(fig, [
            "a)  △ABD je pravoúhlý (pravý úhel při A), přepona BD,",
            "AE … výška na přeponu, DE … úsek přilehlý k AD",
            "Eukleidova věta o odvěsně:  |AD|² = |DB| · |DE|  ⇒  |DE| · |DB| = a²  ∎",
            "b)  |BD| = √((2a)² + a²) = a√5 = 4√5 ≐ 8,94 cm",
            "|DE| = a² / |BD| = a/√5 = 4√5/5 ≐ 1,79 cm",
            "½ · |AB| · |AD| = ½ · |BD| · |AE|  ⇒  |AE| = 2a/√5 = 8√5/5 ≐ 3,58 cm"],
            "Shrnutí. Část á: trojúhelník á bé dé je pravoúhlý s pravým úhlem u á, á é je výška na přeponu a dé é je úsek "
            "přilehlý k odvěsně á dé. Eukleidova věta o odvěsně dá á dé na druhou rovno dé bé krát dé é. Část bé: přepona "
            "čtyři odmocniny z pěti, dé é je á na druhou lomeno přeponou, a výšku á é dostaneme z obsahu spočítaného dvakrát.",
            size=26, dy=0.56, fig_w=4.4, x_text=-2.0,
            final="Zastav si video a zkus si to spočítat sám.")


def unit_out(P, Q, R):
    """Jednotkový vektor kolmý na PQ, mířící od bodu R (ven z trojúhelníku)."""
    d = Q - P
    n = np.array([-d[1], d[0], 0]) / np.linalg.norm(d)
    if np.dot(n, R - (P + Q) / 2) > 0:
        n = -n
    return n
