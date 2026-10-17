import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

ALPHA = 60
LAB = 3.0                                   # |AB| na obrazovce (5 cm)
A = np.array([-5.1, -1.05, 0])
B = A + np.array([LAB, 0, 0])
MID = (A + B) / 2


def center_for(alpha_deg, below=False):
    """Střed kružnice, ze které je AB vidět pod úhlem alfa (oblouk nad AB)."""
    a = np.radians(alpha_deg)
    h = (LAB / 2) / np.tan(a)
    c = MID + np.array([0, h, 0])
    if below:
        c = MID - np.array([0, h, 0])
    return c, (LAB / 2) / np.sin(a)


S, R = center_for(ALPHA)
S2, _ = center_for(ALPHA, below=True)


def dir_of(C, P):
    return np.arctan2(*(P - C)[1::-1])


def upper_arc(C, r, color=RED, width=5, mob=False):
    a0 = dir_of(C, B)
    d = (dir_of(C, A) - a0) % (2 * PI)
    if mob:
        return Arc(radius=r, start_angle=a0, angle=d, arc_center=C, color=color, stroke_width=width)
    return harc(C, r, a0, a0 + d, color=color, width=width)


def lower_arc(C, r, color=RED, width=5):
    a0 = dir_of(C, A)
    d = (dir_of(C, B) - a0) % (2 * PI)
    return harc(C, r, a0, a0 + d, color=color, width=width)


def on_k(deg, C=S):
    return on_circle(C, R, deg)


class H1(ProofScene):
    CODE = "H1"
    NAME = "Ekvigonála – proč konstrukce funguje"
    INDEX = 6
    SEED = 601

    def ab(self):
        return VGroup(hseg(A, B, color=INK, width=3.6), Pt(A, "A", DL, color=INK), Pt(B, "B", DR, color=INK))

    def construct(self):
        self.intro(
            ["Je dána úsečka AB, |AB| = 5 cm. Sestrojte množinu všech bodů X roviny, z nichž je",
             "úsečka AB vidět pod úhlem α = 60°, tj.  U = {X ∈ E₂ : |∢AXB| = 60°}."],
            "Úloha há jedna, ekvigonála. Je dána úsečka á bé dlouhá pět centimetrů. Máme sestrojit množinu všech bodů iks, "
            "ze kterých je úsečka á bé vidět pod úhlem šedesát stupňů. Tady se zaměříme hlavně na to, proč ta konstrukce "
            "funguje.")
        ab = self.ab()
        X0 = np.array([-3.0, 1.0, 0])
        with self.say("Nejdřív, co znamená vidět úsečku pod úhlem. Stojíš v bodě iks a díváš se na oba konce úsečky. "
                      "Úhel mezi těmi dvěma směry, tedy úhel á iks bé, je úhel, pod kterým úsečku vidíš."):
            self.draw(ab, run_time=1.0)
            self.draw(Pt(X0, "X", UP), hseg(X0, A, color=GRAY, width=2.4), hseg(X0, B, color=GRAY, width=2.4), run_time=1.0)
            m = AngleMark(X0, A, B, 0.5, RED, label=f"{angle_deg(X0, A, B):.0f}°", label_r=0.85)
            self.draw(m, run_time=0.6)
        self.clear_body()
        self.play(FadeIn(self.ab()), run_time=0.3)

        # ---- experiment
        found = VGroup()
        with self.say("Zkusme takové body najít pokusem. Budu bodem iks jezdit po vodorovné přímce nad úsečkou a sledovat úhel. "
                      "Kdykoli ukáže šedesát stupňů, nechám tam červenou tečku."):
            self.wait(self.left())
        heights = [0.55, 1.55, 2.35]
        for i, h in enumerate(heights):
            yh = A[1] + h
            dx = np.sqrt(R * R - (yh - S[1]) ** 2)
            sols = [S[0] - dx, S[0] + dx]
            xt = ValueTracker(-6.7)

            def live(yh=yh, xt=xt):
                Xp = np.array([xt.get_value(), yh, 0])
                ang = angle_deg(Xp, A, B)
                col = RED if abs(ang - 60) < 0.8 else INK
                return VGroup(DashedLine([-6.9, yh, 0], [-0.4, yh, 0], color=GRAY, stroke_width=1.6),
                              Line(Xp, A, color=GRAY, stroke_width=2.2), Line(Xp, B, color=GRAY, stroke_width=2.2),
                              Dot(Xp, radius=0.06, color=col),
                              Text(f"|∢AXB| = {ang:.0f}°", font=FONT, font_size=38, color=col).move_to([3.3, 0.6, 0]))

            lv = always_redraw(live)
            self.add(lv)
            rt = 2.4 if i == 0 else 1.6
            for x in sols:
                self.play(xt.animate.set_value(x), run_time=rt, rate_func=smooth)
                d = Dot([x, yh, 0], radius=0.075, color=RED)
                found.add(d)
                self.add(d)
                self.wait(0.3)
            self.play(xt.animate.set_value(-0.6), run_time=1.0)
            self.remove(lv)
        with self.say("Tečky nevypadají náhodně. Leží na oblouku, který prochází body á a bé."):
            self.draw(upper_arc(S, R, color=RED, width=3), run_time=2.0)
        self.think("Proč by všechny body, ze kterých vidíš AB pod 60°, měly ležet na jedné kružnici?",
                   "Zkus si rozmyslet, proč by všechny takové body měly ležet na jedné kružnici. Která věta z minulého videa to říká?")

        # ---- proč oblouk
        self.clear_body()
        k = hcircle(S, R, color=GRAY, width=2.2)
        pS = Pt(S, "S", DOWN, font_size=28)
        arcU = upper_arc(S, R)
        cen = AngleMark(S, B, A, 0.4, ORANGE, label="120°", label_r=0.7, font_size=24)
        with self.say("Je to věta o středovém a obvodovém úhlu. Vezměme kružnici, na které ty tečky leží, a její střed es. "
                      "Úhel á es bé je středový úhel nad tětivou á bé. Tady má sto dvacet stupňů."):
            self.play(FadeIn(self.ab()), run_time=0.3)
            self.draw(k, arcU, run_time=1.4)
            self.draw(pS, hseg(S, A, color=ORANGE, width=2.6), hseg(S, B, color=ORANGE, width=2.6), run_time=0.8)
            self.draw(cen, run_time=0.6)
        Xs = [on_k(d) for d in (55, 95, 140)]
        marks = VGroup()
        for X in Xs:
            marks.add(hseg(X, A, color=GRAY, width=2.2), hseg(X, B, color=GRAY, width=2.2), Dot(X, radius=0.06, color=RED),
                      AngleMark(X, A, B, 0.38, RED, label="60°", label_r=0.66, font_size=22))
        with self.say("A každý bod iks na tomhle oblouku vidí úsečku á bé pod obvodovým úhlem, který je polovinou středového. "
                      "Polovina ze sto dvaceti je šedesát. Pro každý bod oblouku stejně, protože středový úhel je pro všechny "
                      "ten samý. Proto mají všechny obvodové úhly nad stejným obloukem stejnou velikost."):
            self.draw(marks, run_time=2.0, lag=0.1)
            self.board.write("X na oblouku  ⇒  |∢AXB| = ½ |∢ASB|   (V 10.4)")
            self.board.write("⇒  stačí kružnice, kde  |∢ASB| = 2α = 120°", indent=0.45)
        self.wait(0.5)

        # ---- jak najít S
        self.clear_body()
        o = hline(MID + DOWN * 0.1, MID + UP * 0.1, ext=2.6, ext2=2.6, color=GREEN, width=2.6)
        olab = Tx("o", 28, GREEN).move_to(MID + np.array([0.25, 2.45, 0]))
        with self.say("Celá konstrukce je tedy o tom, jak najít střed es. Víme o něm dvě věci. První: es á a es bé jsou poloměry, "
                      "takže jsou stejně dlouhé. Bod stejně daleko od á a bé leží na ose úsečky á bé."):
            self.play(FadeIn(self.ab()), run_time=0.3)
            self.draw(o, olab, run_time=1.2)
            self.board.write("1)  |SA| = |SB|  ⇒  S ∈ o  (osa AB)")
        tri = hfill(A, B, S, ORANGE, 0.22)
        with self.say("Druhá: trojúhelník á es bé je rovnoramenný a úhel u es má sto dvacet stupňů, tedy dvakrát alfa. "
                      "Na dva úhly u základny zbývá sto osmdesát minus sto dvacet, šedesát, každý třicet stupňů."):
            self.play(FadeIn(tri), run_time=0.6)
            self.draw(hseg(A, S, color=ORANGE, width=2.6), hseg(B, S, color=ORANGE, width=2.6), Pt(S, "S", UP + RIGHT * 0.3),
                      run_time=0.8)
            self.draw(AngleMark(S, B, A, 0.28, ORANGE, label="2α", label_r=0.5, font_size=22),
                      AngleMark(A, B, S, 0.6, PURPLE, label="30°", label_r=0.88, font_size=22),
                      AngleMark(B, S, A, 0.6, PURPLE, label="30°", label_r=0.88, font_size=22), run_time=0.8)
            self.board.write("2)  △ASB rovnoramenný, |∢ASB| = 2α", gap=0.1)
            self.board.write("⇒  |∢SAB| = (180° − 2α)/2 = 90° − α = 30°", indent=0.45)
        with self.say("Takže es najdeme tak, že z bodu á narýsujeme polopřímku pod úhlem třicet stupňů k á bé, "
                      "tedy devadesát minus alfa, a kde protne osu, tam je střed."):
            self.board.write("S = (polopřímka z A pod 90° − α) ∩ o", indent=0.45, color=RED)
        self.wait(0.5)

        # ---- úsekový úhel / postup ze skript
        self.clear_body()
        kk = hcircle(S, R, color=GRAY, width=2.2)
        self.play(FadeIn(self.ab()), FadeIn(kk), FadeIn(Pt(S, "S", UP + RIGHT * 0.3)), run_time=0.5)
        with self.say("Ve skriptech je ale konstrukce zapsaná trochu jinak, přes tečnu. Ukážu ti, že je to přesně totéž. "
                      "Nejdřív pochopíme úsekový úhel. Budu posouvat bod iks po oblouku směrem k bodu á a sledovat přímku iks á."):
            self.board.write("Proč tečna?  (úsekový úhel)")
        th = ValueTracker(95)
        tdir = np.array([np.cos(np.radians(-60)), np.sin(np.radians(-60)), 0])

        def live2():
            X = on_k(th.get_value())
            u = (A - X) / np.linalg.norm(A - X)
            return VGroup(Line(X - u * 0.3, A + u * 1.5, color=TEAL, stroke_width=3), Line(X, B, color=GRAY, stroke_width=2.4),
                          Dot(X, radius=0.065, color=RED),
                          Text(f"|∢AXB| = {angle_deg(X, A, B):.0f}°", font=FONT, font_size=34, color=RED).move_to([3.3, 0.4, 0]))

        lv2 = always_redraw(live2)
        with self.say("Úhel u iks je pořád šedesát. A čím blíž je iks k bodu á, tím víc se přímka iks á podobá tečně "
                      "ke kružnici v bodě á, a polopřímka iks bé se blíží úsečce á bé."):
            self.add(lv2)
            self.play(th.animate.set_value(185), run_time=4.5, rate_func=smooth)
            self.play(th.animate.set_value(208), run_time=2.0, rate_func=smooth)
        self.remove(lv2)
        tang = hline(A - tdir * 1.2, A + tdir * 1.2, ext=0.0, color=TEAL, width=3.4)
        Q = A + tdir * 1.2
        with self.say("V limitě, když iks splyne s á, se z přímky iks á stane tečna a z úhlu á iks bé úhel mezi tečnou a tětivou "
                      "á bé. Tomu se říká úsekový úhel. A protože se cestou úhel vůbec neměnil, má úsekový úhel taky šedesát stupňů."):
            self.draw(tang, run_time=0.8)
            self.draw(Pt(Q, "Q", DOWN, color=TEAL), run_time=0.3)
            self.draw(AngleMark(A, Q, B, 0.55, TEAL, label="60°", label_r=0.85, font_size=24), run_time=0.6)
            self.board.write("úsekový úhel = obvodový = α", indent=0.45)
        q = hline(A, S, ext=0.5, ext2=1.0, color=PURPLE, width=2.8)
        with self.say("A teď: poloměr es á je kolmý na tečnu. Takže když z á narýsuju polopřímku á kvé pod šedesáti stupni, "
                      "to je tečna, a v bodě á k ní vztyčím kolmici, střed es musí ležet na té kolmici. "
                      "A ta kolmice svírá s á bé právě devadesát minus šedesát, tedy třicet stupňů. Přesně to, co jsme odvodili."):
            self.draw(q, run_time=0.8)
            self.draw(RightMark(A, Q, S, r=0.25, color=PURPLE), run_time=0.4)
            self.draw(AngleMark(A, B, S, 0.9, PURPLE, label="30°", label_r=1.2, font_size=24), run_time=0.5)
            self.board.write("SA ⊥ tečna AQ  ⇒  S ∈ q,  q ⊥ AQ", indent=0.45)
            self.board.write("q svírá s AB  90° − α = 30°  ✓", indent=0.45)
        self.wait(0.5)

        # ---- konstrukce krok za krokem
        self.clear_body()
        self.board = Board(self, y=self.header_bottom - 0.5, dy=0.58)
        self.board.size = 29
        ab = self.ab()
        with self.say("Teď celá konstrukce podle postupu. Jedna: úsečka á bé, pět centimetrů."):
            self.draw(ab, run_time=0.8)
            self.board.write("1.  AB;  |AB| = 5 cm")
        o = hline(MID + DOWN * 0.1, MID + UP * 0.1, ext=2.6, ext2=2.6, color=GREEN, width=2.4)
        with self.say("Dva: osa ó úsečky á bé."):
            self.draw(o, Tx("o", 26, GREEN).move_to(MID + np.array([0.22, 2.45, 0])), run_time=0.8)
            self.board.write("2.  o;  o … osa úsečky AB")
        with self.say("Tři: polopřímka á kvé, která svírá s á bé šedesát stupňů. Kreslíme ji do dolní poloroviny, "
                      "bude to tečna."):
            self.draw(hseg(A, Q, color=TEAL, width=3), Pt(Q, "Q", DOWN, color=TEAL),
                      AngleMark(A, Q, B, 0.5, TEAL, label="60°", label_r=0.8, font_size=22), run_time=0.8)
            self.board.write("3.  ^{AQ};  |∢BAQ| = 60°   (tečna)")
        with self.say("Čtyři: kolmice kvé na á kvé v bodě á."):
            self.draw(hline(A, S, ext=0.5, ext2=0.6, color=PURPLE, width=2.6), RightMark(A, Q, S, r=0.22, color=PURPLE),
                      run_time=0.8)
            self.board.write("4.  q;  q ⊥ AQ,  A ∈ q")
        with self.say("Pět: střed es je průsečík kvé a osy ó. Šest: es s čárkou je obraz es v osové souměrnosti podle přímky á bé."):
            self.draw(Pt(S, "S", RIGHT, font_size=28), run_time=0.4)
            self.board.write("5.  S;  S ∈ q ∩ o")
            self.draw(Pt(S2, "S′", RIGHT, font_size=28), run_time=0.4)
            self.board.write("6.  S′;  S′ = O_{AB}(S)")
        with self.say("Sedm: kružnice ká se středem es a ká s čárkou se středem es s čárkou, obě procházejí body á a bé."):
            self.draw(hcircle(S, R, color=GRAY, width=2.0), hcircle(S2, R, color=GRAY, width=2.0), run_time=1.4)
            self.board.write("7.  k(S; |SA|),  k′(S′; |S′A|)")
        with self.say("A osm: hledaná množina jsou dva oblouky, horní oblouk kružnice ká a dolní oblouk kružnice ká s čárkou, "
                      "bez bodů á a bé. Proč dva? Kdo stojí pod úsečkou, vidí ji úplně stejně jako jeho zrcadlový obraz nad ní."):
            self.draw(upper_arc(S, R, width=6), lower_arc(S2, R, width=6), run_time=1.6)
            self.board.write("8.  U;  U = oblouk AB ⊂ k ∪ oblouk AB ⊂ k′")
            self.board.write("∖ {A, B}", indent=1.6)
            self.play(Create(Circle(radius=0.12, arc_center=A, color=RED, stroke_width=3)),
                      Create(Circle(radius=0.12, arc_center=B, color=RED, stroke_width=3)), run_time=0.5)

        # ---- proč žádné jiné body
        self.clear_body()
        self.play(FadeIn(self.ab()), FadeIn(hcircle(S, R, color=GRAY, width=2.2)), FadeIn(upper_arc(S, R, width=5)),
                  run_time=0.5)
        with self.say("Zbývá poslední otázka, kterou si málokdo položí: proč ze žádného jiného bodu není úsečka vidět pod "
                      "šedesáti stupni? Na oblouku šedesát stupňů je, to už víme. Ale co body mimo něj?"):
            self.board.write("Proč jen body oblouku?")
        self.think("Bod Y je uvnitř kružnice. Vidí AB pod větším, nebo menším úhlem? Proč?",
                   "Zkus si rozmyslet: bod ypsilon uvnitř kružnice vidí úsečku pod větším, nebo menším úhlem? A proč?", pause=6)
        Y = np.array([-3.35, 0.15, 0])
        uY = (Y - A) / np.linalg.norm(Y - A)
        fdir = np.dot(A - S, uY)
        tY = -fdir + np.sqrt(fdir * fdir - (np.dot(A - S, A - S) - R * R))
        XY = A + uY * tY
        with self.say("Vezmi bod ypsilon uvnitř kružnice a prodluž úsečku á ypsilon, až narazí na oblouk v bodě iks. "
                      "Úhel á ypsilon bé je vnějším úhlem trojúhelníku ypsilon iks bé. A vnější úhel je součet dvou vnitřních "
                      "nepřilehlých: šedesát stupňů u iks plus ještě úhel u bé. Je tedy větší než šedesát."):
            self.draw(Pt(Y, "Y", LEFT, color=PURPLE), hseg(A, XY, color=GRAY, width=2.2), Pt(XY, "X", UP, color=RED),
                      hseg(Y, B, color=PURPLE, width=2.6), hseg(XY, B, color=GRAY, width=2.2), run_time=1.2)
            self.play(FadeIn(hfill(Y, XY, B, PURPLE, 0.2)), run_time=0.4)
            self.draw(AngleMark(XY, A, B, 0.45, RED, label="60°", label_r=0.72, font_size=22),
                      AngleMark(Y, A, B, 0.45, PURPLE), run_time=0.7)
            self.board.write("Y uvnitř:  |∢AYB| = |∢AXB| + |∢XBY| > 60°", indent=0.45)
        Z = np.array([-2.0, 1.75, 0])
        uZ = (Z - A) / np.linalg.norm(Z - A)
        fz = np.dot(A - S, uZ)
        tZ = -fz + np.sqrt(fz * fz - (np.dot(A - S, A - S) - R * R))
        XZ = A + uZ * tZ
        with self.say("A bod zet venku: úsečka á zet protne oblouk v bodě iks. Teď je naopak šedesátistupňový úhel u iks vnějším "
                      "úhlem trojúhelníku iks zet bé, takže šedesát je úhel u zet plus ještě něco. Úhel u zet je tedy menší než šedesát."):
            self.draw(Pt(Z, "Z", UR, color=TEAL), hseg(A, Z, color=GRAY, width=2.2), Pt(XZ, "X", UL, color=RED),
                      hseg(Z, B, color=TEAL, width=2.6), hseg(XZ, B, color=GRAY, width=2.2), run_time=1.2)
            self.play(FadeIn(hfill(XZ, Z, B, TEAL, 0.2)), run_time=0.4)
            self.board.write("Z vně:  60° = |∢AXB| = |∢XZB| + |∢XBZ|", indent=0.45)
            self.board.write("⇒  |∢AZB| < 60°", indent=1.4)
        with self.say("Takže šedesát stupňů je přesně na oblouku, uvnitř víc, venku míň. Body pod úsečkou řeší zrcadlový oblouk "
                      "a body na přímce á bé vidí úsečku pod nulou nebo sto osmdesáti stupni. Množina je tedy přesně ty dva oblouky."):
            self.board.write("⇒  U jsou přesně dva oblouky", indent=0.45, color=RED)

        # ---- diskuse s živou ukázkou
        self.clear_body()
        al = ValueTracker(60)

        def live3():
            a = al.get_value()
            C1, r1 = center_for(a)
            C2, _ = center_for(a, below=True)
            g = VGroup(Line(A, B, color=INK, stroke_width=3.6), Dot(A, radius=0.06, color=INK), Dot(B, radius=0.06, color=INK),
                       Circle(radius=r1, arc_center=C1, color=GRAY, stroke_width=1.6),
                       Circle(radius=r1, arc_center=C2, color=GRAY, stroke_width=1.6),
                       upper_arc(C1, r1, mob=True, width=6),
                       Dot(C1, radius=0.05, color=PEN), Dot(C2, radius=0.05, color=PEN))
            a0 = dir_of(C2, A)
            d = (dir_of(C2, B) - a0) % (2 * PI)
            g.add(Arc(radius=r1, start_angle=a0, angle=d, arc_center=C2, color=RED, stroke_width=6))
            g.add(Text(f"α = {a:.0f}°", font=FONT, font_size=40, color=RED).move_to([3.3, 0.7, 0]))
            g.add(Text("větší oblouky" if a < 89.5 else ("Thaletova kružnice" if a < 90.5 else "menší oblouky"),
                       font=FONT, font_size=34, color=INK).move_to([3.3, -0.1, 0]))
            return g

        lv3 = always_redraw(live3)
        with self.say("Na závěr diskuse. Když měním úhel alfa, mění se oblouky. Pro alfa menší než devadesát jsou to větší oblouky "
                      "a střed leží na stejné straně jako oblouk. Pro alfa rovno devadesát dostaneme dvě polokružnice, dohromady "
                      "Thaletovu kružnici. A pro alfa větší než devadesát jsou to menší oblouky."):
            self.add(lv3)
            self.play(al.animate.set_value(40), run_time=2.0)
            self.play(al.animate.set_value(90), run_time=3.0)
            self.wait(1.0)
            self.play(al.animate.set_value(130), run_time=2.5)
            self.play(al.animate.set_value(60), run_time=2.0)
        with self.say("Osa a kolmice kvé jsou vždy různoběžné, takže střed es existuje vždy a jen jeden. Úloha má tedy vždy právě "
                      "jedno řešení, dvojici oblouků souměrnou podle přímky á bé, bez bodů á a bé."):
            self.wait(self.left())
        self.remove(lv3)

        fig = VGroup(self.ab(), hline(MID + DOWN * 0.1, MID + UP * 0.1, ext=2.6, ext2=2.6, color=GREEN, width=2.2),
                     hseg(A, Q, color=TEAL, width=2.6), Pt(Q, "Q", DOWN, color=TEAL),
                     AngleMark(A, Q, B, 0.5, TEAL, label="60°", label_r=0.8, font_size=22),
                     hline(A, S, ext=0.5, ext2=0.6, color=PURPLE, width=2.4), Pt(S, "S", RIGHT, font_size=26),
                     Pt(S2, "S′", RIGHT, font_size=26), hcircle(S, R, color=GRAY, width=1.8),
                     hcircle(S2, R, color=GRAY, width=1.8), upper_arc(S, R, width=5), lower_arc(S2, R, width=5))
        self.summary(fig, [
            "Rozbor: X ∈ U ⇒ ∢AXB je obvodový úhel nad AB (V 10.5)",
            "|∢ASB| = 2α,  S ∈ o,  |∢SAB| = 90° − α",
            "(tečna AQ: úsekový úhel = α,  SA ⊥ AQ)",
            "1. AB; |AB| = 5 cm      2. o; o … osa AB",
            "3. ^{AQ}; |∢BAQ| = 60°     4. q; q ⊥ AQ, A ∈ q",
            "5. S; S ∈ q ∩ o      6. S′; S′ = O_{AB}(S)",
            "7. k(S; |SA|), k′(S′; |S′A|)",
            "8. U = oblouk AB ⊂ k ∪ oblouk AB ⊂ k′ ∖ {A, B}",
            "Diskuse: vždy 1 řešení (dva oblouky); α = 90° Thaletova k."],
            "Shrnutí. Rozbor: bod množiny vidí á bé pod obvodovým úhlem, takže leží na oblouku kružnice, jejíž středový úhel nad "
            "á bé je dvakrát alfa. Střed leží na ose á bé a úsečka es á svírá s á bé devadesát minus alfa, což v postupu "
            "zařídíme tečnou á kvé pod úhlem alfa a kolmicí na ni. Druhý oblouk je souměrný podle á bé. Diskuse: vždy jedno řešení.",
            size=25, dy=0.52, fig_w=4.0, fig_h=5.2, x_text=-2.4,
            final="Zastav si video a zkus si konstrukci narýsovat a vysvětlit sám.")
