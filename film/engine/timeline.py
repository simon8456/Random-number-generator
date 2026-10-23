"""Sestavení časové osy filmu ze scénáře a délek namluvených replik."""
import hashlib
import math
import json
import os

GAP = 0.38          # mezera mezi replikami
SCENE_TAIL = 0.6    # dojezd na konci scény
FPS = 24


def line_key(who, text):
    return hashlib.md5(f"{who}|{text}".encode('utf8')).hexdigest()[:16]


def est_dur(text):
    return max(1.0, len(text) / 14.5 + 0.3)


class Tween:
    __slots__ = ('t0', 't1', 'a', 'b')

    def __init__(self, t0, t1, a, b):
        self.t0, self.t1, self.a, self.b = t0, t1, a, b


class Actor:
    def __init__(self, name, x, pose, facing, t):
        self.name = name
        self.moves = [Tween(t, t, x, x)]
        self.pose = [(t, pose)]
        self.facing = [(t, facing)]   # None = auto
        self.mood = [(t, 'n')]
        self.prop = [(t, None)]
        self.visible = [(t, True)]

    @staticmethod
    def at(track, t):
        v = track[0][1]
        for tt, val in track:
            if tt <= t + 1e-9:
                v = val
            else:
                break
        return v

    def x_at(self, t):
        cur = self.moves[0].a
        walking = False
        for tw in self.moves:
            if t < tw.t0:
                break
            if t >= tw.t1:
                cur = tw.b
            else:
                k = (t - tw.t0) / max(1e-6, tw.t1 - tw.t0)
                k = k * k * (3 - 2 * k) * 0.3 + k * 0.7
                cur = tw.a + (tw.b - tw.a) * k
                walking = True
        return cur, walking

    def last_x(self):
        return self.moves[-1].b


class SceneTL:
    def __init__(self, sc, t0):
        self.sc = sc
        self.id = sc.id
        self.set = sc.set
        self.tod = sc.tod
        self.t0 = t0
        self.t1 = t0
        self.actors = {}
        self.lines = []      # dict(start,end,who,text,vo,mood,key)
        self.shots = []      # (t, spec)  spec: ('auto',) ('wide',) ('cu',name) ('two',a,b)
        self.seqs = []       # (t, name)
        self.fx = []         # (t, name)
        self.overlays = []   # dict(kind,text,start,dur)
        self.fades = []      # (t, kind, dur)
        self.sfx = []        # (t, name)
        self.music = []      # (t, cue)
        self.amb = []        # (t, name)
        self.overlays_t = [] # (t, kind) začátky titulků — konec zatmívačky


def build(scenes, durations=None, voice_dir=None):
    durations = durations or {}
    t = 0.0
    out = []
    for sc in scenes:
        S = SceneTL(sc, t)
        S.shots.append((t, ('auto',)))
        S.seqs.append((t, None))
        S.fx.append((t, None))
        for kind, a, b in sc.cmds:
            if kind == 'line':
                who, info = a, b
                key = line_key(who, info['text'])
                d = durations.get(key, est_dur(info['text']))
                S.lines.append(dict(start=t, end=t + d, who=who, text=info['text'], vo=info['vo'],
                                    mood=info['mood'], key=key))
                if who in S.actors and info['mood']:
                    S.actors[who].mood.append((t, info['mood']))
                t += d + GAP
                continue
            cmd, args = a, b
            if cmd == 'wait':
                t += float(args[0])
            elif cmd == 'cast':
                for spec in args:
                    p = spec.split(':')
                    name, pose, x = p[0], p[1], float(p[2])
                    fac = {'L': -1, 'R': 1}.get(p[3]) if len(p) > 3 else None
                    if name in S.actors:
                        A = S.actors[name]
                        A.moves.append(Tween(t, t, x, x))
                        A.pose.append((t, pose))
                    else:
                        S.actors[name] = Actor(name, x, pose, fac, t)
            elif cmd == 'enter':
                name, x = args[0], float(args[1])
                side = args[2] if len(args) > 2 else 'R'
                dur = float(args[3]) if len(args) > 3 else 2.0
                start_x = -0.15 if side == 'L' else 1.15
                if name not in S.actors:
                    S.actors[name] = Actor(name, start_x, 'stand', None, S.t0)
                    S.actors[name].visible = [(S.t0, False), (t, True)]
                else:
                    S.actors[name].visible.append((t, True))
                    S.actors[name].moves.append(Tween(t, t, start_x, start_x))
                S.actors[name].pose.append((t, 'stand'))
                S.actors[name].moves.append(Tween(t, t + dur, start_x, x))
            elif cmd == 'exit':
                name = args[0]
                side = args[1] if len(args) > 1 else 'R'
                dur = float(args[2]) if len(args) > 2 else 2.0
                A = S.actors[name]
                end_x = -0.2 if side == 'L' else 1.2
                A.pose.append((t, 'stand'))
                A.moves.append(Tween(t, t + dur, A.last_x(), end_x))
                A.visible.append((t + dur, False))
            elif cmd == 'move':
                name, x = args[0], float(args[1])
                dur = float(args[2]) if len(args) > 2 else 2.0
                A = S.actors[name]
                A.moves.append(Tween(t, t + dur, A.last_x(), x))
                if Actor.at(A.pose, t) == 'crouch':
                    A.pose.append((t, 'stand'))
            elif cmd == 'pose':
                S.actors[args[0]].pose.append((t, args[1]))
            elif cmd == 'mood':
                S.actors[args[0]].mood.append((t, args[1]))
            elif cmd == 'prop':
                if args[0] in S.actors:
                    S.actors[args[0]].prop.append((t, None if args[1] == 'none' else args[1]))
            elif cmd == 'shot':
                if args[0] == 'cu':
                    S.shots.append((t, ('cu', args[1])))
                elif args[0] == 'two':
                    S.shots.append((t, ('two', args[1], args[2])))
                else:
                    S.shots.append((t, (args[0],)))
            elif cmd == 'seq':
                S.seqs.append((t, None if args[0] == 'none' else args[0]))
            elif cmd == 'fx':
                S.fx.append((t, None if args[0] == 'none' else args[0]))
            elif cmd == 'caption':
                S.overlays.append(dict(kind='caption', text=args[0], start=t + 0.3, dur=float(args[1]) + 1.0))
            elif cmd == 'title':
                d = float(args[1])
                S.overlays.append(dict(kind='title', text=args[0], start=t, dur=d))
                S.overlays_t.append((t + d, 'title_end'))
                t += d
            elif cmd == 'fade':
                d = float(args[1])
                S.fades.append((t, args[0], d))
                t += d
            elif cmd == 'sfx':
                S.sfx.append((t, args[0]))
            elif cmd == 'music':
                S.music.append((t, args[0]))
            elif cmd == 'amb':
                S.amb.append((t, args[0]))
            else:
                raise ValueError('Neznámý příkaz ' + cmd)
        # počkej, až všichni dojdou
        tail = t
        for A in S.actors.values():
            tail = max(tail, A.moves[-1].t1)
        t = tail + SCENE_TAIL
        t = math.ceil(t * FPS - 1e-6) / FPS   # hranice scén na celé snímky
        S.t1 = t
        out.append(S)
    return out


def load_manifest(voice_dir):
    import glob
    m = {}
    for p in sorted(glob.glob(os.path.join(voice_dir, 'manifest*.json'))):
        try:
            with open(p) as f:
                m.update(json.load(f))
        except Exception:  # noqa
            pass
    return m


def load_durations(voice_dir):
    return {k: v['dur'] for k, v in load_manifest(voice_dir).items()}
