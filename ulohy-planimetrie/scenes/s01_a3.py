import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

O = np.array([-3.75, -0.95, 0])
R = 2.3
DEG = {"C": 60, "A": 150, "D": 230, "B": 340}
DIRS = {"C": UR, "A": UL, "D": DL, "B": RIGHT}


def P(n):
    return on_circle(O, R, DEG[n])


def arc(d0, d1, color, width=7):
    return harc(O, R, np.radians(d0), np.radians(d1), color=color, width=width)


def arc_label(text, d0, d1, color, k=0.42, size=28):
    m = np.radians((d0 + d1) / 2)
    return Tx(text, size, color).move_to(O + (R + k) * np.array([np.cos(m), np.sin(m), 0]))


class A3(ProofScene):
    CODE = "A3"
    NAME = "Úhel dvou tětiv protínajících se uvnitř"
    INDEX = 1
    SEED = 103

    def base(self):
        A, B, C, D = P("A"), P("B"), P("C"), P("D")
        M = line_intersection(A, B, C, D)
        g = VGroup(hcircle(O, R), hseg(A, B), hseg(C, D))
        pts = VGroup(*[Pt(P(n), n, DIRS[n]) for n in "ABCD"], Pt(M, "M", DOWN + LEFT * 0.2, color=RED))
        return g, pts, M

    def construct(self):
        self.intro(
            ["Tětivy AB a CD kružnice k se protínají v bodě M uvnitř k (pořadí bodů C, A, D, B).",
             "Oblouk AC má středový úhel 90°, oblouk BD 110°.   a) Určete |∢AMC|.",
             "b) Dokažte obecně, že  |∢AMC| = ½(ω_{AC} + ω_{BD})."],
            "Úloha á tři. Tětivy á bé a cé dé kružnice ká se protínají v bodě em uvnitř kružnice. "
            "Oblouk á cé má středový úhel devadesát stupňů, oblouk bé dé sto deset stupňů. "
            "Máme určit úhel á em cé a dokázat obecně, že je roven polovině součtu oblouků á cé a bé dé.")
        A, B, C, D = P("A"), P("B"), P("C"), P("D")
        g, pts, M = self.base()
        with self.say("Nejdřív si nakreslíme, co máme. Na kružnici leží čtyři body v pořadí cé, á, dé, bé. "
                      "Tětivy á bé a cé dé se protínají v bodě em uvnitř kružnice."):
            self.draw(g[0], run_time=1.2)
            self.draw(*pts[:4], run_time=0.6)
            self.draw(g[1], g[2], run_time=1.2)
            self.draw(pts[4], run_time=0.4)
        aAC = arc(60, 150, RED)
        aBD = arc(230, 340, GREEN)
        lAC = arc_label("90°", 60, 150, RED)
        lBD = arc_label("110°", 230, 340, GREEN)
        mM = AngleMark(M, A, C, 0.5, RED, label="?", label_r=0.78)
        with self.say("Oblouk á cé, tady červeně, má středový úhel devadesát stupňů. Oblouk bé dé, zeleně, "
                      "má sto deset stupňů. A hledáme úhel á em cé, ten s otazníkem."):
            self.draw(aAC, lAC, run_time=1.0)
            self.draw(aBD, lBD, run_time=1.0)
            self.draw(mM, run_time=0.7)

        with self.say("Proč je to vůbec problém? Z minulého videa umíme dva druhy úhlů. Středový úhel má vrchol "
                      "ve středu kružnice a je stejně velký jako jeho oblouk. Obvodový úhel má vrchol přímo na kružnici "
                      "a je polovinou svého oblouku."):
            self.board.write("středový: vrchol v S  ⇒  úhel = ω")
            self.board.write("obvodový: vrchol na k  ⇒  úhel = ½ω")
        with self.say("Jenže náš úhel má vrchol v bodě em, který není ani ve středu, ani na kružnici. "
                      "Žádnou z těch dvou vět tedy nemůžeme použít přímo."):
            self.board.write("∢AMC: vrchol v M  ⇒  ???", color=RED)
            self.flash(pts[4].dot, run_time=0.8)

        self.think("Jak bys úhel u bodu M převedl na úhly, které už spočítat umíš?",
                   "Zkus si na chvíli zastavit a rozmyslet, jak bys úhel u bodu em převedl na úhly, které už umíš.")

        self.play(self.board.clear_anim(), run_time=0.6)
        tri = hfill(A, M, C, ORANGE, 0.25)
        with self.say("Trik je najít trojúhelník, ve kterém je úhel u em jedním z vnitřních úhlů a zbylé dva vrcholy "
                      "leží na kružnici. Takový je trojúhelník á em cé. Jeho vrcholy á a cé leží na kružnici, "
                      "takže úhly u nich už jsou obvodové, a ty umíme."):
            self.play(FadeIn(tri), run_time=0.8)
            self.draw(hseg(A, C, color=ORANGE, width=3), run_time=0.6)
            self.board.write("[b)  △AMC:  úhly při A a C jsou obvodové")
        angA = AngleMark(A, M, C, 0.55, ORANGE)
        aBC = arc(340, 420, ORANGE)
        with self.say("Podívej se na úhel u vrcholu á, tedy úhel em á cé. Bod em leží na tětivě á bé, takže je to "
                      "vlastně úhel bé á cé. Jeho ramena míří do bodů bé a cé, je to tedy obvodový úhel příslušný "
                      "oblouku bé cé. Tomu oblouku, na kterém á neleží. Proto je polovinou oblouku bé cé."):
            self.draw(angA, run_time=0.7)
            self.hl((A, B), color=ORANGE, run_time=1.0)
            self.draw(aBC, run_time=1.0)
            self.board.write("|∢MAC| = |∢BAC| = ½ω_{BC}", indent=0.95)
        angC = AngleMark(C, A, M, 0.55, PURPLE)
        aAD = arc(150, 230, PURPLE)
        with self.say("Úplně stejně úhel u vrcholu cé. Bod em leží na tětivě cé dé, takže úhel em cé á je úhel dé cé á. "
                      "Ten vidí oblouk á dé, a je tedy jeho polovinou."):
            self.draw(angC, run_time=0.7)
            self.hl((C, D), color=PURPLE, run_time=1.0)
            self.draw(aAD, run_time=1.0)
            self.board.write("|∢MCA| = |∢DCA| = ½ω_{AD}", indent=0.95)
        with self.say("Teď součet úhlů v trojúhelníku á em cé. Úhel u em je sto osmdesát stupňů minus ty dva zbylé."):
            self.blink(mM, angA, angC, run_time=1.0)
            self.board.write("|∢AMC| = 180° − ½ω_{BC} − ½ω_{AD}", indent=0.95)
        self.think("Neznáme ω_{BC} ani ω_{AD}. Jak se jich zbavit?",
                   "Jenže oblouky bé cé a á dé neznáme. Zkus přijít na to, jak se jich zbavit.", pause=5)
        with self.say("Pomůže celá kružnice. Všechny čtyři oblouky dohromady dají plný úhel, tři sta šedesát stupňů. "
                      "A polovina z toho je přesně sto osmdesát stupňů, které máme ve vzorci."):
            self.play(*[Indicate(m, color=RED) for m in (aAC, aBC, aBD, aAD)], run_time=1.5)
            self.board.write("ω_{AC} + ω_{CB} + ω_{BD} + ω_{DA} = 360°", indent=0.95)
            self.board.write("⇒  180° = ½(ω_{AC} + ω_{CB} + ω_{BD} + ω_{DA})", indent=0.95)
        with self.say("Dosadíme to místo sto osmdesáti stupňů. Polovina oblouku bé cé se odečte, polovina oblouku á dé "
                      "taky, a zbude přesně polovina součtu oblouků á cé a bé dé. To je vzorec, který jsme měli dokázat."):
            self.board.write("|∢AMC| = ½(ω_{AC} + ω_{CB} + ω_{BD} + ω_{DA})", indent=0.95)
            self.board.write("− ½ω_{BC} − ½ω_{AD}", indent=2.3)
            r = self.board.write("= ½(ω_{AC} + ω_{BD})   ∎", indent=1.6)
            self.box(r, run_time=0.7)
        self.wait(1.0)

        # ---- druhý pohled
        self.clear_body()
        g, pts, M = self.base()
        self.play(FadeIn(g), FadeIn(pts), FadeIn(arc(60, 150, RED)), FadeIn(arc(230, 340, GREEN)),
                  FadeIn(arc_label("90°", 60, 150, RED)), FadeIn(arc_label("110°", 230, 340, GREEN)), run_time=0.8)
        m1 = AngleMark(M, A, C, 0.5, RED)
        m2 = AngleMark(M, B, D, 0.5, RED)
        with self.say("Teď ještě jiný pohled, který ti možná dá větší aha. Naproti úhlu á em cé leží vrcholový úhel "
                      "bé em dé, a ten je stejně velký. Úhel u em se tedy dívá na dva oblouky: dopředu na oblouk á cé "
                      "a dozadu na oblouk bé dé. Proto se ve vzorci objeví oba."):
            self.draw(m1, m2, run_time=1.0)
            self.board.write("Proč oba oblouky?")
            self.board.write("|∢AMC| = |∢BMD|   (vrcholové úhly)", indent=0.45)
            self.blink(m1, m2, run_time=1.0)
        AD = hseg(A, D, color=TEAL, width=3)
        tri = hfill(A, M, D, TEAL, 0.22)
        with self.say("A dá se to ukázat i rychleji, přes vnější úhel. Spojíme á s dé. Bod cé leží na prodloužení "
                      "úsečky dé em za bod em, takže úhel á em cé je vnějším úhlem trojúhelníku á em dé. "
                      "A vnější úhel je součtem dvou vnitřních úhlů u zbylých vrcholů."):
            self.draw(AD, run_time=0.7)
            self.play(FadeIn(tri), run_time=0.6)
            self.board.write("∢AMC … vnější úhel △AMD  (V 6.4)")
        aA = AngleMark(A, M, D, 0.6, GREEN)
        aD = AngleMark(D, A, M, 0.6, RED)
        with self.say("Úhel u á, tedy bé á dé, je obvodový nad obloukem bé dé, polovina ze sto deseti. "
                      "Úhel u dé, tedy cé dé á, je obvodový nad obloukem á cé, polovina z devadesáti. "
                      "Sečteme je a máme zase polovinu součtu obou oblouků."):
            self.draw(aA, run_time=0.6)
            self.draw(aD, run_time=0.6)
            self.board.write("|∢AMC| = |∢BAD| + |∢CDA|", indent=0.45)
            self.board.write("= ½ω_{BD} + ½ω_{AC}", indent=1.6)

        # ---- živá ukázka
        self.clear_body()
        bt = ValueTracker(340)
        Cc, Aa, Dd = P("C"), P("A"), P("D")

        def live():
            Bb = on_circle(O, R, bt.get_value())
            Mm = line_intersection(Aa, Bb, Cc, Dd)
            om = bt.get_value() - 230
            ang = angle_deg(Mm, Aa, Cc)
            gg = VGroup(Circle(radius=R, arc_center=O, color=PEN, stroke_width=3),
                        Line(Aa, Bb, color=PEN, stroke_width=3), Line(Cc, Dd, color=PEN, stroke_width=3),
                        Arc(radius=R, start_angle=np.radians(60), angle=np.radians(90), arc_center=O,
                            color=RED, stroke_width=7),
                        Arc(radius=R, start_angle=np.radians(230), angle=np.radians(om), arc_center=O,
                            color=GREEN, stroke_width=7),
                        AngleMark(Mm, Aa, Cc, 0.45, RED))
            for n, X in (("A", Aa), ("B", Bb), ("C", Cc), ("D", Dd)):
                gg.add(Dot(X, radius=0.055, color=PEN))
                gg.add(Text(n, font=FONT, font_size=32, color=PEN).move_to(O + (X - O) * 1.13))
            gg.add(Text("M", font=FONT, font_size=30, color=RED).next_to(Mm, DL, buff=0.06))
            gg.add(Text(f"|∢AMC| = {ang:.0f}°", font=FONT, font_size=34, color=RED).move_to([3.4, 1.2, 0]))
            gg.add(Text(f"½(90° + {om:.0f}°) = {(90 + om) / 2:.0f}°", font=FONT, font_size=34, color=GREEN)
                   .move_to([3.4, 0.3, 0]))
            return gg

        lv = always_redraw(live)
        with self.say("Ověřme si, že to platí opravdu vždycky. Budu posouvat bod bé po kružnici. Oblouk bé dé se mění, "
                      "úhel u em se mění taky, ale pořád platí, že úhel u em je polovina součtu obou oblouků."):
            self.add(lv)
            self.play(bt.animate.set_value(300), run_time=3)
            self.play(bt.animate.set_value(395), run_time=4)
            self.play(bt.animate.set_value(340), run_time=2.5)
        self.remove(lv)
        self.add(live())
        with self.say("A teď část á. Stačí dosadit: polovina z devadesáti plus sto deset je polovina z dvou set, "
                      "tedy sto stupňů. Vedlejší úhel á em dé má pak osmdesát stupňů."):
            self.board.write("a)  |∢AMC| = ½(90° + 110°) = 100°", gap=2.2)
            self.board.write("|∢AMD| = 180° − 100° = 80°", indent=0.45)
        with self.say("Zapamatuj si: úhel dvou tětiv uvnitř kružnice je polovina součtu obou protilehlých oblouků. "
                      "Kdyby se přímky protínaly vně kružnice, vyšla by polovina rozdílu. Odvodí se to stejně, přes vnější úhel."):
            self.board.write("uvnitř: ½(součet oblouků),  vně: ½(rozdíl)", color=GRAY, size=28)

        g, pts, M = self.base()
        fig = VGroup(g, pts, arc(60, 150, RED), arc(230, 340, GREEN), arc_label("90°", 60, 150, RED),
                     arc_label("110°", 230, 340, GREEN), hfill(A, M, C, ORANGE, 0.22),
                     AngleMark(A, M, C, 0.5, ORANGE), AngleMark(C, A, M, 0.5, PURPLE), AngleMark(M, A, C, 0.45, RED))
        self.summary(fig, [
            "a)  |∢AMC| = ½(90° + 110°) = 100°",
            "b)  △AMC:  |∢MAC| = |∢BAC| = ½ω_{BC}  (obvodový)",
            "|∢MCA| = |∢DCA| = ½ω_{AD}  (obvodový)",
            "|∢AMC| = 180° − ½ω_{BC} − ½ω_{AD}",
            "180° = ½(ω_{AC} + ω_{CB} + ω_{BD} + ω_{DA})",
            "⇒  |∢AMC| = ½(ω_{AC} + ω_{BD})   ∎"],
            "Shrnutí. Část á: polovina z devadesáti plus sto deset, tedy sto stupňů. Část bé: v trojúhelníku á em cé jsou "
            "úhly u á a cé obvodové, polovina oblouku bé cé a polovina oblouku á dé. Úhel u em je sto osmdesát minus oba. "
            "Sto osmdesát nahradíme polovinou součtu všech čtyř oblouků, a zbude polovina součtu oblouků á cé a bé dé.",
            final="Zastav si video a zkus si celý postup napsat sám.")
