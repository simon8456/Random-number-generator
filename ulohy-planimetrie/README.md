# Úlohy z planimetrie – ručně kreslené video

Druhé video (navazuje na `../dukazy-planimetrie`): osm úloh z dokumentů *Planimetrie před písemkou*
a *Konstrukční úlohy před písemkou*. Důraz je na tom, **proč** řešení funguje – s kartičkami
„Zastav se a zkus si to sám“, živými ukázkami (posouvání bodů, otáčení přímek) a na konci vždy „Zápis do písemky“.

| # | Úloha | Hlavní myšlenka |
|---|-------|-----------------|
| 1 | A3 úhel dvou tětiv | úhel u M rozložit přes △AMC na obvodové úhly |
| 2 | B3 bod uvnitř kružnice | mocnost bodu – součin spočítat na průměru; nejkratší tětiva ⊥ SM |
| 3 | B5 společná tečna | obrácená V 13.2: \|SB\|² = mocnost ⇒ tečna |
| 4 | C6 obdélník a výška | Eukleides v otočeném △ABD |
| 5 | D2 tečnový čtyřúhelník | tečny z jednoho bodu jsou stejné |
| 6 | H1 ekvigonála | obvodový = ½ středového, střed na ose, tečna a úsekový úhel |
| 7 | I4 tětiva se středem M | středová souměrnost, Y ∈ k ∩ k′ |
| 8 | I3 rovnostranný △ na kružnicích | otočení R(A; ±60°), C ∈ k₁′ ∩ k₂ |

Generování stejně jako v prvním videu:

```bash
/opt/venv/bin/python extract_texts.py
/opt/tts/bin/python tts_gen.py && /opt/tts/bin/python tts_recheck.py --delete && /opt/tts/bin/python tts_gen.py
/opt/venv/bin/python render_all.py      # -> ulohy_planimetrie.mp4
```
