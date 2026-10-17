"""Vyrenderuje všechny scény (paralelně) a spojí je do jednoho videa.

    /opt/venv/bin/python render_all.py            # 1080p30, výsledek dukazy_planimetrie.mp4
    /opt/venv/bin/python render_all.py --low      # rychlý náhled 480p15
"""
import concurrent.futures as cf
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.environ.get("MEDIA_DIR", "/tmp/claude-0/media_final")

ORDER = [("s00_intro", "Intro"), ("s01_v42", "V42"), ("s02_v51", "V51"), ("s03_v52", "V52"),
         ("s04_v62", "V62"), ("s05_v43", "V43"), ("s06_v64", "V64"), ("s07_v66", "V66"),
         ("s08_v81", "V81"), ("s09_v82", "V82"), ("s10_v83", "V83"), ("s11_v85", "V85"),
         ("s12_v73", "V73"), ("s13_v74", "V74"), ("s14_v104", "V104"), ("s15_v111", "V111"),
         ("s16_v112", "V112"), ("s17_v131", "V131"), ("s18_v132", "V132"), ("s00_intro", "Outro")]


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
    out = os.path.join(ROOT, "dukazy_planimetrie" + ("_nahled" if low else "") + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", out],
                   check=True)
    print("hotovo:", out)


if __name__ == "__main__":
    main()
