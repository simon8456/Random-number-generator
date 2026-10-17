import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

S0 = np.array([-2.88, -1.36, 0])
u = np.array([np.cos(np.radians(25)), np.sin(np.radians(25)), 0])
v = np.array([np.cos(np.radians(95)), np.sin(np.radians(95)), 0])
a, b = 2.4, 1.08
A, C = S0 - a * u, S0 + a * u
B, D = S0 - b * v, S0 + b * v
M = S0 - (b * b / a) * u
W = circumcenter(B, C, D)
RW = np.linalg.norm(B - W)
K1 = circumcenter(A, M, B)
R1 = np.linalg.norm(A - K1)
K2 = circumcenter(A, M, D)
R2 = np.linalg.norm(A - K2)
LBL = {"A": LEFT, "B": DOWN, "C": RIGHT, "D": UP}


class B5(ProofScene):
    CODE = "B5"
    NAME = "Společná tečna dvou opsaných kružnic"
    INDEX = 3
    SEED = 205

    def para(self):
        return VGroup(hpoly(A, B, C, D, color=INK), *[Pt(X, n, LBL[n], color=INK) for n, X in zip("ABCD", (A, B, C, D))])

    def construct(self):
        self.intro(
            ["V rovnoběžníku ABCD platí |AC| > |BD|. Bod M leží na úhlopříčce AC tak,",
             "že čtyřúhelník BCDM je tětivový. Dokažte, že přímka BD je společnou tečnou",
             "kružnic opsaných trojúhelníkům AMB a AMD."],
            "Úloha bé pět, profesorova oblíbená. V rovnoběžníku á bé cé dé je úhlopříčka á cé delší než bé dé. "
            "Bod em leží na úhlopříčce á cé tak, že čtyřúhelník bé cé dé em je tětivový. Máme dokázat, že přímka "
            "bé dé je společnou tečnou kružnic opsaných trojúhelníkům á em bé a á em dé.")
        par = self.para()
        diag = VGroup(hseg(A, C, color=GRAY, width=2.4), hseg(B, D, color=GRAY, width=2.4))
        with self.say("Nejdřív náčrtek. Pozor, profesor to zdůrazňoval: nakresli obecný rovnoběžník, kosodélník, "
                      "ne obdélník ani kosočtverec. U speciálního tvaru by tě obrázek mohl svést k něčemu, co obecně neplatí."):
            self.draw(par[0], run_time=1.5)
            self.draw(*par[1:], run_time=0.5)
            self.draw(diag, run_time=1.0)
        pS = Pt(S0, "S", DOWN + RIGHT * 0.5, font_size=28)
        pM = Pt(M, "M", DOWN, color=RED)
        w = hcircle(W, RW, color=PURPLE, width=2.6)
        with self.say("Průsečík úhlopříček označíme es. Bod em leží na úhlopříčce á cé, a to tak, že body bé, cé, dé, em "
                      "leží na jedné kružnici. Nakreslíme si ji fialově a označíme omega."):
            self.draw(pS, run_time=0.4)
            self.draw(w, run_time=1.4)
            self.draw(pM, run_time=0.5)
            self.draw(Tx("ω", 30, PURPLE).move_to(W + (RW + 0.25) * np.array([0.7, 0.7, 0])), run_time=0.3)
        k1 = hcircle(K1, R1, color=ORANGE, width=2.6)
        k2 = hcircle(K2, R2, color=TEAL, width=2.6)
        with self.say("A teď kružnice, o kterých je řeč: ká jedna opsaná trojúhelníku á em bé, oranžově, "
                      "a ká dvě opsaná trojúhelníku á em dé, tyrkysově. Obě procházejí body á a em. "
                      "Na obrázku to vypadá, že se přímky bé dé jen dotýkají. To máme dokázat."):
            self.draw(k1, run_time=1.4)
            self.draw(k2, run_time=1.4)
            self.play(Indicate(diag[1], color=RED, scale_factor=1.0), run_time=1.2)
        self.wait(0.5)

        # ---- jak dokázat dotyk
        self.clear_body()
        Oc = np.array([-3.9, -0.4, 0])
        rc = 1.7
        Pp = np.array([-0.9, -2.3, 0])
        d1 = Oc + rc * np.array([np.cos(np.radians(200)), np.sin(np.radians(200)), 0])
        tt = np.arccos(rc / np.linalg.norm(Pp - Oc))
        base_ang = np.arctan2(*(Pp - Oc)[1::-1])
        T = Oc + rc * np.array([np.cos(base_ang - tt), np.sin(base_ang - tt), 0])
        sec_dir = (d1 - Pp) / np.linalg.norm(d1 - Pp)
        f = Pp - Oc
        bb = np.dot(f, sec_dir)
        disc = np.sqrt(bb * bb - (np.dot(f, f) - rc * rc))
        X1, X2 = Pp + (-bb - disc) * sec_dir, Pp + (-bb + disc) * sec_dir
        g = VGroup(hcircle(Oc, rc), Pt(Pp, "S", RIGHT), hseg(Pp, X2 + sec_dir * 0.4, color=PEN),
                   Pt(X1, "X", DOWN), Pt(X2, "Y", LEFT), hseg(Pp, T, color=RED, width=3.4), Pt(T, "T", DOWN))
        with self.say("Než začneme, musíme vědět, jak se vůbec dokazuje, že je přímka tečnou. Připomeňme si mocnost bodu. "
                      "Z bodu es vně kružnice vedeme sečnu, ta protne kružnici v bodech iks a ypsilon, a součin es iks krát es ypsilon "
                      "je mocnost bodu es. A pro tečnu s bodem dotyku té platí, že es té na druhou je ta samá mocnost."):
            self.draw(g[0], g[1], run_time=1.0)
            self.draw(g[2], g[3], g[4], run_time=1.0)
            self.draw(g[5], g[6], run_time=0.8)
            self.board.write("m_{S} = |SX| · |SY| = |ST|²   (V 13.2)")
        with self.say("Tahle věta platí i obráceně, a právě to potřebujeme. Když bod bé leží na kružnici a platí, že "
                      "es bé na druhou je rovno mocnosti bodu es, pak je přímka es bé tečna a bé je bod dotyku."):
            self.board.write("obráceně:  B ∈ k  ∧  |SB|² = m_{S}", color=RED)
            self.board.write("⇒  SB je tečna", indent=0.95, color=RED)
        self.think("Proč by z rovnosti |SB|² = m_{S} mělo plynout, že je SB tečna?",
                   "Zkus si rozmyslet, proč by z té rovnosti mělo plynout, že je přímka es bé tečna.", pause=6)
        with self.say("Představ si, že by přímka es bé nebyla tečna. Pak by kružnici protínala ještě v druhém bodě, "
                      "řekněme bé s čárkou. Mocnost by pak byla es bé krát es bé s čárkou. Jenže podle předpokladu je mocnost "
                      "es bé krát es bé. Tedy es bé s čárkou se rovná es bé, oba body jsou na stejné polopřímce ve stejné "
                      "vzdálenosti, a tak splynou. Přímka má s kružnicí jen jeden společný bod, je to tečna."):
            self.board.write("kdyby SB protínala k ještě v B′:", indent=0.45)
            self.board.write("|SB| · |SB′| = m_{S} = |SB|²  ⇒  |SB′| = |SB|", indent=0.45)
            self.board.write("⇒  B′ = B  ⇒  jediný společný bod ⇒ tečna", indent=0.45)
        with self.say("Takže celý důkaz se scvrkne na jednu rovnost délek. Pro tečnu ke ká jedna potřebujeme, aby es bé na druhou "
                      "byla mocnost bodu es ke kružnici ká jedna."):
            self.board.write("cíl:  |SB|² = m_{S}(k₁)  a  |SD|² = m_{S}(k₂)", gap=0.15, color=RED)

        # ---- důkaz
        self.clear_body()
        par = self.para()
        self.play(FadeIn(par), FadeIn(VGroup(hseg(A, C, color=GRAY, width=2.4), hseg(B, D, color=GRAY, width=2.4))),
                  FadeIn(Pt(S0, "S", DOWN + RIGHT * 0.5, font_size=28)), FadeIn(Pt(M, "M", DOWN, color=RED)),
                  FadeIn(hcircle(W, RW, color=PURPLE, width=2.6)), run_time=0.8)
        self.think("Odkud vezmeme nějaký součin úseků z bodu S?",
                   "Odkud bychom mohli vzít nějaký součin úseků vycházejících z bodu es? Podívej se na fialovou kružnici.", pause=6)
        with self.say("Bodem es procházejí dvě přímky, které protínají fialovou kružnici omega. Přímka á cé ji protíná v bodech "
                      "em a cé, přímka bé dé v bodech bé a dé. Bod es je uvnitř kružnice, a podle věty o mocnosti bodu jsou "
                      "součiny úseků na obou tětivách stejné."):
            self.hl((M, C), color=RED, run_time=1.0)
            self.hl((B, D), color=RED, run_time=1.0)
            self.board.write("[Dk.:  mocnost S ke kružnici ω (BCDM):")
            self.board.write("|SM| · |SC| = |SB| · |SD|", indent=0.95)
        with self.say("Teď přijde na řadu rovnoběžník. Jeho úhlopříčky se navzájem půlí. Takže es cé je stejně dlouhé jako es á "
                      "a es dé stejně jako es bé."):
            self.draw(VGroup(ticks(S0, A, 1), ticks(S0, C, 1), ticks(S0, B, 2), ticks(S0, D, 2)), run_time=0.8)
            self.board.write("úhlopříčky se půlí:", indent=0.45)
            self.board.write("|SC| = |SA|,  |SD| = |SB|", indent=0.95)
        with self.say("Dosadíme. Místo es cé napíšeme es á a místo es dé napíšeme es bé. Dostaneme es em krát es á "
                      "se rovná es bé na druhou. A stejně tak se to rovná es dé na druhou."):
            r = self.board.write("⇒  |SM| · |SA| = |SB|² = |SD|²", indent=0.95)
            self.box(r, run_time=0.6)
        k1 = hcircle(K1, R1, color=ORANGE, width=2.6)
        with self.say("A teď to hlavní. Co je es em krát es á? Body em a á leží obě na kružnici ká jedna, a přímka á cé jimi "
                      "prochází i bodem es. Takže es em krát es á je přesně mocnost bodu es ke kružnici ká jedna."):
            self.draw(k1, run_time=1.4)
            self.hl((S0, A), color=ORANGE, run_time=1.0)
            self.board.write("A, M ∈ k₁  ⇒  m_{S}(k₁) = |SM| · |SA|", indent=0.95)
        with self.say("Jen pro úplnost: es je vně ká jedna, protože body em i á leží od es na stejnou stranu, na polopřímce es á. "
                      "Máme tedy es bé na druhou rovno mocnosti, bé leží na ká jedna, a podle obrácené věty je es bé tečna ke ká jedna "
                      "s bodem dotyku bé."):
            self.board.write("|SB|² = m_{S}(k₁),  B ∈ k₁", indent=0.95)
            self.board.write("⇒  SB je tečna k₁", indent=0.95)
        k2 = hcircle(K2, R2, color=TEAL, width=2.6)
        with self.say("A tady je ta krása. Kružnice ká dvě prochází stejnými body á a em. Mocnost bodu es ke ká dvě je tedy "
                      "taky es em krát es á, a to se rovná es dé na druhou. Takže es dé je tečna ke ká dvě s bodem dotyku dé."):
            self.draw(k2, run_time=1.4)
            self.board.write("A, M ∈ k₂  ⇒  m_{S}(k₂) = |SM| · |SA|", indent=0.95)
            self.board.write("= |SD|²,  D ∈ k₂  ⇒  SD je tečna k₂", indent=0.95)
        bd = hline(B, D, ext=1.0, color=RED, width=4)
        with self.say("A nakonec: body bé, es a dé leží na jedné přímce, na úhlopříčce bé dé. Přímky es bé a es dé jsou tedy "
                      "jedna a táž přímka bé dé. Ta se dotýká ká jedna v bodě bé a ká dvě v bodě dé. Je to společná tečna."):
            self.draw(bd, run_time=1.2)
            self.board.write("B, S, D ∈ BD", indent=0.95)
            r = self.board.write("⇒  BD je společná tečna   ∎", indent=0.95)
            self.box(r, run_time=0.6)
        with self.say("Shrnu, proč to celé funguje. Tětivový čtyřúhelník nám dal rovnost součinů. Rovnoběžník nám dovolil "
                      "přepsat cé na á a dé na bé. A protože obě malé kružnice procházejí stejnými body á a em, mají k bodu es "
                      "stejnou mocnost, takže tečna k jedné je zároveň tečnou k druhé."):
            self.wait(self.left())

        fig = VGroup(self.para(), hseg(A, C, color=GRAY, width=2.4), Pt(S0, "S", DOWN + RIGHT * 0.5, font_size=28),
                     Pt(M, "M", DOWN, color=RED), hcircle(W, RW, color=PURPLE, width=2.4),
                     hcircle(K1, R1, color=ORANGE, width=2.4), hcircle(K2, R2, color=TEAL, width=2.4),
                     hline(B, D, ext=0.8, color=RED, width=3.4))
        self.summary(fig, [
            "[Dk.:  S = AC ∩ BD,  k₁ … opsaná △AMB,  k₂ … opsaná △AMD",
            "úhlopříčky rovnoběžníku se půlí:  |SA| = |SC|,  |SB| = |SD|",
            "mocnost S k ω (BCDM):  |SM| · |SC| = |SB| · |SD|",
            "⇒  |SM| · |SA| = |SB|² = |SD|²",
            "A, M ∈ k₁:  m_{S}(k₁) = |SM| · |SA| = |SB|²,  B ∈ k₁",
            "⇒  SB je tečna k₁  (obrácená V 13.2)",
            "A, M ∈ k₂:  m_{S}(k₂) = |SM| · |SA| = |SD|²,  D ∈ k₂",
            "⇒  SD je tečna k₂;   B, S, D ∈ BD  ⇒  BD společná tečna  ∎"],
            "Shrnutí. Es je průsečík úhlopříček. Mocnost bodu es ke kružnici bé cé dé em: es em krát es cé se rovná es bé krát es dé. "
            "Úhlopříčky se půlí, takže es em krát es á je es bé na druhou a zároveň es dé na druhou. Body á a em leží na obou "
            "malých kružnicích, takže es em krát es á je mocnost es k oběma. Podle obrácené věty třináct celá dva je es bé "
            "tečna ke ká jedna a es dé tečna ke ká dvě, a protože jde o jednu přímku bé dé, je to společná tečna.",
            size=26, dy=0.55, fig_w=4.6, x_text=-1.9,
            final="Zastav si video a zkus si důkaz napsat sám.")
