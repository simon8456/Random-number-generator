"""Vykreslování snímků filmu."""
import math
import os
import random

import cairo
import numpy as np

from .chars import Look, draw_character, CHARS, hexc
from .sets import draw_set, STAGE, W, H
from . import seqs as SEQ
from .timeline import Actor, FPS

FONT = 'DejaVu Sans'
DARK_SETS = {'forest', 'bunker', 'quarry', 'street', 'garage', 'videocall'}


def np_to_surface(arr):
    """arr: HxWx4 uint8 (premultiplied BGRA)"""
    h, w = arr.shape[:2]
    arr = np.ascontiguousarray(arr)
    surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, w, h, w * 4)
    return surf, arr


def make_grain(seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (360, 640))
    v = np.clip(128 + n * 40, 0, 255).astype(np.uint8)
    a = np.full_like(v, 255)
    arr = np.dstack([v, v, v, a])
    return np_to_surface(arr)


def make_vignette():
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
    a = np.clip((d - 0.55) / 0.6, 0, 1) ** 1.6 * 0.75
    a8 = (a * 255).astype(np.uint8)
    z = np.zeros_like(a8)
    arr = np.dstack([z, z, z, a8])
    return np_to_surface(arr)


def make_fog(seed):
    rng = np.random.default_rng(seed)
    w, h = 640, 360
    acc = np.zeros((h, w))
    for scale, amp in ((64, 1.0), (32, 0.5), (16, 0.25)):
        g = rng.random((h // scale + 2, w // scale + 2))
        # bilineární zvětšení
        ys = np.linspace(0, g.shape[0] - 1.001, h)
        xs = np.linspace(0, g.shape[1] - 1.001, w)
        y0 = ys.astype(int)
        x0 = xs.astype(int)
        fy = (ys - y0)[:, None]
        fx = (xs - x0)[None, :]
        fy = fy * fy * (3 - 2 * fy)
        fx = fx * fx * (3 - 2 * fx)
        a = g[y0][:, x0]
        b = g[y0][:, x0 + 1]
        c = g[y0 + 1][:, x0]
        d = g[y0 + 1][:, x0 + 1]
        acc += amp * ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy)
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    alpha = np.clip((acc - 0.35) * 1.6, 0, 1) * 0.55
    # vlnité dlaždicování: zrcadlení pro bezešvé posouvání
    alpha = np.concatenate([alpha, alpha[:, ::-1]], axis=1)
    a8 = (alpha * 255).astype(np.uint8)
    col = (a8.astype(np.float32) * 0.78).astype(np.uint8)  # premultiplied šedomodrá
    arr = np.dstack([(a8 * 0.86).astype(np.uint8), (a8 * 0.80).astype(np.uint8), col, a8])
    return np_to_surface(arr)


def last_at(track, T):
    cur = track[0]
    for item in track:
        if item[0] <= T + 1e-9:
            cur = item
        else:
            break
    return cur


def wrap_text(ctx, text, maxw):
    words = text.split()
    lines, cur = [], ''
    for w_ in words:
        test = (cur + ' ' + w_).strip()
        if ctx.text_extents(test).x_advance > maxw and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


class Renderer:
    def __init__(self, tl, env=None, subtitles=True):
        self.tl = tl
        self.env = env or {}     # key -> np.array obálky hlasitosti (FPS)
        self.subs = subtitles
        self.looks = {n: Look(n) for n in CHARS}
        self.grain = [make_grain(i) for i in range(6)]
        self.vign = make_vignette()
        self.fog = [make_fog(11), make_fog(23)]
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.cam_segments = {S.id: self._camera_segments(S) for S in tl}
        self.starts = [S.t0 for S in tl]
        self.total = tl[-1].t1

    # ------------------------------------------------------------ kamera
    def _onstage(self, S, name, t):
        A = S.actors.get(name)
        if not A:
            return False
        if not Actor.at(A.visible, t):
            return False
        x, _ = A.x_at(t)
        return -0.05 < x < 1.05

    def _camera_segments(self, S):
        events = sorted(set([t for t, _ in S.shots] + [L['start'] for L in S.lines]))
        segs = []
        prev_auto = None
        last_spk = None
        auto_count = 0
        for e in events:
            explicit_t, explicit = last_at(S.shots, e)
            # poslední replika začatá po explicitním záběru
            line = None
            for L in S.lines:
                if explicit_t - 1e-9 <= L['start'] <= e + 1e-9:
                    line = L
            spec = explicit
            onstage_speaker = line is not None and self._onstage(S, line['who'], line['start']) and not (
                line['who'] == 'VIKTOR' and line['vo'])
            if explicit[0] != 'auto' and onstage_speaker:
                subj = set(explicit[1:]) if explicit[0] in ('cu', 'two') else set()
                if line['who'] not in subj:
                    spec = ('auto',)
            if spec[0] == 'auto':
                present = [n for n in S.actors if self._onstage(S, n, e)]
                if onstage_speaker:
                    spk = line['who']
                    if prev_auto is not None and spk == last_spk:
                        spec = prev_auto
                    else:
                        auto_count += 1
                        if auto_count == 1 and len(present) >= 2:
                            spec = ('wide',) if len(present) >= 3 else ('two',) + tuple(present[:2])
                        elif auto_count % 4 == 0 and len(present) >= 2:
                            if len(present) >= 3:
                                spec = ('wide',)
                            elif last_spk and last_spk in present and last_spk != spk:
                                spec = ('two', last_spk, spk)
                            else:
                                spec = ('wide',)
                        else:
                            spec = ('cu', spk) if len(present) >= 2 else ('med', spk)
                    last_spk = spk
                    prev_auto = spec
                else:
                    if prev_auto is not None:
                        spec = prev_auto
                    else:
                        spec = ('wide',) if len(present) != 1 else ('med', present[0])
            if not segs or segs[-1][1] != spec:
                segs.append((e, spec))
        return segs

    def _shot(self, S, T):
        segs = self.cam_segments[S.id]
        cur = segs[0]
        for sg in segs:
            if sg[0] <= T + 1e-9:
                cur = sg
            else:
                break
        return cur

    def _actor_screen(self, S, name, T):
        A = S.actors[name]
        x, walking = A.x_at(T)
        floor, sc = STAGE.get(S.set, (650, 1.0))
        return x * W, floor, sc

    def _head_pos(self, S, name, T):
        x, floor, sc = self._actor_screen(S, name, T)
        lk = self.looks[name]
        pose = Actor.at(S.actors[name].pose, T)
        hfac = {'stand': 0.87, 'sit': 0.71, 'crouch': 0.6, 'bed': 0.52}.get(pose, 0.87)
        return x + (lk.body_w * 0.4 if pose == 'bed' else 0), floor - lk.H * sc * hfac, lk.H * sc

    def _camera(self, S, T):
        t0, spec = self._shot(S, T)
        dt = T - t0
        kind = spec[0]
        if kind == 'wide':
            cx, cy, z = W / 2, H / 2, 1.0
        elif kind in ('cu', 'med'):
            name = spec[1]
            if name not in S.actors:
                cx, cy, z = W / 2, H / 2, 1.0
            else:
                hx, hy, hh = self._head_pos(S, name, T)
                z = (1.8 if kind == 'cu' else 1.35) * 360 / max(260, hh)
                z = min(z, 2.4)
                cx = hx
                cy = hy + 120 / z
        elif kind == 'two':
            names = [n for n in spec[1:] if n in S.actors]
            if not names:
                cx, cy, z = W / 2, H / 2, 1.0
            else:
                ps = [self._head_pos(S, n, T) for n in names]
                xs = [p[0] for p in ps]
                ys = [p[1] for p in ps]
                span = max(xs) - min(xs) + 420
                z = max(1.0, min(1.7, W / span))
                cx = (max(xs) + min(xs)) / 2
                cy = sum(ys) / len(ys) + 0.28 * H / z
        else:
            cx, cy, z = W / 2, H / 2, 1.0
        z *= 1.0 + 0.012 * min(dt, 12)   # pomalý nájezd
        # omezení, aby kamera nevyjela z kulisy
        vw, vh = W / z, H / z
        cx = min(max(cx, vw / 2 - 60), W + 60 - vw / 2)
        cy = min(max(cy, vh / 2 - 40), H + 40 - vh / 2)
        return cx, cy, z

    # ------------------------------------------------------------ snímek
    def scene_at(self, T):
        import bisect
        i = bisect.bisect_right(self.starts, T) - 1
        return self.tl[max(0, min(i, len(self.tl) - 1))]

    def current_line(self, S, T, pad=0.0):
        for L in S.lines:
            if L['start'] - 0.05 <= T < L['end'] + pad:
                return L
        return None

    def mouth(self, key, start, T):
        env = self.env.get(key)
        if env is None:
            # odhad: pseudo-náhodné kmitání
            return 0.5 + 0.5 * math.sin((T - start) * 17) * math.sin((T - start) * 5.3)
        i = int((T - start) * FPS)
        if 0 <= i < len(env):
            return float(env[i])
        return 0.0

    def amp(self, S, name, T):
        L = self.current_line(S, T)
        if L and L['who'] == name:
            return self.mouth(L['key'], L['start'], T)
        return 0.0

    def render(self, T):
        S = self.scene_at(T)
        ctx = cairo.Context(self.surface)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        seq_t, seq = last_at(S.seqs, T)
        fx = last_at(S.fx, T)[1]
        if seq:
            # délka sekvence = do další změny
            nxt = [t for t, s in S.seqs if t > seq_t + 1e-9]
            dur = (nxt[0] if nxt else S.t1) - seq_t
            info = SEQ.Info(T - seq_t, T, dur, S, self)
            ctx.save()
            SEQ.draw(seq, ctx, info)
            ctx.restore()
        else:
            self._draw_stage(ctx, S, T, fx)
        self._post(ctx, S, T, fx if not seq else None)
        self._overlays(ctx, S, T)
        self.surface.flush()
        return self.surface.get_data()

    def _draw_stage(self, ctx, S, T, fx):
        cx, cy, z = self._camera(S, T)
        if fx == 'shake' or fx == 'flashlight':
            pass
        ctx.save()
        ctx.translate(W / 2, H / 2)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)
        draw_set(ctx, S.set, S.tod, T)
        L = self.current_line(S, T)
        speaker = L['who'] if L else None
        names = [n for n in S.actors if Actor.at(S.actors[n].visible, T)]
        # bed vzadu, ostatní podle pořadí
        names.sort(key=lambda n: 0 if Actor.at(S.actors[n].pose, T) == 'bed' else 1)
        floor, sc = STAGE.get(S.set, (650, 1.0))
        xs = {n: S.actors[n].x_at(T) for n in names}
        foc = speaker if speaker in xs else (names[-1] if names else None)
        if foc:
            fx_ = xs[foc][0] * W
            fy_ = floor - self.looks[foc].H * sc * 0.65
            self._focus = ((fx_ - cx) * z + W / 2, (fy_ - cy) * z + H / 2)
        else:
            self._focus = (W / 2, H / 2)
        for n in names:
            A = S.actors[n]
            x, walking = xs[n]
            pose = Actor.at(A.pose, T)
            fac = Actor.at(A.facing, T)
            if walking:
                # směr chůze
                x2, _ = A.x_at(T + 0.1)
                fac = 1 if x2 >= x else -1
            elif fac is None or (speaker and speaker != n and speaker in xs and fac is not None and pose != 'bed'):
                target = None
                if speaker and speaker != n and speaker in xs:
                    target = xs[speaker][0]
                else:
                    others = [xs[o][0] for o in names if o != n]
                    if others:
                        target = min(others, key=lambda ox: abs(ox - x))
                if target is not None:
                    fac = 1 if target > x else -1
                elif fac is None:
                    fac = 1 if x < 0.5 else -1
            if pose == 'bed':
                fac = 1
            talking = 0.0
            mouth = 0.0
            if L and L['who'] == n and not (n == 'VIKTOR' and L['vo'] and S.set != 'garage'):
                mouth = self.mouth(L['key'], L['start'], T)
                talking = 1.0
            gest = 0.0
            if talking and (hash(L['key']) % 3 != 0):
                gest = 0.5 + 0.5 * math.sin((T - L['start']) * 1.7)
            st = dict(x=x * W, y=floor, scale=sc, facing=fac, pose=pose, mood=Actor.at(A.mood, T),
                      mouth=min(1.0, mouth * 1.25), t=T, walking=walking,
                      walk=(x * W) / 38.0, talk=talking, gest=gest, prop=Actor.at(A.prop, T),
                      tilt=0.025 * math.sin(T * 0.7 + len(n)) + talking * 0.035 * math.sin(T * 2.3),
                      look_x=0.35 * fac if pose != 'bed' else 0.2)
            if S.set in ('forest', 'bunker', 'quarry') and self.looks[n].kind in ('tm', 'tf') and n != 'RYBAROVA':
                st['headlamp'] = True
            if n == 'RYBAROVA' and S.set == 'bunker' and T < S.t0 + (S.t1 - S.t0) * 0.75:
                st['tied'] = True
            draw_character(ctx, self.looks[n], st)
        ctx.restore()

    def _post(self, ctx, S, T, fx):
        if S.tod == 'night' and S.set not in DARK_SETS and fx is not None or (
                S.tod == 'night' and S.set not in DARK_SETS):
            ctx.set_operator(cairo.OPERATOR_MULTIPLY)
            ctx.set_source_rgb(0.55, 0.6, 0.85)
            ctx.paint()
            ctx.set_operator(cairo.OPERATOR_OVER)
        if S.tod == 'dusk':
            ctx.set_operator(cairo.OPERATOR_MULTIPLY)
            ctx.set_source_rgb(1.0, 0.85, 0.75)
            ctx.paint()
            ctx.set_operator(cairo.OPERATOR_OVER)
        if S.set in ('garage', 'bunker'):
            ctx.set_operator(cairo.OPERATOR_MULTIPLY)
            ctx.set_source_rgb(0.68, 0.7, 0.8)
            ctx.paint()
            ctx.set_operator(cairo.OPERATOR_OVER)
        if fx == 'flashlight':
            # tma s kuželem světla, který bloudí
            fpx, fpy = getattr(self, '_focus', (W / 2, H / 2))
            self._fl = getattr(self, '_fl', (fpx, fpy))
            px = fpx + 50 * math.sin(T * 0.9) + 25 * math.sin(T * 2.3)
            py = fpy + 30 * math.sin(T * 1.1)
            import cairo as C
            g = C.RadialGradient(px, py, 80, px, py, 620)
            g.add_color_stop_rgba(0, 0, 0, 0, 0.0)
            g.add_color_stop_rgba(0.5, 0, 0, 0, 0.35)
            g.add_color_stop_rgba(1, 0, 0, 0, 0.8)
            ctx.set_source(g)
            ctx.paint()
            g2 = C.RadialGradient(px, py, 0, px, py, 260)
            g2.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.18)
            g2.add_color_stop_rgba(1, 1, 0.95, 0.75, 0.0)
            ctx.set_source(g2)
            ctx.paint()
        elif fx == 'police':
            SEQ.police_flash(ctx, T)
            SEQ.police_flash(ctx, T + 0.2)
        elif fx == 'dark':
            ctx.set_source_rgba(0, 0, 0.02, 0.94)
            ctx.paint()
        elif fx == 'fog':
            for i, (fs, _) in enumerate(self.fog):
                speed = 14 + i * 9
                off = (T * speed) % 1280
                ctx.save()
                ctx.scale(2, 2)
                ctx.set_source_surface(fs, -off / 2 if i == 0 else -(640 - off / 2) % 640 - 0, 40 * i - 30)
                ctx.paint_with_alpha(0.5)
                ctx.restore()
        # vinětace a zrno
        ctx.set_source_surface(self.vign[0], 0, 0)
        ctx.paint()
        g = self.grain[0][0]   # statická textura papíru — šetří datový tok
        ctx.save()
        ctx.scale(2, 2)
        ctx.set_operator(cairo.OPERATOR_OVERLAY)
        ctx.set_source_surface(g, 0, 0)
        ctx.paint_with_alpha(0.05)
        ctx.restore()
        ctx.set_operator(cairo.OPERATOR_OVER)

    def _overlays(self, ctx, S, T):
        # fade-in na začátku scény po předchozím zatmívání
        idx = self.tl.index(S)
        prev = self.tl[idx - 1] if idx > 0 else None
        if prev and prev.fades and prev.fades[-1][1] == 'out' and not [
                t for t, _ in prev.seqs if t > prev.fades[-1][0] + prev.fades[-1][2] - 1e-6]:
            k = (T - S.t0) / 1.2
            if k < 1:
                ctx.set_source_rgba(0, 0, 0, 1 - k)
                ctx.paint()
        for t0, kind, d in S.fades:
            if kind == 'out' and T >= t0:
                # černá trvá do další změny obrazu, pak se rozsvítí
                nxt = [t for t, _ in S.seqs if t > t0 + d - 1e-6] + [t for t, _ in S.overlays_t if t > t0 + d - 1e-6]
                te = min(nxt) if nxt else 1e9
                if T < t0 + d:
                    a = (T - t0) / d
                elif T < te:
                    a = 1.0
                else:
                    a = max(0.0, 1 - (T - te) / 0.8)
                if a > 0:
                    ctx.set_source_rgba(0, 0, 0, a)
                    ctx.paint()
        if idx == 0 and T < 1.5:
            ctx.set_source_rgba(0, 0, 0, 1 - T / 1.5)
            ctx.paint()
        for ov in S.overlays:
            k = T - ov['start']
            if not (0 <= k < ov['dur']):
                continue
            if ov['kind'] == 'title':
                self._title(ctx, ov['text'], k, ov['dur'])
            else:
                self._caption(ctx, ov['text'], k, ov['dur'])
        if self.subs:
            L = self.current_line(S, T, pad=0.25)
            if L:
                self._subtitle(ctx, L)

    def _title(self, ctx, text, k, dur):
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        a = min(1, k / 1.5, (dur - k) / 1.2)
        a = max(0, a)
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        size = 92
        ctx.set_font_size(size)
        # rozprostřená písmena
        spacing = 14 + k * 1.5
        widths = [ctx.text_extents(ch).x_advance for ch in text]
        total = sum(widths) + spacing * (len(text) - 1)
        x = W / 2 - total / 2
        for ch, wdt in zip(text, widths):
            ctx.move_to(x, H / 2 + 30)
            ctx.set_source_rgba(0.92, 0.9, 0.86, a)
            ctx.show_text(ch)
            x += wdt + spacing
        # červený špendlík místo tečky
        ctx.arc(W / 2, H / 2 + 80, 7, 0, 6.3)
        ctx.set_source_rgba(0.85, 0.05, 0.05, a)
        ctx.fill()
        ctx.move_to(W / 2, H / 2 + 87)
        ctx.line_to(W / 2, H / 2 + 110)
        ctx.set_source_rgba(0.8, 0.8, 0.8, a)
        ctx.set_line_width(2)
        ctx.stroke()

    def _caption(self, ctx, text, k, dur):
        n = int(min(len(text), k * 28))
        shown = text[:n]
        a = max(0.0, min(1.0, (dur - k) / 0.6))
        ctx.select_font_face('DejaVu Sans Mono', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(26)
        ext = ctx.text_extents(text)
        ctx.set_source_rgba(0, 0, 0, 0.55 * a)
        ctx.rectangle(40, 40, ext.x_advance + 40, 50)
        ctx.fill()
        ctx.set_source_rgba(0.85, 0.08, 0.08, a)
        ctx.rectangle(40, 40, 6, 50)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.move_to(62, 74)
        ctx.show_text(shown + ('▌' if n < len(text) and int(k * 4) % 2 == 0 else ''))

    def _subtitle(self, ctx, L):
        slant = cairo.FONT_SLANT_ITALIC if L['vo'] else cairo.FONT_SLANT_NORMAL
        ctx.select_font_face(FONT, slant, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(29)
        lines = wrap_text(ctx, L['text'], 1060)
        lh = 38
        y0 = H - 30 - lh * (len(lines) - 1)
        for i, ln in enumerate(lines):
            ext = ctx.text_extents(ln)
            x = W / 2 - ext.x_advance / 2
            y = y0 + i * lh
            ctx.move_to(x, y)
            ctx.text_path(ln)
            ctx.set_source_rgba(0, 0, 0, 0.85)
            ctx.set_line_width(5)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke_preserve()
            col = (1, 1, 1) if not L['vo'] else (1, 0.95, 0.75)
            ctx.set_source_rgb(*col)
            ctx.fill()
