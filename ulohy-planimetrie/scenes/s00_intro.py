import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

ITEMS = [("A3", "úhel dvou tětiv"), ("B3", "bod uvnitř kružnice"), ("B5", "společná tečna"),
         ("C6", "obdélník a Eukleides"), ("D2", "tečnový čtyřúhelník"), ("H1", "ekvigonála"),
         ("I4", "tětiva se středem M"), ("I3", "rovnostranný △ na kružnicích")]


class Intro(ProofScene):
    SEED = 11

    def construct(self):
        title = Text("Úlohy z planimetrie", font=FONT, font_size=76, color=RED, weight=BOLD).move_to(UP * 1.9)
        ul = wavy_underline(title, RED)
        sub = Text("ne jen jak, ale hlavně proč to funguje", font=FONT, font_size=38, color=INK).next_to(ul, DOWN, buff=0.45)
        rows = VGroup()
        for i, (c, t) in enumerate(ITEMS):
            code = Text(c, font=CODE_FONT, font_size=28, color=RED, weight=BOLD)
            rest = Tx(f"…  {t}", 30, PEN)
            x, y = -5.9 if i < 4 else 0.2, -0.4 - (i % 4) * 0.62
            place(rest, x + 0.75, y)
            code.move_to([x + 0.3, rest.axis_y + 0.02, 0])
            rows.add(VGroup(code, rest))
        with self.say("Ahoj! V tomhle videu projdeme osm úloh z planimetrie. U každé už znáš zadání i řešení, takže se nebudeme "
                      "zdržovat jen počítáním. Hlavně si ukážeme, proč to řešení funguje a jak bys na ten nápad mohl přijít sám."):
            self.play(Write(title), Create(ul), run_time=1.5)
            self.play(Write(sub), run_time=1.3)
            self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rows], lag_ratio=0.12), run_time=2.5)
        card = VGroup(RoundedRectangle(width=7.4, height=1.3, corner_radius=0.18, fill_color=PAPER, fill_opacity=1,
                                       stroke_color=RED, stroke_width=2.6),
                      Text("Zastav se a zkus si to sám", font=FONT, font_size=30, color=RED))
        card.move_to(DOWN * 3.2)
        with self.say("Občas se objeví takováhle kartička s otázkou. To je chvilka na přemýšlení. Klidně si video zastav "
                      "a zkus na odpověď přijít dřív, než ji řeknu. Právě tak se z řešení stane něco, co opravdu chápeš."):
            self.play(FadeIn(card, shift=UP * 0.2), run_time=0.7)
        self.play(*[FadeOut(m) for m in (title, ul, sub, rows, card)], run_time=0.8)

        h = Text("Tři nápady, které se budou opakovat", font=FONT, font_size=42, color=RED).to_edge(UP, buff=0.5)
        hu = wavy_underline(h, RED)
        t1 = VGroup(Tx("1)  Když nějaký úhel neumíš spočítat přímo, rozlož ho", 32, INK),
                    Tx("na úhly, které umíš: středové, obvodové, vnější úhel △.", 32, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        t2 = VGroup(Tx("2)  Když je v konstrukci víc neznámých naráz, najdi zobrazení,", 32, INK),
                    Tx("které jednu neznámou pošle na druhou. Pak zbude jediná.", 32, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        t3 = VGroup(Tx("3)  Když je něco „pro libovolnou přímku stejné“, spočítej to", 32, INK),
                    Tx("na té nejšikovnější (mocnost bodu).", 32, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        g = VGroup(t1, t2, t3).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(DOWN * 0.4)
        with self.say("Než začneme, tři obecné nápady, které uvidíš znovu a znovu. Za prvé: když úhel neumíš spočítat přímo, "
                      "rozlož ho na úhly, které umíš. Za druhé: když jsou v konstrukci dvě neznámé naráz, najdi zobrazení, "
                      "které jednu pošle na druhou. A za třetí: když je něco stejné pro libovolnou přímku, spočítej to na té "
                      "nejšikovnější. Tak jdeme na to."):
            self.play(Write(h), Create(hu), run_time=1.0)
            for t in (t1, t2, t3):
                self.play(Write(t), run_time=max(1.0, (self.left() - 1) / 3))
        self.play(*[FadeOut(m) for m in self.mobjects if m.z_index > -100], run_time=0.8)


class Outro(ProofScene):
    SEED = 12

    def construct(self):
        h = Text("Co si odnést", font=FONT, font_size=46, color=RED).to_edge(UP, buff=0.45)
        rows = [
            "A3:  úhel u M rozlož přes △ na obvodové úhly  →  ½(součet oblouků)",
            "B3:  součin úseků je pro všechny tětivy stejný  →  počítej na průměru",
            "B5:  tečna  ⇔  |SB|² = mocnost;  stejné body A, M  ⇒  stejná mocnost",
            "C6:  najdi pravoúhlý △ v otočené poloze  →  Eukleides",
            "D2:  tečny z jednoho bodu jsou stejné  →  tečnové délky",
            "H1:  obvodový úhel = ½ středového  →  střed na ose, ∢SAB = 90° − α",
            "I4:  M střed XY  ⇔  Y = S_{M}(X)  →  Y ∈ k ∩ k′",
            "I3:  C = R_{A; ±60°}(B)  →  C ∈ k₁′ ∩ k₂, nezapomeň na druhý smysl",
        ]
        items = VGroup()
        for r in rows:
            c, rest = r.split(":", 1)
            code = Text(c, font=CODE_FONT, font_size=26, color=RED, weight=BOLD)
            t = Tx(rest.strip(), 28, INK)
            items.add(VGroup(code, t))
        for i, it in enumerate(items):
            place(it[1], -5.9, 2.35 - i * 0.68)
            it[0].move_to([-6.45, it[1].axis_y + 0.02, 0])
        if items.width > 13.2:
            items.scale_to_fit_width(13.2)
        with self.say("A to je všech osm úloh. Tady je na jednom místě hlavní myšlenka každé z nich. Až budeš úlohy řešit sám, "
                      "zkus si nejdřív vzpomenout na tu myšlenku, zbytek už se dá dopočítat. Hodně štěstí u písemky!"):
            self.play(Write(h), run_time=0.8)
            self.play(LaggedStart(*[Write(i) for i in items], lag_ratio=0.25), run_time=max(3.0, self.left() - 0.5))
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects if m.z_index > -100], run_time=1.0)
