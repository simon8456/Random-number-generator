import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

ORDER = ["V 4.2", "V 5.1", "V 5.2", "V 6.2", "V 4.3", "V 6.4", "V 6.6", "V 8.1", "V 8.2",
         "V 8.3", "V 8.5", "V 7.3", "V 7.4", "V 10.4", "V 11.1", "V 11.2", "V 13.1", "V 13.2"]


class Intro(ProofScene):
    SEED = 1

    def construct(self):
        title = Text("Důkazy z planimetrie", font=FONT, font_size=76, color=RED, weight=BOLD).move_to(UP * 1.4)
        ul = wavy_underline(title, RED)
        sub = Text("18 vět  ·  pochopit obrázek  ·  umět napsat zápis", font=FONT, font_size=38, color=INK)
        sub.next_to(ul, DOWN, buff=0.5)
        nums = VGroup(*[Text(c, font=FONT, font_size=28, color=PEN) for c in ORDER])
        nums.arrange_in_grid(rows=2, buff=(0.45, 0.3)).next_to(sub, DOWN, buff=0.8)
        with self.say("Ahoj! V tomhle videu spolu projdeme důkazy osmnácti vět z planimetrie. U každé věty "
                      "nejdřív na obrázku uvidíš, proč platí, a zároveň se bude psát matematický zápis, "
                      "přesně tak, jak ho máš napsat v písemce."):
            self.play(Write(title), run_time=1.5)
            self.play(Create(ul), run_time=0.6)
            self.play(Write(sub), run_time=1.5)
            self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in nums], lag_ratio=0.08), run_time=2.5)
        with self.say("Věty nejdou úplně podle čísel, ale tak, aby na sebe navazovaly. Na konci každé věty je "
                      "zápis do písemky. Tam si video klidně zastav a zkus si důkaz napsat sám bez koukání."):
            self.play(Indicate(nums, color=RED, scale_factor=1.05), run_time=1.5)
        self.play(*[FadeOut(m) for m in (title, ul, sub, nums)], run_time=0.8)

        h = Text("Značení, které budeme používat", font=FONT, font_size=40, color=RED).to_edge(UP, buff=0.45)
        hu = wavy_underline(h, RED)
        rows = [("|AB|", "délka úsečky AB"), ("|∢ABC|", "velikost úhlu ABC"), ("△ABC", "trojúhelník ABC"),
                ("^{AB}", "polopřímka AB"), ("={AB}", "přímka AB"), ("@{BD}", "oblouk BD"),
                ("∥ ,  ⊥", "rovnoběžné, kolmé"), ("≅ ,  ∼", "shodné, podobné"),
                ("∈ ,  ∉", "leží, neleží"), ("∧ ,  ∨", "a zároveň, nebo"),
                ("⇒ ,  ⇔", "z toho plyne, právě když"), ("∀ ,  ∃", "pro každý, existuje")]
        col = VGroup()
        for i, (sym, txt) in enumerate(rows):
            a = Tx(sym, 34, INK)
            b = Tx("…  " + txt, 30, PEN)
            col.add(VGroup(a, b))
        for i, g in enumerate(col):
            x = -6.4 if i < 6 else 0.9
            yy = 2.3 - (i % 6) * 0.85
            place(g[0], x, yy)
            place(g[1], x + (1.9 if i < 6 else 1.5), yy)
        with self.say("Rychle si zopakujme značení. Svislé čáry znamenají délku úsečky nebo velikost úhlu. "
                      "Šipka nad dvěma písmeny je polopřímka, oboustranná šipka přímka a oblouček nahoře oblouk kružnice. "
                      "Dál rovnoběžnost, kolmost, shodnost a podobnost, a logické symboly: a zároveň, nebo, "
                      "z toho plyne, právě když, pro každý a existuje."):
            self.play(Write(h), Create(hu), run_time=1.0)
            for g in col:
                self.play(Write(g), run_time=max(0.5, (self.left() - 1) / len(col)))
        self.play(FadeOut(col), run_time=0.6)

        tips = VGroup(
            Tx("„právě jedna“  =  existence  +  jednoznačnost", 32, INK),
            Tx("důkaz sporem:  předpokládám opak  ⇒  nesmysl (spor)", 32, INK),
            Tx("A ⇔ B:  dokážu  „⇒“  i  „⇐“", 32, INK),
            Tx("množina bodů U = M:  dokážu  M ⊆ U  i  U ⊆ M", 32, INK),
            Tx("nástroje:  vedlejší a střídavé úhly,  sus, usu, sss,  uu", 32, INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42).move_to(DOWN * 0.3)
        h2 = Text("Typy důkazů a nástroje", font=FONT, font_size=40, color=RED).to_edge(UP, buff=0.45)
        with self.say("A ještě pár obecných triků, které se budou opakovat. Když věta říká právě jedna, dokazujeme "
                      "existenci a jednoznačnost. Důkaz sporem: předpokládáme opak a dojdeme ke sporu. Ekvivalence znamená "
                      "dokázat oba směry. U množin bodů dokazujeme dvě inkluze. A nejčastější nástroje jsou vedlejší a střídavé "
                      "úhly, věty o shodnosti es u es, u es u, es es es a věta u u o podobnosti. Tak jdeme na to!"):
            self.play(ReplacementTransform(h, h2), FadeOut(hu), run_time=0.8)
            for tp in tips:
                self.play(Write(tp), run_time=max(0.6, (self.left() - 1.5) / len(tips)))
        self.play(*[FadeOut(m) for m in self.mobjects if m.z_index > -100], run_time=0.8)


class Outro(ProofScene):
    SEED = 2

    def construct(self):
        names = ["V 4.2 kolmice bodem na přímce", "V 5.1 vedlejší úhly", "V 5.2 vrcholové úhly",
                 "V 6.2 součet úhlů v △", "V 4.3 kolmice bodem mimo přímku", "V 6.4 vnější úhel △",
                 "V 6.6 rovnoramenný △", "V 8.1 úhly ve čtyřúhelníku", "V 8.2 vnější úhly čtyřúhelníku",
                 "V 8.3 vlastnosti rovnoběžníku", "V 8.5 kritéria rovnoběžníku", "V 7.3 Eukleidova o výšce",
                 "V 7.4 Eukleidova o odvěsně", "V 10.4 středový a obvodový úhel", "V 11.1 osa úsečky",
                 "V 11.2 poloroviny osy", "V 13.1 mocnost bodu", "V 13.2 mocnost a tečna"]
        h = Text("Hotovo – všech 18 důkazů", font=FONT, font_size=44, color=RED).to_edge(UP, buff=0.4)
        items = VGroup(*[Tx("✓  " + n, 27, INK) for n in names])
        for i, it in enumerate(items):
            place(it, -6.4 if i < 9 else 0.4, 2.3 - (i % 9) * 0.62)
        with self.say("A to je všech osmnáct důkazů. Doporučuju si teď každý zápis zkusit napsat zpaměti a pak "
                      "ho porovnat s videem. Když se někde zasekneš, vrať se k obrázku, protože z něj se důkaz "
                      "dá vždycky znovu odvodit. Hodně štěstí u písemky!"):
            self.play(Write(h), run_time=1.0)
            self.play(LaggedStart(*[Write(it) for it in items], lag_ratio=0.15), run_time=max(2.0, self.left() - 1.0))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects if m.z_index > -100], run_time=1.0)
