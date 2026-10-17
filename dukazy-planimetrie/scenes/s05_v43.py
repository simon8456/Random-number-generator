import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


class V43(ProofScene):
    CODE = "V 4.3"
    NAME = "Kolmice bodem, který neleží na přímce"
    INDEX = 5
    SEED = 43

    def construct(self):
        self.intro(
            ["Nechť p ∈ 𝒫 je přímka, P ∉ p bod. Pak existuje právě jedna přímka q",
             "taková, že  p ⊥ q ∧ P ∈ q."],
            "Věta čtyři celá tři. Teď bod pé na přímce pé neleží. I tak existuje právě jedna přímka kvé, "
            "která je kolmá na pé a prochází bodem pé. Zase máme dvě části: existenci a jednoznačnost.")

        y = -0.55
        P = np.array([-4.7, 1.6, 0])
        X = np.array([-2.0, y, 0])
        A = np.array([P[0], y, 0])
        Q = np.array([P[0], 2 * y - P[1], 0])
        Lp, Rp = np.array([-6.9, y, 0]), np.array([-0.5, y, 0])
        p = hseg(Lp, Rp)
        plab = label("p", Rp + np.array([-0.15, 0.3, 0]))
        pP, pX = Pt(P, "P", UL), Pt(X, "X", UR)
        with self.say("Nakreslíme přímku pé a bod pé mimo ni. Na přímce pé zvolíme libovolný bod iks."):
            self.draw(p, run_time=1.0)
            self.draw(plab, pP, run_time=0.5)
            self.draw(pX, run_time=0.5)
            self.board.write("1. existence:   Nechť X ∈ p.")
        PX = hseg(P, X, color=PEN)
        with self.say("Spojíme pé a iks. Pokud by přímka pé iks byla kolmá na pé, máme hotovo, kolmice existuje. "
                      "To je ten jednoduchý případ á."):
            self.draw(PX, run_time=1.0)
            self.board.write("a)  Je-li  PX ⊥ p, pak existuje.", indent=0.45)
        Aleft = np.array([-6.3, y, 0])
        ang = AngleMark(X, Aleft, P, 0.8, RED, label="", fill=True)
        with self.say("Zajímavější je případ bé, kdy pé iks na pé kolmá není. Pé iks pak svírá s přímkou pé "
                      "nějaký úhel, tady červeně. Tento úhel přeneseme do opačné poloroviny, pod přímku pé, "
                      "se stejným vrcholem iks."):
            self.board.write("b)  Je-li  PX ⊥̸ p:  přeneseme ∢PXA", indent=0.45)
            self.board.write("do opačné poloroviny s hranicí p", indent=0.95)
            self.board.write("a vrcholem X", indent=0.95)
            self.draw(ang, run_time=0.8)
            cp = ang.copy()
            self.add(cp)
            self.play(Rotate(cp, PI, axis=RIGHT, about_point=X), run_time=1.8)
            self.angle_low = cp
        Z = X + (Q - X) * 1.32
        XZ = hseg(X, Z, color=PEN)
        zlab = label("Z", Z + np.array([0.3, 0.05, 0]))
        rr = np.linalg.norm(P - X)
        compass = harc(X, rr, direction(X, P) + 0.12, direction(X, Q) % (2 * PI) - 0.12, color=GRAY, width=2.2)
        pQ = Pt(Q, "Q", LEFT)
        with self.say("Druhé rameno přeneseného úhlu je polopřímka iks zet. Na ní sestrojíme bod kvé tak, "
                      "aby vzdálenost iks kvé byla stejná jako iks pé. Kružítkem tedy přeneseme délku úsečky iks pé."):
            self.draw(XZ, zlab, run_time=1.0)
            self.draw(compass, run_time=1.5)
            self.draw(pQ, run_time=0.4)
            self.board.write("Q ∈ ^{XZ}:  |XP| = |XQ|", indent=0.95)
        PQ = hseg(P, Q, color=INK, width=3.4)
        pA = Pt(A, "A", UL)
        with self.say("Body pé a kvé leží v opačných polorovinách, takže úsečka pé kvé protne přímku pé. "
                      "Průsečík označíme á."):
            self.draw(PQ, run_time=1.0)
            self.draw(pA, run_time=0.5)
            self.board.write("A ∈ PQ ∩ p", indent=0.95)

        t1 = hfill(X, A, P, color=ORANGE, opacity=0.25)
        t2 = hfill(X, A, Q, color=TEAL, opacity=0.25)
        tk = VGroup(ticks(X, P, 1), ticks(X, Q, 1))
        with self.say("Teď porovnáme trojúhelníky iks á pé a iks á kvé. Jsou shodné podle věty es u es. "
                      "Strana iks á je společná. Úhly u vrcholu iks jsou stejné, to jsme tak sestrojili. "
                      "A strany iks pé a iks kvé jsou stejně dlouhé, to jsme taky sestrojili."):
            self.play(FadeIn(t1), FadeIn(t2), run_time=0.8)
            self.board.write("△XAP ≅ △XAQ (sus):", indent=0.95)
            self.board.write("XA … společná strana,", indent=1.45)
            self.hl((X, A), color=RED, run_time=0.8)
            self.board.write("|∢AXP| = |∢AXQ|  (konstrukce),", indent=1.45)
            self.board.write("|XP| = |XQ|  (konstrukce)", indent=1.45)
            self.draw(tk, run_time=0.6)
        aP = AngleMark(A, X, P, 0.45, PURPLE)
        aQ = AngleMark(A, X, Q, 0.45, PURPLE)
        with self.say("Ze shodnosti plyne, že i úhly u vrcholu á jsou stejně velké. Úhel iks á pé se rovná "
                      "úhlu iks á kvé. Na obrázku to vidíš, když trojúhelník překlopíme přes přímku pé."):
            cp = VGroup(t1.copy(), hpoly(X, A, P, color=ORANGE))
            self.play(Rotate(cp, PI, axis=RIGHT, about_point=X), run_time=1.6)
            self.play(FadeOut(cp), run_time=0.4)
            self.draw(aP, aQ, run_time=0.8)
            self.board.write("⇒  |∢XAP| = |∢XAQ|", indent=0.95)
        rm = RightMark(A, X, P, r=0.45)
        with self.say("Ale úhel pé á kvé je přímý, protože pé, á, kvé leží na jedné přímce. "
                      "Dva stejné úhly, které dohromady dají sto osmdesát stupňů, musí mít každý devadesát stupňů. "
                      "Takže pé á je kolmá na pé a kolmice existuje."):
            self.play(Indicate(PQ, color=RED), run_time=0.9)
            self.board.write("∢PAQ přímý  ⇒  |∢XAP| = 90°", indent=0.95)
            self.board.write("⇒  PA ⊥ p", indent=0.95)
            self.play(FadeOut(aP), FadeOut(aQ), FadeIn(rm), run_time=0.6)

        # jednoznačnost
        self.clear_body()
        P2 = np.array([-3.7, 1.4, 0])
        y2 = -1.8
        Q1, Q2 = np.array([-3.7, y2, 0]), np.array([-2.0, y2, 0])
        g = VGroup(hseg([-6.9, y2, 0], [-0.5, y2, 0]), label("p", [-0.65, y2 + 0.3, 0]), Pt(P2, "P", UP))
        q1, q2 = hline(P2, Q1, ext=0.1, ext2=0.6, color=INK), hline(P2, Q2, ext=0.1, ext2=0.6, color=ORANGE)
        pq1, pq2 = Pt(Q1, "Q₁", DL), Pt(Q2, "Q₂", DR)
        with self.say("Druhá část, jednoznačnost, zase sporem. Předpokládejme, že bodem pé vedou dvě různé kolmice "
                      "na přímku pé, kvé jedna a kvé dva."):
            self.draw(g, run_time=1.0)
            self.draw(q1, q2, run_time=1.2)
            self.board.write("2. jednoznačnost:  sporem")
            self.board.write("Nechť ∃ q₁, q₂ ∈ 𝒫:  q₁ ⊥ p,  q₂ ⊥ p,", indent=0.45)
            self.board.write("P ∈ q₁,  P ∈ q₂,  q₁ ≠ q₂", indent=0.95)
        r1, r2 = RightMark(Q1, Q2, P2), RightMark(Q2, Q1, P2)
        with self.say("Průsečíky kolmic s přímkou pé označíme kvé jedna a kvé dva. Body pé, kvé jedna, kvé dva tvoří "
                      "trojúhelník, a ten by měl u vrcholů kvé jedna i kvé dva pravý úhel."):
            self.draw(pq1, pq2, run_time=0.6)
            self.play(FadeIn(hfill(P2, Q1, Q2, color=RED, opacity=0.15)), run_time=0.6)
            self.draw(r1, r2, run_time=0.8)
            self.board.write("Označme  Q₁ = q₁ ∩ p,  Q₂ = q₂ ∩ p", indent=0.45)
            self.board.write("⇒  ∃ △PQ₁Q₂,  v němž jsou dva pravé úhly", indent=0.45)
        with self.say("Dva pravé úhly mají dohromady už sto osmdesát stupňů a na třetí úhel nic nezbude. "
                      "To je spor s větou, že součet vnitřních úhlů v trojúhelníku je sto osmdesát stupňů. "
                      "Kolmice je tedy jen jedna."):
            self.board.write("— spor se součtem úhlů v △ (180°)  ]", indent=0.45, color=RED)

        fig = VGroup(hseg(Lp, Rp), label("p", Rp + np.array([-0.15, 0.3, 0])), Pt(P, "P", UL), Pt(X, "X", UR),
                     hseg(P, X), hseg(X, Z), label("Z", Z + np.array([0.3, 0.05, 0])), Pt(Q, "Q", LEFT),
                     hseg(P, Q, color=INK), Pt(A, "A", UL), RightMark(A, X, P, r=0.45),
                     AngleMark(X, Aleft, P, 0.8, RED), AngleMark(X, Aleft, Q, 0.8, RED),
                     ticks(X, P, 1), ticks(X, Q, 1))
        self.summary(fig, [
            "[Dk.:  1. existence:  Nechť X ∈ p.   a) PX ⊥ p  ⇒  existuje.",
            "b) PX ⊥̸ p:  přeneseme ∢PXA do opačné poloroviny s hranicí p",
            "a vrcholem X;   Q ∈ ^{XZ}:  |XP| = |XQ|,   A ∈ PQ ∩ p",
            "△XAP ≅ △XAQ (sus):  XA společná,  |∢AXP| = |∢AXQ|,",
            "|XP| = |XQ|  (podle konstrukce)",
            "⇒  |∢XAP| = |∢XAQ|,  ∢PAQ přímý  ⇒  |∢XAP| = 90°  ⇒  PA ⊥ p",
            "2. jednoznačnost: sporem –  Nechť ∃ q₁, q₂ ∈ 𝒫:  q₁ ⊥ p,  q₂ ⊥ p,",
            "P ∈ q₁,  P ∈ q₂,  q₁ ≠ q₂.   Označme  Q₁ = q₁ ∩ p,  Q₂ = q₂ ∩ p",
            "⇒  ∃ △PQ₁Q₂ se dvěma pravými úhly – spor se součtem úhlů v △  ]"],
            "Shrnutí do písemky. Existence: zvolíme bod iks na pé. Je-li pé iks kolmá, je hotovo. Jinak přeneseme "
            "úhel pé iks á do opačné poloroviny, na nové rameno naneseme bod kvé, aby iks pé se rovnalo iks kvé, "
            "a průsečík pé kvé s přímkou pé je á. Trojúhelníky iks á pé a iks á kvé jsou shodné podle es u es, "
            "takže úhly u á jsou shodné, dohromady přímý úhel, tedy každý devadesát stupňů. "
            "Jednoznačnost sporem: dvě kolmice by daly trojúhelník se dvěma pravými úhly, a to nejde.",
            size=26, dy=0.54, fig_w=3.3, fig_h=5.0, x_text=-3.2)
