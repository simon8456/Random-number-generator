import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

A, B, C, D = (np.array([-6.4, -2.4, 0]), np.array([-2.8, -2.4, 0]),
              np.array([-1.0, 0.9, 0]), np.array([-4.6, 0.9, 0]))


class V85(ProofScene):
    CODE = "V 8.5"
    NAME = "Kdy je čtyřúhelník rovnoběžník"
    INDEX = 11
    SEED = 85

    def construct(self):
        self.intro(
            ["Nechť ABCD je konvexní čtyřúhelník, pak platí:",
             "1)  |AB| = |CD| ∧ AB ∥ CD  ⇔  ABCD je rovnoběžník",
             "2)  |AB| = |CD| ∧ |BC| = |DA|  ⇔  ABCD je rovnoběžník"],
            "Věta osm celá pět. Pro konvexní čtyřúhelník á bé cé dé platí dvě kritéria. Za prvé: "
            "jedna dvojice protějších stran je stejně dlouhá a rovnoběžná, právě když je to rovnoběžník. "
            "Za druhé: obě dvojice protějších stran jsou stejně dlouhé, právě když je to rovnoběžník.")

        q = hpoly(A, B, C, D)
        pts = VGroup(Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UR), Pt(D, "D", UL))
        diag = hseg(B, D, color=INK, width=3.4)
        with self.say("Začneme první částí, směrem tam. Víme, že á bé a cé dé jsou stejně dlouhé a rovnoběžné. "
                      "O stranách á dé a bé cé zatím nevíme nic. Chceme ukázat, že jsou také rovnoběžné."):
            self.draw(q, run_time=1.5)
            self.draw(pts, run_time=0.5)
            self.draw(VGroup(ticks(A, B, 1), ticks(D, C, 1)), run_time=0.6)
            self.hl((A, B), (D, C), color=RED, run_time=1.0)
            self.board.write("1)  a) „⇒“:  |AB| = |CD|  ∧  AB ∥ CD")
        f1, f2 = hfill(A, B, D, ORANGE, 0.2), hfill(C, D, B, TEAL, 0.2)
        phi1 = AngleMark(B, A, D, 0.7, RED, label="φ", label_r=1.0)
        phi2 = AngleMark(D, C, B, 0.7, RED, label="φ", label_r=1.0)
        with self.say("Zase vedeme úhlopříčku bé dé. Čtyřúhelník je konvexní, takže body á a cé leží na opačných "
                      "stranách úhlopříčky. Úhly á bé dé a cé dé bé jsou střídavé úhly u rovnoběžek á bé a cé dé, "
                      "a proto jsou shodné."):
            self.draw(diag, run_time=0.8)
            self.play(FadeIn(f1), FadeIn(f2), run_time=0.6)
            self.draw(phi1, phi2, run_time=1.0)
        with self.say("Trojúhelníky á bé dé a cé dé bé jsou tedy shodné podle es u es: strana á bé se rovná cé dé, "
                      "úhly fí jsou shodné a strana bé dé je společná."):
            self.board.write("△ABD ≅ △CDB (sus):", indent=0.95)
            self.board.write("|AB| = |CD|,   BD společná,", indent=1.45)
            self.board.write("|∢ABD| = |∢CDB|  (střídavé)", indent=1.45)
        om1 = AngleMark(D, A, B, 0.5, TEAL, label="ω", label_r=0.8, n=2)
        om2 = AngleMark(B, C, D, 0.5, TEAL, label="ω", label_r=0.8, n=2)
        with self.say("Ze shodnosti plyne, že i úhly á dé bé a cé bé dé jsou shodné. To jsou ale střídavé úhly "
                      "pro přímky á dé a bé cé s příčkou bé dé. A když jsou střídavé úhly shodné, přímky jsou rovnoběžné. "
                      "Takže á dé je rovnoběžná s bé cé a á bé cé dé je rovnoběžník."):
            self.draw(om1, om2, run_time=1.0)
            self.board.write("⇒  |∢ADB| = |∢CBD|", indent=0.95)
            self.board.write("⇒  AD ∥ BC  (střídavé úhly)", indent=0.95)
            self.board.write("⇒  ABCD je rovnoběžník", indent=0.95)
        with self.say("Směr zpátky je snadný. Když je á bé cé dé rovnoběžník, je á bé rovnoběžná s cé dé podle definice "
                      "a délka á bé se rovná délce cé dé podle předchozí věty osm celá tři."):
            self.board.write("b) „⇐“:  ABCD rovnoběžník  ⇒", indent=0.45, gap=0.1)
            self.board.write("AB ∥ CD (definice),  |AB| = |CD| (V 8.3)", indent=0.95)

        # část 2
        self.clear_body()
        q2 = VGroup(hpoly(A, B, C, D), pts.copy(), hseg(B, D, color=INK, width=3.4))
        tk = VGroup(ticks(A, B, 1), ticks(D, C, 1), ticks(A, D, 2), ticks(B, C, 2))
        with self.say("Druhá část, směr tam. Teď víme, že obě dvojice protějších stran jsou stejně dlouhé: "
                      "á bé se rovná cé dé a bé cé se rovná dé á."):
            self.play(FadeIn(q2), run_time=0.8)
            self.draw(tk, run_time=0.8)
            self.board.write("2)  a) „⇒“:  |AB| = |CD|  ∧  |BC| = |DA|")
        with self.say("Trojúhelníky á bé dé a cé dé bé mají všechny tři strany stejné: á bé a cé dé, á dé a cé bé, "
                      "a společnou stranu bé dé. Jsou tedy shodné podle věty es es es."):
            self.play(FadeIn(hfill(A, B, D, ORANGE, 0.2)), FadeIn(hfill(C, D, B, TEAL, 0.2)), run_time=0.6)
            self.board.write("△ABD ≅ △CDB (sss)", indent=0.95)
        with self.say("Ze shodnosti dostaneme dvě dvojice shodných úhlů. Úhel á bé dé se rovná úhlu cé dé bé "
                      "a úhel á dé bé se rovná úhlu cé bé dé."):
            self.draw(AngleMark(B, A, D, 0.7, RED, label="φ", label_r=1.0), AngleMark(D, C, B, 0.7, RED, label="φ", label_r=1.0),
                      run_time=0.8)
            self.draw(AngleMark(D, A, B, 0.5, TEAL, label="ω", label_r=0.8, n=2),
                      AngleMark(B, C, D, 0.5, TEAL, label="ω", label_r=0.8, n=2), run_time=0.8)
            self.board.write("⇒  |∢ABD| = |∢CDB|", indent=0.95)
            self.board.write("∧  |∢ADB| = |∢CBD|", indent=0.95)
        with self.say("To jsou v obou případech střídavé úhly, takže á bé je rovnoběžná s cé dé "
                      "a á dé je rovnoběžná s bé cé. Á bé cé dé je rovnoběžník."):
            self.board.write("⇒  AB ∥ CD  ∧  AD ∥ BC", indent=0.95)
            self.board.write("(střídavé úhly)", indent=1.45)
            self.board.write("⇒  ABCD je rovnoběžník", indent=0.95)
        with self.say("A směr zpátky plyne zase přímo z věty osm celá tři."):
            self.board.write("b) „⇐“:  plyne z V 8.3   ]", indent=0.45, gap=0.1)

        fig = VGroup(hpoly(A, B, C, D), hseg(B, D, color=INK), Pt(A, "A", DL), Pt(B, "B", DR), Pt(C, "C", UR),
                     Pt(D, "D", UL), ticks(A, B, 1), ticks(D, C, 1),
                     AngleMark(B, A, D, 0.7, RED), AngleMark(D, C, B, 0.7, RED),
                     AngleMark(D, A, B, 0.5, TEAL, n=2), AngleMark(B, C, D, 0.5, TEAL, n=2))
        self.summary(fig, [
            "[Dk.: 1) a) „⇒“: |AB| = |CD| ∧ AB ∥ CD:",
            "△ABD ≅ △CDB (sus)  ⇒  |∢ADB| = |∢DBC|",
            "⇒  AD ∥ BC  ⇒  ABCD je rovnoběžník",
            "b) „⇐“: ABCD rovnoběžník ⇒ |AB| = |CD| ∧ AB ∥ CD",
            "(definice a V 8.3)",
            "2) a) „⇒“: △ABD ≅ △CDB (sss) ⇒ shodné střídavé úhly",
            "⇒ AB ∥ CD ∧ AD ∥ BC;   b) „⇐“: V 8.3  ]"],
            "Shrnutí do písemky. Jedna, směr tam: trojúhelník á bé dé je shodný s cé dé bé podle es u es, "
            "proto úhel á dé bé se rovná úhlu dé bé cé, a tedy á dé je rovnoběžná s bé cé. "
            "Směr zpátky z definice a věty osm celá tři. Dva: trojúhelníky jsou shodné podle es es es, "
            "takže střídavé úhly jsou shodné a obě dvojice stran jsou rovnoběžné. Směr zpátky je věta osm celá tři.",
            size=27, dy=0.58)
