import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


class V51(ProofScene):
    CODE = "V 5.1"
    NAME = "Vedlejší úhly"
    INDEX = 2
    SEED = 51

    def construct(self):
        self.intro(
            ["Součet každých dvou vedlejších úhlů je 180°."],
            "Věta pět celá jedna. Součet každých dvou vedlejších úhlů je sto osmdesát stupňů.")

        y = -1.4
        A, V, C = np.array([-6.5, y, 0]), np.array([-3.7, y, 0]), np.array([-0.9, y, 0])
        B = V + 3.0 * np.array([np.cos(np.radians(62)), np.sin(np.radians(62)), 0])
        line = hseg(A + LEFT * 0.3, C + RIGHT * 0.3)
        rayB = hseg(V, B)
        pA, pV, pC, pB = Pt(A, "A", DOWN), Pt(V, "V", DOWN), Pt(C, "C", DOWN), Pt(B, "B", UR)
        al = AngleMark(V, A, B, 0.85, RED, label="α", label_r=1.15)
        be = AngleMark(V, B, C, 0.85, GREEN, label="β", label_r=1.15)
        with self.say("Nejdřív si připomeňme, co jsou vedlejší úhly. Jsou to dva úhly, které mají jedno rameno společné "
                      "a jejich zbývající ramena jsou opačné polopřímky. Na obrázku je společné rameno vé bé, "
                      "a ramena vé á a vé cé jsou opačné polopřímky, leží na jedné přímce."):
            self.draw(line, run_time=1.2)
            self.draw(pA, pV, pC, run_time=0.6)
            self.draw(rayB, pB, run_time=1.0)
            self.draw(al, run_time=0.8)
            self.draw(be, run_time=0.8)
            self.play(Indicate(rayB, color=ORANGE), run_time=1.0)

        half = AngleMark(V, C, A, 1.6, ORANGE, fill_opacity=0.12, ccw=True)
        with self.say("Vedlejší úhly dohromady vyplní celou polorovinu, tedy přímý úhel á vé cé. "
                      "Polopřímka vé bé prochází mezi rameny tohoto úhlu."):
            self.draw(half, run_time=1.5)
            self.board.write("[Dk.:  ^{VB} prochází mezi rameny ∢AVC")
        with self.say("Z vlastností velikosti úhlu víme: když polopřímka prochází mezi rameny úhlu, "
                      "rozdělí ho na dva úhly a jejich velikosti se sečtou na velikost celého úhlu. "
                      "Takže velikost úhlu á vé bé plus velikost úhlu bé vé cé se rovná velikosti úhlu á vé cé."):
            self.blink(al, be, run_time=1.2)
            self.board.write("⇒  |∢AVB| + |∢BVC| = |∢AVC|")
        with self.say("Jenže úhel á vé cé je přímý, protože jeho ramena jsou opačné polopřímky. "
                      "A přímý úhel má velikost sto osmdesát stupňů."):
            self.play(Indicate(line, color=RED), run_time=1.0)
            self.board.write("∢AVC je přímý  ⇒  |∢AVC| = 180°")
        with self.say("Dosadíme a máme výsledek: součet velikostí vedlejších úhlů je sto osmdesát stupňů."):
            r = self.board.write("⇒  |∢AVB| + |∢BVC| = 180°  ]")
            self.play(Create(hbox(r)), run_time=0.8)

        fig = VGroup(hseg(A + LEFT * 0.3, C + RIGHT * 0.3), hseg(V, B), Pt(A, "A", DOWN), Pt(V, "V", DOWN),
                     Pt(C, "C", DOWN), Pt(B, "B", UR), AngleMark(V, A, B, 0.85, RED, label="α", label_r=1.15),
                     AngleMark(V, B, C, 0.85, GREEN, label="β", label_r=1.15))
        self.summary(fig, [
            "[Dk.:  ^{VB} prochází mezi rameny ∢AVC",
            "⇒  |∢AVB| + |∢BVC| = |∢AVC|",
            "∢AVC – přímý  ⇒  |∢AVC| = 180°",
            "⇒  |∢AVB| + |∢BVC| = 180°  ]"],
            "Shrnutí do písemky: polopřímka vé bé prochází mezi rameny úhlu á vé cé, proto velikost úhlu á vé bé "
            "plus velikost úhlu bé vé cé je velikost úhlu á vé cé. Úhel á vé cé je přímý, má tedy sto osmdesát stupňů.")
