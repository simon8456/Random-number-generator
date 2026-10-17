import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


def chord(c, r, M, u):
    """Průsečíky přímky M + t·u s kružnicí (c, r); vrací (t_min bod, t_max bod)."""
    u = u / np.linalg.norm(u)
    f = M - c
    b = np.dot(f, u)
    disc = b * b - (np.dot(f, f) - r * r)
    t1, t2 = -b - np.sqrt(disc), -b + np.sqrt(disc)
    return M + t1 * u, M + t2 * u


def unit(v):
    return v / np.linalg.norm(v)


class V131(ProofScene):
    CODE = "V 13.1"
    NAME = "Mocnost bodu ke kružnici"
    INDEX = 17
    SEED = 131

    def config_out(self):
        c, r = np.array([-4.6, -0.7, 0]), 2.0
        M = np.array([-0.7, -1.1, 0])
        B, A = chord(c, r, M, (c + np.array([0, 1.15, 0])) - M)
        D, C = chord(c, r, M, (c + np.array([0, -1.05, 0])) - M)
        return c, r, M, A, B, C, D

    def config_in(self):
        c, r = np.array([-3.8, -0.75, 0]), 2.3
        M = c + np.array([0.35, -0.35, 0])
        B, A = chord(c, r, M, np.array([np.cos(np.radians(115)), np.sin(np.radians(115)), 0]))
        C, D = chord(c, r, M, np.array([np.cos(np.radians(20)), np.sin(np.radians(20)), 0]))
        return c, r, M, A, B, C, D

    def fig(self, cfg, inside):
        c, r, M, A, B, C, D = cfg
        g = VGroup(hcircle(c, r), Pt(c, "S", LEFT if inside else DOWN, font_size=26, radius=0.04))
        if inside:
            g.add(hseg(A, B, color=PEN), hseg(C, D, color=PEN))
            dirs = {"A": UL, "B": DR, "C": DL, "D": UR}
        else:
            g.add(hseg(M, A + (A - M) * 0.12 / np.linalg.norm(A - M), color=PEN),
                  hseg(M, C + (C - M) * 0.12 / np.linalg.norm(C - M), color=PEN))
            dirs = {"A": UL, "B": UP, "C": DL, "D": DOWN}
        for n, Pp in zip("ABCD", (A, B, C, D)):
            g.add(Pt(Pp, n, dirs[n]))
        g.add(Pt(M, "M", RIGHT if not inside else DOWN + RIGHT * 0.3))
        return g

    def construct(self):
        self.intro(
            ["Nechť k(S, r) je kružnice, M ∉ k bod, s₁, s₂ dvě sečny kružnice k procházející bodem M,",
             "s₁ ∩ k = {A, B},  s₂ ∩ k = {C, D}.  Pak platí:  |MA| · |MB| = |MC| · |MD|."],
            "Věta třináct celá jedna. Bodem em, který neleží na kružnici, vedeme dvě sečny. První protne kružnici "
            "v bodech á a bé, druhá v bodech cé a dé. Pak em á krát em bé se rovná em cé krát em dé. "
            "Součin vzdáleností tedy nezávisí na tom, jakou sečnu zvolíme.")

        # ---- a) vně
        cfg = self.config_out()
        c, r, M, A, B, C, D = cfg
        g = self.fig(cfg, False)
        with self.say("Rozlišíme dva případy. Případ á: bod em leží ve vnější oblasti kružnice. "
                      "Obě sečny vycházejí z em, bližší průsečíky jsou bé a dé, vzdálenější á a cé."):
            self.draw(g[0], g[1], run_time=1.2)
            self.draw(g[2], g[3], run_time=1.0)
            self.draw(*g[4:], run_time=0.8)
            self.board.write("a)  M leží ve vnější oblasti k:")
        AD, CB = hseg(A, D, color=ORANGE), hseg(C, B, color=TEAL)
        f1, f2 = hfill(M, A, D, ORANGE, 0.18), hfill(M, C, B, TEAL, 0.18)
        with self.say("Spojíme á s dé a cé s bé. Vzniknou dva trojúhelníky: em á dé a em cé bé. Ukážeme, že jsou podobné."):
            self.draw(AD, CB, run_time=1.0)
            self.play(FadeIn(f1), FadeIn(f2), run_time=0.6)
        al = AngleMark(A, M, D, 0.55, RED, label="α", label_r=0.82)
        ga = AngleMark(C, B, M, 0.55, RED, label="γ", label_r=0.82)
        arc = harc(c, r, direction(c, D), direction(c, B), color=PURPLE, width=6)
        with self.say("Úhel alfa u vrcholu á a úhel gama u vrcholu cé jsou obvodové úhly příslušné ke stejnému oblouku "
                      "bé dé. Podle předchozí věty jsou oba polovinou téhož středového úhlu, takže jsou shodné."):
            self.draw(al, ga, run_time=1.0)
            self.draw(arc, run_time=0.8)
            self.board.write("α = γ   (obvodové úhly k oblouku @{BD})", indent=0.45)
        aM = AngleMark(M, A, C, 0.7, GREEN)
        with self.say("A úhel u vrcholu em mají oba trojúhelníky společný. Shodují se ve dvou úhlech, "
                      "takže jsou podobné podle věty u u."):
            self.draw(aM, run_time=0.7)
            self.board.write("∢AMD = ∢CMB   (společný úhel)", indent=0.45)
            self.board.write("⇒  △MAD ∼ △MCB   (uu)", indent=0.45)
        bis = unit(A - M) + unit(C - M)
        k = np.linalg.norm(A - M) / np.linalg.norm(C - M)
        with self.say("Odpovídají si vrcholy em a em, á a cé, dé a bé. Když trojúhelník em cé bé překlopíme podle osy "
                      "úhlu u em a zvětšíme, přesně padne na trojúhelník em á dé."):
            cp = VGroup(f2.copy().set_fill(opacity=0.35), hpoly(M, C, B, color=TEAL))
            self.play(Rotate(cp, PI, axis=bis, about_point=M), run_time=1.8)
            self.play(cp.animate.scale(k, about_point=M), run_time=1.2)
            self.wait(0.4)
            self.play(FadeOut(cp), run_time=0.5)
        with self.say("Poměr odpovídajících si stran je stejný: em á ku em cé se rovná em dé ku em bé. "
                      "Vynásobíme do kříže a dostaneme em á krát em bé se rovná em cé krát em dé."):
            self.board.write(Row("⇒", Frac("|MA|", "|MC|", 30), "=", Frac("|MD|", "|MB|", 30), size=30), indent=0.45)
            self.board.write("⇒  |MA| · |MB| = |MC| · |MD|", indent=0.45)

        # ---- b) uvnitř
        self.clear_body()
        cfg = self.config_in()
        c, r, M, A, B, C, D = cfg
        g = self.fig(cfg, True)
        with self.say("Případ bé: bod em leží uvnitř kružnice. Sečny jsou teď tětivy á bé a cé dé, které se protínají v bodě em."):
            self.draw(g[0], g[1], run_time=1.2)
            self.draw(g[2], g[3], run_time=1.0)
            self.draw(*g[4:], run_time=0.8)
            self.board.write("b)  M leží ve vnitřní oblasti k:")
        f1, f2 = hfill(M, A, D, ORANGE, 0.2), hfill(M, C, B, TEAL, 0.2)
        al = AngleMark(A, M, D, 0.55, RED, label="α", label_r=0.82)
        ga = AngleMark(C, B, M, 0.55, RED, label="γ", label_r=0.82)
        with self.say("Zase vezmeme trojúhelníky em á dé a em cé bé. Úhly alfa a gama jsou obvodové úhly "
                      "ke stejnému oblouku bé dé, takže jsou shodné."):
            self.draw(hseg(A, D, color=ORANGE), hseg(C, B, color=TEAL), run_time=1.0)
            self.play(FadeIn(f1), FadeIn(f2), run_time=0.5)
            self.draw(al, ga, run_time=0.8)
            self.draw(harc(c, r, direction(c, B), direction(c, D) + 2 * PI if direction(c, D) < direction(c, B) else direction(c, D),
                           color=PURPLE, width=6), run_time=0.8)
            self.board.write("α = γ   (obvodové úhly k oblouku @{BD})", indent=0.45)
        aM1 = AngleMark(M, A, D, 0.45, GREEN)
        aM2 = AngleMark(M, C, B, 0.45, GREEN)
        with self.say("Úhly u vrcholu em, tedy á em dé a cé em bé, jsou vrcholové, a proto shodné. "
                      "Takže trojúhelníky jsou opět podobné podle u u."):
            self.draw(aM1, aM2, run_time=0.8)
            self.board.write("|∢AMD| = |∢CMB|   (vrcholové úhly)", indent=0.45)
            self.board.write("⇒  △MAD ∼ △MCB   (uu)", indent=0.45)
        bis = unit(A - M) + unit(C - M)
        k = np.linalg.norm(A - M) / np.linalg.norm(C - M)
        with self.say("Na obrázku: trojúhelník em cé bé překlopíme podle osy úhlu á em cé a zvětšíme. Padne na em á dé."):
            cp = VGroup(f2.copy().set_fill(opacity=0.35), hpoly(M, C, B, color=TEAL))
            self.play(Rotate(cp, PI, axis=bis, about_point=M), run_time=1.8)
            self.play(cp.animate.scale(k, about_point=M), run_time=1.2)
            self.wait(0.4)
            self.play(FadeOut(cp), run_time=0.5)
        with self.say("A stejný poměr stran: em á ku em cé se rovná em dé ku em bé, tedy em á krát em bé "
                      "se rovná em cé krát em dé."):
            self.board.write(Row("⇒", Frac("|MA|", "|MC|", 30), "=", Frac("|MD|", "|MB|", 30), size=30), indent=0.45)
            self.board.write("⇒  |MA| · |MB| = |MC| · |MD|   ]", indent=0.45)

        cfg = self.config_out()
        c, r, M, A, B, C, D = cfg
        sfig = VGroup(self.fig(cfg, False), hseg(A, D, color=ORANGE), hseg(C, B, color=TEAL),
                      AngleMark(A, M, D, 0.55, RED, label="α", label_r=0.82),
                      AngleMark(C, B, M, 0.55, RED, label="γ", label_r=0.82))
        self.summary(sfig, [
            "[Dk.:  a)  M ve vnější oblasti k:",
            "α = γ (obvodové úhly @{BD})  ⇒  △MAD ∼ △MCB (uu)",
            Row("⇒", Frac("|MA|", "|MC|", 27), "=", Frac("|MD|", "|MB|", 27), "⇒  |MA| · |MB| = |MC| · |MD|", size=27),
            "b)  M ve vnitřní oblasti k:  γ = α (obvodové úhly @{BD}),",
            "|∢CMB| = |∢AMD| (vrcholové úhly)  ⇒  △MAD ∼ △MCB (uu)",
            Row("⇒", Frac("|MA|", "|MC|", 27), "=", Frac("|MD|", "|MB|", 27), "⇒  |MA| · |MB| = |MC| · |MD|  ]", size=27)],
            "Shrnutí do písemky. Případ á, em vně: alfa se rovná gama, protože jsou to obvodové úhly k oblouku bé dé, "
            "úhel u em je společný, takže trojúhelník em á dé je podobný trojúhelníku em cé bé podle u u. "
            "Proto em á ku em cé se rovná em dé ku em bé, a tedy em á krát em bé se rovná em cé krát em dé. "
            "Případ bé, em uvnitř: stejně, jen místo společného úhlu jsou to vrcholové úhly.",
            size=27, dy=0.6, fig_w=5.0, x_text=-1.3)
