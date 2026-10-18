"""Vyrenderuje všechny scény (paralelně) a spojí je do jednoho videa.

    /opt/venv/bin/python render_all.py            # 1080p30, výsledek b5_spolecna_tecna.mp4
    /opt/venv/bin/python render_all.py --low      # rychlý náhled 480p15
"""
import concurrent.futures as cf
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.environ.get("MEDIA_DIR", "/tmp/claude-0/media_final")

ORDER = [("s1_obrazek", "B5a"), ("s2_tecna", "B5b"), ("s3_omega", "B5c"), ("s4_prenos", "B5d"), ("s5_shrnuti", "B5e")]

CHAPTERS = {"B5a": "Zadání a obrázek krok za krokem", "B5b": "Krok 1: jak dokázat tečnu",
            "B5c": "Kroky 2 a 3: kružnice ω a rovnoběžník", "B5d": "Krok 4: přenos na k₁ a k₂",
            "B5e": "Shrnutí, kontrolní otázky, zápis"}


def render(item, low):
    mod, cls = item
    q = ["-ql"] if low else ["--resolution", "1920,1080", "--frame_rate", "30"]
    cmd = ["/opt/venv/bin/manim", *q, "--media_dir", MEDIA, os.path.join(ROOT, "scenes", mod + ".py"), cls]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    path = None
    sub = "480p15" if low else "1080p30"
    cand = os.path.join(MEDIA, "videos", mod, sub, cls + ".mp4")
    if os.path.exists(cand):
        path = cand
    if r.returncode != 0 or not path:
        print(f"FAIL {cls}\n{out[-2000:]}", flush=True)
        return item, None
    print(f"ok {cls}", flush=True)
    return item, path


def main():
    low = "--low" in sys.argv
    jobs = int(os.environ.get("JOBS", "3"))
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    items = [it for it in ORDER if not only or it[1] in only]
    with cf.ThreadPoolExecutor(jobs) as ex:
        res = dict(ex.map(lambda it: render(it, low), items))
    if only:
        return
    paths = [res.get(it) for it in ORDER]
    if not all(paths):
        print("některé scény selhaly, nespojuji")
        return
    lst = os.path.join(MEDIA, "concat.txt")
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    # kapitoly (aby šlo v přehrávači skákat po větách)
    meta = os.path.join(MEDIA, "chapters.txt")
    t = 0.0
    with open(meta, "w", encoding="utf-8") as f:
        f.write(";FFMETADATA1\ntitle=B5 – společná tečna\n")
        for (mod, cls), p in zip(ORDER, paths):
            d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                      "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
            f.write(f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(t * 1000)}\nEND={int((t + d) * 1000)}\n"
                    f"title={CHAPTERS.get(cls, cls)}\n")
            print(f"{int(t // 60):02d}:{int(t % 60):02d}  {CHAPTERS.get(cls, cls)}")
            t += d
    out = os.path.join(ROOT, "b5_spolecna_tecna" + ("_nahled" if low else "") + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", meta, "-map_metadata", "1", "-map_chapters", "1",
                    "-c:v", "copy", "-af", "aresample=async=1:first_pts=0", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", out],
                   check=True)
    print("hotovo:", out)


if __name__ == "__main__":
    main()
