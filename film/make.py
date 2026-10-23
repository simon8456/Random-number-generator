"""Hlavní skript: python3 make.py stills|video|info  [--build DIR]"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from engine.parse import parse  # noqa
from engine.timeline import build, load_durations, FPS  # noqa


def load(build_dir):
    scenes = parse(os.path.join(HERE, 'scenar.txt'))
    vdir = os.path.join(build_dir, 'voice')
    durs = load_durations(vdir)
    tl = build(scenes, durs)
    env = {}
    ep = os.path.join(vdir, 'env.npz')
    if os.path.exists(ep):
        z = np.load(ep)
        env = {k: z[k] for k in z.files}
    return scenes, tl, env


def cmd_info(args):
    scenes, tl, env = load(args.build)
    for S in tl:
        print(f"{S.id:>3} {S.set:10} {S.t0:8.1f}–{S.t1:8.1f}  ({S.t1 - S.t0:5.1f}s)  {len(S.lines)} replik")
    print('celkem %.1f min' % (tl[-1].t1 / 60))


def cmd_stills(args):
    import cairo
    from engine.render import Renderer
    scenes, tl, env = load(args.build)
    R = Renderer(tl, env)
    out = os.path.join(args.build, 'stills')
    os.makedirs(out, exist_ok=True)
    only = set(args.scenes.split(',')) if args.scenes else None
    for S in tl:
        if only and S.id not in only:
            continue
        n = args.per_scene
        for k in range(n):
            T = S.t0 + (S.t1 - S.t0) * (k + 0.5) / n
            R.render(T)
            R.surface.write_to_png(os.path.join(out, f'{S.id}_{k}.png'))
    print('ok', out)


def render_range(args_tuple):
    build_dir, f0, f1, path = args_tuple
    from engine.render import Renderer
    scenes, tl, env = load(build_dir)
    R = Renderer(tl, env)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', '1280x720',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-tune', 'animation',
           '-pix_fmt', 'yuv420p', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t = time.time()
    for f in range(f0, f1):
        data = R.render(f / FPS)
        p.stdin.write(bytes(data))
        if (f - f0) % 480 == 0:
            el = time.time() - t
            print(f'[{os.path.basename(path)}] {f - f0}/{f1 - f0} ({el:.0f}s)', flush=True)
    p.stdin.close()
    p.wait()
    return path


def cmd_video(args):
    from multiprocessing import Pool
    scenes, tl, env = load(args.build)
    total = int(tl[-1].t1 * FPS)
    if args.limit:
        total = min(total, int(args.limit * FPS))
    start = int(args.start * FPS)
    vdir = os.path.join(args.build, 'video')
    os.makedirs(vdir, exist_ok=True)
    n = args.jobs * 3
    chunks = []
    step = (total - start) // n + 1
    for i in range(n):
        f0 = start + i * step
        f1 = min(total, f0 + step)
        if f0 >= f1:
            break
        chunks.append((args.build, f0, f1, os.path.join(vdir, f'part{i:03d}.mp4')))
    with Pool(args.jobs) as pool:
        parts = pool.map(render_range, chunks, chunksize=1)
    lst = os.path.join(vdir, 'parts.txt')
    with open(lst, 'w') as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    out = os.path.join(args.build, 'video_noaudio.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    out], check=True)
    print('video', out)


def cmd_audio(args):
    from engine import audio
    scenes, tl, env = load(args.build)
    audio.mix(tl, os.path.join(args.build, 'voice'), os.path.join(args.build, 'mix.wav'), tl[-1].t1)


def cmd_final(args):
    out = args.out or os.path.join(args.build, 'Posledni_kontrola.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(args.build, 'video_noaudio.mp4'),
                    '-i', os.path.join(args.build, 'mix.wav'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', '-movflags', '+faststart', out], check=True)
    print('hotovo', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--build', default=os.environ.get('FILM_BUILD', os.path.join(HERE, 'build')))
    ap.add_argument('--scenes', default='')
    ap.add_argument('--per-scene', type=int, default=2)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--limit', type=float, default=0)
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    {'info': cmd_info, 'stills': cmd_stills, 'video': cmd_video, 'audio': cmd_audio, 'final': cmd_final}[a.cmd](a)
