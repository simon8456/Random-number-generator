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
    env = load_env(vdir)
    return scenes, tl, env


def load_env(vdir):
    """obálky hlasitosti replik (pro pohyb rtů), cachované po souborech"""
    import wave
    from engine.timeline import load_manifest
    man = load_manifest(vdir)
    cdir = os.path.join(vdir, 'env_cache')
    os.makedirs(cdir, exist_ok=True)
    env = {}
    for key, m in man.items():
        cp = os.path.join(cdir, key + '.npy')
        if os.path.exists(cp):
            env[key] = np.load(cp)
            continue
        wp = os.path.join(vdir, m['file'])
        if not os.path.exists(wp):
            continue
        with wave.open(wp) as w:
            sr = w.getframerate()
            y = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
        hop = sr // FPS
        n = len(y) // hop + 1
        r = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(y) else 0.0
                      for i in range(n)])
        if (r > 0.005).any():
            r = r / (np.percentile(r[r > 0.005], 90) + 1e-6)
        r = np.clip(r, 0, 1).astype(np.float32)
        np.save(cp, r)
        env[key] = r
    return env


def complete_scenes(build_dir):
    from engine.timeline import load_manifest, line_key
    scenes = parse(os.path.join(HERE, 'scenar.txt'))
    man = load_manifest(os.path.join(build_dir, 'voice'))
    out = []
    for sc in scenes:
        keys = [line_key(w, i['text']) for k, w, i in sc.cmds if k == 'line']
        if all(k in man for k in keys):
            out.append(sc.id)
    return out


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


def render_scene(args_tuple):
    build_dir, sid, path = args_tuple
    from engine.render import Renderer
    scenes, tl, env = load(build_dir)
    R = Renderer(tl, env)
    S = [s for s in tl if s.id == sid][0]
    f0, f1 = round(S.t0 * FPS), round(S.t1 * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', '1280x720',
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-tune', 'animation',
           '-g', '96', '-pix_fmt', 'yuv420p', path + '.tmp.mp4']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t = time.time()
    for f in range(f0, f1):
        p.stdin.write(bytes(R.render(f / FPS)))
    p.stdin.close()
    p.wait()
    os.replace(path + '.tmp.mp4', path)
    print(f'scéna {sid}: {f1 - f0} snímků za {time.time() - t:.0f}s', flush=True)
    return path


def cmd_video(args):
    from multiprocessing import Pool
    scenes, tl, env = load(args.build)
    vdir = os.path.join(args.build, 'video')
    os.makedirs(vdir, exist_ok=True)
    only = set(args.scenes.split(',')) if args.scenes else None
    jobs = []
    for S in tl:
        path = os.path.join(vdir, f'scene_{S.id}.mp4')
        if (only is None or S.id in only) and (args.force or only or not os.path.exists(path)):
            jobs.append((args.build, S.id, path))
    # nejdelší scény první
    lens = {S.id: S.t1 - S.t0 for S in tl}
    jobs.sort(key=lambda j: -lens[j[1]])
    if jobs:
        with Pool(args.jobs) as pool:
            pool.map(render_scene, jobs, chunksize=1)
    missing = [S.id for S in tl if not os.path.exists(os.path.join(vdir, f'scene_{S.id}.mp4'))]
    if missing:
        print('chybí scény:', ','.join(missing))
        return
    lst = os.path.join(vdir, 'parts.txt')
    with open(lst, 'w') as f:
        for S in tl:
            f.write(f"file '{os.path.join(vdir, f'scene_{S.id}.mp4')}'\n")
    out = os.path.join(args.build, 'video_noaudio.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    out], check=True)
    print('video', out)


def cmd_preview(args):
    """ukázka: souvislý začátek filmu z hotových scén"""
    from engine import audio
    scenes, tl, env = load(args.build)
    ready = set(complete_scenes(args.build))
    vdir = os.path.join(args.build, 'video')
    n = 0
    for S in tl:
        if S.id in ready and os.path.exists(os.path.join(vdir, f'scene_{S.id}.mp4')):
            n += 1
        else:
            break
    if args.limit:
        n = min(n, int(args.limit))
    part = tl[:n]
    total = part[-1].t1
    print('ukázka: scény', part[0].id, '–', part[-1].id, f'{total / 60:.1f} min', flush=True)
    wav = os.path.join(args.build, 'preview.wav')
    audio.mix(part, os.path.join(args.build, 'voice'), wav, total)
    lst = os.path.join(vdir, 'preview.txt')
    with open(lst, 'w') as f:
        for S in part:
            f.write(f"file '{os.path.join(vdir, f'scene_{S.id}.mp4')}'\n")
    vid = os.path.join(args.build, 'preview_video.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid],
                   check=True)
    out = args.out or os.path.join(args.build, 'Posledni_kontrola_ukazka.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', wav, '-c:v', 'copy', '-c:a', 'aac',
                    '-b:a', '128k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('hotovo', out)


def cmd_ready(args):
    print(','.join(complete_scenes(args.build)))


def cmd_audio(args):
    from engine import audio
    scenes, tl, env = load(args.build)
    audio.mix(tl, os.path.join(args.build, 'voice'), os.path.join(args.build, 'mix.wav'), tl[-1].t1)


def cmd_final(args):
    out = args.out or os.path.join(args.build, 'Posledni_kontrola.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(args.build, 'video_noaudio.mp4'),
                    '-i', os.path.join(args.build, 'mix.wav'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
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
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    {'info': cmd_info, 'stills': cmd_stills, 'video': cmd_video, 'audio': cmd_audio, 'final': cmd_final,
     'ready': cmd_ready, 'preview': cmd_preview}[a.cmd](a)
