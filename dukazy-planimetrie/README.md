# Důkazy z planimetrie – ručně kreslené video

Animované video (česky namluvené) s důkazy 18 vět z planimetrie
(VI.1 axiomatika, VI.2 úhly a útvary, VI.3 množiny bodů a mocnost).
U každé věty: znění → vizuální vysvětlení → postupně psaný zápis → „Zápis do písemky“.

Pořadí (navazuje na sebe):

| # | Věta | Téma |
|---|------|------|
| 1 | V 4.2 | kolmice bodem ležícím na přímce |
| 2 | V 5.1 | vedlejší úhly |
| 3 | V 5.2 | vrcholové úhly |
| 4 | V 6.2 | součet vnitřních úhlů v trojúhelníku |
| 5 | V 4.3 | kolmice bodem mimo přímku |
| 6 | V 6.4 | vnější úhel trojúhelníku |
| 7 | V 6.6 | rovnoramenný trojúhelník |
| 8 | V 8.1 | součet úhlů ve čtyřúhelníku |
| 9 | V 8.2 | vnější úhly konvexního čtyřúhelníku |
| 10 | V 8.3 | vlastnosti rovnoběžníku |
| 11 | V 8.5 | kritéria rovnoběžníku |
| 12 | V 7.3 | Eukleidova věta o výšce |
| 13 | V 7.4 | Eukleidova věta o odvěsně |
| 14 | V 10.4 | středový a obvodový úhel |
| 15 | V 11.1 | osa úsečky jako množina bodů |
| 16 | V 11.2 | poloroviny určené osou |
| 17 | V 13.1 | mocnost bodu ke kružnici |
| 18 | V 13.2 | mocnost bodu a tečna |

## Jak video znovu vygenerovat

Potřeba: Python 3.11+, ffmpeg, Cairo/Pango, písmo [Kalam](https://fonts.google.com/specimen/Kalam).

```bash
# animace
python -m venv /opt/venv && /opt/venv/bin/pip install manim
# hlas (OmniVoice, klon hlasu z voice_ref.wav) + kontrola přes Whisper
python -m venv /opt/tts && /opt/tts/bin/pip install torch torchaudio omnivoice faster-whisper soundfile num2words

/opt/venv/bin/python extract_texts.py      # vytáhne komentář ze scén -> texts.json
/opt/tts/bin/python tts_gen.py             # vygeneruje chybějící audio do audio/
/opt/venv/bin/python render_all.py         # 1080p30 -> dukazy_planimetrie.mp4
/opt/venv/bin/python render_all.py --low   # rychlý náhled
```

Komentář je přímo ve scénách (`with self.say("...")`), animace se automaticky
natáhnou podle délky namluveného textu. Po změně textu stačí znovu spustit
`extract_texts.py` a `tts_gen.py` – vygenerují se jen změněné věty.

- `common.py` – ručně kreslené čáry, kružnice, úhly, text s polopřímkami (`^{AB}`), přímkami (`={AB}`),
  oblouky (`@{BD}`) a indexy (`v_{c}`, `C₀`), tabule s důkazem, synchronizace s hlasem.
- `scenes/` – jedna scéna = jedna věta.
