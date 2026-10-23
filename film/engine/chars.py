"""Postavy: definice vzhledu a kreslení „vystřihovánkových“ figurek v cairo."""
import math
import random

OUT = (0.10, 0.08, 0.10)  # barva obrysu


def hexc(h, a=None):
    h = h.lstrip('#')
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else c + (a,)


def mix(c1, c2, k):
    return tuple(c1[i] * (1 - k) + c2[i] * k for i in range(3))


def shade(c, k):
    """k<0 ztmavit, k>0 zesvětlit"""
    return mix(c, (0, 0, 0), -k) if k < 0 else mix(c, (1, 1, 1), k)


SKIN = {
    'light': hexc('f1c9a5'), 'fair': hexc('f5d6bd'), 'medium': hexc('dcae86'),
    'tan': hexc('c99069'), 'old': hexc('ecc6a8'), 'pale': hexc('efd9c8'),
}

# typ: 'm','f' dospělí, 'tm','tf' teenageři, 'cf' dítě, 'om','of' staří
CHARS = {
    'VIKTOR': dict(kind='tm', skin='light', hair='messy', hair_c='6b4a2f', top='hoodie', top_c='3e6e57',
                   bottom_c='4a5878', shoe_c='e8e8e8', eye_c='3b6e8f'),
    'SIMON': dict(kind='tm', skin='light', hair='quiff', hair_c='c9a35a', top='jacket', top_c='d9663b',
                  under_c='f2f2f2', bottom_c='3c5a86', shoe_c='222222', eye_c='5a8a4a'),
    'HELENA': dict(kind='f', skin='light', hair='bob', hair_c='8a3b25', top='cardigan', top_c='5f9ea0',
                   under_c='efe6d8', bottom_c='3a3a48', shoe_c='4a3020', eye_c='6b4a2f'),
    'BEATA': dict(kind='cf', skin='fair', hair='pigtails', hair_c='e8c060', top='sweater', top_c='9b59b6',
                  bottom_c='e07aa0', shoe_c='ffffff', eye_c='3b6e8f', clip=True),
    'KUNESOVA': dict(kind='of', skin='old', hair='bun', hair_c='c8c8cc', top='dress', top_c='6c4a8a',
                     under_c='d8b4e2', bottom_c='6c4a8a', shoe_c='3a2a20', glasses='round', eye_c='4a4a4a'),
    'BURES': dict(kind='m', skin='medium', hair='short', hair_c='3a2a20', top='uniform', top_c='3b4a63',
                  bottom_c='2d3850', shoe_c='111111', cap='police', stubble=True, eye_c='4a3020'),
    'HRUBAN': dict(kind='om', skin='light', hair='bald', hair_c='9a9a9a', top='suit', top_c='6b4f3a',
                   under_c='f0f0e8', tie_c='8a1f2a', bottom_c='4a3a2a', shoe_c='2a1a10', belly=True,
                   glasses='square', eye_c='4a3020'),
    'LISKUTIN': dict(kind='m', skin='tan', hair='buzz', hair_c='2a2420', top='track', top_c='c0392b',
                     under_c='ffffff', bottom_c='c0392b', shoe_c='f0f0f0', mustache=True, whistle=True,
                     broad=True, eye_c='3a2a20'),
    'SEBESTOVA': dict(kind='f', skin='fair', hair='lowbun', hair_c='3a2a28', top='cardigan', top_c='a0607a',
                      under_c='f3e6d6', bottom_c='4a3a4a', shoe_c='3a2020', glasses='thin', scarf_c='e0b050',
                      eye_c='5a3a2a'),
    'KRIZENECKY': dict(kind='m', skin='light', hair='side', hair_c='2e2622', top='tweed', top_c='7d6b55',
                       under_c='2b2b33', bottom_c='3a3a40', shoe_c='3a2416', beard=True, tall=True,
                       eye_c='6a8a9a', temples=True),
    'VAREJKA': dict(kind='om', skin='old', hair='white', hair_c='f2f2f2', top='suit', top_c='777a80',
                    under_c='f4f0e8', bow_c='2a4a8a', bottom_c='55585e', shoe_c='2a2020', glasses='thick',
                    eye_c='4a4a4a'),
    'BOUCNIK': dict(kind='m', skin='pale', hair='comb', hair_c='5a4a3a', top='vest', top_c='8a7a5a',
                    under_c='e8dcc0', bottom_c='4a4a40', shoe_c='2a2a20', glasses='square', thin=True,
                    eye_c='4a3020'),
    'CHOVANCOVA': dict(kind='f', skin='fair', hair='curly', hair_c='c0502a', top='labcoat', top_c='f4f4f4',
                       under_c='2e7d6b', bottom_c='334', shoe_c='2a2a2a', goggles=True, eye_c='4a8a5a'),
    'FIALA': dict(kind='f', skin='medium', hair='pixie', hair_c='1a1a1a', top='labcoat', top_c='f4f4f4',
                  under_c='4a7ab0', bottom_c='4a7ab0', shoe_c='f0f0f0', stetho=True, eye_c='3a2a20'),
    'PAZDERA': dict(kind='tm', skin='fair', hair='part', hair_c='1e1a18', top='vestshirt', top_c='2c3e66',
                    under_c='f4f4f4', bottom_c='6a6a6a', shoe_c='3a2a20', glasses='round', eye_c='4a3020'),
    'ZEMANOVA': dict(kind='tf', skin='light', hair='ponytail', hair_c='5a3a22', top='jacket', top_c='4f7fb0',
                     under_c='f4f4f4', bottom_c='2a2a38', shoe_c='e0e0e0', band_c='d03030', eye_c='4a7a3a'),
    'OLEKSII': dict(kind='tm', skin='light', hair='buzz', hair_c='d8c080', top='track', top_c='2a5aa8',
                    under_c='f4d03f', bottom_c='2a2a3a', shoe_c='f0f0f0', broad=True, eye_c='5a8aa8',
                    brow_k=1.4),
    'KOVAR': dict(kind='tm', skin='fair', hair='curly', hair_c='c8642a', top='tee', top_c='7a3fa0',
                  bottom_c='3a5070', shoe_c='d03030', cap='back', freckles=True, eye_c='4a6a3a'),
    'BLASKA': dict(kind='tm', skin='medium', hair='short', hair_c='1a1410', top='track', top_c='e67e22',
                   under_c='222222', bottom_c='222222', shoe_c='f4f4f4', band_c='ffffff', eye_c='3a2a20'),
    'RYBAROVA': dict(kind='tf', skin='pale', hair='short_f', hair_c='e0c890', top='sweater', top_c='8a8a7a',
                     bottom_c='4a4a50', shoe_c='5a5a5a', dirty=True, eye_c='4a6a8a'),
    'BRABEC': dict(kind='tm', skin='light', hair='short', hair_c='4a3020', top='jacket', top_c='1f6fb0',
                   under_c='ffffff', bottom_c='2a2a3a', shoe_c='ffffff', eye_c='3a2a20'),
    'MLEJNEK': dict(kind='tm', skin='fair', hair='part', hair_c='6a5a4a', top='jacket', top_c='556b2f',
                    under_c='dddddd', bottom_c='3a3a3a', shoe_c='3a3a3a', glasses='round', small=True,
                    eye_c='4a3020'),
}

KIND_H = {'m': 400, 'f': 378, 'tm': 362, 'tf': 350, 'cf': 268, 'om': 380, 'of': 330}
CHILDLIKE = {'cf': 1.25, 'tm': 1.06, 'tf': 1.08}


def rrect(ctx, x, y, w, h, r):
    r = min(r, abs(w) / 2, abs(h) / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def fill_stroke(ctx, col, lw=3.0, out=OUT, alpha=1.0):
    ctx.set_source_rgba(*col[:3], alpha)
    ctx.fill_preserve()
    ctx.set_source_rgba(*out, alpha)
    ctx.set_line_width(lw)
    ctx.stroke()


def limb(ctx, x1, y1, x2, y2, x3, y3, w, col, lw=3.0):
    """Končetina ze dvou segmentů — obrys a výplň tlustou čarou."""
    ctx.set_line_cap(1)  # ROUND
    ctx.set_line_join(1)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.line_to(x3, y3)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(w + 2 * lw)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*col)
    ctx.set_line_width(w)
    ctx.stroke()


class Look:
    def __init__(self, name):
        d = dict(CHARS[name])
        self.name = name
        self.d = d
        self.kind = d['kind']
        H = KIND_H[self.kind]
        if d.get('tall'):
            H *= 1.07
        if d.get('small'):
            H *= 0.94
        self.H = H
        self.skin = SKIN[d['skin']]
        self.hair_c = hexc(d['hair_c'])
        self.top_c = hexc(d['top_c'])
        self.under_c = hexc(d.get('under_c', d['top_c']))
        self.bottom_c = hexc(d['bottom_c']) if len(d['bottom_c']) == 6 else hexc('333344')
        self.shoe_c = hexc(d['shoe_c'])
        self.eye_c = hexc(d.get('eye_c', '3a2a20'))
        child = CHILDLIKE.get(self.kind, 1.0)
        self.head_r = H * 0.122 * child
        self.female = self.kind in ('f', 'tf', 'cf', 'of')
        bw = 0.27 if not self.female else 0.24
        if d.get('broad'):
            bw *= 1.15
        if d.get('thin'):
            bw *= 0.86
        if self.kind == 'cf':
            bw = 0.30
        self.body_w = H * bw
        self.rng = random.Random(hash(name) & 0xffff)
        self.blink_seed = self.rng.random() * 10


def blink_amount(look, t):
    """0 = otevřené, 1 = zavřené"""
    period = 3.1 + (look.blink_seed % 2.3)
    ph = (t + look.blink_seed) % period
    if ph < 0.13:
        return math.sin(ph / 0.13 * math.pi)
    return 0.0


MOODS = {
    # brow_angle (+ = vnitřní konce dolů = zlost), brow_raise, mouth_curve, eye_open, pupil
    'n': (0.0, 0.0, 0.15, 1.0, 1.0),
    'happy': (-0.1, 0.15, 0.85, 0.85, 1.0),
    'sad': (-0.55, 0.15, -0.6, 0.85, 1.0),
    'angry': (0.75, -0.25, -0.45, 0.9, 0.9),
    'scared': (-0.6, 0.55, -0.3, 1.35, 0.6),
    'worried': (-0.4, 0.25, -0.2, 1.0, 1.0),
    'sly': (0.35, 0.0, 0.55, 0.62, 1.0),
    'sick': (-0.25, 0.0, -0.15, 0.62, 1.0),
    'surprised': (-0.1, 0.6, 0.0, 1.3, 0.8),
    'smug': (0.3, 0.1, 0.6, 0.7, 1.0),
}


def draw_character(ctx, look, st):
    """st: dict(x, y, scale, facing, pose, mood, mouth, t, walk, talk, prop, sick, gest)."""
    x, y, s = st['x'], st['y'], st.get('scale', 1.0)
    f = st.get('facing', 1)
    pose = st.get('pose', 'stand')
    t = st.get('t', 0.0)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    H = look.H
    walk = st.get('walk', 0.0)  # fáze chůze (rad), None když stojí
    walking = st.get('walking', False)
    breath = math.sin(t * 2.1 + look.blink_seed) * 0.008
    bob = abs(math.sin(walk)) * H * 0.018 if walking else 0.0
    # stín na zemi
    if pose not in ('bed',):
        ctx.save()
        ctx.scale(1, 0.18)
        ctx.arc(0, 0, look.body_w * 0.95, 0, 2 * math.pi)
        ctx.set_source_rgba(0, 0, 0, 0.22)
        ctx.fill()
        ctx.restore()

    leg_len = H * 0.43
    hip_y = -leg_len + bob
    if pose == 'crouch':
        hip_y = -H * 0.2
    if pose == 'sit':
        hip_y = -H * 0.27
    torso_h = H * 0.31
    if look.kind == 'cf':
        torso_h = H * 0.29
        leg_len = H * 0.36
        hip_y = -leg_len + bob if pose == 'stand' else hip_y
    sh_y = hip_y - torso_h * (1 + breath)
    bw = look.body_w
    hw = bw * 0.5

    if pose == 'bed':
        _draw_bed_back(ctx, look, f)
        hip_y = -H * 0.05
        sh_y = hip_y - torso_h * 0.95 * (1 + breath)

    # nohy
    if pose == 'stand':
        sw = math.sin(walk) * 0.42 if walking else 0.0
        for side, ph in ((-1, sw), (1, -sw)):
            hx = side * hw * 0.42
            kx = hx + math.sin(ph) * leg_len * 0.5
            ky = hip_y + math.cos(ph) * leg_len * 0.5
            fx = kx + math.sin(ph * 0.6) * leg_len * 0.5
            fy = min(0, ky + leg_len * 0.5)
            limb(ctx, hx, hip_y, kx, ky, fx, fy - 6, bw * 0.30, look.bottom_c)
            _shoe(ctx, fx, fy, f, bw, look)
    elif pose == 'sit':
        for side in (-1, 1):
            hx = side * hw * 0.42
            kx = hx + f * leg_len * 0.48
            ky = hip_y + 4
            limb(ctx, hx, hip_y, kx, ky, kx + f * 4, -6, bw * 0.30, look.bottom_c)
            _shoe(ctx, kx + f * 4, 0, f, bw, look)
    elif pose == 'crouch':
        for side in (-1, 1):
            hx = side * hw * 0.45
            kx = hx + side * bw * 0.25 + f * bw * 0.25
            limb(ctx, hx, hip_y, kx, hip_y - H * 0.06, hx + side * 6, -6, bw * 0.3, look.bottom_c)
            _shoe(ctx, hx + side * 6, 0, f, bw, look)

    # paže — vzadu
    gest = st.get('gest', 0.0)
    arm_w = bw * 0.24
    sleeve = look.top_c
    if look.d['top'] in ('tee',):
        sleeve = look.top_c
    arm_len = H * 0.30
    prop = st.get('prop')
    swing = math.sin(walk) * 0.35 if walking else 0.0
    # zadní paže
    back_side = -f
    _arm(ctx, look, back_side * hw * 0.9, sh_y + 10, back_side, -swing * 0.8, 0.0, arm_len, arm_w, sleeve, False,
         pose)

    # trup
    _torso(ctx, look, hip_y, sh_y, bw, f, pose)

    # hlava
    neck_h = H * 0.03
    hr = look.head_r
    head_y = sh_y - neck_h - hr * 0.92
    head_bob = math.sin(t * 9.0) * hr * 0.03 * st.get('talk', 0.0)
    tilt = st.get('tilt', 0.0)
    # krk
    ctx.rectangle(-hr * 0.22, sh_y - neck_h - hr * 0.3, hr * 0.44, neck_h + hr * 0.4)
    fill_stroke(ctx, shade(look.skin, -0.08), 2.5)
    _torso_collar(ctx, look, sh_y, bw, f)
    ctx.save()
    ctx.translate(0, head_y + head_bob)
    ctx.rotate(tilt)
    _head(ctx, look, hr, f, st, t)
    ctx.restore()

    # přední paže (gesta / rekvizity)
    front_side = f
    raise_a = 0.0
    fore = 0.0
    if prop in ('phone', 'thermos', 'flashlight', 'card', 'hairclip', 'flowers', 'notebook', 'megaphone'):
        raise_a, fore = 0.55, 1.35
        if prop == 'megaphone':
            raise_a, fore = 1.3, 0.9
    elif gest > 0:
        raise_a = 0.35 * gest
        fore = 1.2 * gest
    hand = _arm(ctx, look, front_side * hw * 0.9, sh_y + 10, front_side, swing * 0.8 + raise_a, fore, arm_len,
                arm_w, sleeve, True, pose)
    if prop:
        _prop(ctx, prop, hand, f, H, t)
    if pose == 'bed':
        _draw_bed_front(ctx, look, f, hip_y)
    if st.get('tied'):
        ctx.set_source_rgb(*hexc('b08a50'))
        ctx.set_line_width(5)
        for k in (0.3, 0.55, 0.8):
            yy = sh_y + (hip_y - sh_y) * k
            ctx.move_to(-hw * 1.15, yy)
            ctx.curve_to(-hw * 0.5, yy + 8, hw * 0.5, yy + 8, hw * 1.15, yy)
        ctx.stroke()
    ctx.restore()


def _shoe(ctx, x, y, f, bw, look):
    w = bw * 0.36
    ctx.save()
    ctx.translate(x, y)
    ctx.move_to(-w * 0.55 * (1 if f > 0 else 1.4), 0)
    ctx.line_to(w * (1.4 if f > 0 else 0.55), 0)
    ctx.curve_to(w * (1.4 if f > 0 else 0.55), -w * 0.55, w * 0.2 * f, -w * 0.75, -w * 0.3 * f, -w * 0.6)
    ctx.close_path()
    fill_stroke(ctx, look.shoe_c, 2.5)
    ctx.restore()


def _arm(ctx, look, sx, sy, side, ang, fore, L, w, col, front, pose):
    """ang: zvednutí paže dopředu (rad), fore: ohnutí lokte (rad). Vrací pozici ruky."""
    base = 0.12 * side  # mírně od těla
    a1 = base + ang * side * 0.0
    # paže dolů = úhel 0, dopředu (směrem facing) kladné
    ex = sx + math.sin(a1) * L * 0.5 + side * L * 0.05
    ey = sy + math.cos(a1) * L * 0.5
    # zvednutí: paže se otáčí kolem ramene ve směru 'side'
    ux = math.sin(ang) * side
    uy = math.cos(ang)
    ex = sx + ux * L * 0.5 + side * 4
    ey = sy + uy * L * 0.5
    a2 = ang + fore
    hx = ex + math.sin(a2) * side * L * 0.5
    hy = ey + math.cos(a2) * L * 0.5
    if pose == 'bed' and not front:
        hy = min(hy, sy + L * 0.6)
    limb(ctx, sx, sy, ex, ey, hx, hy, w, col)
    ctx.arc(hx, hy, w * 0.62, 0, 2 * math.pi)
    fill_stroke(ctx, look.skin, 2.5)
    return hx, hy


def _torso(ctx, look, hip_y, sh_y, bw, f, pose):
    d = look.d
    top = d['top']
    hw = bw / 2
    belly = 1.12 if d.get('belly') else 1.0
    ctx.save()
    # tvar trupu
    ctx.move_to(-hw * 0.95, sh_y + 8)
    ctx.curve_to(-hw * 1.05, sh_y - 2, -hw * 0.6, sh_y - 6, 0, sh_y - 6)
    ctx.curve_to(hw * 0.6, sh_y - 6, hw * 1.05, sh_y - 2, hw * 0.95, sh_y + 8)
    ctx.curve_to(hw * belly * 1.02, (sh_y + hip_y) / 2, hw * belly, hip_y - 6, hw * 0.92, hip_y + 6)
    ctx.line_to(-hw * 0.92, hip_y + 6)
    ctx.curve_to(-hw * belly, hip_y - 6, -hw * belly * 1.02, (sh_y + hip_y) / 2, -hw * 0.95, sh_y + 8)
    ctx.close_path()
    if top == 'dress':
        ctx.new_path()
        ctx.move_to(-hw * 0.95, sh_y + 8)
        ctx.curve_to(-hw * 1.05, sh_y - 2, -hw * 0.6, sh_y - 6, 0, sh_y - 6)
        ctx.curve_to(hw * 0.6, sh_y - 6, hw * 1.05, sh_y - 2, hw * 0.95, sh_y + 8)
        ctx.line_to(hw * 1.35, hip_y + look.H * 0.2)
        ctx.line_to(-hw * 1.35, hip_y + look.H * 0.2)
        ctx.close_path()
    path = ctx.copy_path()
    fill_stroke(ctx, look.top_c, 3)
    # stínování — jedna strana tmavší
    ctx.append_path(path)
    ctx.clip()
    ctx.rectangle(-f * hw * 0.25 - (hw * 2 if f > 0 else 0), sh_y - 20, hw * 2, (hip_y - sh_y) + 100)
    ctx.set_source_rgba(0, 0, 0, 0.12)
    ctx.fill()
    # detaily
    if top in ('jacket', 'cardigan', 'tweed', 'suit', 'labcoat', 'uniform', 'track'):
        # spodní vrstva uprostřed
        ctx.move_to(-hw * 0.28, sh_y - 4)
        ctx.line_to(hw * 0.28, sh_y - 4)
        ctx.line_to(hw * 0.12, hip_y + 8)
        ctx.line_to(-hw * 0.12, hip_y + 8)
        ctx.close_path()
        ctx.set_source_rgb(*look.under_c)
        ctx.fill()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(2)
        ctx.move_to(-hw * 0.28, sh_y - 4)
        ctx.line_to(-hw * 0.12, hip_y + 8)
        ctx.move_to(hw * 0.28, sh_y - 4)
        ctx.line_to(hw * 0.12, hip_y + 8)
        ctx.stroke()
        if top == 'track':
            ctx.set_source_rgb(1, 1, 1)
            ctx.set_line_width(3)
            for sd in (-1, 1):
                ctx.move_to(sd * hw * 0.85, sh_y + 10)
                ctx.line_to(sd * hw * 0.92, hip_y)
            ctx.stroke()
        if top == 'tweed':
            ctx.set_source_rgba(0, 0, 0, 0.12)
            ctx.set_line_width(1.2)
            for i in range(-6, 7):
                ctx.move_to(i * hw * 0.16, sh_y)
                ctx.line_to(i * hw * 0.16 + 8, hip_y)
            ctx.stroke()
        if top == 'uniform':
            ctx.set_source_rgb(*hexc('d8c070'))
            for yy in (0.3, 0.55, 0.8):
                ctx.arc(0, sh_y + (hip_y - sh_y) * yy, 3, 0, 6.3)
                ctx.fill()
            # odznak
            ctx.move_to(-hw * 0.6, sh_y + 22)
            ctx.line_to(-hw * 0.4, sh_y + 18)
            ctx.line_to(-hw * 0.4, sh_y + 34)
            ctx.line_to(-hw * 0.5, sh_y + 40)
            ctx.line_to(-hw * 0.6, sh_y + 34)
            ctx.close_path()
            ctx.fill()
        if top == 'suit' and d.get('tie_c'):
            c = hexc(d['tie_c'])
            ctx.move_to(-5, sh_y)
            ctx.line_to(5, sh_y)
            ctx.line_to(8, sh_y + (hip_y - sh_y) * 0.7)
            ctx.line_to(0, sh_y + (hip_y - sh_y) * 0.8)
            ctx.line_to(-8, sh_y + (hip_y - sh_y) * 0.7)
            ctx.close_path()
            fill_stroke(ctx, c, 1.5)
        if top == 'labcoat':
            ctx.set_source_rgba(0, 0, 0, 0.25)
            ctx.set_line_width(1.5)
            rrect(ctx, f * hw * 0.35 - 10, sh_y + (hip_y - sh_y) * 0.25, 20, 14, 2)
            ctx.stroke()
    elif top == 'hoodie':
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.set_line_width(2.5)
        ctx.move_to(-8, sh_y + 2)
        ctx.line_to(-10, sh_y + 30)
        ctx.move_to(8, sh_y + 2)
        ctx.line_to(10, sh_y + 30)
        ctx.stroke()
        rrect(ctx, -hw * 0.55, hip_y - (hip_y - sh_y) * 0.32, hw * 1.1, (hip_y - sh_y) * 0.22, 6)
        ctx.set_source_rgba(0, 0, 0, 0.15)
        ctx.fill()
    elif top == 'vest' or top == 'vestshirt':
        ctx.move_to(-hw * 0.3, sh_y - 4)
        ctx.line_to(hw * 0.3, sh_y - 4)
        ctx.line_to(0, sh_y + (hip_y - sh_y) * 0.4)
        ctx.close_path()
        ctx.set_source_rgb(*look.under_c)
        ctx.fill()
    elif top == 'sweater':
        ctx.set_source_rgba(0, 0, 0, 0.12)
        ctx.set_line_width(4)
        ctx.move_to(-hw, hip_y - 4)
        ctx.line_to(hw, hip_y - 4)
        ctx.stroke()
    elif top == 'tee':
        ctx.set_source_rgb(*hexc('f4d03f'))
        ctx.move_to(0, sh_y + 20)
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            a2 = a + math.pi / 5
            ctx.line_to(math.cos(a) * 16, sh_y + 40 + math.sin(a) * 16)
            ctx.line_to(math.cos(a2) * 7, sh_y + 40 + math.sin(a2) * 7)
        ctx.close_path()
        ctx.fill()
    if d.get('dirty'):
        ctx.set_source_rgba(0.3, 0.25, 0.2, 0.35)
        for i in range(7):
            ctx.arc(look.rng.uniform(-hw, hw), look.rng.uniform(sh_y, hip_y), look.rng.uniform(3, 8), 0, 6.3)
            ctx.fill()
    ctx.restore()
    if d.get('scarf_c'):
        c = hexc(d['scarf_c'])
        rrect(ctx, -hw * 0.55, sh_y - 10, hw * 1.1, 18, 8)
        fill_stroke(ctx, c, 2)
        rrect(ctx, f * hw * 0.25 - 7, sh_y, 14, (hip_y - sh_y) * 0.45, 5)
        fill_stroke(ctx, c, 2)
    if d.get('whistle'):
        ctx.set_source_rgb(0.15, 0.15, 0.15)
        ctx.set_line_width(1.5)
        ctx.move_to(-10, sh_y - 4)
        ctx.line_to(0, sh_y + 26)
        ctx.line_to(10, sh_y - 4)
        ctx.stroke()
        rrect(ctx, -6, sh_y + 24, 14, 8, 3)
        fill_stroke(ctx, (0.8, 0.8, 0.85), 1.5)
    if d.get('stetho'):
        ctx.set_source_rgb(0.2, 0.2, 0.25)
        ctx.set_line_width(2.5)
        ctx.move_to(-12, sh_y - 4)
        ctx.curve_to(-18, sh_y + 30, 18, sh_y + 30, 12, sh_y - 4)
        ctx.stroke()
        ctx.arc(0, sh_y + 28, 5, 0, 6.3)
        fill_stroke(ctx, (0.7, 0.7, 0.75), 1.5)


def _torso_collar(ctx, look, sh_y, bw, f):
    top = look.d['top']
    if top in ('hoodie',):
        ctx.move_to(-bw * 0.3, sh_y - 2)
        ctx.curve_to(-bw * 0.25, sh_y - 16, bw * 0.25, sh_y - 16, bw * 0.3, sh_y - 2)
        ctx.curve_to(bw * 0.15, sh_y + 6, -bw * 0.15, sh_y + 6, -bw * 0.3, sh_y - 2)
        fill_stroke(ctx, shade(look.top_c, -0.15), 2.5)
    if top in ('tweed', 'suit', 'uniform', 'labcoat'):
        c = shade(look.top_c, -0.1)
        for sd in (-1, 1):
            ctx.move_to(sd * bw * 0.06, sh_y - 6)
            ctx.line_to(sd * bw * 0.26, sh_y - 8)
            ctx.line_to(sd * bw * 0.16, sh_y + 22)
            ctx.close_path()
            fill_stroke(ctx, c, 2)
    if look.d.get('bow_c'):
        c = hexc(look.d['bow_c'])
        ctx.move_to(0, sh_y)
        ctx.line_to(-12, sh_y - 7)
        ctx.line_to(-12, sh_y + 7)
        ctx.close_path()
        ctx.move_to(0, sh_y)
        ctx.line_to(12, sh_y - 7)
        ctx.line_to(12, sh_y + 7)
        ctx.close_path()
        fill_stroke(ctx, c, 1.5)


def _head(ctx, look, r, f, st, t):
    d = look.d
    mood = st.get('mood', 'n') or 'n'
    sick = st.get('sick', False) or mood == 'sick'
    skin = look.skin
    if sick:
        skin = mix(skin, (0.86, 0.9, 0.82), 0.35)
    fx = f * r * 0.16  # posun obličeje ve směru pohledu
    hair = look.hair_c
    style = d['hair']
    # vlasy vzadu
    if style in ('bob', 'lowbun', 'curly', 'ponytail', 'pigtails', 'bun', 'short_f'):
        _hair_back(ctx, style, r, f, hair, look, t)
    # uši
    for sd in (-1, 1):
        ex = sd * r * 0.92 + fx * 0.3
        if sd == -f and abs(f) > 0:
            ex = sd * r * 0.88
        ctx.save()
        ctx.translate(ex, r * 0.08)
        ctx.scale(0.55, 1)
        ctx.arc(0, 0, r * 0.22, 0, 2 * math.pi)
        ctx.restore()
        fill_stroke(ctx, shade(skin, -0.05), 2.5)
    # hlava
    ctx.save()
    ctx.scale(1.0, 1.08)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.restore()
    if look.kind in ('m', 'om') or d.get('broad'):
        ctx.new_path()
        ctx.move_to(-r, -r * 0.2)
        ctx.curve_to(-r, -r * 1.25, r, -r * 1.25, r, -r * 0.2)
        ctx.curve_to(r, r * 0.7, r * 0.5, r * 1.12, 0, r * 1.12)
        ctx.curve_to(-r * 0.5, r * 1.12, -r, r * 0.7, -r, -r * 0.2)
        ctx.close_path()
    fill_stroke(ctx, skin, 3)
    # stín na tváři
    ctx.save()
    ctx.scale(1.0, 1.08)
    ctx.arc(0, 0, r * 0.98, 0, 2 * math.pi)
    ctx.restore()
    ctx.clip()
    ctx.arc(f * r * 0.5, -r * 0.1, r * 1.25, 0, 2 * math.pi)
    ctx.set_fill_rule(1)
    ctx.rectangle(-r * 3, -r * 3, r * 6, r * 6)
    ctx.set_source_rgba(0.35, 0.15, 0.1, 0.12)
    ctx.fill()
    ctx.set_fill_rule(0)
    ctx.reset_clip()
    if d.get('stubble') or d.get('beard'):
        ctx.save()
        ctx.move_to(-r * 0.86, r * 0.1)
        ctx.curve_to(-r * 0.8, r * 1.2, r * 0.8, r * 1.2, r * 0.86, r * 0.1)
        ctx.curve_to(r * 0.6, r * 0.55, -r * 0.6, r * 0.55, -r * 0.86, r * 0.1)
        ctx.close_path()
        if d.get('beard'):
            fill_stroke(ctx, shade(hair, 0.05), 2.5)
        else:
            ctx.set_source_rgba(0.2, 0.18, 0.18, 0.22)
            ctx.fill()
        ctx.restore()
    # tváře (červeň)
    blush = 0.18 if mood in ('happy', 'sly') else 0.08
    if sick:
        blush = 0.0
    for sd in (-1, 1):
        ctx.arc(fx + sd * r * 0.5, r * 0.35, r * 0.17, 0, 2 * math.pi)
        ctx.set_source_rgba(0.95, 0.4, 0.4, blush)
        ctx.fill()
    if d.get('freckles'):
        ctx.set_source_rgba(0.6, 0.35, 0.2, 0.6)
        for sd in (-1, 1):
            for i in range(4):
                ctx.arc(fx + sd * r * (0.35 + 0.08 * (i % 2)), r * (0.22 + 0.07 * i), 1.6, 0, 6.3)
                ctx.fill()
    ba, braise, mc, eo, pup = MOODS.get(mood, MOODS['n'])
    if d.get('brow_k'):
        ba = ba + 0.25
    blink = blink_amount(look, t)
    look_x = st.get('look_x', 0.0)
    eye_y = -r * 0.02
    ew, eh = r * 0.2, r * 0.25 * eo
    for sd in (-1, 1):
        exx = fx + sd * r * 0.36
        # perspektivní zúžení vzdálenějšího oka
        k = 1.0 - 0.18 * (1 if sd == -f else 0)
        ctx.save()
        ctx.translate(exx, eye_y)
        ctx.scale(k, 1)
        op = max(0.06, 1 - blink)
        ctx.save()
        ctx.scale(1, op)
        ctx.arc(0, 0, ew, 0, 2 * math.pi)
        ctx.restore()
        fill_stroke(ctx, (1, 1, 1), 2.2)
        if op > 0.2:
            ctx.save()
            ctx.scale(1, op)
            pr = ew * 0.55 * pup
            ctx.arc(f * ew * 0.25 + look_x * ew * 0.4, eh * 0.05, pr, 0, 2 * math.pi)
            ctx.set_source_rgb(*look.eye_c)
            ctx.fill()
            ctx.arc(f * ew * 0.25 + look_x * ew * 0.4, eh * 0.05, pr * 0.55, 0, 2 * math.pi)
            ctx.set_source_rgb(0.05, 0.05, 0.08)
            ctx.fill()
            ctx.arc(f * ew * 0.25 + look_x * ew * 0.4 - pr * 0.35, -pr * 0.35, pr * 0.28, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
            ctx.restore()
        # víčko (napůl zavřené u sly/sick)
        if eo < 0.8 and blink < 0.5:
            ctx.save()
            ctx.arc(0, 0, ew * 1.02, 0, 2 * math.pi)
            ctx.clip()
            ctx.rectangle(-ew * 1.2, -ew * 1.3, ew * 2.4, ew * (1.3 - (eo - 0.25) * 1.4))
            ctx.set_source_rgb(*shade(skin, -0.08))
            ctx.fill()
            ctx.restore()
            ctx.set_source_rgb(*OUT)
            ctx.set_line_width(2.2)
            yy = -ew + ew * (1.3 - (eo - 0.25) * 1.4) - ew * 0.3
            ctx.move_to(-ew, yy)
            ctx.line_to(ew, yy)
            ctx.stroke()
        if sick:
            ctx.arc(0, ew * 1.2, ew * 0.9, 0.2, math.pi - 0.2)
            ctx.set_source_rgba(0.45, 0.3, 0.45, 0.35)
            ctx.set_line_width(2)
            ctx.stroke()
        ctx.restore()
        # obočí
        bx = exx
        by = eye_y - eh - r * 0.12 - braise * r * 0.18
        inner = -sd  # směr k nosu
        ctx.set_line_cap(1)
        ctx.set_source_rgb(*shade(hair, -0.35) if style not in ('white', 'bald') else (0.55, 0.55, 0.55))
        ctx.set_line_width(r * 0.085 * (1.3 if d.get('brow_k') else 1.0))
        a = ba * 0.5
        if mood == 'sly' and sd == f:
            a = -0.3
        ctx.move_to(bx - inner * ew * 1.1, by - math.sin(-a) * ew * 0.8 * 0)
        ctx.line_to(bx + inner * ew * 1.0, by + a * ew * 0.9)
        ctx.stroke()
    # nos
    ctx.set_source_rgb(*shade(skin, -0.28))
    ctx.set_line_width(2.4)
    ctx.move_to(fx + f * r * 0.06, r * 0.12)
    ctx.curve_to(fx + f * r * 0.2, r * 0.3, fx + f * r * 0.14, r * 0.36, fx - f * r * 0.02, r * 0.36)
    ctx.stroke()
    if d.get('mustache'):
        ctx.move_to(fx - r * 0.35, r * 0.55)
        ctx.curve_to(fx - r * 0.2, r * 0.38, fx + r * 0.2, r * 0.38, fx + r * 0.35, r * 0.55)
        ctx.curve_to(fx + r * 0.15, r * 0.48, fx - r * 0.15, r * 0.48, fx - r * 0.35, r * 0.55)
        fill_stroke(ctx, hair, 2)
    # ústa
    mo = st.get('mouth', 0.0)
    my = r * 0.58
    mw = r * 0.28
    mx = fx + f * r * 0.04
    if mo > 0.06:
        hgt = r * 0.06 + mo * r * 0.26
        ctx.save()
        ctx.translate(mx, my + mc * r * -0.02)
        ctx.move_to(-mw, 0)
        ctx.curve_to(-mw * 0.6, -hgt * 0.3 - mc * r * 0.06, mw * 0.6, -hgt * 0.3 - mc * r * 0.06, mw, 0)
        ctx.curve_to(mw * 0.7, hgt * 1.1, -mw * 0.7, hgt * 1.1, -mw, 0)
        ctx.close_path()
        fill_stroke(ctx, (0.35, 0.08, 0.1), 2.2)
        ctx.move_to(-mw * 0.5, hgt * 0.75)
        ctx.curve_to(-mw * 0.3, hgt * 0.4, mw * 0.3, hgt * 0.4, mw * 0.5, hgt * 0.75)
        ctx.set_source_rgb(0.85, 0.35, 0.38)
        ctx.fill()
        ctx.restore()
    else:
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(2.6)
        ctx.set_line_cap(1)
        if mood == 'surprised' or mood == 'scared':
            ctx.save()
            ctx.translate(mx, my + r * 0.04)
            ctx.scale(1, 1.3)
            ctx.arc(0, 0, r * 0.07, 0, 2 * math.pi)
            ctx.restore()
            ctx.stroke()
        elif mood == 'sly' or mood == 'smug':
            ctx.move_to(mx - mw, my + r * 0.02)
            ctx.curve_to(mx - mw * 0.2, my + r * 0.06, mx + mw * 0.5, my + r * 0.02, mx + mw * 1.05 * f, my - r * 0.1)
            ctx.stroke()
        else:
            ctx.move_to(mx - mw, my - mc * r * 0.06)
            ctx.curve_to(mx - mw * 0.4, my + mc * r * 0.16, mx + mw * 0.4, my + mc * r * 0.16, mx + mw,
                         my - mc * r * 0.06)
            ctx.stroke()
    if sick and (int(t * 0.5) % 3 == 0):
        ctx.save()
        ctx.translate(fx + f * r * 0.75, -r * 0.45)
        ctx.move_to(0, -6)
        ctx.curve_to(5, 2, 4, 7, 0, 7)
        ctx.curve_to(-4, 7, -5, 2, 0, -6)
        ctx.set_source_rgba(0.6, 0.85, 1.0, 0.8)
        ctx.fill()
        ctx.restore()
    # vlasy vepředu
    _hair_front(ctx, style, r, f, hair, look, t)
    if d.get('temples'):
        ctx.set_source_rgba(0.75, 0.75, 0.75, 0.9)
        for sd in (-1, 1):
            ctx.arc(sd * r * 0.88, -r * 0.35, r * 0.13, 0, 6.3)
            ctx.fill()
    if d.get('cap') == 'police':
        ctx.move_to(-r * 1.05, -r * 0.55)
        ctx.curve_to(-r * 1.0, -r * 1.35, r * 1.0, -r * 1.35, r * 1.05, -r * 0.55)
        ctx.close_path()
        fill_stroke(ctx, hexc('2a3448'), 3)
        ctx.move_to(-r * 0.2 + f * r * 0.3, -r * 0.55)
        ctx.curve_to(f * r * 0.6, -r * 0.45, f * r * 1.4, -r * 0.42, f * r * 1.3, -r * 0.6)
        ctx.close_path()
        fill_stroke(ctx, hexc('15151a'), 2.5)
        ctx.arc(0, -r * 0.85, r * 0.12, 0, 6.3)
        fill_stroke(ctx, hexc('d8c070'), 1.5)
    if d.get('cap') == 'back':
        ctx.move_to(-r * 1.0, -r * 0.45)
        ctx.curve_to(-r * 0.95, -r * 1.3, r * 0.95, -r * 1.3, r * 1.0, -r * 0.45)
        ctx.close_path()
        fill_stroke(ctx, hexc('d03030'), 3)
        ctx.move_to(-f * r * 0.8, -r * 0.5)
        ctx.line_to(-f * r * 1.45, -r * 0.4)
        ctx.line_to(-f * r * 1.4, -r * 0.6)
        ctx.close_path()
        fill_stroke(ctx, hexc('a02020'), 2.5)
    if d.get('band_c'):
        ctx.save()
        ctx.scale(1.0, 1.08)
        ctx.arc(0, 0, r * 1.0, 0, 2 * math.pi)
        ctx.restore()
        ctx.clip()
        ctx.rectangle(-r * 1.2, -r * 0.72, r * 2.4, r * 0.2)
        ctx.set_source_rgb(*hexc(d['band_c']))
        ctx.fill()
        ctx.reset_clip()
    if d.get('goggles'):
        ctx.set_line_width(2.5)
        for sd in (-1, 1):
            rrect(ctx, sd * r * 0.42 - r * 0.25, -r * 1.02, r * 0.5, r * 0.3, 6)
            ctx.set_source_rgba(0.7, 0.9, 0.95, 0.85)
            ctx.fill_preserve()
            ctx.set_source_rgb(*OUT)
            ctx.stroke()
    g = d.get('glasses')
    if g:
        ctx.set_source_rgb(0.12, 0.1, 0.12)
        lw = {'thin': 1.8, 'round': 2.6, 'square': 2.8, 'thick': 4.5}[g]
        ctx.set_line_width(lw)
        for sd in (-1, 1):
            exx = fx + sd * r * 0.36
            if g == 'square':
                rrect(ctx, exx - r * 0.27, -r * 0.24, r * 0.54, r * 0.42, 4)
            else:
                ctx.new_sub_path()
                ctx.arc(exx, -r * 0.02, r * 0.28, 0, 2 * math.pi)
            ctx.set_source_rgba(0.85, 0.92, 1.0, 0.18)
            ctx.fill_preserve()
            ctx.set_source_rgb(0.12, 0.1, 0.12)
            ctx.stroke()
        ctx.move_to(fx - r * 0.1, -r * 0.05)
        ctx.line_to(fx + r * 0.1, -r * 0.05)
        ctx.stroke()
    if st.get('headlamp'):
        ctx.save()
        ctx.set_source_rgb(0.15, 0.15, 0.15)
        ctx.set_line_width(r * 0.12)
        ctx.arc(0, -r * 0.1, r * 1.0, math.pi * 1.08, math.pi * 1.92)
        ctx.stroke()
        rrect(ctx, fx - r * 0.2, -r * 0.92, r * 0.4, r * 0.26, 4)
        fill_stroke(ctx, (0.25, 0.25, 0.25), 2)
        ctx.arc(fx + f * r * 0.02, -r * 0.79, r * 0.09, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.97, 0.8)
        ctx.fill()
        import cairo as _c
        g = _c.RadialGradient(fx, -r * 0.79, 0, fx, -r * 0.79, r * 1.4)
        g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.55)
        g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
        ctx.set_source(g)
        ctx.arc(fx, -r * 0.79, r * 1.4, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
    if d.get('clip'):
        ctx.save()
        ctx.translate(-f * r * 0.55, -r * 0.82)
        ctx.move_to(0, -9)
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = 10 if i % 2 == 0 else 4.5
            ctx.line_to(math.cos(a) * rr, math.sin(a) * rr)
        ctx.close_path()
        fill_stroke(ctx, hexc('ff5fa2'), 1.8)
        ctx.restore()


def _hair_back(ctx, style, r, f, c, look, t):
    if style == 'bob':
        ctx.move_to(-r * 1.15, -r * 0.2)
        ctx.curve_to(-r * 1.3, -r * 1.5, r * 1.3, -r * 1.5, r * 1.15, -r * 0.2)
        ctx.line_to(r * 1.12, r * 0.85)
        ctx.curve_to(r * 0.7, r * 1.0, -r * 0.7, r * 1.0, -r * 1.12, r * 0.85)
        ctx.close_path()
        fill_stroke(ctx, c, 3)
    elif style == 'lowbun':
        ctx.arc(-f * r * 0.6, r * 0.55, r * 0.42, 0, 2 * math.pi)
        fill_stroke(ctx, c, 3)
    elif style == 'bun':
        ctx.arc(0, -r * 1.12, r * 0.42, 0, 2 * math.pi)
        fill_stroke(ctx, c, 3)
    elif style == 'curly':
        rng = random.Random(7)
        for i in range(14):
            a = math.pi + i * math.pi / 13
            ctx.new_sub_path()
            ctx.arc(math.cos(a) * r * 1.0, math.sin(a) * r * 1.0 + r * 0.05, r * 0.33, 0, 2 * math.pi)
        for sd in (-1, 1):
            ctx.new_sub_path()
            ctx.arc(sd * r * 1.05, r * 0.3, r * 0.33, 0, 2 * math.pi)
        fill_stroke(ctx, c, 2.5)
    elif style == 'ponytail':
        sw = math.sin(t * 3) * 0.08
        ctx.save()
        ctx.translate(-f * r * 0.85, -r * 0.5)
        ctx.rotate(-f * (0.5 + sw))
        ctx.move_to(0, 0)
        ctx.curve_to(-f * r * 0.6, r * 0.4, -f * r * 0.4, r * 1.5, -f * r * 0.1, r * 1.9)
        ctx.curve_to(f * r * 0.2, r * 1.2, f * r * 0.3, r * 0.4, 0, 0)
        ctx.close_path()
        fill_stroke(ctx, c, 3)
        ctx.restore()
    elif style == 'pigtails':
        for sd in (-1, 1):
            ctx.save()
            ctx.translate(sd * r * 1.0, -r * 0.1)
            ctx.rotate(sd * 0.4 + math.sin(t * 4 + sd) * 0.05)
            ctx.move_to(0, -r * 0.2)
            ctx.curve_to(sd * r * 0.6, 0, sd * r * 0.5, r * 0.9, sd * r * 0.2, r * 1.1)
            ctx.curve_to(sd * r * 0.0, r * 0.7, -sd * r * 0.1, r * 0.2, 0, -r * 0.2)
            ctx.close_path()
            fill_stroke(ctx, c, 3)
            ctx.restore()
    elif style == 'short_f':
        ctx.move_to(-r * 1.1, -r * 0.2)
        ctx.curve_to(-r * 1.25, -r * 1.45, r * 1.25, -r * 1.45, r * 1.1, -r * 0.2)
        ctx.line_to(r * 1.05, r * 0.45)
        ctx.line_to(-r * 1.05, r * 0.45)
        ctx.close_path()
        fill_stroke(ctx, c, 3)


def _hair_front(ctx, style, r, f, c, look, t):
    ctx.save()
    if style == 'messy':
        ctx.move_to(-r * 1.02, -r * 0.1)
        pts = [(-1.1, -0.75), (-0.75, -1.25), (-0.35, -1.05), (-0.1, -1.4), (0.25, -1.1), (0.55, -1.38),
               (0.8, -1.0), (1.15, -0.95), (1.02, -0.1)]
        for px, py in pts:
            ctx.line_to(px * r, py * r)
        ctx.curve_to(r * 0.9, -r * 0.55, r * 0.4, -r * 0.75, r * 0.1 * f, -r * 0.5)
        ctx.curve_to(-r * 0.3, -r * 0.75, -r * 0.8, -r * 0.6, -r * 1.02, -r * 0.1)
        ctx.close_path()
        fill_stroke(ctx, c, 3)
    elif style == 'quiff':
        ctx.move_to(-r * 1.02, -r * 0.15)
        ctx.curve_to(-r * 1.1, -r * 1.2, -r * 0.2, -r * 1.25, f * r * 0.3, -r * 1.45)
        ctx.curve_to(f * r * 1.2, -r * 1.5, r * 1.15, -r * 0.9, r * 1.02, -r * 0.15)
        ctx.curve_to(r * 0.8, -r * 0.6, -r * 0.6, -r * 0.7, -r * 1.02, -r * 0.15)
        ctx.close_path()
        fill_stroke(ctx, c, 3)
    elif style in ('short', 'part', 'side', 'comb'):
        ctx.move_to(-r * 1.02, -r * 0.05)
        ctx.curve_to(-r * 1.15, -r * 1.3, r * 1.15, -r * 1.3, r * 1.02, -r * 0.05)
        if style == 'part' or style == 'side':
            ctx.curve_to(r * 0.95, -r * 0.6, r * 0.2, -r * 0.6, -f * r * 0.25, -r * 0.88)
            ctx.curve_to(-f * r * 0.5, -r * 0.55, -r * 0.9, -r * 0.5, -r * 1.02, -r * 0.05)
        else:
            ctx.curve_to(r * 0.85, -r * 0.65, -r * 0.85, -r * 0.65, -r * 1.02, -r * 0.05)
        ctx.close_path()
        fill_stroke(ctx, c, 3)
        if style == 'comb':
            ctx.set_source_rgba(0, 0, 0, 0.25)
            ctx.set_line_width(1.5)
            for i in range(4):
                ctx.move_to(-r * 0.8, -r * (0.75 + i * 0.1))
                ctx.curve_to(-r * 0.2, -r * (1.0 + i * 0.05), r * 0.3, -r * (1.0 + i * 0.05), r * 0.85,
                             -r * (0.6 + i * 0.1))
            ctx.stroke()
    elif style == 'buzz':
        ctx.move_to(-r * 1.0, -r * 0.3)
        ctx.curve_to(-r * 1.05, -r * 1.22, r * 1.05, -r * 1.22, r * 1.0, -r * 0.3)
        ctx.curve_to(r * 0.7, -r * 0.75, -r * 0.7, -r * 0.75, -r * 1.0, -r * 0.3)
        ctx.close_path()
        ctx.set_source_rgba(*c, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgb(*OUT)
        ctx.set_line_width(2)
        ctx.stroke()
    elif style == 'bald':
        for sd in (-1, 1):
            ctx.move_to(sd * r * 1.02, r * 0.05)
            ctx.curve_to(sd * r * 1.1, -r * 0.4, sd * r * 0.95, -r * 0.7, sd * r * 0.7, -r * 0.8)
            ctx.curve_to(sd * r * 0.8, -r * 0.4, sd * r * 0.85, -r * 0.2, sd * r * 1.02, r * 0.05)
            ctx.close_path()
            fill_stroke(ctx, c, 2.5)
        ctx.arc(-r * 0.3, -r * 0.75, r * 0.18, 0, 6.3)
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.fill()
    elif style == 'white':
        rng = random.Random(3)
        for sd in (-1, 1):
            for i in range(4):
                ctx.new_sub_path()
                ctx.arc(sd * r * (0.75 + 0.1 * i), -r * (0.65 - 0.25 * i), r * 0.26, 0, 2 * math.pi)
        ctx.new_sub_path()
        ctx.arc(0, -r * 1.05, r * 0.25, 0, 2 * math.pi)
        fill_stroke(ctx, c, 2.5)
    elif style == 'bob':
        ctx.move_to(-r * 1.08, -r * 0.1)
        ctx.curve_to(-r * 1.15, -r * 1.35, r * 1.15, -r * 1.35, r * 1.08, -r * 0.1)
        ctx.curve_to(r * 0.6, -r * 0.55, -f * r * 0.1, -r * 0.6, -f * r * 0.3, -r * 0.9)
        ctx.curve_to(-r * 0.6, -r * 0.5, -r * 0.9, -r * 0.45, -r * 1.08, -r * 0.1)
        ctx.close_path()
        fill_stroke(ctx, c, 3)
    elif style in ('lowbun', 'bun', 'ponytail', 'pigtails', 'short_f'):
        ctx.move_to(-r * 1.04, -r * 0.05)
        ctx.curve_to(-r * 1.15, -r * 1.32, r * 1.15, -r * 1.32, r * 1.04, -r * 0.05)
        ctx.curve_to(r * 0.9, -r * 0.6, r * 0.2, -r * 0.7, 0, -r * 0.9)
        ctx.curve_to(-r * 0.2, -r * 0.7, -r * 0.9, -r * 0.6, -r * 1.04, -r * 0.05)
        ctx.close_path()
        fill_stroke(ctx, c, 3)
        if style == 'short_f':
            ctx.move_to(-r * 0.9, -r * 0.6)
            ctx.curve_to(-r * 0.4, -r * 0.4, f * r * 0.2, -r * 0.5, f * r * 0.6, -r * 0.65)
            ctx.line_to(f * r * 0.3, -r * 0.95)
            ctx.close_path()
            fill_stroke(ctx, c, 2)
    elif style == 'curly':
        for i in range(7):
            a = math.pi * 1.1 + i * math.pi * 0.8 / 6
            ctx.new_sub_path()
            ctx.arc(math.cos(a) * r * 0.85, math.sin(a) * r * 0.85 - r * 0.1, r * 0.3, 0, 2 * math.pi)
        fill_stroke(ctx, c, 2.5)
    elif style == 'pixie':
        ctx.move_to(-r * 1.04, -r * 0.1)
        ctx.curve_to(-r * 1.15, -r * 1.32, r * 1.15, -r * 1.32, r * 1.04, -r * 0.1)
        ctx.line_to(f * r * 0.3, -r * 0.55)
        ctx.line_to(-f * r * 0.2, -r * 0.7)
        ctx.close_path()
        fill_stroke(ctx, c, 3)
    ctx.restore()


def _draw_bed_back(ctx, look, f):
    W = look.H * 1.25
    # čelo postele
    rrect(ctx, -look.body_w * 1.1, -look.H * 0.7, 28, look.H * 0.7, 6)
    fill_stroke(ctx, hexc('8a5a3a'), 3)
    # polštář
    rrect(ctx, -look.body_w * 1.0, -look.H * 0.55, look.body_w * 1.9, look.H * 0.22, 26)
    fill_stroke(ctx, hexc('eef0f8'), 3)


def _draw_bed_front(ctx, look, f, hip_y):
    W = look.H * 1.3
    x0 = -look.body_w * 1.1
    # matrace + deka
    rrect(ctx, x0, hip_y - 8, W, look.H * 0.2, 14)
    fill_stroke(ctx, hexc('c94f4f'), 3)
    ctx.set_source_rgba(1, 1, 1, 0.25)
    ctx.set_line_width(3)
    for i in range(1, 6):
        ctx.move_to(x0 + W * i / 6, hip_y - 6)
        ctx.line_to(x0 + W * i / 6, hip_y + look.H * 0.19)
    ctx.stroke()
    # nohy postele
    rrect(ctx, x0, hip_y + look.H * 0.17, W, 16, 4)
    fill_stroke(ctx, hexc('8a5a3a'), 3)
    rrect(ctx, x0 + W - 26, -look.H * 0.42, 26, look.H * 0.42, 6)
    fill_stroke(ctx, hexc('8a5a3a'), 3)


def _prop(ctx, prop, hand, f, H, t):
    hx, hy = hand
    ctx.save()
    ctx.translate(hx, hy)
    if prop == 'thermos':
        rrect(ctx, -9, -40, 18, 46, 5)
        fill_stroke(ctx, hexc('2f6f8f'), 2.5)
        rrect(ctx, -10, -46, 20, 9, 3)
        fill_stroke(ctx, hexc('cfcfcf'), 2.5)
    elif prop == 'phone':
        rrect(ctx, -10, -30, 20, 36, 4)
        fill_stroke(ctx, hexc('1a1a22'), 2.5)
        rrect(ctx, -7, -26, 14, 26, 2)
        ctx.set_source_rgb(0.5, 0.75, 1.0)
        ctx.fill()
    elif prop == 'flashlight':
        ctx.rotate(-f * 1.3)
        rrect(ctx, -6, -6, 34 * 1, 12, 3)
        fill_stroke(ctx, hexc('333333'), 2)
    elif prop == 'card':
        rrect(ctx, -14, -12, 28, 18, 2)
        fill_stroke(ctx, (1, 1, 1), 2)
    elif prop == 'hairclip':
        ctx.translate(0, -14)
        ctx.move_to(0, -9)
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = 10 if i % 2 == 0 else 4.5
            ctx.line_to(math.cos(a) * rr, math.sin(a) * rr)
        ctx.close_path()
        fill_stroke(ctx, hexc('ff5fa2'), 1.8)
    elif prop == 'flowers':
        rrect(ctx, -16, -10, 32, 34, 5)
        fill_stroke(ctx, hexc('d9c7a0'), 2)
        for dx, dy in ((-8, -14), (6, -16), (-1, -22), (10, -8), (-11, -6)):
            ctx.arc(dx, dy, 7, 0, 6.3)
            fill_stroke(ctx, hexc('f39c12'), 1.8)
    elif prop == 'notebook':
        rrect(ctx, -16, -24, 30, 36, 2)
        fill_stroke(ctx, hexc('2e4a7a'), 2)
    elif prop == 'megaphone':
        ctx.rotate(-f * 0.2)
        ctx.move_to(0, -6)
        ctx.line_to(f * 40, -18)
        ctx.line_to(f * 40, 18)
        ctx.line_to(0, 6)
        ctx.close_path()
        fill_stroke(ctx, (0.95, 0.95, 0.95), 2.5)
        ctx.rectangle(f * 36, -18, f * 6, 36)
        fill_stroke(ctx, hexc('e74c3c'), 2)
    ctx.restore()
