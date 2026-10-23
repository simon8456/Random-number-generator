"""Speciální sekvence: pohled z okna, dalekohled, telefony, mapy, sny, flashbacky, titulky."""
import math
import random

import cairo

from .chars import Look, draw_character, hexc, shade, mix, rrect, fill_stroke, OUT
from .sets import lin, rad, box, lamp_glow, _tree, _dog, draw_set

W, H = 1280, 720
_LOOKS = {}


def look(n):
    if n not in _LOOKS:
        _LOOKS[n] = Look(n)
    return _LOOKS[n]


class Info:
    def __init__(self, t, T, dur, S, R):
        self.t, self.T, self.dur, self.S, self.R = t, T, dur, S, R
        self.t0 = T - t
        self.lines = [L for L in S.lines if self.t0 - 1e-6 <= L['start'] < self.t0 + dur]
        self.sfx = [(tt - self.t0, n) for tt, n in S.sfx]

    def ls(self, i, default=None):
        """čas začátku i-té repliky v sekvenci (lokální)"""
        if -len(self.lines) <= i < len(self.lines):
            return self.lines[i]['start'] - self.t0
        return default if default is not None else self.dur

    def le(self, i, default=None):
        if -len(self.lines) <= i < len(self.lines):
            return self.lines[i]['end'] - self.t0
        return default if default is not None else self.dur

    def sfx_t(self, name, nth=0, default=None):
        c = [tt for tt, n in self.sfx if n == name and tt >= -0.05]
        if len(c) > nth:
            return c[nth]
        return default if default is not None else 1e9

    def amp(self, name):
        return self.R.amp(self.S, name, self.T)

    def spoken(self):
        return [L for L in self.lines if L['start'] <= self.T]


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def kf(keys, t):
    """keys: [(t, v1, v2, ...)] lineární interpolace"""
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            k = ease((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(x + (y - x) * k for x, y in zip(a[1:], b[1:]))
    return keys[-1][1:]


def text(ctx, s, x, y, size=24, col=(1, 1, 1), bold=False, font='DejaVu Sans', center=False, alpha=1.0,
         italic=False):
    ctx.select_font_face(font, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    if center:
        x -= ctx.text_extents(s).x_advance / 2
    ctx.move_to(x, y)
    ctx.set_source_rgba(*col[:3], alpha)
    ctx.show_text(s)


def wrap(ctx, s, maxw, size, bold=False, font='DejaVu Sans'):
    ctx.select_font_face(font, 0, 1 if bold else 0)
    ctx.set_font_size(size)
    out, cur = [], ''
    for w in s.split():
        tst = (cur + ' ' + w).strip()
        if ctx.text_extents(tst).x_advance > maxw and cur:
            out.append(cur)
            cur = w
        else:
            cur = tst
    if cur:
        out.append(cur)
    return out


def fig(ctx, name, x, y, s, facing=1, walking=False, t=0.0, pose='stand', mood='n', prop=None, mouth=0.0,
        gest=0.0):
    draw_character(ctx, look(name), dict(x=x, y=y, scale=s, facing=facing, walking=walking, walk=x / 9.0,
                                          t=t, pose=pose, mood=mood, prop=prop, mouth=mouth, gest=gest))


def car(ctx, x, y, s, col, facing=1, lights=False, t=0.0, brake=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    ctx.move_to(-110, -20)
    ctx.line_to(-105, -50)
    ctx.line_to(-60, -55)
    ctx.line_to(-35, -90)
    ctx.line_to(40, -90)
    ctx.line_to(70, -55)
    ctx.line_to(110, -48)
    ctx.line_to(112, -20)
    ctx.close_path()
    fill_stroke(ctx, col, 4)
    for x0, x1 in ((-28, 2), (10, 38)):
        ctx.move_to(x0, -82)
        ctx.line_to(x1, -82)
        ctx.line_to(x1 + (20 if x1 > 30 else 0), -57)
        ctx.line_to(x0 - (18 if x0 < -20 else 0), -57)
        ctx.close_path()
        fill_stroke(ctx, (0.55, 0.7, 0.85), 3)
    for wx in (-65, 65):
        ctx.arc(wx, -18, 22, 0, 6.3)
        fill_stroke(ctx, (0.12, 0.12, 0.12), 3)
        ctx.arc(wx, -18, 9, 0, 6.3)
        ctx.set_source_rgb(0.7, 0.7, 0.7)
        ctx.fill()
    if lights:
        ctx.arc(108, -38, 6, 0, 6.3)
        ctx.set_source_rgb(1, 0.95, 0.7)
        ctx.fill()
        g = cairo.LinearGradient(110, 0, 420, 0)
        g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.45)
        g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
        ctx.move_to(108, -40)
        ctx.line_to(420, -90)
        ctx.line_to(420, 20)
        ctx.close_path()
        ctx.set_source(g)
        ctx.fill()
    if brake or lights:
        ctx.rectangle(-112, -46, 6, 12)
        ctx.set_source_rgb(0.9, 0.1, 0.1)
        ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ pohled z okna

def window_scene(ctx, tod, T, garage_open=0.0, garage_light=False, office_light=True, office_k=0.0,
                 sale=False, rain=False, draw_after=None, villa_lights=True, fire=0.0):
    night = tod == 'night'
    sky = [(0, hexc('8fc3e8')), (1, hexc('e2f0f5'))] if not night else [(0, hexc('050914')), (1, hexc('18223c'))]
    ctx.set_source(lin(ctx, 0, 0, 0, 330, sky))
    ctx.rectangle(-200, -200, W + 400, 560)
    ctx.fill()
    if night:
        rng = random.Random(1)
        for i in range(80):
            ctx.arc(rng.uniform(0, W), rng.uniform(0, 240), rng.uniform(0.6, 1.6), 0, 6.3)
            ctx.set_source_rgba(1, 1, 1, rng.uniform(0.3, 0.8) * (0.7 + 0.3 * math.sin(T * 2 + i)))
            ctx.fill()
        ctx.arc(1120, 80, 26, 0, 6.3)
        ctx.set_source_rgb(0.93, 0.93, 0.85)
        ctx.fill()
    else:
        for cx, cy, s in ((200 + T * 4 % 1500 - 100, 70, 1.0), (800 + T * 3 % 1500 - 300, 110, 0.7)):
            for dx, dy, r in ((0, 0, 30), (30, -12, 36), (64, 0, 28), (32, 10, 30)):
                ctx.arc(cx + dx * s, cy + dy * s, r * s, 0, 6.3)
            ctx.set_source_rgba(1, 1, 1, 0.85)
            ctx.fill()
    # kopce a les v dálce
    hill = hexc('6f9a6a') if not night else hexc('0d1520')
    ctx.move_to(-200, 300)
    for i in range(0, 1700, 80):
        ctx.line_to(i - 200, 250 + 30 * math.sin(i * 0.006) + 12 * math.sin(i * 0.02))
    ctx.line_to(W + 200, 420)
    ctx.line_to(-200, 420)
    ctx.close_path()
    ctx.set_source_rgb(*hill)
    ctx.fill()
    rng = random.Random(8)
    for i in range(46):
        x = 900 + i * 12 + rng.uniform(-8, 8)
        _tree(ctx, x, 300 + rng.uniform(-30, 40) + (x - 900) * 0.15, 0.28 + rng.uniform(0, 0.1),
              hexc('3f6e45') if not night else hexc('0a1018'))
    # země
    ground = hexc('9cb48a') if not night else hexc('1a2420')
    ctx.rectangle(-200, 420, W + 400, 400)
    ctx.set_source_rgb(*ground)
    ctx.fill()
    # škola
    brick = hexc('c46a4a') if not night else hexc('4a2a2a')
    box(ctx, 540, 150, 460, 320, brick, 3)
    ctx.move_to(530, 155)
    ctx.line_to(770, 95)
    ctx.line_to(1010, 155)
    ctx.close_path()
    fill_stroke(ctx, hexc('5a3a30') if not night else hexc('1f1414'), 3)
    text(ctx, 'GYMNÁZIUM', 770, 140, 18, (1, 1, 1) if not night else (0.6, 0.6, 0.6), True, center=True)
    for row in range(3):
        for col in range(7):
            wx, wy = 560 + col * 63, 175 + row * 92
            is_office = (row == 1 and col == 3)
            lit = night and is_office and office_light
            c = hexc('cfe4f0') if not night else (hexc('f6d58a') if lit else hexc('1a2030'))
            box(ctx, wx, wy, 44, 58, c, 2.5)
            if lit:
                lamp_glow(ctx, wx + 22, wy + 29, 70, a=0.35)
                if draw_after == 'office':
                    pass
    box(ctx, 745, 395, 50, 75, hexc('5a3a22'), 2.5)   # vchod zezadu
    # tělocvična
    gym = hexc('d8cfb8') if not night else hexc('2e2c28')
    box(ctx, 1000, 280, 190, 190, gym, 3)
    ctx.move_to(995, 285)
    ctx.curve_to(1030, 230, 1160, 230, 1195, 285)
    ctx.close_path()
    fill_stroke(ctx, hexc('7a8a9a') if not night else hexc('22262c'), 3)
    text(ctx, 'TĚLOCVIČNA', 1095, 330, 13, (0.2, 0.2, 0.2) if not night else (0.5, 0.5, 0.5), True, center=True)
    # dvůr a ovál
    ctx.rectangle(520, 470, 680, 80)
    ctx.set_source_rgb(*(hexc('8a8a86') if not night else hexc('24262a')))
    ctx.fill()
    ctx.save()
    ctx.translate(800, 510)
    ctx.scale(1, 0.16)
    ctx.arc(0, 0, 230, 0, 6.3)
    ctx.restore()
    ctx.set_source_rgb(*(hexc('c0503a') if not night else hexc('3a2020')))
    ctx.set_line_width(14)
    ctx.stroke()
    # sud
    box(ctx, 1150, 495, 34, 46, hexc('4a4a50'), 2.5, 4)
    if fire > 0:
        for i in range(10):
            fx = 1167 + math.sin(T * 9 + i * 1.7) * 12 * fire
            fy = 492 - ((T * 60 + i * 13) % 60) * fire
            r = (8 - ((T * 60 + i * 13) % 60) / 9) * fire
            if r > 0:
                ctx.arc(fx, fy, r, 0, 6.3)
                ctx.set_source_rgba(1, 0.55 + 0.4 * (i % 2), 0.1, 0.8)
                ctx.fill()
        lamp_glow(ctx, 1167, 480, 120 * fire, (1, 0.5, 0.15), 0.4)
    # vila
    villa = hexc('f0ece0') if not night else hexc('3a3c44')
    box(ctx, 70, 300, 260, 220, villa, 3)
    ctx.move_to(50, 310)
    ctx.line_to(200, 210)
    ctx.line_to(350, 310)
    ctx.close_path()
    fill_stroke(ctx, hexc('7a3a2a') if not night else hexc('2a1a18'), 3)
    for wx, wy in ((100, 340), (230, 340), (100, 430)):
        lit = night and villa_lights and wx != 100
        box(ctx, wx, wy, 60, 54, hexc('cfe4f0') if not night else (hexc('f6d58a') if lit else hexc('1a2030')), 2.5)
        if lit:
            lamp_glow(ctx, wx + 30, wy + 27, 60, a=0.3)
    box(ctx, 230, 440, 46, 80, hexc('5a3a22'), 2.5)  # vchodové dveře
    # garáž
    box(ctx, 330, 400, 160, 120, villa, 3)
    ctx.rectangle(345, 425, 130, 95)
    ctx.set_source_rgb(*(hexc('2a2a2e') if garage_light is False else hexc('f6e2a8')))
    ctx.fill()
    if garage_light:
        lamp_glow(ctx, 410, 480, 160, a=0.35)
    # vrata (roleta) — garage_open 0..1
    gh = 95 * (1 - garage_open)
    ctx.rectangle(345, 425, 130, gh)
    ctx.set_source_rgb(*(hexc('b8b8b0') if not night else hexc('4a4a4e')))
    ctx.fill_preserve()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(2.5)
    ctx.stroke()
    ctx.set_source_rgba(0, 0, 0, 0.2)
    ctx.set_line_width(1.5)
    for i in range(1, int(gh / 12) + 1):
        ctx.move_to(345, 425 + i * 12)
        ctx.line_to(475, 425 + i * 12)
    ctx.stroke()
    # boční dvířka a květináč
    box(ctx, 495, 450, 26, 70, hexc('6a4a30') if not night else hexc('2a2018'), 2)
    ctx.move_to(522, 520)
    ctx.line_to(540, 520)
    ctx.line_to(537, 504)
    ctx.line_to(525, 504)
    ctx.close_path()
    fill_stroke(ctx, hexc('c0603a'), 1.5)
    ctx.arc(531, 498, 8, 0, 6.3)
    ctx.set_source_rgb(*(hexc('3a8a3a') if not night else hexc('1a3a1a')))
    ctx.fill()
    # plot a živý plot
    ctx.rectangle(40, 522, 480, 22)
    ctx.set_source_rgb(*(hexc('4a7a3a') if not night else hexc('14241a')))
    ctx.fill()
    ctx.rectangle(260, 522, 50, 22)
    ctx.set_source_rgb(*(hexc('9cb48a') if not night else hexc('1a2420')))
    ctx.fill()
    if sale:
        box(ctx, 120, 470, 100, 50, hexc('ffffff'), 2)
        text(ctx, 'NA PRODEJ', 170, 500, 13, (0.8, 0.1, 0.1), True, center=True)
        box(ctx, 166, 520, 6, 20, hexc('6a4a30'), 1.5)
    # cesta do lesa
    ctx.move_to(1190, 548)
    ctx.curve_to(1230, 520, 1250, 480, 1300, 430)
    ctx.line_to(1340, 440)
    ctx.curve_to(1290, 490, 1270, 530, 1250, 548)
    ctx.close_path()
    ctx.set_source_rgb(*(hexc('b8a080') if not night else hexc('2a261e')))
    ctx.fill()
    # chodníky a silnice
    ctx.rectangle(-200, 544, W + 400, 16)
    ctx.set_source_rgb(*(hexc('c8c4bc') if not night else hexc('34343a')))
    ctx.fill()
    ctx.rectangle(-200, 560, W + 400, 82)
    ctx.set_source_rgb(*(hexc('5a5a60') if not night else hexc('1c1c22')))
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.7 if not night else 0.3)
    for i in range(-2, 18):
        ctx.rectangle(i * 90 + 20, 598, 46, 5)
    ctx.fill()
    ctx.rectangle(-200, 642, W + 400, 18)
    ctx.set_source_rgb(*(hexc('c8c4bc') if not night else hexc('34343a')))
    ctx.fill()
    ctx.rectangle(-200, 660, W + 400, 100)
    ctx.set_source_rgb(*(hexc('8aa878') if not night else hexc('141c18')))
    ctx.fill()
    # zastávka
    box(ctx, 1010, 495, 90, 50, (0.75, 0.85, 0.9, 0.5) if not night else hexc('2a3440'), 2)
    box(ctx, 1010, 488, 90, 8, hexc('3a5a7a'), 2)
    text(ctx, 'BUS', 1055, 520, 12, (0.1, 0.2, 0.4) if not night else (0.6, 0.6, 0.7), True, center=True)
    # lavička dole (paní Kunešová)
    box(ctx, 1060, 690, 120, 10, hexc('7a5a3a'), 2)
    # lampy
    for lx in (180, 640, 960):
        box(ctx, lx - 3, 440, 6, 105, hexc('2a2a2a'), 1.5)
        ctx.arc(lx, 437, 8, 0, 6.3)
        fill_stroke(ctx, hexc('fff2b0') if night else hexc('dddddd'), 1.5)
        if night:
            lamp_glow(ctx, lx, 460, 110, a=0.3)


def window_frame_overlay(ctx, tod, rain=False, T=0.0):
    night = tod == 'night'
    fr = hexc('e8e4dc') if not night else hexc('3a3a40')
    ctx.set_source_rgb(*fr)
    ctx.rectangle(0, 0, W, 26)
    ctx.rectangle(0, 0, 30, H)
    ctx.rectangle(W - 30, 0, 30, H)
    ctx.fill()
    ctx.set_source_rgba(*(hexc('2a4a7a') if not night else hexc('101a30')), 0.95)
    ctx.move_to(0, 0)
    ctx.curve_to(80, 200, 30, 500, 70, H)
    ctx.line_to(0, H)
    ctx.close_path()
    ctx.move_to(W, 0)
    ctx.curve_to(W - 80, 200, W - 30, 500, W - 70, H)
    ctx.line_to(W, H)
    ctx.close_path()
    ctx.fill()
    if rain:
        rain_overlay(ctx, T)


def rain_overlay(ctx, T, k=1.0):
    rng = random.Random(int(T * 24) % 6)
    ctx.set_source_rgba(0.75, 0.82, 0.95, 0.35 * k)
    ctx.set_line_width(1.3)
    for i in range(160):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H)
        ctx.move_to(x, y)
        ctx.line_to(x - 6, y + 26)
    ctx.stroke()
    rng2 = random.Random(5)
    for i in range(40):
        x = rng2.uniform(0, W)
        y = (rng2.uniform(0, H) + T * rng2.uniform(10, 40)) % H
        ctx.arc(x, y, rng2.uniform(2, 4), 0, 6.3)
        ctx.set_source_rgba(0.8, 0.9, 1, 0.25 * k)
        ctx.fill()


def with_cam(ctx, cx, cy, z):
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)


def binoculars_mask(ctx, T, shake=1.0):
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(0, 0, W, H)
    ox = math.sin(T * 1.3) * 4 * shake
    oy = math.cos(T * 1.7) * 3 * shake
    ctx.arc(W / 2 - 200 + ox, H / 2 + oy, 300, 0, 6.3)
    ctx.new_sub_path()
    ctx.arc(W / 2 + 200 + ox, H / 2 + oy, 300, 0, 6.3)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    ctx.restore()
    # překrytí: vyplnit průnik kruhů (even-odd vytvoří díru) — znovu vyplnit oblast mimo oba kruhy
    ctx.save()
    g = cairo.RadialGradient(W / 2, H / 2, 200, W / 2, H / 2, 520)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()


def binocular_clip(ctx, T):
    ox = math.sin(T * 1.3) * 4
    oy = math.cos(T * 1.7) * 3
    ctx.new_path()
    ctx.arc(W / 2 - 200 + ox, H / 2 + oy, 300, 0, 6.3)
    ctx.new_sub_path()
    ctx.arc(W / 2 + 200 + ox, H / 2 + oy, 300, 0, 6.3)
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.clip()


def binocular_view(ctx, info, cx, cy, z, draw_fn):
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    ctx.save()
    binocular_clip(ctx, info.T)
    ctx.save()
    with_cam(ctx, cx, cy, z)
    draw_fn(ctx)
    ctx.restore()
    g = cairo.RadialGradient(W / 2, H / 2, 150, W / 2, H / 2, 560)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.7)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()
    # focus click: krátké rozostření
    ft = info.sfx_t('focus')
    if 0 <= info.t - ft < 0.6:
        ctx.set_source_rgba(1, 1, 1, 0.12 * (1 - (info.t - ft) / 0.6))
        ctx.paint()
    # stupnice
    ctx.set_source_rgba(1, 1, 1, 0.25)
    ctx.set_line_width(1.5)
    ctx.move_to(W / 2 - 40, H / 2)
    ctx.line_to(W / 2 + 40, H / 2)
    ctx.move_to(W / 2, H / 2 - 40)
    ctx.line_to(W / 2, H / 2 + 40)
    ctx.stroke()


def seq_window_intro(ctx, info):
    t, T = info.t, info.T
    # kamera: přehled → vila → škola → dvůr → les → dole
    keys = [(0, 640, 360, 1.0)]
    marks = [(1, 230, 420, 1.9), (2, 820, 330, 1.6), (3, 900, 500, 2.0), (4, 820, 500, 2.2), (5, 1150, 450, 1.9),
             (6, 1120, 640, 2.1)]
    for i, cx, cy, z in marks:
        st = info.ls(i, None)
        if st is None or st >= info.dur:
            continue
        keys.append((max(keys[-1][0] + 0.1, st - 0.5), *keys[-1][1:]))
        keys.append((st + 1.2, cx, cy, z))
    keys.append((info.dur, *keys[-1][1:]))
    cx, cy, z = kf(keys, t)
    ctx.save()
    with_cam(ctx, cx, cy, z)
    window_scene(ctx, 'day', T)
    # Kříženecký myje auto u vily a mává
    car(ctx, 220, 590, 0.42, hexc('2c3e50'), 1)
    fig(ctx, 'KRIZENECKY', 330, 585, 0.2, -1, t=T, mood='happy', gest=0.5 + 0.5 * math.sin(T * 3))
    # běžci na oválu
    for i, n in enumerate(('BRABEC', 'BLASKA')):
        a = T * 0.45 + i * 0.35
        x = 800 + math.cos(a) * 225
        y = 515 + math.sin(a) * 34
        fig(ctx, n, x, y, 0.15, -1 if math.sin(a) > 0 else 1, True, T)
    fig(ctx, 'LISKUTIN', 1000, 540, 0.16, -1, t=T, mood='angry', prop='megaphone' if info.amp('LISKUTIN') else None,
        mouth=info.amp('LISKUTIN'))
    # paní Kunešová na lavičce se psem
    fig(ctx, 'KUNESOVA', 1110, 712, 0.2, -1, t=T, pose='sit')
    ctx.save()
    ctx.translate(1185, 712)
    ctx.scale(0.3, 0.3)
    _dog(ctx, 0, 0, -1, T)
    ctx.restore()
    ctx.restore()
    window_frame_overlay(ctx, 'day')


def seq_binoculars_intro(ctx, info):
    t, T = info.t, info.T
    cx, cy = kf([(0, 900, 480), (4, 820, 500), (8, 330, 560), (12, 280, 520), (info.dur, 260, 520)], t)

    def draw(c):
        window_scene(c, 'day', T)
        car(c, 220, 590, 0.42, hexc('2c3e50'), 1)
        fig(c, 'KRIZENECKY', 330, 585, 0.2, -1, t=T, mood='happy',
            gest=0.5 + 0.5 * math.sin(T * 3))
        for i, n in enumerate(('BRABEC', 'BLASKA')):
            a = T * 0.45 + i * 0.35
            fig(c, n, 800 + math.cos(a) * 225, 515 + math.sin(a) * 34, 0.15, -1 if math.sin(a) > 0 else 1, True, T)
    binocular_view(ctx, info, cx, cy, 3.2, draw)


def seq_bike_garage(ctx, info):
    t, T = info.t, info.T
    l1, l2 = info.ls(1, 10), info.ls(2, 18)
    close = info.sfx_t('garage_close', default=l2 + 5)
    # Matěj s kolem zprava k vile
    mx = kf([(0, 1250), (l1, 470), (l2, 470), (l2 + 3, 410), (close, 410)], t)[0]
    walking_m = t < l1 or l2 < t < l2 + 3
    kx = kf([(0, 260), (l1 - 2, 260), (l1, 420), (l2, 420), (l2 + 3, 380)], t)[0]
    k_vis = t > l1 - 3
    gopen = kf([(0, 0.0), (l2 - 1, 0.0), (l2, 1.0), (close, 1.0), (close + 1.5, 0.0)], t)[0]
    inside = t > l2 + 3
    z = kf([(0, 1.0), (4, 1.0), (l1, 1.8), (info.dur, 2.1)], t)[0]
    cx, cy = kf([(0, 640, 360), (l1, 430, 500), (info.dur, 420, 500)], t)
    ctx.save()
    with_cam(ctx, cx, cy, z)
    window_scene(ctx, 'night', T, garage_open=gopen, garage_light=gopen > 0.05)
    if not inside:
        _bike(ctx, mx + 18, 580, 0.42)
        fig(ctx, 'BRABEC', mx, 585, 0.2, -1, walking_m, T, mood='happy' if l1 < t < l2 else 'n')
    if k_vis and not inside:
        fig(ctx, 'KRIZENECKY', kx, 585, 0.21, 1, (l1 - 2 < t < l1) or t > l2, T, mood='happy',
            gest=0.6 if l1 < t < l2 else 0)
    ctx.restore()
    window_frame_overlay(ctx, 'night', rain=True, T=T)


def _bike(ctx, x, y, s, col=hexc('c0392b')):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for wx in (-40, 40):
        ctx.arc(wx, -30, 28, 0, 6.3)
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.set_line_width(6)
        ctx.stroke()
    ctx.move_to(-40, -30)
    ctx.line_to(-5, -75)
    ctx.line_to(30, -75)
    ctx.line_to(40, -30)
    ctx.move_to(-5, -75)
    ctx.line_to(5, -30)
    ctx.line_to(-40, -30)
    ctx.set_source_rgb(*col)
    ctx.set_line_width(7)
    ctx.stroke()
    ctx.restore()


def seq_clock(ctx, info, s='23:10'):
    ctx.set_source_rgb(0.02, 0.02, 0.03)
    ctx.paint()
    box(ctx, 390, 240, 500, 240, hexc('111114'), 4, 30)
    blink = int(info.T * 2) % 2 == 0
    shown = s if blink else s.replace(':', ' ')
    text(ctx, shown, 640, 405, 150, (1, 0.15, 0.1), True, 'DejaVu Sans Mono', center=True)
    lamp_glow(ctx, 640, 360, 400, (1, 0.1, 0.05), 0.15)


def seq_garage_hose(ctx, info):
    T, t = info.T, info.t
    ctx.save()
    with_cam(ctx, 420, 500, 2.4)
    window_scene(ctx, 'night', T, garage_open=1.0, garage_light=True)
    fig(ctx, 'KRIZENECKY', 410, 520, 0.2, 1, t=T, prop='flashlight')
    rng = random.Random(int(T * 24))
    for i in range(30):
        k = rng.random()
        x = 425 + k * 50
        y = 505 + k * k * 15 + rng.uniform(-3, 3)
        ctx.arc(x, y, 1.4, 0, 6.3)
        ctx.set_source_rgba(0.8, 0.9, 1.0, 0.8)
        ctx.fill()
    ctx.restore()
    window_frame_overlay(ctx, 'night', rain=True, T=T)


def seq_liskutin_fire(ctx, info):
    T, t = info.T, info.t
    l1 = info.ls(1, 6)
    fire_t = info.sfx_t('fire', default=l1 + 3)
    lx = kf([(0, 1000), (l1, 1000), (fire_t - 0.5, 1120), (info.dur, 1120)], t)[0]
    fire = kf([(0, 0), (fire_t, 0), (fire_t + 1.5, 1), (info.dur, 1)], t)[0]
    ctx.save()
    with_cam(ctx, 1080, 470, 2.6)
    window_scene(ctx, 'night', T, fire=fire)
    fig(ctx, 'LISKUTIN', lx, 540, 0.16, 1, l1 < t < fire_t - 0.5, T)
    if fire < 0.3:
        ctx.save()
        ctx.translate(lx + 14, 538)
        ctx.scale(1, 0.8)
        ctx.arc(0, -10, 12, 0, 6.3)
        ctx.restore()
        fill_stroke(ctx, (0.1, 0.1, 0.1), 2)
    ctx.restore()
    window_frame_overlay(ctx, 'night')


def seq_car_forest(ctx, info):
    T, t = info.T, info.t
    l1 = info.ls(1, 10)
    # odjezd bez světel
    if t < l1 - 1:
        k = t / max(1, l1 - 1)
        cx_ = kf([(0, 410), (2, 410), (5, 900), (l1 - 1, 1400)], t)[0]
        gopen = kf([(0, 0), (1, 1), (3, 1), (5, 0)], t)[0]
        ctx.save()
        with_cam(ctx, 700, 450, 1.4)
        window_scene(ctx, 'night', T, garage_open=gopen, garage_light=False)
        car(ctx, cx_, 610, 0.42, hexc('2c3e50'), 1, lights=False)
        ctx.restore()
    else:
        tt = t - l1
        cx_ = kf([(0, 1400), (3, 470), (info.dur, 470)], tt)[0]
        gopen = kf([(0, 0), (2, 0), (3, 1), (info.dur, 1)], tt)[0]
        ctx.save()
        with_cam(ctx, 470, 520, 2.0)
        window_scene(ctx, 'night', T, garage_open=gopen, garage_light=tt > 3)
        car(ctx, cx_, 610, 0.42, hexc('2c3e50'), -1, lights=tt > 2.5)
        if tt > 4:
            fig(ctx, 'KRIZENECKY', 520, 600, 0.2, -1, t=T)
            # lopata od bláta
            ctx.save()
            ctx.translate(545, 590)
            ctx.rotate(0.3)
            box(ctx, -2, -60, 4, 50, hexc('8a6a3a'), 1)
            ctx.move_to(-9, -12)
            ctx.line_to(9, -12)
            ctx.line_to(7, 6)
            ctx.line_to(-7, 6)
            ctx.close_path()
            fill_stroke(ctx, hexc('5a4a30'), 1.5)
            ctx.restore()
        ctx.restore()
    window_frame_overlay(ctx, 'night')


def seq_red_car(ctx, info, leave=False):
    T, t = info.T, info.t
    door_t = info.sfx_t('car_door', default=info.ls(1, 5) + 3)
    ctx.save()
    with_cam(ctx, 1000, 520, 2.0)
    window_scene(ctx, 'night', T)
    if not leave:
        cx_ = kf([(0, -200), (0.1, -200), (info.ls(1, 4), 1060), (info.dur, 1060)], t)[0]
        if t < door_t:
            fig(ctx, 'MLEJNEK', 1050, 548, 0.18, -1, t=T, mood='happy' if t > info.ls(1, 4) else 'n')
        car(ctx, cx_, 625, 0.4, hexc('c0392b'), 1, lights=True)
    else:
        cx_ = kf([(0, 1060), (1, 1060), (info.dur, 1700)], t)[0]
        car(ctx, cx_, 625, 0.4, hexc('c0392b'), 1, lights=True)
    ctx.restore()
    window_frame_overlay(ctx, 'night', rain=True, T=T)


def seq_binoculars_plate(ctx, info):
    T = info.T

    def draw(c):
        window_scene(c, 'night', T)
        car(c, 1060, 625, 0.4, hexc('c0392b'), 1, lights=True)
        # SPZ
        box(c, 1010, 607, 30, 9, (0.95, 0.95, 0.95), 1)
        text(c, '3P', 1013, 615, 7, (0.1, 0.1, 0.1), True, 'DejaVu Sans Mono')
        c.set_source_rgba(0.35, 0.25, 0.15, 0.85)
        c.rectangle(1024, 607, 16, 9)
        c.fill()
    binocular_view(ctx, info, 1028, 612, 9.0, draw)
    rain_overlay(ctx, T, 0.6)


def seq_garage_approach(ctx, info):
    T, t = info.T, info.t
    st = [info.ls(i, 3 + 3 * i) for i in range(4)]
    car_x = kf([(0, 410), (st[0] + 1, 410), (st[0] + 4, 1500)], t)[0]
    gopen = kf([(0, 1), (st[0] + 2, 1), (st[0] + 4, 0)], t)[0]
    bx = kf([(0, 1300), (st[1], 1300), (st[2], 290), (st[3], 500), (info.dur, 505)], t)[0]
    by = kf([(0, 650), (st[1], 650), (st[2], 650), (st[2] + 1.5, 540), (st[3], 522), (info.dur, 522)], t)[0]
    dog_x = kf([(0, 1240), (st[1], 1240), (st[1] + 2, 330), (info.dur, 330)], t)[0]
    ctx.save()
    with_cam(ctx, *kf([(0, 640, 450, 1.2), (st[2], 420, 500, 2.0), (info.dur, 480, 500, 2.6)], t))
    window_scene(ctx, 'day', T, garage_open=gopen)
    if car_x < 1450:
        car(ctx, car_x, 610 if car_x > 420 else 560, 0.42, hexc('2c3e50'), 1)
    ctx.save()
    ctx.translate(dog_x, by - 2 if t > st[2] else 652)
    ctx.scale(0.22, 0.22)
    _dog(ctx, 0, 0, -1, T)
    ctx.restore()
    if t > st[1] and t < info.dur - 0.5:
        fig(ctx, 'BEATA', bx, by, 0.2, -1 if bx > 500 else 1, st[1] < t < st[3], T, prop='phone', mood='scared')
    ctx.restore()
    window_frame_overlay(ctx, 'day')


def seq_garage_map(ctx, info):
    """detail mapy na stěně garáže ve světle baterky"""
    T, t = info.T, info.t
    ctx.set_source_rgb(*hexc('3a3a38'))
    ctx.paint()
    draw_map(ctx, 140, 60, 1000, 600, T, pins=True, flags=True, aged=True)
    # baterka
    px = 640 + 380 * math.sin(t * 0.45)
    py = 360 + 120 * math.sin(t * 0.8)
    g = cairo.RadialGradient(px, py, 40, px, py, 360)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(0.6, 0, 0, 0, 0.6)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.93)
    ctx.set_source(g)
    ctx.paint()
    cam = info.sfx_t('camera')
    for k in range(3):
        ct = info.sfx_t('camera', k)
        if 0 <= t - ct < 0.25:
            ctx.set_source_rgba(1, 1, 1, 0.8 * (1 - (t - ct) / 0.25))
            ctx.paint()


PINS = [  # (x, y v 0..1, popisek, starý?)
    (0.18, 0.30, 'S.H.', True), (0.25, 0.62, 'J.K.', True), (0.33, 0.20, 'T.V.', True), (0.41, 0.75, 'L.P.', True),
    (0.47, 0.40, 'O.D.', True), (0.55, 0.66, 'P.R.', True), (0.62, 0.26, 'M.B.', False), (0.70, 0.55, 'K.M.', False),
    (0.12, 0.80, 'R.Š.', True), (0.80, 0.35, 'D.F.', True), (0.86, 0.70, 'A.N.', True), (0.74, 0.14, '', False),
]


def draw_map(ctx, x, y, w, h, T, pins=True, flags=True, aged=False, labels=False, highlight=None, empty_glow=0.0):
    paper = hexc('efe4c4') if not aged else hexc('e4d6b0')
    box(ctx, x, y, w, h, paper, 4, 3)
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    rng = random.Random(42)
    # lesy
    for i in range(14):
        cx_, cy_ = x + rng.uniform(0, w), y + rng.uniform(0, h)
        ctx.arc(cx_, cy_, rng.uniform(60, 160), 0, 6.3)
        ctx.set_source_rgba(0.45, 0.7, 0.4, 0.35)
        ctx.fill()
    # vrstevnice
    ctx.set_line_width(1.4)
    for i in range(5):
        cx_, cy_ = x + rng.uniform(0.1, 0.9) * w, y + rng.uniform(0.1, 0.9) * h
        for r in range(1, 7):
            ctx.save()
            ctx.translate(cx_, cy_)
            ctx.scale(1.4, 1.0)
            ctx.arc(0, 0, r * 18 + rng.uniform(-3, 3), 0, 6.3)
            ctx.restore()
            ctx.set_source_rgba(0.6, 0.4, 0.2, 0.45)
            ctx.stroke()
    # potok a cesty
    ctx.set_source_rgba(0.2, 0.45, 0.85, 0.8)
    ctx.set_line_width(4)
    ctx.move_to(x, y + h * 0.5)
    ctx.curve_to(x + w * 0.3, y + h * 0.3, x + w * 0.5, y + h * 0.8, x + w, y + h * 0.6)
    ctx.stroke()
    ctx.set_source_rgba(0.1, 0.1, 0.1, 0.6)
    ctx.set_line_width(2)
    ctx.set_dash([10, 6])
    ctx.move_to(x, y + h * 0.9)
    ctx.curve_to(x + w * 0.4, y + h * 0.7, x + w * 0.6, y + h * 0.2, x + w, y + h * 0.1)
    ctx.stroke()
    ctx.set_dash([])
    # mřížka
    ctx.set_source_rgba(0.2, 0.2, 0.5, 0.25)
    ctx.set_line_width(1)
    for i in range(1, 8):
        ctx.move_to(x + w * i / 8, y)
        ctx.line_to(x + w * i / 8, y + h)
    for i in range(1, 6):
        ctx.move_to(x, y + h * i / 6)
        ctx.line_to(x + w, y + h * i / 6)
    ctx.stroke()
    if labels:
        for (lx, ly, s) in ((0.62, 0.26, 'Starý lom'), (0.70, 0.55, 'Bažina'), (0.25, 0.62, 'Hájovna'),
                            (0.74, 0.14, 'Vyhlídka — kryt')):
            text(ctx, s, x + lx * w + 16, y + ly * h + 5, 18, (0.15, 0.1, 0.05), True)
    ctx.restore()
    if pins:
        for i, (px, py, lab, old) in enumerate(PINS):
            X, Y = x + px * w, y + py * h
            if lab == '' and empty_glow > 0:
                lamp_glow(ctx, X, Y, 70, (1, 0.2, 0.2), 0.5 * empty_glow)
            ctx.set_source_rgba(0, 0, 0, 0.3)
            ctx.arc(X + 4, Y + 6, 7, 0, 6.3)
            ctx.fill()
            col = (0.65, 0.25, 0.15) if old else (0.9, 0.05, 0.05)
            ctx.arc(X, Y, 9, 0, 6.3)
            fill_stroke(ctx, col, 2)
            ctx.arc(X - 3, Y - 3, 3, 0, 6.3)
            ctx.set_source_rgba(1, 1, 1, 0.6)
            ctx.fill()
            if flags and lab:
                ctx.move_to(X, Y)
                ctx.line_to(X, Y - 36)
                ctx.set_source_rgb(0.2, 0.2, 0.2)
                ctx.set_line_width(1.5)
                ctx.stroke()
                box(ctx, X, Y - 36, 42, 18, (1, 1, 1) if not old else hexc('d8ccb0'), 1.2)
                text(ctx, lab, X + 4, Y - 22, 13, (0.6, 0, 0) if not old else (0.3, 0.2, 0.1), True)
            if highlight is not None and i == highlight:
                ctx.arc(X, Y, 30 + 6 * math.sin(T * 5), 0, 6.3)
                ctx.set_source_rgba(1, 0.9, 0.1, 0.9)
                ctx.set_line_width(4)
                ctx.stroke()


def seq_prolog_map(ctx, info):
    T, t = info.T, info.t
    ctx.set_source_rgb(*hexc('1a1410'))
    ctx.paint()
    zoom = 1.0 + t * 0.006
    ctx.save()
    with_cam(ctx, 640, 360, zoom)
    # stůl
    ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, hexc('3a2618')), (1, hexc('2a1a10'))]))
    ctx.rectangle(-200, -200, W + 400, H + 400)
    ctx.fill()
    ctx.save()
    ctx.translate(640, 360)
    ctx.rotate(-0.06)
    ctx.translate(-640, -360)
    p1 = info.sfx_t('pin', 0)
    p2 = info.sfx_t('pin', 1)
    old = list(PINS)
    # nejprve mapa bez posledních dvou špendlíků
    global PINS_SHOWN
    draw_map(ctx, 170, 80, 940, 560, T, pins=False)
    for i, (px, py, lab, o) in enumerate(PINS):
        if lab == '':
            continue
        if lab == 'M.B.' and t < p1:
            continue
        if lab == 'K.M.' and t < p2:
            continue
        X, Y = 170 + px * 940, 80 + py * 560
        ctx.arc(X, Y, 9, 0, 6.3)
        fill_stroke(ctx, (0.65, 0.25, 0.15) if o else (0.9, 0.05, 0.05), 2)
    ctx.restore()
    # třídní fotka
    ctx.save()
    ctx.translate(1000, 560)
    ctx.rotate(0.18)
    box(ctx, -110, -75, 220, 150, (0.95, 0.95, 0.92), 2)
    ctx.rectangle(-100, -65, 200, 110)
    ctx.set_source_rgb(0.55, 0.6, 0.65)
    ctx.fill()
    for i in range(10):
        ctx.arc(-80 + (i % 5) * 40, -35 + (i // 5) * 45, 11, 0, 6.3)
        ctx.set_source_rgb(0.9, 0.78, 0.65)
        ctx.fill()
    ctx.arc(-40, -35, 17, 0, 6.3)
    ctx.set_source_rgb(0.85, 0.05, 0.05)
    ctx.set_line_width(3)
    ctx.stroke()
    text(ctx, '2.A', -95, 65, 14, (0.2, 0.2, 0.2), True)
    ctx.restore()
    # ruka v rukavici se špendlíkem
    for k, (pt, lab) in enumerate(((p1, 'M.B.'), (p2, 'K.M.'))):
        tgt = [p for p in PINS if p[2] == lab][0]
        X, Y = 170 + tgt[0] * 940, 80 + tgt[1] * 560
        if pt - 2.5 < t < pt + 1.2:
            u = (t - (pt - 2.5)) / 2.5
            hx = X + (1 - ease(u)) * 300 if t < pt else X + ease((t - pt) / 1.2) * 300
            hy = Y + (1 - ease(u)) * 260 if t < pt else Y + ease((t - pt) / 1.2) * 260
            _glove(ctx, hx, hy, holding=t < pt)
    ctx.restore()
    lamp_glow(ctx, 400, 200, 700, (1, 0.8, 0.5), 0.25)


def _glove(ctx, x, y, holding=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.7)
    c = hexc('1a1a1e')
    rrect(ctx, 10, 20, 70, 260, 30)
    fill_stroke(ctx, hexc('3a2e28'), 3)
    rrect(ctx, -10, -30, 90, 90, 30)
    fill_stroke(ctx, c, 3)
    for i in range(3):
        rrect(ctx, -2 + i * 24, -70, 20, 60, 10)
        fill_stroke(ctx, c, 3)
    rrect(ctx, -40, -20, 50, 22, 10)
    fill_stroke(ctx, c, 3)
    if holding:
        ctx.move_to(-20, -60)
        ctx.line_to(-20, -10)
        ctx.set_source_rgb(0.8, 0.8, 0.85)
        ctx.set_line_width(3)
        ctx.stroke()
        ctx.arc(-20, -64, 9, 0, 6.3)
        fill_stroke(ctx, (0.9, 0.05, 0.05), 2)
    ctx.restore()


# ------------------------------------------------------------------ telefon a počítač

def room_blur_bg(ctx, info, tod='day'):
    ctx.save()
    draw_set(ctx, 'room', tod, info.T)
    ctx.restore()
    ctx.set_source_rgba(0.05, 0.05, 0.1, 0.6)
    ctx.paint()


def phone_frame(ctx, x=440, y=40, w=400, h=680):
    rrect(ctx, x - 14, y - 14, w + 28, h + 60, 48)
    fill_stroke(ctx, hexc('16161c'), 3)
    rrect(ctx, x, y, w, h, 30)
    ctx.set_source_rgb(0.97, 0.97, 0.98)
    ctx.fill()
    # ruka
    ctx.save()
    ctx.translate(x + w + 10, y + h - 40)
    rrect(ctx, -60, 0, 140, 300, 60)
    fill_stroke(ctx, hexc('f1c9a5'), 3)
    rrect(ctx, -70, -40, 50, 120, 25)
    fill_stroke(ctx, hexc('f1c9a5'), 3)
    ctx.restore()
    text(ctx, '21:47' if False else '14:32', x + 30, y + 30, 16, (0.1, 0.1, 0.1), True)
    ctx.arc(x + w / 2, y + 18, 8, 0, 6.3)
    ctx.set_source_rgb(0.1, 0.1, 0.12)
    ctx.fill()


def seq_phone_mail(ctx, info, sender, subject, body, tod='day'):
    room_blur_bg(ctx, info, tod)
    x, y, w, h = 440, 40, 400, 680
    phone_frame(ctx, x, y, w, h)
    box(ctx, x, y + 44, w, 70, hexc('2c5aa0'), 0)
    text(ctx, 'Pošta', x + 20, y + 88, 24, (1, 1, 1), True)
    text(ctx, sender, x + 20, y + 150, 17, (0.1, 0.1, 0.1), True)
    text(ctx, subject, x + 20, y + 180, 16, (0.2, 0.2, 0.3), False)
    ctx.set_source_rgba(0, 0, 0, 0.15)
    ctx.rectangle(x + 20, y + 196, w - 40, 1.5)
    ctx.fill()
    lines = wrap(ctx, body, w - 44, 17)
    t0 = info.ls(0, 1.0)
    total = sum(len(l) for l in lines)
    L = info.lines[0] if info.lines else None
    dur = (L['end'] - L['start']) if L else 8.0
    nchars = int(total * max(0.0, min(1.0, (info.t - t0 + 0.6) / dur))) if info.t > t0 - 0.6 else 0
    shown = 0
    yy = y + 230
    for ln in lines:
        k = max(0, min(len(ln), nchars - shown))
        shown += len(ln)
        text(ctx, ln, x + 22, yy, 17, (0.12, 0.12, 0.14), False)
        if k < len(ln):
            # překrýt zatím nepřečtené — šedě
            ctx.select_font_face('DejaVu Sans', 0, 0)
            ctx.set_font_size(17)
            pre = ctx.text_extents(ln[:k]).x_advance
            ctx.rectangle(x + 22 + pre, yy - 16, w, 22)
            ctx.set_source_rgba(0.97, 0.97, 0.98, 0.75)
            ctx.fill()
        yy += 26
    # zvýraznit podpis
    if 'klidných dnů' in body and nchars >= total - 5:
        ctx.rectangle(x + 18, yy - 52, w - 36, 50)
        ctx.set_source_rgba(1, 0.9, 0.2, 0.35)
        ctx.fill()


def seq_phone_chat(ctx, info, title, me='VIKTOR', tod='day', names=None):
    room_blur_bg(ctx, info, tod)
    x, y, w, h = 440, 40, 400, 680
    phone_frame(ctx, x, y, w, h)
    box(ctx, x, y + 44, w, 64, hexc('128c7e'), 0)
    text(ctx, title, x + 20, y + 84, 20, (1, 1, 1), True)
    msgs = info.spoken()
    names = names or {}
    yy = y + 130
    blocks = []
    for L in msgs:
        ln = wrap(ctx, L['text'], w - 140, 16)
        blocks.append((L, ln))
    total_h = sum(30 + 22 * len(b[1]) for b in blocks)
    yy = y + h - 20 - total_h if total_h > h - 150 else y + 130
    for L, ln in blocks:
        mine = L['who'] == me
        bh = 22 * len(ln) + 26
        bw = max(ctx.text_extents(s).x_advance for s in ln) + 30 if ln else 60
        bw = max(bw, 120)
        bx = x + w - bw - 16 if mine else x + 16
        if yy > y + 110:
            box(ctx, bx, yy, bw, bh, hexc('dcf8c6') if mine else (1, 1, 1), 1.5, 12)
            if not mine:
                text(ctx, names.get(L['who'], L['who'].title()), bx + 12, yy + 16, 12, (0.1, 0.5, 0.45), True)
            for i, s in enumerate(ln):
                text(ctx, s, bx + 14, yy + 36 + i * 22 - (0 if not mine else 14), 16, (0.1, 0.1, 0.1))
        yy += bh + 8


def seq_phone_photo(ctx, info, kind):
    room_blur_bg(ctx, info, 'day')
    x, y, w, h = 440, 40, 400, 680
    phone_frame(ctx, x, y, w, h)
    ctx.rectangle(x, y + 44, w, h - 44)
    ctx.set_source_rgb(0.05, 0.05, 0.05)
    ctx.fill()
    ctx.save()
    ctx.rectangle(x, y + 44, w, h - 44)
    ctx.clip()
    z = 1.0 + info.t * 0.08
    ctx.translate(x + w / 2, y + h / 2)
    ctx.scale(z, z)
    ctx.translate(-(x + w / 2), -(y + h / 2))
    if kind == 'keychain':
        # vojenská bedna a klíčenka
        box(ctx, x + 40, y + 260, 320, 200, hexc('5a6a3a'), 4, 6)
        text(ctx, 'ВАГ 1974', x + 110, y + 350, 28, (0.9, 0.9, 0.8), True)
        ctx.set_source_rgb(0.75, 0.75, 0.8)
        ctx.set_line_width(4)
        ctx.arc(x + 200, y + 230, 20, 0, 6.3)
        ctx.stroke()
        ctx.save()
        ctx.translate(x + 200, y + 250)
        ctx.rotate(0.3)
        rrect(ctx, -6, 0, 12, 110, 5)
        fill_stroke(ctx, (0.82, 0.82, 0.86), 2)
        ctx.move_to(-6, 110)
        ctx.curve_to(-26, 130, -20, 170, 0, 180)
        ctx.curve_to(20, 170, 26, 130, 6, 110)
        ctx.close_path()
        fill_stroke(ctx, (0.82, 0.82, 0.86), 2)
        text(ctx, 'VK', -10, 150, 13, (0.1, 0.2, 0.5), True)
        ctx.restore()
    elif kind == 'map':
        ctx.save()
        ctx.translate(x - 160, y + 120)
        ctx.scale(0.72, 0.72)
        draw_map(ctx, 0, 0, 1000, 600, info.T, pins=True, flags=True, aged=True,
                 empty_glow=ease((info.t - info.ls(0, 2)) / 3))
        ctx.restore()
        ctx.set_source_rgba(0, 0, 0, 0.25)
        ctx.paint()
        g = cairo.RadialGradient(x + w / 2, y + h / 2, 30, x + w / 2, y + h / 2, 400)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.15)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.5)
        ctx.set_source(g)
        ctx.paint()
    ctx.restore()


def seq_laptop(ctx, info, content):
    ctx.set_source_rgb(*hexc('2a2420'))
    ctx.paint()
    box(ctx, 150, 50, 980, 600, hexc('2a2a30'), 4, 20)
    ctx.rectangle(180, 80, 920, 540)
    ctx.set_source_rgb(0.97, 0.97, 0.97)
    ctx.fill()
    box(ctx, 80, 650, 1120, 40, hexc('3a3a42'), 3, 10)
    content(ctx, info)


def _cache_page(ctx, info):
    box(ctx, 180, 80, 920, 70, hexc('1d3557'), 0)
    text(ctx, 'Gymnázium Sokolí  ·  Zeměpisná soutěž', 210, 125, 26, (1, 1, 1), True)
    text(ctx, 'Zeměpisná keška týdne č. 4', 220, 210, 34, (0.1, 0.1, 0.15), True)
    text(ctx, 'N 49°36.214′   E 13°12.881′', 220, 290, 40, (0.75, 0.1, 0.1), True, 'DejaVu Sans Mono')
    text(ctx, 'Nápověda: „Kde voda spí pod kamenem.“', 220, 360, 28, (0.2, 0.2, 0.25), False, italic=True)
    text(ctx, 'Kdo najde krabičku první, má jedničku!  — R. Kříženecký', 220, 430, 22, (0.3, 0.3, 0.35))
    # kurzor
    cx = 400 + 200 * math.sin(info.t * 0.5)
    ctx.move_to(cx, 300)
    ctx.line_to(cx, 324)
    ctx.line_to(cx + 7, 318)
    ctx.line_to(cx + 12, 328)
    ctx.line_to(cx + 15, 326)
    ctx.line_to(cx + 10, 316)
    ctx.line_to(cx + 18, 316)
    ctx.close_path()
    fill_stroke(ctx, (1, 1, 1), 1.5)


def seq_map_cache(ctx, info):
    t = info.t
    ctx.set_source_rgb(*hexc('2a2420'))
    ctx.paint()
    draw_map(ctx, 100, 60, 1080, 600, info.T, pins=False, labels=False)
    # vila, škola, lom
    text(ctx, 'Sokolí ul.', 180, 600, 18, (0.1, 0.1, 0.1), True)
    ctx.arc(200, 560, 10, 0, 6.3)
    fill_stroke(ctx, hexc('2c3e50'), 2)
    k = ease(t / 4)
    # trasa auta
    ctx.set_source_rgba(0.85, 0.1, 0.1, 0.9)
    ctx.set_line_width(4)
    ctx.set_dash([12, 8])
    ctx.move_to(200, 560)
    ex, ey = 200 + (770 - 200) * k, 560 + (215 - 560) * k
    ctx.curve_to(300, 500, 500, 300 + (1 - k) * 200, ex, ey)
    ctx.stroke()
    ctx.set_dash([])
    if t > 3:
        a = min(1, (t - 3) / 1)
        ctx.arc(770, 215, 22 + 4 * math.sin(info.T * 4), 0, 6.3)
        ctx.set_source_rgba(0.9, 0.05, 0.05, a)
        ctx.set_line_width(5)
        ctx.stroke()
        text(ctx, 'STARÝ LOM', 800, 210, 24, (0.6, 0, 0), True, alpha=a)
        text(ctx, 'N 49°36.214′  E 13°12.881′', 800, 240, 18, (0.3, 0.1, 0.1), False, 'DejaVu Sans Mono', alpha=a)


def seq_videocall(ctx, info, frozen=False):
    T = info.T
    ctx.set_source_rgb(*hexc('2a2420'))
    ctx.paint()
    box(ctx, 120, 40, 1040, 620, hexc('2a2a30'), 4, 20)
    ctx.rectangle(150, 70, 980, 560)
    ctx.set_source_rgb(*hexc('3a3a44'))
    ctx.fill()
    ctx.save()
    ctx.rectangle(150, 70, 980, 560)
    ctx.clip()
    # pozadí: knihovna paní profesorky
    ctx.set_source(lin(ctx, 0, 70, 0, 630, [(0, hexc('c8b89a')), (1, hexc('a89878'))]))
    ctx.paint()
    rng = random.Random(3)
    for shelf in range(3):
        yy = 150 + shelf * 140
        box(ctx, 150, yy + 90, 980, 10, hexc('6a4a30'), 1.5)
        bx = 160
        while bx < 1120:
            bw = rng.randint(14, 30)
            bh = rng.randint(55, 85)
            box(ctx, bx, yy + 90 - bh, bw, bh, hexc(rng.choice(['8a2a2a', '2a4a7a', '4a6a3a', 'a07030', '5a3a6a'])),
                1.2)
            bx += bw + 3
    if frozen:
        mood, mouth, lx = 'n', 0.0, -0.8
    else:
        mood = 'n'
        L = None
        for LL in info.lines:
            if LL['start'] <= T:
                L = LL
        mood = (L['mood'] if L and L['who'] == 'SEBESTOVA' and L['mood'] else 'happy') if L else 'happy'
        mouth = info.amp('SEBESTOVA')
        lx = 0.0
    lk = look('SEBESTOVA')
    st = dict(x=640, y=640 + lk.H * 2.4 * 0.42, scale=2.4, facing=1, pose='stand', mood=mood, mouth=mouth,
              t=T if not frozen else info.t0, look_x=lx)
    draw_character(ctx, lk, st)
    ctx.restore()
    # malé okno Viktor
    box(ctx, 920, 440, 190, 170, hexc('d9cdb5'), 2, 6)
    ctx.save()
    rrect(ctx, 920, 440, 190, 170, 6)
    ctx.clip()
    lv = look('VIKTOR')
    draw_character(ctx, lv, dict(x=1015, y=610 + lv.H * 0.7 * 0.3, scale=0.7, facing=-1, mood='worried' if not
                                 frozen else 'scared', mouth=info.amp('VIKTOR'), t=T))
    ctx.restore()
    # lišta hovoru
    box(ctx, 150, 590, 980, 40, (0, 0, 0, 0.5), 0)
    text(ctx, 'Mgr. Jarmila Šebestová', 170, 617, 18, (1, 1, 1), True)
    text(ctx, '● REC' if False else '00:%02d:%02d' % (int(info.t) // 60, int(info.t) % 60), 1040, 617, 16,
         (0.8, 0.8, 0.8))
    if frozen:
        ctx.set_source_rgba(0, 0, 0, 0.35)
        ctx.rectangle(150, 70, 980, 560)
        ctx.fill()
        text(ctx, 'Hovor ukončen', 640, 360, 40, (1, 1, 1), True, center=True)


def seq_kunes_notebook(ctx, info):
    ctx.set_source_rgb(*hexc('5a3a22'))
    ctx.paint()
    ctx.save()
    ctx.translate(640, 380)
    ctx.rotate(-0.04)
    box(ctx, -420, -300, 840, 600, hexc('f6f0dc'), 3, 6)
    ctx.set_source_rgba(0.3, 0.4, 0.8, 0.35)
    ctx.set_line_width(1.2)
    for i in range(14):
        ctx.move_to(-400, -240 + i * 38)
        ctx.line_to(400, -240 + i * 38)
    ctx.stroke()
    ctx.set_source_rgba(0.85, 0.2, 0.2, 0.5)
    ctx.move_to(-330, -300)
    ctx.line_to(-330, 300)
    ctx.stroke()
    entries = ['Po 21:47 — kluk s červeným kolem jde', 'k učiteli do garáže. NEVYŠEL.',
               'Po 23:10 — učitel stříká garáž.', '', 'Po (o týden) 19:32 — kluk s brýlemi',
               'nastoupil u zastávky do ČERVENÉHO auta.', 'Auto jelo do LESA.', '',
               'Čt — červené auto u školy, místo pro učitele.']
    L = info.lines[0] if info.lines else None
    k = 1.0
    if L:
        k = max(0, min(1, (info.T - L['start']) / max(1, L['end'] - L['start'])))
    n = int(len(entries) * k + 0.999) if info.T >= (L['start'] if L else 0) else 0
    for i, e in enumerate(entries[:max(n, 1)]):
        text(ctx, e, -310, -250 + i * 38 + 30, 26, (0.12, 0.12, 0.35), False, 'DejaVu Serif', italic=True)
    ctx.restore()


def seq_chem_test(ctx, info):
    t = info.t
    ctx.set_source_rgb(*hexc('d5e0d0'))
    ctx.paint()
    # TLC destička
    box(ctx, 380, 100, 520, 520, hexc('f4f4ee'), 3, 6)
    text(ctx, 'vzorek', 470, 600, 20, (0.2, 0.2, 0.2), True, center=True)
    text(ctx, 'skopolamin', 640, 600, 20, (0.2, 0.2, 0.2), True, center=True)
    text(ctx, 'atropin', 810, 600, 20, (0.2, 0.2, 0.2), True, center=True)
    front = 560 - min(1, t / 4) * 420
    ctx.rectangle(383, front, 514, 560 - front)
    ctx.set_source_rgba(0.6, 0.75, 0.9, 0.25)
    ctx.fill()
    for i, (x, spots) in enumerate(((470, [0.35, 0.62]), (640, [0.62]), (810, [0.35]))):
        ctx.arc(x, 560, 6, 0, 6.3)
        ctx.set_source_rgb(0.4, 0.4, 0.4)
        ctx.fill()
        for s in spots:
            y = 560 - s * 420
            if y > front:
                a = min(1, (y - front) / 40 + 0.2) if t > 1 else 0
                ctx.save()
                ctx.translate(x, y)
                ctx.scale(1.4, 1)
                ctx.arc(0, 0, 14, 0, 6.3)
                ctx.restore()
                ctx.set_source_rgba(0.55, 0.15, 0.5, 0.85 * a)
                ctx.fill()
    if t > 4:
        a = min(1, (t - 4))
        ctx.set_source_rgba(0.9, 0.1, 0.1, a)
        ctx.set_line_width(3)
        ctx.set_dash([8, 6])
        ctx.move_to(440, 560 - 0.62 * 420)
        ctx.line_to(680, 560 - 0.62 * 420)
        ctx.stroke()
        ctx.set_dash([])
        text(ctx, 'SHODA', 920, 560 - 0.62 * 420 + 8, 30, (0.8, 0, 0), True, alpha=a)


def seq_archive_file(ctx, info):
    T, t = info.T, info.t
    ctx.set_source_rgb(*hexc('4a3a28'))
    ctx.paint()
    ctx.save()
    ctx.translate(640, 370)
    ctx.rotate(0.02)
    box(ctx, -470, -320, 940, 640, hexc('d8c48a'), 3, 8)
    box(ctx, -440, -290, 880, 590, hexc('f6f2e4'), 2, 2)
    text(ctx, 'OSOBNÍ SPIS — Mgr. Radovan KŘÍŽENECKÝ', -410, -240, 26, (0.1, 0.1, 0.1), True, 'DejaVu Serif')
    rows = [('2001–2004', 'Gymnázium Sušice', '2 studenti „odstěhováni“'),
            ('2006–2010', 'Gymnázium Domažlice', '1 student „odstěhován“'),
            ('2012–2016', 'Gymnázium Tachov', '2 studenti „odstěhováni“'),
            ('2018–', 'Gymnázium Sokolí', '???')]
    n = 0
    for L in info.lines:
        if L['start'] <= T:
            n = len(rows) * min(1, (T - L['start']) / max(1, L['end'] - L['start'])) if L['who'] == 'BOUCNIK' else 4
    for i, (y_, s, note) in enumerate(rows):
        if i < n + 0.5:
            yy = -170 + i * 70
            text(ctx, y_, -400, yy, 24, (0.15, 0.15, 0.2), False, 'DejaVu Sans Mono')
            text(ctx, s, -200, yy, 24, (0.1, 0.1, 0.1), True, 'DejaVu Serif')
            text(ctx, note, 140, yy, 22, (0.7, 0.1, 0.1), False, 'DejaVu Serif', italic=True)
    if info.T > info.ls(1, 1e9) + info.t0:
        ctx.save()
        ctx.translate(280, 200)
        ctx.rotate(-0.2)
        rrect(ctx, -150, -40, 300, 80, 8)
        ctx.set_source_rgba(0.8, 0.1, 0.1, 0.8)
        ctx.set_line_width(5)
        ctx.stroke()
        text(ctx, 'NEZVĚSTNÍ', 0, 16, 40, (0.8, 0.1, 0.1), True, center=True, alpha=0.8)
        ctx.restore()
    ctx.restore()


def seq_office(ctx, info, dark=False):
    T, t = info.T, info.t
    ctx.save()
    with_cam(ctx, 750, 290, 3.6 + t * 0.02)
    window_scene(ctx, 'night', T, office_light=not dark)
    if not dark:
        # siluety v okně ředitelny
        ctx.save()
        ctx.rectangle(749, 267, 44, 58)
        ctx.clip()
        hx = 758 + math.sin(t * 2.2) * 2
        kx = 784
        for (x, hh, wobble) in ((hx, 40, math.sin(t * 5) * 1.5), (kx, 46, 0)):
            ctx.arc(x + wobble, 325 - hh, 5.5, 0, 6.3)
            ctx.set_source_rgba(0.05, 0.03, 0.02, 0.9)
            ctx.fill()
            rrect(ctx, x - 7, 330 - hh + 4, 14, hh, 4)
            ctx.fill()
        # ruka ředitele ukazuje
        if int(t * 1.5) % 3 == 0:
            ctx.move_to(hx + 5, 300)
            ctx.line_to(hx + 15, 292)
            ctx.set_line_width(3)
            ctx.stroke()
        ctx.restore()
    ctx.restore()
    window_frame_overlay(ctx, 'night')


def seq_flash(ctx, info, kind):
    """rychlé záblesky vzpomínek — odbarvené"""
    t = info.t
    if kind == 'keychain':
        ctx.set_source_rgb(*hexc('8fb0c0'))
        ctx.paint()
        fig(ctx, 'BRABEC', 640, 1100, 2.2, 1, True, info.T, mood='happy')
        ctx.save()
        ctx.translate(820 + math.sin(info.T * 6) * 10, 520)
        ctx.rotate(math.sin(info.T * 6) * 0.4)
        rrect(ctx, -10, 0, 20, 160, 8)
        fill_stroke(ctx, (0.82, 0.82, 0.86), 3)
        ctx.move_to(-10, 160)
        ctx.curve_to(-40, 190, -30, 240, 0, 255)
        ctx.curve_to(30, 240, 40, 190, 10, 160)
        ctx.close_path()
        fill_stroke(ctx, (0.82, 0.82, 0.86), 3)
        ctx.restore()
    elif kind == 'essay':
        ctx.set_source_rgb(*hexc('f6f2e4'))
        ctx.paint()
        ctx.set_source_rgba(0.3, 0.4, 0.8, 0.3)
        for i in range(16):
            ctx.rectangle(0, 60 + i * 42, W, 1.5)
        ctx.fill()
        essay = ['Úvaha: Co nám říká krajina, ve které žijeme', 'Krajina není jen mapa. Je to paměť lidí,',
                 'kteří v ní žili, a stop, které v ní nechali.', 'Když se díváme dost dlouho, krajina nám',
                 'začne vyprávět. O lesích, o cestách, o lidech,', 'kteří jimi chodili — a o těch, kteří se už',
                 'nevrátili.  Viktor Skácel, 2.A']
        for i, ln in enumerate(essay):
            text(ctx, ln, 120, 100 + i * 42, 26, (0.2, 0.2, 0.3), False, 'DejaVu Serif', italic=True)
        text(ctx, 'Skvělá práce, Viktore. Uzdrav se.', 160, 500, 38, (0.8, 0.1, 0.1), False, 'DejaVu Serif', italic=True)
        text(ctx, 'S pozdravem a přáním klidných dnů, J. Š.', 160, 560, 38, (0.8, 0.1, 0.1), False, 'DejaVu Serif',
             italic=True)
        ctx.rectangle(150, 525, 900, 50)
        ctx.set_source_rgba(1, 0.9, 0.1, 0.35)
        ctx.fill()
    elif kind == 'redcar':
        ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, hexc('9ab0c0')), (1, hexc('6a7078'))]))
        ctx.paint()
        car(ctx, 640, 600, 2.4, hexc('c0392b'), 1)
        box(ctx, 860, 120, 300, 110, (1, 1, 1), 3, 6)
        text(ctx, 'PARKOVÁNÍ', 1010, 160, 24, (0.1, 0.2, 0.5), True, center=True)
        text(ctx, 'Mgr. J. Šebestová', 1010, 205, 28, (0.1, 0.1, 0.1), True, center=True)
        box(ctx, 1003, 230, 14, 200, hexc('7a7a7a'), 2)
    elif kind == 'promise':
        seq_videocall(ctx, info, frozen=False)
    elif kind == 'tea':
        draw_set(ctx, 'sborovna', 'day', info.T)
        fig(ctx, 'SEBESTOVA', 520, 760, 1.25, 1, t=info.T, mood='happy', prop='thermos')
        fig(ctx, 'SIMON', 860, 760, 1.25, -1, t=info.T, mood='happy')
    # odbarvení + záblesk
    ctx.set_operator(cairo.OPERATOR_HSL_SATURATION)
    ctx.set_source_rgba(0.5, 0.5, 0.5, 0.75)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)
    if t < 0.25:
        ctx.set_source_rgba(1, 1, 1, 1 - t / 0.25)
        ctx.paint()
    ctx.set_source_rgba(0.1, 0.05, 0.0, 0.2)
    ctx.paint()


def seq_fever_dream(ctx, info):
    T, t = info.T, info.t
    ctx.set_source(rad(ctx, 640, 360, 50, 800, [(0, hexc('5a1a3a')), (0.5, hexc('2a0a2a')), (1, hexc('05000a'))]))
    ctx.paint()
    # spirála špendlíků
    for i in range(60):
        a = i * 0.5 + t * 0.4
        r = 30 + i * 9 + 20 * math.sin(t + i)
        x = 640 + math.cos(a) * r
        y = 360 + math.sin(a) * r * 0.7
        ctx.arc(x, y, 6 + (i % 4), 0, 6.3)
        ctx.set_source_rgba(0.9, 0.1, 0.15, 0.8)
        ctx.fill()
    # obří glóbus
    ctx.save()
    ctx.translate(640, 330)
    s = 1 + 0.08 * math.sin(t * 1.3)
    ctx.scale(s, s)
    ctx.arc(0, 0, 150, 0, 6.3)
    fill_stroke(ctx, hexc('2a5a8a'), 4)
    ctx.arc(0, 0, 150, 0, 6.3)
    ctx.clip()
    for i in range(6):
        ox = ((t * 60 + i * 110) % 660) - 330
        ctx.save()
        ctx.translate(ox, -60 + (i % 3) * 50)
        ctx.scale(1.4, 0.8)
        ctx.arc(0, 0, 40, 0, 6.3)
        ctx.restore()
        ctx.set_source_rgb(*hexc('4a8a4a'))
        ctx.fill()
    ctx.reset_clip()
    ctx.restore()
    # obří stín učitele
    a = 0.5 + 0.3 * math.sin(t * 0.7)
    ctx.save()
    ctx.translate(640 + math.sin(t * 0.3) * 200, 760)
    ctx.scale(3.2, 3.2)
    ctx.arc(0, -150, 30, 0, 6.3)
    ctx.set_source_rgba(0, 0, 0, a)
    ctx.fill()
    rrect(ctx, -45, -118, 90, 140, 30)
    ctx.fill()
    ctx.restore()
    # hrnky čaje létající
    for i in range(5):
        x = (i * 300 + t * 70) % 1500 - 100
        y = 140 + 90 * math.sin(t + i * 2)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(t + i)
        rrect(ctx, -22, -18, 44, 40, 8)
        fill_stroke(ctx, hexc('f4f0e8'), 3)
        ctx.arc(26, 0, 12, -1.5, 1.5)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.restore()
    # zvlnění — pruhy
    for i in range(0, H, 6):
        dx = math.sin(i * 0.03 + t * 3) * 8
        ctx.set_source_rgba(0.3, 0, 0.3, 0.05)
        ctx.rectangle(dx, i, W, 3)
        ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.08 * (1 + math.sin(t * 7)))
    ctx.paint()


def seq_window_man(ctx, info, empty=False):
    T, t = info.T, info.t
    ctx.save()
    with_cam(ctx, 200, 470, 2.8)
    window_scene(ctx, 'night', T, villa_lights=False)
    if not empty:
        l1 = info.ls(1, 5)
        g = ease((t - l1) / 3.0)
        lk = look('KRIZENECKY')
        draw_character(ctx, lk, dict(x=190, y=515, scale=0.2, facing=1, t=T, mood='n', gest=g * 1.0, look_x=0))
        # zdvižená ruka jako silueta
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0.05, 0.35)
    ctx.paint()
    window_frame_overlay(ctx, 'night')


def seq_doubt(ctx, info):
    t = info.t
    seg = int(t / 1.6) % 4
    tt = t % 1.6
    if seg == 0:
        ctx.save()
        with_cam(ctx, 430, 500, 1.8)
        window_scene(ctx, 'night', info.T, garage_open=1, garage_light=True)
        ctx.restore()
    elif seg == 1:
        seq_phone_photo(ctx, info, 'keychain')
    elif seg == 2:
        ctx.save()
        with_cam(ctx, 1000, 520, 2.0)
        window_scene(ctx, 'night', info.T)
        car(ctx, 1060, 625, 0.4, hexc('c0392b'), 1, lights=True)
        ctx.restore()
    else:
        seq_garage_map(ctx, info)
    # glitch
    rng = random.Random(int(info.T * 12))
    for i in range(8):
        y = rng.uniform(0, H)
        ctx.set_source_rgba(rng.random(), 0, rng.random(), 0.2)
        ctx.rectangle(0, y, W, rng.uniform(2, 14))
        ctx.fill()
    ctx.set_operator(cairo.OPERATOR_HSL_SATURATION)
    ctx.set_source_rgba(0.5, 0.5, 0.5, 0.9)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)
    a = 0.4 + 0.3 * math.sin(t * 4)
    text(ctx, '?', 640, 470, 300, (1, 1, 1), True, center=True, alpha=a * 0.6)


def seq_photo_overlay(ctx, info):
    t = info.t
    ctx.set_source_rgb(*hexc('2a2420'))
    ctx.paint()
    draw_map(ctx, 100, 60, 1080, 600, info.T, pins=t > 1.0, flags=False, labels=t > 3,
             highlight=11 if t > info.ls(1, 6) else None)


def seq_race_map(ctx, info):
    ctx.set_source_rgb(*hexc('2a2420'))
    ctx.paint()
    draw_map(ctx, 100, 60, 1080, 600, info.T, pins=False)
    pts = [(0.08, 0.92), (0.2, 0.7), (0.3, 0.5), (0.45, 0.62), (0.5, 0.35), (0.62, 0.45), (0.58, 0.2),
           (0.68, 0.32), (0.8, 0.5), (0.85, 0.3), (0.74, 0.14)]
    k = min(1, info.t / 3)
    n = max(1, int(len(pts) * k))
    ctx.set_source_rgb(0.75, 0.1, 0.55)
    ctx.set_line_width(3)
    for i, (px, py) in enumerate(pts[:n]):
        X, Y = 100 + px * 1080, 60 + py * 600
        if i == 0:
            ctx.move_to(X + 20, Y)
            ctx.line_to(X, Y - 30)
            ctx.line_to(X - 20, Y)
            ctx.close_path()
            ctx.stroke()
        else:
            ctx.arc(X, Y, 18, 0, 6.3)
            ctx.stroke()
            text(ctx, str(i), X + 20, Y - 14, 18, (0.75, 0.1, 0.55), True)
        if i > 0:
            pX, pY = 100 + pts[i - 1][0] * 1080, 60 + pts[i - 1][1] * 600
            ctx.move_to(pX, pY)
            ctx.line_to(X, Y)
            ctx.stroke()
    if n == len(pts):
        X, Y = 100 + 0.74 * 1080, 60 + 0.14 * 600
        ctx.arc(X, Y, 26 + 4 * math.sin(info.T * 5), 0, 6.3)
        ctx.set_source_rgba(0.9, 0.05, 0.05, 1)
        ctx.set_line_width(5)
        ctx.stroke()
        text(ctx, '11 — POSLEDNÍ KONTROLA', X - 360, Y + 10, 26, (0.7, 0, 0), True)
    text(ctx, 'NOČNÍ ORIENŤÁK — Sokolí les', 130, 110, 30, (0.1, 0.1, 0.1), True)


def seq_peephole(ctx, info, call=False):
    T = info.T
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    ctx.save()
    ctx.arc(640, 360, 330, 0, 6.3)
    ctx.clip()
    ctx.translate(640, 360)
    ctx.scale(1.0, 1.0)
    ctx.translate(-640, -360)
    # chodba paneláku
    ctx.set_source(rad(ctx, 640, 300, 50, 500, [(0, hexc('a8a890')), (1, hexc('3a3a30'))]))
    ctx.paint()
    box(ctx, 380, 120, 520, 600, hexc('8a8a7a'), 3)
    ctx.move_to(250, 720)
    ctx.line_to(400, 520)
    ctx.line_to(880, 520)
    ctx.line_to(1030, 720)
    ctx.close_path()
    ctx.set_source_rgb(*hexc('6a5a4a'))
    ctx.fill()
    mood = 'happy' if not call else 'angry'
    L = None
    for LL in info.lines:
        if LL['start'] <= T:
            L = LL
    if L and L['mood']:
        mood = L['mood']
    lk = look('SEBESTOVA')
    draw_character(ctx, lk, dict(x=640, y=900, scale=1.9, facing=-1 if call else 1, mood=mood,
                                 mouth=info.amp('SEBESTOVA'), t=T, prop='phone' if call else 'thermos'))
    ctx.restore()
    # rybí oko — vinětace
    g = cairo.RadialGradient(640, 360, 180, 640, 360, 340)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(0.85, 0, 0, 0, 0.5)
    g.add_color_stop_rgba(1, 0, 0, 0, 1)
    ctx.set_source(g)
    ctx.arc(640, 360, 335, 0, 6.3)
    ctx.fill()


def seq_quarry_fall(ctx, info):
    T, t = info.T, info.t
    draw_set(ctx, 'quarry', 'night', T)
    lk = look('KRIZENECKY')
    if t < 0.8:
        x, y, rot = 790, 645, 0
    else:
        u = min(1, (t - 0.8) / 1.0)
        x = 790 + u * 80
        y = 645 + u * u * 200
        rot = u * 1.8
    if t < 2.0:
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        draw_character(ctx, lk, dict(x=0, y=0, scale=1.0, facing=1, t=T, mood='scared', gest=1.0))
        ctx.restore()
    # padající kamení
    for i in range(8):
        if t > 0.6:
            u = t - 0.6
            ctx.arc(780 + i * 12, 640 + u * u * 300 + i * 10, 6, 0, 6.3)
            fill_stroke(ctx, hexc('5a5a60'), 1.5)
    sp = info.sfx_t('splash', default=2.0)
    if t > sp - 0.1:
        u = t - sp
        for i in range(30):
            a = -math.pi * (0.1 + 0.8 * i / 29)
            r = u * 260 * (0.6 + 0.4 * ((i * 7) % 5) / 4)
            X = 870 + math.cos(a) * r
            Y = 700 + math.sin(a) * r + 300 * u * u
            if Y < 720:
                ctx.arc(X, Y, 5, 0, 6.3)
                ctx.set_source_rgba(0.75, 0.9, 1, max(0, 1 - u / 2))
                ctx.fill()
        for k in range(3):
            rr = u * 120 + k * 30
            ctx.save()
            ctx.translate(870, 700)
            ctx.scale(1, 0.2)
            ctx.arc(0, 0, rr, 0, 6.3)
            ctx.restore()
            ctx.set_source_rgba(0.75, 0.9, 1, max(0, 0.6 - u / 4))
            ctx.set_line_width(3)
            ctx.stroke()
    ctx.set_source_rgba(0.6, 0.65, 0.75, 0.15)
    ctx.paint()


def seq_quarry_arrest(ctx, info):
    T, t = info.T, info.t
    draw_set(ctx, 'quarry', 'night', T)
    fig(ctx, 'BURES', 520, 645, 1.0, 1, t=T, mood='n', mouth=info.amp('BURES'))
    fig(ctx, 'KRIZENECKY', 680, 645, 1.0, -1, t=T, mood='angry')
    # pouta
    ctx.arc(640, 470, 10, 0, 6.3)
    ctx.set_source_rgb(0.75, 0.75, 0.8)
    ctx.set_line_width(4)
    ctx.stroke()
    # mokrý
    ctx.set_source_rgba(0.4, 0.6, 0.9, 0.25)
    rrect(ctx, 620, 280, 120, 360, 30)
    ctx.fill()
    police_flash(ctx, T)


def police_flash(ctx, T):
    ph = (T * 2.5) % 1
    col = (0.1, 0.3, 1.0) if ph < 0.5 else (1.0, 0.1, 0.1)
    a = 0.22 * abs(math.sin(T * 2.5 * math.pi))
    g = cairo.RadialGradient(1200 if ph < 0.5 else 80, 100, 50, 640, 360, 1100)
    g.add_color_stop_rgba(0, *col, a * 1.6)
    g.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(g)
    ctx.paint()


def seq_memorial(ctx, info):
    T = info.T
    ctx.set_source_rgb(*hexc('1a1410'))
    ctx.paint()
    box(ctx, 80, 470, 1120, 250, hexc('3a2a1e'), 3)
    for i, (name, who) in enumerate((('Matěj Brabec', 'BRABEC'), ('Kryštof Mlejnek', 'MLEJNEK'),
                                     ('Zdeněk Hruban', 'HRUBAN'))):
        x = 290 + i * 350
        box(ctx, x - 110, 160, 220, 270, hexc('1a1a1a'), 4, 4)
        ctx.save()
        ctx.rectangle(x - 96, 174, 192, 200)
        ctx.clip()
        ctx.set_source_rgb(0.8, 0.8, 0.78)
        ctx.paint()
        lk = look(who)
        draw_character(ctx, lk, dict(x=x, y=174 + 200 + lk.H * 0.62, scale=1.05, facing=1, t=0, mood='happy'))
        ctx.restore()
        ctx.set_operator(cairo.OPERATOR_HSL_SATURATION)
        ctx.set_source_rgba(0.5, 0.5, 0.5, 1)
        ctx.rectangle(x - 96, 174, 192, 200)
        ctx.fill()
        ctx.set_operator(cairo.OPERATOR_OVER)
        text(ctx, name, x, 405, 20, (0.9, 0.9, 0.85), True, center=True)
        # svíčka
        box(ctx, x - 14, 480, 28, 70, hexc('f4f0e0'), 2, 4)
        fl = 1 + 0.15 * math.sin(T * 13 + i)
        ctx.save()
        ctx.translate(x, 470)
        ctx.scale(1, fl)
        ctx.move_to(0, -26)
        ctx.curve_to(10, -10, 8, 4, 0, 6)
        ctx.curve_to(-8, 4, -10, -10, 0, -26)
        ctx.restore()
        ctx.set_source_rgb(1, 0.75, 0.2)
        ctx.fill()
        lamp_glow(ctx, x, 465, 160, (1, 0.7, 0.3), 0.35)
    # černá stuha
    ctx.move_to(0, 0)
    ctx.line_to(140, 0)
    ctx.line_to(0, 140)
    ctx.close_path()
    ctx.set_source_rgb(0.05, 0.05, 0.05)
    ctx.fill()


def seq_villa(ctx, info, truck=False):
    T, t = info.T, info.t
    ctx.save()
    if not truck:
        with_cam(ctx, 300, 450, 1.8 + t * 0.01)
        window_scene(ctx, 'night', T, sale=True, villa_lights=False)
    else:
        with_cam(ctx, 330, 520, 2.4)
        window_scene(ctx, 'night', T, sale=True, villa_lights=True)
        vx = kf([(0, -200), (3, 260), (info.dur, 260)], t)[0]
        _truck(ctx, vx, 625, 0.5)
        if t > 3.5:
            px = kf([(3.5, 300), (info.dur, 270)], t)[0]
            # neznámá postava — silueta
            ctx.save()
            ctx.translate(px, 590)
            ctx.arc(0, -64, 9, 0, 6.3)
            ctx.set_source_rgb(0.05, 0.05, 0.07)
            ctx.fill()
            rrect(ctx, -10, -55, 20, 55, 6)
            ctx.fill()
            box(ctx, -14, -48, 28, 22, hexc('b08a5a'), 1.5)
            ctx.restore()
    ctx.restore()
    window_frame_overlay(ctx, 'night')


def _truck(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    box(ctx, -150, -150, 200, 130, (0.9, 0.9, 0.88), 4, 6)
    text(ctx, 'STĚHOVÁNÍ', -50, -80, 22, (0.2, 0.3, 0.6), True, center=True)
    ctx.move_to(50, -110)
    ctx.line_to(110, -110)
    ctx.line_to(140, -60)
    ctx.line_to(140, -20)
    ctx.line_to(50, -20)
    ctx.close_path()
    fill_stroke(ctx, hexc('3a5a8a'), 4)
    for wx in (-100, 90):
        ctx.arc(wx, -18, 22, 0, 6.3)
        fill_stroke(ctx, (0.1, 0.1, 0.1), 3)
    ctx.restore()


def seq_binoculars_globe(ctx, info):
    T = info.T

    def draw(c):
        window_scene(c, 'night', T, sale=True)
        _truck(c, 260, 625, 0.5)
        c.save()
        c.translate(272, 590)
        c.arc(0, -64, 9, 0, 6.3)
        c.set_source_rgb(0.05, 0.05, 0.07)
        c.fill()
        rrect(c, -10, -55, 20, 55, 6)
        c.fill()
        box(c, -14, -48, 28, 22, hexc('b08a5a'), 1.0)
        c.arc(0, -52, 10, 0, 6.3)
        fill_stroke(c, hexc('2a5a8a'), 1.0)
        c.arc(0, -52, 10, 0, 6.3)
        c.clip()
        c.arc(-3 + math.sin(T) * 3, -54, 5, 0, 6.3)
        c.set_source_rgb(*hexc('4a8a4a'))
        c.fill()
        c.restore()
    binocular_view(ctx, info, 272, 545, 8.0, draw)


def seq_phone_final(ctx, info):
    room_blur_bg(ctx, info, 'night')
    x, y, w, h = 440, 40, 400, 680
    phone_frame(ctx, x, y, w, h)
    ctx.rectangle(x, y + 44, w, h - 44)
    ctx.set_source_rgb(0.08, 0.08, 0.12)
    ctx.fill()
    a = min(1, info.t / 0.6)
    box(ctx, x + 16, y + 120, w - 32, 220, (0.97, 0.97, 0.98), 1.5, 16)
    text(ctx, 'Gymnázium Sokolí · Soutěž', x + 34, y + 155, 15, (0.4, 0.4, 0.45), True)
    text(ctx, 'Zeměpisná keška týdne č. 5', x + 34, y + 190, 19, (0.1, 0.1, 0.1), True)
    text(ctx, 'N 49°37.001′  E 13°13.474′', x + 34, y + 230, 17, (0.75, 0.1, 0.1), True, 'DejaVu Sans Mono')
    text(ctx, 'Nápověda:', x + 34, y + 270, 16, (0.2, 0.2, 0.2), True)
    text(ctx, '„Poslední kontrola ještě nebyla.“', x + 34, y + 300, 17, (0.2, 0.2, 0.2), italic=True)
    text(ctx, 'Odesílatel: neznámý', x + 34, y + 326, 13, (0.5, 0.5, 0.5))
    lamp_glow(ctx, 640, 300, 400, (0.6, 0.7, 1.0), 0.1 * a)


def seq_credits(ctx, info):
    t = info.t
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    cast = [
        ('POSLEDNÍ KONTROLA', None), ('', None), ('Hrají (hlasy XTTS v2)', None), ('', None),
        ('Viktor Skácel', 'student, 16 let'), ('Šimon Pokorný', 'jeho nejlepší kamarád'),
        ('Helena Skácelová', 'máma, zdravotní sestra'), ('Beata Skácelová', 'sestra, skoro 10 let'),
        ('Mgr. Radovan Kříženecký', 'učitel zeměpisu'), ('Mgr. Jarmila Šebestová', 'učitelka češtiny'),
        ('paní Kunešová', 'sousedka'), ('praporčík Tomáš Bureš', 'policie ČR'),
        ('Bohumil Liškutín', 'tělocvikář'), ('profesor Vařejka', 'dějepis'), ('pan Boucník', 'matrikář'),
        ('Mgr. Chovancová', 'chemie'), ('PaedDr. Zdeněk Hruban', 'ředitel'), ('MUDr. Fialová', 'nemocnice'),
        ('Kubička Zemanová', '2.A'), ('Oleksii', '2.A'), ('David Kovář', '2.A'), ('Pazdera', '2.A'),
        ('Pavel Blaška', '2.A'), ('Matěj Brabec', '2.A'), ('Kryštof Mlejnek', '2.A'), ('Klára Rybářová', '2.B'),
        ('Bobík', 'pes'), ('', None), ('', None),
        ('Námět a postava Šimona Pokorného', None), ('Šimon Pokorný', ''), ('', None),
        ('Scénář, animace, hudba, střih', None), ('Claude (Anthropic)', ''), ('', None),
        ('Všechny postavy a události jsou smyšlené.', None), ('', None), ('', None), ('KONEC', None),
    ]
    y = H + 40 - t * 52
    for a, b in cast:
        if b is None:
            text(ctx, a, 640, y, 34 if a in ('POSLEDNÍ KONTROLA', 'KONEC') else 26, (0.9, 0.88, 0.84), True,
                 center=True)
        else:
            ctx.select_font_face('DejaVu Sans', 0, 1)
            ctx.set_font_size(24)
            text(ctx, a, 620 - ctx.text_extents(a).x_advance, y, 24, (1, 1, 1), True)
            if b:
                text(ctx, b, 660, y, 22, (0.7, 0.7, 0.7), False)
            # zarovnat jméno doprava
        y += 46
    if y < H / 2 - 40:
        pass


SEQS = {
    'prolog_map': seq_prolog_map,
    'window_intro': seq_window_intro,
    'binoculars_intro': seq_binoculars_intro,
    'bike_garage': seq_bike_garage,
    'clock_2310': lambda c, i: seq_clock(c, i, '23:10'),
    'garage_hose': seq_garage_hose,
    'phone_mail_brabec': lambda c, i: seq_phone_mail(
        c, i, 'Vedení školy — Gymnázium Sokolí', 'Informace o studentovi 2.A',
        'Vážení studenti, Matěj Brabec ze 2.A se z rodinných důvodů nečekaně přestěhoval k otci do Anglie. '
        'Přejeme mu mnoho úspěchů. S pozdravem a přáním klidných dnů, vedení školy'),
    'binoculars_bike': lambda c, i: binocular_view(c, i, 410, 500, 7.0, lambda cc: (
        window_scene(cc, 'day', i.T, garage_open=0.45), _bike(cc, 405, 518, 0.4),
        box(cc, 392, 488, 14, 6, hexc('1f6fb0'), 0.8))),
    'liskutin_fire': seq_liskutin_fire,
    'car_forest': seq_car_forest,
    'laptop_cache': lambda c, i: seq_laptop(c, i, _cache_page),
    'map_cache': seq_map_cache,
    'phone_chat_cache': lambda c, i: seq_phone_chat(c, i, '2.A — třída 🧭', names={
        'KOVAR': 'David Kovář', 'OLEKSII': 'Oleksii', 'PAZDERA': 'Pazdera', 'ZEMANOVA': 'Kubička Zemanová'}),
    'phone_photo_keychain': lambda c, i: seq_phone_photo(c, i, 'keychain'),
    'flash_keychain': lambda c, i: seq_flash(c, i, 'keychain'),
    'videocall_sebestova': seq_videocall,
    'videocall_frozen': lambda c, i: seq_videocall(c, i, frozen=True),
    'red_car': seq_red_car,
    'binoculars_plate': seq_binoculars_plate,
    'red_car_leave': lambda c, i: seq_red_car(c, i, leave=True),
    'garage_approach': seq_garage_approach,
    'garage_map': seq_garage_map,
    'phone_photo_map': lambda c, i: seq_phone_photo(c, i, 'map'),
    'fever_dream': seq_fever_dream,
    'window_man': seq_window_man,
    'window_empty': lambda c, i: seq_window_man(c, i, empty=True),
    'doubt_montage': seq_doubt,
    'kunes_notebook': seq_kunes_notebook,
    'phone_chat_pazdera': lambda c, i: seq_phone_chat(c, i, 'Pazdera', names={'PAZDERA': 'Pazdera'}),
    'chem_test': seq_chem_test,
    'archive_file': seq_archive_file,
    'office_silhouettes': seq_office,
    'office_dark': lambda c, i: seq_office(c, i, dark=True),
    'phone_mail_hruban': lambda c, i: seq_phone_mail(
        c, i, 'Vedení školy — Gymnázium Sokolí', 'Smutná zpráva',
        'S hlubokým zármutkem oznamujeme, že pan ředitel Zdeněk Hruban včera večer tragicky zahynul po '
        'nešťastném pádu ze schodiště ve škole. Výuka je dnes zrušena. Zastupující ředitel Mgr. Přikryl. '
        'S pozdravem a přáním klidných dnů'),
    'flash_essay': lambda c, i: seq_flash(c, i, 'essay'),
    'flash_redcar': lambda c, i: seq_flash(c, i, 'redcar'),
    'flash_promise': lambda c, i: seq_flash(c, i, 'promise'),
    'flash_tea': lambda c, i: seq_flash(c, i, 'tea'),
    'photo_overlay': seq_photo_overlay,
    'race_map': seq_race_map,
    'phone_chat_klara': lambda c, i: seq_phone_chat(c, i, 'Kubička Zemanová', tod='night',
                                                    names={'ZEMANOVA': 'Kubička'}),
    'peephole_sebestova': seq_peephole,
    'peephole_call': lambda c, i: seq_peephole(c, i, call=True),
    'quarry_fall': seq_quarry_fall,
    'quarry_arrest': seq_quarry_arrest,
    'memorial': seq_memorial,
    'villa_sale': seq_villa,
    'moving_truck': lambda c, i: seq_villa(c, i, truck=True),
    'binoculars_globe': seq_binoculars_globe,
    'phone_final_cache': seq_phone_final,
    'credits': seq_credits,
}


def draw(name, ctx, info):
    fn = SEQS.get(name)
    if fn is None:
        ctx.set_source_rgb(0.1, 0, 0.1)
        ctx.paint()
        text(ctx, name, 640, 360, 40, (1, 1, 1), True, center=True)
        return
    fn(ctx, info)
