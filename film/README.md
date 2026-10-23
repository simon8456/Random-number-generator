# Poslední kontrola

Asi 45minutový 2D animovaný thriller. Obraz, hudbu, zvuky i hlasy generuje kód v tomto adresáři.

> ⚠️ **SPOILERY:** `scenar.txt` a `engine/seqs.py` obsahují celý děj. Pokud chceš film vidět bez spoilerů,
> nejdřív se podívej na video.

## Film

Hotový film (46 min, 1280×720, české hlasy, hudba, titulky) je kvůli limitu GitHubu (100 MB na soubor)
rozdělený na tři části: `video/Posledni_kontrola_cast1.mp4`, `cast2.mp4` a `cast3.mp4`.

## Jak film vzniká

| Část | Soubor | Co dělá |
|---|---|---|
| Scénář | `scenar.txt` | 35 scén, repliky a režijní příkazy (`@seq`, `@shot`, `@enter`…) |
| Postavy | `engine/chars.py` | vektorové postavičky s mimikou, mrkáním, pohybem rtů a chůzí |
| Prostředí | `engine/sets.py` | pokoj, sborovna, garáž, les, bunkr, lom… |
| Sekvence | `engine/seqs.py` | pohled z okna, dalekohled, telefon, mapy, sen, flashbacky, titulky |
| Časová osa | `engine/timeline.py` | ze scénáře a délek replik skládá přesné časování |
| Render | `engine/render.py` | kamera (celek, polodetail, detail), světlo, mlha, baterka, titulky |
| Hlasy | `engine/voices.py` + `engine/casting.json` | české hlasy XTTS v2, každá replika se kontroluje přepisem (Whisper) |
| Zvuk | `engine/audio.py` | syntetizovaná hudba (21 motivů), zvukové efekty, atmosféry a mix |

## Spuštění

```bash
export FILM_BUILD=/cesta/k/build
python engine/voices.py $FILM_BUILD     # ve venv s coqui-tts (XTTS v2) + transformers
python make.py info                      # přehled scén a délek
python make.py stills --per-scene 2      # kontrolní snímky
python make.py video --jobs 4            # obraz (1280×720, 24 fps)
python make.py audio                     # hudba + ruchy + hlasy -> mix.wav
python make.py final                     # výsledné MP4
```

Všechny postavy a události jsou smyšlené.
