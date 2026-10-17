import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


class V42(ProofScene):
    CODE = "V 4.2"
    NAME = "Kolmice bodem ležícím na přímce"
    INDEX = 1
    SEED = 42

    def construct(self):
        self.intro(
            ["Nechť p ∈ 𝒫 je přímka, P ∈ p bod. Pak existuje právě jedna přímka q",
             "taková, že  p ⊥ q ∧ P ∈ q."],
            "Věta čtyři celá dva. Mějme přímku pé a bod velké pé, který na ní leží. "
            "Pak existuje právě jedna přímka kvé, která je kolmá na přímku pé a prochází bodem pé.")

        y = -1.6
        P = np.array([-3.9, y, 0])
        X = np.array([-1.2, y, 0])
        p = hseg([-6.9, y, 0], [-0.5, y, 0], color=PEN)
        plab = label("p", [-6.6, y + 0.3, 0])
        pP = Pt(P, "P", DL)
        pX = Pt(X, "X", DOWN)
        with self.say("Nakreslíme si přímku pé a na ní bod pé. Slova právě jedna v matematice znamenají dvě věci. "
                      "Za prvé, že taková přímka existuje, tedy že je aspoň jedna. "
                      "A za druhé, že je jen jedna, tomu říkáme jednoznačnost. Proto má důkaz dvě části."):
            self.draw(p, run_time=1.2)
            self.draw(plab, pP, run_time=0.6)
            self.wait(1.5)
            t1 = self.board.write("1. existence")
            self.wait(1.0)
            t2 = self.board.make("2. jednoznačnost", gap=0.0)
            self.write(t2)
        self.play(FadeOut(t2), run_time=0.4)
        self.board.lines.remove(t2)
        self.board.y = t1.axis_y - self.board.dy

        # existence – otáčející se polopřímka
        th = ValueTracker(0.35)
        R = 3.0

        def ray():
            a = th.get_value()
            return Line(P, P + R * np.array([np.cos(a), np.sin(a), 0]), color=INK, stroke_width=3.2)

        def arc():
            a = th.get_value()
            return Arc(radius=0.55, start_angle=0, angle=a, arc_center=P, color=RED, stroke_width=3)

        def val():
            a = th.get_value()
            t = Text(f"{round(np.degrees(a))}°", font=FONT, font_size=30, color=RED)
            return t.move_to(P + 0.95 * np.array([np.cos(a / 2), np.sin(a / 2), 0]))

        r_m, a_m, v_m = always_redraw(ray), always_redraw(arc), always_redraw(val)
        with self.say("Nejdřív existence. Vezmeme na přímce pé ještě jeden bod iks, takže máme polopřímku pé iks. "
                      "Z polopřímky pé iks můžeme otáčet druhé rameno úhlu a velikost úhlu se plynule mění. "
                      "Podle definice velikosti úhlu ke každému číslu mezi nula a sto osmdesáti stupni existuje "
                      "polopřímka, která s pé iks svírá přesně tento úhel. Tedy i úhel devadesát stupňů."):
            self.draw(pX, run_time=0.5)
            self.add(r_m, a_m, v_m)
            self.play(th.animate.set_value(2.4), run_time=3.0)
            self.play(th.animate.set_value(PI / 2), run_time=2.0)
            self.wait(max(0.1, self.left() - 0.2))
        q = hline(P + DOWN * 0.01, P + UP * 3.6, ext=1.5, ext2=0.0, color=INK, width=3.4)
        qlab = label("q", P + np.array([0.3, 3.4, 0]), INK)
        rm = RightMark(P, X, P + UP)
        Q = P + UP * 2.2
        pQ = Pt(Q, "Q", LEFT)
        with self.say("Polopřímka svírající s pé iks devadesát stupňů leží na přímce kvé, a ta je kolmá na pé. "
                      "Existence tedy plyne přímo z definice velikosti úhlu."):
            self.play(FadeOut(a_m), FadeOut(v_m), run_time=0.4)
            self.remove(r_m)
            self.draw(q, run_time=1.2)
            self.draw(rm, qlab, pQ, run_time=0.8)
            self.board.write("plyne z definice velikosti úhlu", indent=0.45)
            self.board.write("(∃ ^{PQ}:  |∢XPQ| = 90°)", indent=0.45)

        # jednoznačnost
        Q2 = P + 2.3 * np.array([np.cos(np.radians(68)), np.sin(np.radians(68)), 0])
        q2 = hline(P, Q2, ext=1.4, ext2=1.0, color=ORANGE, width=3.4)
        pQ2 = Pt(Q2, "Q₂", RIGHT, color=ORANGE)
        q1lab = label("q₁", P + np.array([-0.35, 3.4, 0]), INK)
        with self.say("Teď jednoznačnost. Tu dokážeme sporem. Důkaz sporem funguje takhle: předpokládáme opak toho, "
                      "co chceme dokázat, a ukážeme, že to vede k nesmyslu."):
            self.board.write("2. jednoznačnost:  sporem", gap=0.15)
        with self.say("Předpokládejme tedy, že bodem pé procházejí dvě různé kolmice na pé. Označíme je kvé jedna a kvé dva."):
            self.play(ReplacementTransform(qlab, q1lab), run_time=0.5)
            self.draw(q2, run_time=1.2)
            self.board.write("Nechť ∃ q₁, q₂ ∈ 𝒫:  q₁ ⊥ p,  q₂ ⊥ p,")
            self.board.write("P ∈ q₁,  P ∈ q₂,  q₁ ≠ q₂", indent=0.45)
        a1 = AngleMark(P, X, Q, 0.75, INK, label="", fill=True)
        a2 = AngleMark(P, X, Q2, 1.15, ORANGE, label="", fill=True, fill_opacity=0.15)
        Q1lab = label("Q₁", Q + np.array([-0.35, 0.0, 0]), INK)
        with self.say("Na obou kolmicích zvolíme body kvé jedna a kvé dva ve stejné polorovině, nad přímkou pé. "
                      "Protože jsou přímky různé, jsou různé i polopřímky pé kvé jedna a pé kvé dva, a proto "
                      "svírají s polopřímkou pé iks různě velké úhly."):
            self.play(ReplacementTransform(pQ.label, Q1lab), run_time=0.5)
            self.draw(pQ2, run_time=0.5)
            self.draw(a1, a2, run_time=1.2)
            self.board.write("⇒ |∢XPQ₁| ≠ |∢XPQ₂|")
        with self.say("Jenže když je jeden z těch úhlů devadesát stupňů, ten druhý devadesát stupňů mít nemůže. "
                      "Přímka kvé dva by tedy nebyla kolmá na pé. To je spor s předpokladem. "
                      "Kolmice je proto jen jedna."):
            self.board.write("⇒ jestliže |∢XPQ₁| = 90°, pak |∢XPQ₂| ≠ 90°")
            cross = VGroup(Line(Q2 + UL * 0.25, Q2 + DR * 0.25), Line(Q2 + UR * 0.25, Q2 + DL * 0.25)).set_color(RED)
            sp = self.board.write("— spor  ]", indent=0.45, color=RED)
            self.play(Create(cross), run_time=0.6)

        fig = VGroup(hseg([-6.9, y, 0], [-0.5, y, 0]), label("p", [-6.6, y + 0.3, 0]),
                     Pt(P, "P", DL), Pt(X, "X", DOWN), hline(P, P + UP * 3.0, ext=1.0, ext2=0.0, color=INK),
                     RightMark(P, X, P + UP), Pt(Q, "Q₁", LEFT), label("q₁", P + np.array([-0.35, 3.0, 0]), INK),
                     hline(P, Q2, ext=1.2, ext2=0.6, color=ORANGE), Pt(Q2, "Q₂", RIGHT, color=ORANGE),
                     AngleMark(P, X, Q2, 1.15, ORANGE, fill=True, fill_opacity=0.15))
        self.summary(fig, [
            "[Dk.:  1. existence: plyne z definice velikosti úhlu",
            "2. jednoznačnost: sporem –",
            "Nechť ∃ q₁, q₂ ∈ 𝒫:  q₁ ⊥ p,  q₂ ⊥ p,",
            "P ∈ q₁,  P ∈ q₂,  q₁ ≠ q₂",
            "⇒  |∢XPQ₁| ≠ |∢XPQ₂|",
            "⇒ jestliže |∢XPQ₁| = 90°, pak |∢XPQ₂| ≠ 90°",
            "— spor  ]"],
            "Shrnutí do písemky. Jedna: existence plyne z definice velikosti úhlu. "
            "Dva: jednoznačnost sporem. Nechť existují dvě různé přímky kvé jedna a kvé dva, obě kolmé na pé "
            "a obě procházející bodem pé. Pak úhly iks pé kvé jedna a iks pé kvé dva jsou různě velké. "
            "Jestliže je první devadesát stupňů, druhý devadesát stupňů není, a to je spor.")
