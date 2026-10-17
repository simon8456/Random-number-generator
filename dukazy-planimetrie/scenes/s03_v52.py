import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *


class V52(ProofScene):
    CODE = "V 5.2"
    NAME = "Vrcholové úhly"
    INDEX = 3
    SEED = 52

    def construct(self):
        self.intro(
            ["Každé dva vrcholové úhly jsou shodné."],
            "Věta pět celá dva. Každé dva vrcholové úhly jsou shodné.")

        V = np.array([-3.7, -0.6, 0])
        d1 = np.array([np.cos(np.radians(20)), np.sin(np.radians(20)), 0])
        d2 = np.array([np.cos(np.radians(128)), np.sin(np.radians(128)), 0])
        L1a, L1b = V - 3.0 * d1, V + 3.0 * d1
        L2a, L2b = V - 2.8 * d2, V + 2.8 * d2
        l1, l2 = hseg(L1a, L1b), hseg(L2a, L2b)
        pV = Pt(V, "V", DOWN + LEFT * 0.3, buff=0.22)
        # alfa vpravo dole (mezi -d2 a d1), beta vlevo nahoře (mezi -d1 a d2), gama nahoře (mezi d1 a d2)
        al = AngleMark(V, L2a, L1b, 0.75, RED, label="α", label_r=1.05)
        be = AngleMark(V, L1a, L2b, 0.75, RED, label="β", label_r=1.05)
        ga = AngleMark(V, L1b, L2b, 0.6, PURPLE, label="γ", label_r=0.9)
        with self.say("Vrcholové úhly vzniknou, když se protnou dvě přímky. Dva úhly jsou vrcholové, "
                      "když ramena jednoho jsou opačné polopřímky k ramenům druhého. "
                      "Na obrázku jsou to úhly alfa a beta, leží naproti sobě."):
            self.draw(l1, run_time=1.0)
            self.draw(l2, run_time=1.0)
            self.draw(pV, run_time=0.4)
            self.draw(al, be, run_time=1.2)
            self.blink(al, be, run_time=1.0)
        with self.say("Trik je přibrat si ještě třetí úhel gama, který leží mezi nimi. "
                      "Gama je vedlejší úhel k úhlu alfa a zároveň je to vedlejší úhel k úhlu beta."):
            self.draw(ga, run_time=1.0)

        with self.say("Alfa a gama jsou vedlejší úhly, takže podle předchozí věty pět celá jedna je alfa plus gama "
                      "sto osmdesát stupňů. Vidíš, že spolu vyplní polorovinu nad jednou přímkou."):
            h1 = AngleMark(V, L2a, L2b, 1.25, ORANGE, fill_opacity=0.14, ccw=True)
            self.draw(h1, run_time=1.0)
            self.board.write("[Dk.:  α + γ = 180°   (vedlejší úhly)")
            self.play(FadeOut(h1), run_time=0.5)
        with self.say("Stejně tak beta a gama jsou vedlejší úhly, takže beta plus gama je také sto osmdesát stupňů."):
            h2 = AngleMark(V, L1b, L1a, 1.25, ORANGE, fill_opacity=0.14, ccw=True)
            self.draw(h2, run_time=1.0)
            self.board.write("β + γ = 180°   (vedlejší úhly)", indent=0.95)
            self.play(FadeOut(h2), run_time=0.5)
        with self.say("Teď obě rovnosti od sebe odečteme. Gama se odečte a zbude alfa minus beta "
                      "se rovná sto osmdesát minus sto osmdesát, tedy nula. A proto se alfa rovná beta."):
            self.board.write("⇒  α − β = 180° − 180°", gap=0.1)
            r = self.board.write("⇒  α = β   ]")
            self.play(Create(hbox(r)), run_time=0.7)
            self.blink(al, be, run_time=1.0)

        fig = VGroup(hseg(L1a, L1b), hseg(L2a, L2b), Pt(V, "V", DOWN + LEFT * 0.3, buff=0.22),
                     AngleMark(V, L2a, L1b, 0.75, RED, label="α", label_r=1.05),
                     AngleMark(V, L1a, L2b, 0.75, RED, label="β", label_r=1.05),
                     AngleMark(V, L1b, L2b, 0.6, PURPLE, label="γ", label_r=0.9))
        self.summary(fig, [
            "[Dk.:  α + γ = 180°",
            "β + γ = 180°",
            "⇒  α − β = 180° − 180°  ⇒  α = β  ]"],
            "Shrnutí do písemky: alfa plus gama je sto osmdesát stupňů a beta plus gama je sto osmdesát stupňů, "
            "protože jsou to vedlejší úhly. Odečtením dostaneme alfa minus beta je nula, tedy alfa se rovná beta.")
