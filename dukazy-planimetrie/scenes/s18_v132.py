import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

Sc = np.array([-4.5, -1.2, 0])
R = 1.9
M = np.array([-0.8, -1.2, 0])
dd = np.linalg.norm(M - Sc)
th = np.arccos(R / dd)
T = Sc + R * np.array([np.cos(th), np.sin(th), 0])
A, B = Sc + LEFT * R, Sc + RIGHT * R


class V132(ProofScene):
    CODE = "V 13.2"
    NAME = "Mocnost bodu a tečna"
    INDEX = 18
    SEED = 132

    def construct(self):
        self.intro(
            ["Nechť k(S, r) je kružnice, M bod ležící ve vnější oblasti k, t tečna procházející",
             "bodem M ke kružnici k s dotykovým bodem T. Pak platí:  m_{M} = |MT|²."],
            "Věta třináct celá dva. Mějme bod em vně kružnice a tečnu z bodu em, která se kružnice dotýká v bodě té. "
            "Pak mocnost bodu em ke kružnici je rovna em té na druhou.")

        k = hcircle(Sc, R)
        pS, pM, pT = Pt(Sc, "S", DOWN), Pt(M, "M", DR), Pt(T, "T", UP)
        t = hline(M, T, ext=0.4, ext2=1.6, color=INK)
        tl = label("t", T + (T - M) / np.linalg.norm(T - M) * 1.4 + UP * 0.3, INK)
        with self.say("Připomeňme, co je mocnost bodu. Pro bod em vně kružnice vedeme libovolnou sečnu, "
                      "ta protne kružnici v bodech á a bé, a mocnost je součin em á krát em bé. "
                      "Podle předchozí věty třináct celá jedna nezáleží na tom, jakou sečnu zvolíme, součin vyjde pořád stejně."):
            self.draw(k, pS, run_time=1.2)
            self.draw(pM, run_time=0.4)
            self.wait(max(0.1, self.left() - 1.5))
            self.board.write("m_{M} = |MA| · |MB|   (pro libovolnou sečnu)", color=GRAY, size=28)
        with self.say("Tečna je přímka, která se kružnice dotýká v bodě té a je kolmá na poloměr es té."):
            self.draw(t, tl, run_time=1.0)
            self.draw(pT, run_time=0.4)
            self.draw(hseg(Sc, T, color=ORANGE), RightMark(T, Sc, M, r=0.3), run_time=0.8)
        s = hseg(M + RIGHT * 0.3, A + LEFT * 0.5, color=PEN)
        pA, pB = Pt(A, "A", DL), Pt(B, "B", DOWN + RIGHT * 0.3)
        with self.say("Trik důkazu: protože si sečnu můžeme vybrat, zvolíme tu nejšikovnější, sečnu es, která prochází "
                      "středem es. Protne kružnici v bodech á a bé."):
            self.draw(s, run_time=1.0)
            self.draw(pA, pB, run_time=0.5)
            self.board.write("[Dk.:  Nechť s je sečna taková, že S ∈ s;", gap=0.1)
            self.board.write("s ∩ k = {A, B}", indent=0.95)
        dl = Tx("d", 30, PURPLE).move_to((M + Sc) / 2 + DOWN * 0.95)
        dline = hseg(M + DOWN * 0.7, Sc + DOWN * 0.7, color=PURPLE, width=2.4)
        with self.say("Vzdálenost em es označíme dé. V sešitě je to označené písmenem es. Pak em á je dé plus er, "
                      "protože jdeme až za střed, a em bé je dé minus er."):
            self.draw(dline, dl, run_time=0.8)
            self.board.write("označme  d = |MS|:", indent=0.95)
            self.board.write("|MA| = d + r,   |MB| = d − r", indent=0.95)
        with self.say("Takže mocnost em á krát em bé je dé plus er krát dé minus er, a to je podle vzorce "
                      "dé na druhou minus er na druhou."):
            self.board.write("m_{M} = |MA| · |MB| = (d + r)(d − r)", indent=0.95)
            self.board.write("= d² − r²", indent=1.45)
        f = hfill(M, T, Sc, TEAL, 0.22)
        with self.say("Teď se podíváme na trojúhelník em té es. Má pravý úhel u vrcholu té, protože tečna je kolmá na poloměr. "
                      "Přepona je em es o délce dé, odvěsny jsou em té a es té o délce er. Podle Pythagorovy věty je dé na druhou "
                      "rovno em té na druhou plus er na druhou."):
            self.play(FadeIn(f), run_time=0.6)
            self.draw(hseg(M, Sc, color=PURPLE, width=4), run_time=0.6)
            self.board.write("△MTS pravoúhlý (ST ⊥ t)", indent=0.95)
            self.board.write("⇒  d² = |MT|² + r²", indent=0.95)
        with self.say("Odtud dé na druhou minus er na druhou je em té na druhou. A to je přesně mocnost. Hotovo."):
            r = self.board.write("⇒  m_{M} = d² − r² = |MT|²   ]", indent=0.95)
            self.play(Create(hbox(r)), run_time=0.7)

        fig = VGroup(hcircle(Sc, R), Pt(Sc, "S", DOWN), Pt(M, "M", DR), Pt(T, "T", UP),
                     hline(M, T, ext=0.4, ext2=1.6, color=INK), hseg(Sc, T, color=ORANGE), RightMark(T, Sc, M, r=0.3),
                     hseg(M + RIGHT * 0.3, A + LEFT * 0.5), Pt(A, "A", DL), Pt(B, "B", DOWN + RIGHT * 0.3),
                     hfill(M, T, Sc, TEAL, 0.22), label("r", (Sc + T) / 2 + LEFT * 0.25 + UP * 0.1, ORANGE))
        self.summary(fig, [
            "[Dk.:  Nechť s je sečna taková, že S ∈ s;  s ∩ k = {A, B}",
            "m_{M} = |MA| · |MB| = (d + r)(d − r) = d² − r² =",
            "= |MT|²",
            "(⇐  △MTS je pravoúhlý trojúhelník, d = |MS|)  ]"],
            "Shrnutí do písemky: zvolíme sečnu es procházející středem, která protne kružnici v á a bé. "
            "Mocnost je em á krát em bé, to je dé plus er krát dé minus er, tedy dé na druhou minus er na druhou, "
            "a to je em té na druhou, protože trojúhelník em té es je pravoúhlý.",
            size=27, x_text=-1.2)
