import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

A, B, C, D = (np.array([-6.4, -2.4, 0]), np.array([-2.8, -2.4, 0]),
              np.array([-1.0, 0.9, 0]), np.array([-4.6, 0.9, 0]))


def para_fig(with_angles=True):
    g = VGroup(hpoly(A, B, C, D), hseg(B, D, color=INK), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UR),
               Pt(D, "D", UL))
    if with_angles:
        g.add(AngleMark(B, A, D, 0.7, RED, label="φ", label_r=1.0),
              AngleMark(D, C, B, 0.7, RED, label="φ", label_r=1.0),
              AngleMark(D, A, B, 0.5, TEAL, label="ω", label_r=0.8, n=2),
              AngleMark(B, C, D, 0.5, TEAL, label="ω", label_r=0.8, n=2))
    return g


class V83(ProofScene):
    CODE = "V 8.3"
    NAME = "Vlastnosti rovnoběžníku"
    INDEX = 10
    SEED = 83

    def construct(self):
        self.intro(
            ["Nechť ABCD je rovnoběžník, pak platí:  1) |AB| = |CD| ∧ |BC| = |AD|",
             "2) Protilehlé úhly jsou shodné."],
            "Věta osm celá tři. Je-li á bé cé dé rovnoběžník, pak jeho protější strany jsou stejně dlouhé "
            "a protilehlé úhly jsou shodné.")

        q = hpoly(A, B, C, D)
        pts = VGroup(Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UR), Pt(D, "D", UL))
        with self.say("Rovnoběžník je čtyřúhelník, jehož protější strany jsou rovnoběžné. "
                      "Á bé je rovnoběžná s cé dé a á dé je rovnoběžná s bé cé. Nic jiného zatím nevíme."):
            self.draw(q, run_time=1.6)
            self.draw(pts, run_time=0.5)
            self.hl((A, B), (D, C), color=RED, run_time=1.0)
            self.hl((A, D), (B, C), color=TEAL, run_time=1.0)
        diag = hseg(B, D, color=INK, width=3.4)
        f1, f2 = hfill(A, B, D, ORANGE, 0.2), hfill(C, D, B, TEAL, 0.2)
        with self.say("Vedeme úhlopříčku bé dé. Rozdělí rovnoběžník na dva trojúhelníky: á bé dé a cé dé bé. "
                      "Ukážeme, že jsou shodné."):
            self.draw(diag, run_time=1.0)
            self.play(FadeIn(f1), FadeIn(f2), run_time=0.8)
            self.board.write("[Dk.:  △ABD ≅ △CDB  (usu):")
        with self.say("Strana bé dé je oběma trojúhelníkům společná."):
            self.hl((B, D), color=RED, run_time=1.0)
            self.board.write("BD … společná strana", indent=0.95)
        phi1 = AngleMark(B, A, D, 0.7, RED, label="φ", label_r=1.0)
        phi2 = AngleMark(D, C, B, 0.7, RED, label="φ", label_r=1.0)
        with self.say("Úhel á bé dé a úhel cé dé bé jsou střídavé úhly u rovnoběžek á bé a cé dé, "
                      "příčkou je bé dé. Proto jsou shodné, označíme je fí."):
            self.draw(phi1, phi2, run_time=1.0)
            self.board.write("|∢ABD| = |∢CDB|   (střídavé úhly)", indent=0.95)
        om1 = AngleMark(D, A, B, 0.5, TEAL, label="ω", label_r=0.8, n=2)
        om2 = AngleMark(B, C, D, 0.5, TEAL, label="ω", label_r=0.8, n=2)
        with self.say("A úhel á dé bé a úhel cé bé dé jsou střídavé úhly u rovnoběžek á dé a bé cé. "
                      "I ty jsou shodné, označíme je omega. Strana a dva přilehlé úhly, takže věta u es u."):
            self.draw(om1, om2, run_time=1.0)
            self.board.write("|∢ADB| = |∢CBD|   (střídavé úhly)", indent=0.95)
        with self.say("Na obrázku to vypadá takhle: když trojúhelník á bé dé otočíme o sto osmdesát stupňů "
                      "kolem středu úhlopříčky, padne přesně na trojúhelník cé dé bé."):
            cp = VGroup(f1.copy().set_fill(opacity=0.35), hpoly(A, B, D, color=ORANGE))
            self.play(Rotate(cp, PI, about_point=(B + D) / 2), run_time=2.2)
            self.play(FadeOut(cp), run_time=0.5)
        with self.say("Ze shodnosti trojúhelníků plyne, že odpovídající si strany jsou stejně dlouhé. "
                      "Á bé odpovídá cé dé a á dé odpovídá cé bé. To je první část věty."):
            self.draw(VGroup(ticks(A, B, 1), ticks(D, C, 1), ticks(A, D, 2), ticks(B, C, 2)), run_time=0.8)
            self.board.write("⇒ 1)  |AB| = |CD|  ∧  |AD| = |BC|", gap=0.1)
        aA = AngleMark(A, B, D, 0.55, PURPLE)
        aC = AngleMark(C, D, B, 0.55, PURPLE)
        with self.say("Odpovídající si úhly jsou také shodné. Úhel při vrcholu á odpovídá úhlu při vrcholu cé, "
                      "takže tyto protilehlé úhly jsou shodné."):
            self.draw(aA, aC, run_time=0.8)
            self.board.write("2)  |∢DAB| = |∢BCD|   (ze shodnosti)", indent=0.45)
        with self.say("A úhly při vrcholech bé a dé se skládají ze stejných kousků: u vrcholu bé je to fí plus omega "
                      "a u vrcholu dé je to taky fí plus omega. Takže jsou shodné i druhé dva protilehlé úhly."):
            self.blink(phi1, om2, run_time=1.0)
            self.blink(phi2, om1, run_time=1.0)
            self.board.write("|∢ABC| = φ + ω = |∢CDA|   ]", indent=0.95)

        self.summary(para_fig(), [
            "[Dk.:  △ABD ≅ △CDB (usu),",
            "neboť dvě dvojice střídavých úhlů a společná strana:",
            "BD společná,  |∢ABD| = |∢CDB| = φ,",
            "|∢ADB| = |∢CBD| = ω",
            "⇒ 1)  |AB| = |CD|  ∧  |BC| = |AD|",
            "2)  |∢DAB| = |∢BCD|,",
            "|∢ABC| = φ + ω = |∢CDA|  ]"],
            "Shrnutí do písemky: trojúhelník á bé dé je shodný s trojúhelníkem cé dé bé podle u es u, protože "
            "bé dé je společná strana a máme dvě dvojice střídavých úhlů, fí a omega. Z toho plynou stejné délky "
            "protějších stran a shodnost protilehlých úhlů. U vrcholů bé a dé je to fí plus omega.",
            size=27)
