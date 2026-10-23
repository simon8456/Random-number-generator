"""Prostředí (pozadí) pro scény s postavami. Kreslí se v souřadnicích 1280x720.
Každá funkce kreslí pozadí; volitelně vrací funkci pro popředí."""
import math
import random
from .chars import hexc, shade, mix, rrect, fill_stroke, OUT

W, H = 1280, 720
FLOOR = 640


def lin(ctx, x0, y0, x1, y1, stops):
    import cairo
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, c in stops:
        g.add_color_stop_rgba(o, *c[:3], c[3] if len(c) > 3 else 1)
    return g


def rad(ctx, x, y, r0, r1, stops):
    import cairo
    g = cairo.RadialGradient(x, y, r0, x, y, r1)
    for o, c in stops:
        g.add_color_stop_rgba(o, *c[:3], c[3] if len(c) > 3 else 1)
    return g


def box(ctx, x, y, w, h, col, lw=3, r=0):
    if r:
        rrect(ctx, x, y, w, h, r)
    else:
        ctx.rectangle(x, y, w, h)
    fill_stroke(ctx, col, lw)


def wall_floor(ctx, wall, floor, floor_y=560, wall_tex=None, boards=True):
    ctx.set_source(lin(ctx, 0, 0, 0, floor_y, [(0, shade(wall, 0.06)), (1, shade(wall, -0.08))]))
    ctx.rectangle(-400, -200, W + 800, floor_y + 200)
    ctx.fill()
    if wall_tex == 'stripes':
        ctx.set_source_rgba(1, 1, 1, 0.07)
        for i in range(-10, 40):
            ctx.rectangle(i * 46, -200, 18, floor_y + 200)
        ctx.fill()
    if wall_tex == 'tiles':
        ctx.set_source_rgba(0, 0, 0, 0.08)
        ctx.set_line_width(1.5)
        for i in range(-10, 50):
            ctx.move_to(i * 40, 300)
            ctx.line_to(i * 40, floor_y)
        for j in range(8):
            ctx.move_to(-400, 300 + j * 40)
            ctx.line_to(W + 400, 300 + j * 40)
        ctx.stroke()
    ctx.set_source(lin(ctx, 0, floor_y, 0, H + 200, [(0, shade(floor, 0.05)), (1, shade(floor, -0.2))]))
    ctx.rectangle(-400, floor_y, W + 800, H + 400)
    ctx.fill()
    if boards:
        ctx.set_source_rgba(0, 0, 0, 0.12)
        ctx.set_line_width(2)
        for i in range(-30, 60):
            ctx.move_to(i * 60, floor_y)
            ctx.line_to(i * 60 + (i * 60 - W / 2) * 0.8, H + 200)
        ctx.stroke()
    # lišta
    ctx.rectangle(-400, floor_y - 12, W + 800, 14)
    fill_stroke(ctx, shade(wall, -0.3), 2)


def window_frame(ctx, x, y, w, h, tod, t, view='street'):
    """Okno s výhledem ven."""
    sky = {'day': [(0, hexc('8fc3e8')), (1, hexc('d8ecf5'))],
           'dusk': [(0, hexc('3b3b6b')), (1, hexc('e88a5a'))],
           'night': [(0, hexc('0b1026')), (1, hexc('1d2a4a'))]}[tod]
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    ctx.set_source(lin(ctx, 0, y, 0, y + h, sky))
    ctx.paint()
    # silueta domů
    rng = random.Random(int(x))
    bx = x - 20
    while bx < x + w:
        bw = rng.randint(50, 110)
        bh = rng.randint(int(h * 0.25), int(h * 0.6))
        col = hexc('a7b6c4') if tod == 'day' else hexc('1a2033')
        ctx.rectangle(bx, y + h - bh, bw, bh)
        ctx.set_source_rgb(*col)
        ctx.fill()
        if tod != 'day':
            for wy in range(int(y + h - bh + 10), int(y + h - 10), 22):
                for wx in range(int(bx + 8), int(bx + bw - 12), 20):
                    if rng.random() < 0.35:
                        ctx.rectangle(wx, wy, 9, 11)
                        ctx.set_source_rgba(1, 0.85, 0.45, 0.85)
                        ctx.fill()
        bx += bw + 6
    if tod == 'night':
        ctx.arc(x + w * 0.8, y + h * 0.2, 14, 0, 6.3)
        ctx.set_source_rgb(0.95, 0.95, 0.85)
        ctx.fill()
    ctx.restore()
    ctx.set_line_width(10)
    ctx.set_source_rgb(*hexc('f0ece4'))
    ctx.rectangle(x, y, w, h)
    ctx.stroke()
    ctx.set_line_width(6)
    ctx.move_to(x + w / 2, y)
    ctx.line_to(x + w / 2, y + h)
    ctx.move_to(x, y + h * 0.45)
    ctx.line_to(x + w, y + h * 0.45)
    ctx.stroke()
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(2)
    ctx.rectangle(x - 5, y - 5, w + 10, h + 10)
    ctx.stroke()
    # parapet
    box(ctx, x - 20, y + h + 4, w + 40, 14, hexc('e8e4dc'), 2)


def lamp_glow(ctx, x, y, r, col=(1, 0.85, 0.55), a=0.35):
    ctx.set_source(rad(ctx, x, y, 0, r, [(0, col + (a,)), (1, col + (0,))]))
    ctx.arc(x, y, r, 0, 6.3)
    ctx.fill()


# ---------------------------------------------------------------- místnosti

def set_room(ctx, tod, t):
    wall = hexc('d9cdb5') if tod == 'day' else hexc('8a8270')
    wall_floor(ctx, wall, hexc('9a6a44'))
    # tapeta s jemným vzorem
    ctx.set_source_rgba(1, 1, 1, 0.08)
    for i in range(-8, 30):
        for j in range(12):
            ctx.arc(i * 64 + (j % 2) * 32, j * 50, 4, 0, 6.3)
            ctx.fill()
    window_frame(ctx, 470, 110, 300, 250, tod, t)
    # závěsy
    for sx in (430, 770):
        ctx.move_to(sx, 90)
        ctx.curve_to(sx + 25, 200, sx - 15, 300, sx + 10, 420)
        ctx.line_to(sx + 50, 420)
        ctx.curve_to(sx + 25, 300, sx + 65, 200, sx + 40, 90)
        ctx.close_path()
        fill_stroke(ctx, hexc('3a5f8a'), 2.5)
    box(ctx, 410, 82, 420, 10, hexc('5a4030'), 2, 3)
    # dalekohled na parapetu
    ctx.save()
    ctx.translate(700, 362)
    for dx in (0, 22):
        rrect(ctx, dx, -26, 18, 28, 5)
        fill_stroke(ctx, hexc('2a2a2a'), 2)
    ctx.restore()
    # plakáty
    ctx.save()
    ctx.translate(950, 120)
    ctx.rotate(0.03)
    box(ctx, 0, 0, 150, 200, hexc('1d3557'), 2.5)
    # plakát s mapou
    ctx.set_source_rgb(*hexc('a8dadc'))
    ctx.move_to(20, 40)
    ctx.curve_to(60, 20, 90, 70, 130, 50)
    ctx.line_to(125, 160)
    ctx.curve_to(80, 180, 50, 140, 25, 170)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(1, 1, 1)
    ctx.select_font_face('DejaVu Sans', 0, 1)
    ctx.set_font_size(16)
    ctx.move_to(22, 192)
    ctx.show_text('ORIENŤÁK 2025')
    ctx.restore()
    ctx.save()
    ctx.translate(1130, 160)
    ctx.rotate(-0.05)
    box(ctx, 0, 0, 110, 150, hexc('e63946'), 2.5)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_font_size(30)
    ctx.move_to(14, 80)
    ctx.show_text('BUZOLA')
    ctx.restore()
    # stůl s notebookem a deníkem
    box(ctx, 860, 450, 330, 22, hexc('7a5236'), 3, 4)
    box(ctx, 880, 470, 18, 170, hexc('6a4630'), 2.5)
    box(ctx, 1150, 470, 18, 170, hexc('6a4630'), 2.5)
    box(ctx, 950, 400, 120, 52, hexc('3a3a44'), 2.5, 4)
    ctx.set_source_rgb(0.55, 0.75, 0.95) if tod == 'day' else ctx.set_source_rgb(0.35, 0.55, 0.95)
    rrect(ctx, 958, 406, 104, 40, 3)
    ctx.fill()
    box(ctx, 1090, 434, 70, 16, hexc('8b2e2e'), 2, 2)
    # lampička
    box(ctx, 1110, 380, 8, 54, hexc('333333'), 2)
    ctx.move_to(1090, 380)
    ctx.line_to(1140, 380)
    ctx.line_to(1128, 350)
    ctx.line_to(1102, 350)
    ctx.close_path()
    fill_stroke(ctx, hexc('f4d35e'), 2.5)
    if tod != 'day':
        lamp_glow(ctx, 1115, 395, 260, a=0.4)
    # police s knihami
    box(ctx, 80, 170, 230, 12, hexc('7a5236'), 2.5)
    box(ctx, 80, 270, 230, 12, hexc('7a5236'), 2.5)
    rng = random.Random(4)
    for shelf_y in (170, 270):
        bx = 90
        while bx < 290:
            bw = rng.randint(12, 22)
            bh = rng.randint(50, 80)
            box(ctx, bx, shelf_y - bh, bw, bh, hexc(rng.choice(['c0392b', '2980b9', '27ae60', 'f39c12', '8e44ad',
                                                                   '34495e'])), 2)
            bx += bw + 2
    # glóbus na polici
    ctx.arc(250, 140, 26, 0, 6.3)
    fill_stroke(ctx, hexc('4a90c2'), 2.5)
    # koberec
    ctx.save()
    ctx.translate(640, 670)
    ctx.scale(1, 0.22)
    ctx.arc(0, 0, 330, 0, 6.3)
    ctx.restore()
    fill_stroke(ctx, hexc('6d8a96'), 2.5)


def set_hall(ctx, tod, t):
    wall_floor(ctx, hexc('e3d7c1') if tod == 'day' else hexc('9a8e78'), hexc('8a6a4a'))
    # dveře
    box(ctx, 900, 170, 210, 470, hexc('7a4a2a'), 3, 4)
    for yy in (200, 420):
        box(ctx, 925, yy, 160, 190, hexc('8a5a36'), 2, 3)
    ctx.arc(1080, 410, 9, 0, 6.3)
    fill_stroke(ctx, hexc('d4af37'), 2)
    ctx.arc(1005, 260, 7, 0, 6.3)
    fill_stroke(ctx, hexc('222222'), 1.5)
    # věšák s bundami
    box(ctx, 120, 200, 260, 14, hexc('5a3a22'), 2.5, 3)
    for i, c in enumerate(['d9663b', '3a5f8a', 'f1c40f', '6c4a8a']):
        x = 140 + i * 62
        ctx.move_to(x, 214)
        ctx.curve_to(x - 30, 260, x - 26, 360, x - 20, 400)
        ctx.line_to(x + 40, 400)
        ctx.curve_to(x + 44, 360, x + 50, 260, x + 20, 214)
        ctx.close_path()
        fill_stroke(ctx, hexc(c), 2.5)
    # zrcadlo
    ctx.save()
    ctx.translate(560, 300)
    ctx.scale(1, 1.3)
    ctx.arc(0, 0, 80, 0, 6.3)
    ctx.restore()
    fill_stroke(ctx, hexc('c8dbe6'), 5)
    # botník
    box(ctx, 120, 560, 280, 80, hexc('6a4a30'), 3, 4)
    # rohožka
    box(ctx, 860, 630, 290, 18, hexc('5a7a4a'), 2, 6)
    # světlo
    lamp_glow(ctx, 640, 60, 420, a=0.3 if tod != 'day' else 0.15)
    ctx.move_to(600, 0)
    ctx.line_to(600, 40)
    ctx.stroke()
    ctx.arc(600, 60, 26, math.pi, 0)
    fill_stroke(ctx, hexc('f5e6b8'), 2.5)


def set_sborovna(ctx, tod, t):
    wall_floor(ctx, hexc('cfd8c4'), hexc('8a7a5a'), wall_tex='stripes')
    # okna
    for x in (60, 420):
        window_frame(ctx, x, 100, 230, 220, 'day', t)
    # nástěnka
    box(ctx, 760, 110, 360, 230, hexc('c49a6c'), 3, 4)
    rng = random.Random(9)
    for i in range(9):
        px = 780 + (i % 3) * 112 + rng.randint(-6, 6)
        py = 125 + (i // 3) * 70 + rng.randint(-4, 4)
        box(ctx, px, py, 90, 58, hexc(rng.choice(['ffffff', 'fff3b0', 'cde7f0', 'f9d5d3'])), 1.5)
        ctx.arc(px + 45, py + 4, 4, 0, 6.3)
        ctx.set_source_rgb(0.85, 0.1, 0.1)
        ctx.fill()
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.select_font_face('DejaVu Sans', 0, 1)
    ctx.set_font_size(15)
    ctx.move_to(800, 355)
    ctx.show_text('ROZVRH SUPLOVÁNÍ')
    # kávovar
    box(ctx, 1150, 380, 90, 120, hexc('2a2a2a'), 3, 6)
    ctx.arc(1195, 420, 14, 0, 6.3)
    fill_stroke(ctx, hexc('c0392b'), 2)
    box(ctx, 1140, 500, 120, 140, hexc('7a5a3a'), 3, 3)
    # dlouhý stůl
    box(ctx, 120, 520, 1000, 24, hexc('8a6a4a'), 3, 4)
    for x in (150, 1070):
        box(ctx, x, 544, 20, 96, hexc('6a4a30'), 2.5)
    for x, c in ((300, 'ffffff'), (520, 'f4f4f4'), (760, 'ffffff')):
        box(ctx, x, 506, 80, 14, hexc(c), 1.5)
    ctx.arc(640, 508, 12, 0, 6.3)
    fill_stroke(ctx, hexc('ecf0f1'), 2)


def set_office(ctx, tod, t):
    wall_floor(ctx, hexc('b9a88a'), hexc('6a4a30'))
    box(ctx, 200, 520, 880, 30, hexc('5a3a22'), 3, 4)


def set_classroom(ctx, tod, t):
    wall_floor(ctx, hexc('e8e2c8'), hexc('a07850'))
    box(ctx, 360, 110, 620, 260, hexc('2d4a3a'), 6, 4)
    ctx.set_source_rgba(1, 1, 1, 0.85)
    ctx.select_font_face('DejaVu Sans', 1, 0)
    ctx.set_font_size(26)
    ctx.move_to(400, 170)
    ctx.show_text('Zeměpis — Česká republika')
    ctx.set_line_width(3)
    ctx.move_to(420, 240)
    ctx.curve_to(520, 200, 640, 290, 900, 230)
    ctx.line_to(880, 330)
    ctx.curve_to(700, 350, 560, 300, 430, 330)
    ctx.close_path()
    ctx.stroke()
    box(ctx, 360, 370, 620, 12, hexc('8a6a4a'), 2)
    for x in (60, 1060):
        window_frame(ctx, x, 120, 170, 230, 'day', t)
    # mapa na stěně
    box(ctx, 1030, 400, 0, 0, (1, 1, 1), 0)


def set_lab(ctx, tod, t):
    wall_floor(ctx, hexc('d8e8ec'), hexc('9aa8b0'), wall_tex='tiles', boards=False)
    # monitory, mikroskop
    box(ctx, 140, 470, 1000, 26, hexc('e8eef0'), 3, 3)
    box(ctx, 160, 496, 980, 144, hexc('c8d4d8'), 3, 3)
    box(ctx, 220, 330, 200, 140, hexc('2a2f36'), 3, 6)
    ctx.set_source_rgb(0.1, 0.25, 0.2)
    rrect(ctx, 232, 342, 176, 116, 3)
    ctx.fill()
    ctx.set_source_rgb(0.3, 1, 0.6)
    ctx.set_line_width(2.5)
    ph = t * 120
    ctx.move_to(236, 400)
    for i in range(0, 168, 4):
        xx = 236 + i
        v = 0
        k = (i + ph) % 60
        if 20 < k < 24:
            v = -40
        elif 24 <= k < 28:
            v = 25
        ctx.line_to(xx, 400 + v)
    ctx.stroke()
    # zkumavky
    for i in range(8):
        box(ctx, 900 + i * 22, 400, 14, 70, hexc(['e74c3c', 'f1c40f', '9b59b6', '3498db'][i % 4]), 2, 6)
    box(ctx, 880, 460, 200, 12, hexc('7f8c8d'), 2)
    lamp_glow(ctx, 640, 0, 600, (0.85, 0.95, 1.0), 0.25)


def set_chemlab(ctx, tod, t):
    wall_floor(ctx, hexc('d5e0d0'), hexc('8a8a7a'), wall_tex='tiles', boards=False)
    box(ctx, 80, 110, 360, 240, hexc('2d4a3a'), 6, 4)
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.select_font_face('DejaVu Sans', 0, 0)
    ctx.set_font_size(24)
    ctx.move_to(110, 170)
    ctx.show_text('C₁₇H₂₁NO₄')
    ctx.move_to(110, 220)
    ctx.show_text('skopolamin')
    # periodická tabulka
    for i in range(18):
        for j in range(7):
            if j == 0 and 0 < i < 17:
                continue
            if j < 3 and 1 < i < 12:
                continue
            ctx.rectangle(760 + i * 24, 110 + j * 26, 22, 24)
            ctx.set_source_rgb(*hexc(['f9d5d3', 'cde7f0', 'fff3b0', 'd5f5e3'][(i + j) % 4]))
            ctx.fill()
    box(ctx, 100, 480, 1080, 26, hexc('2a2a2a'), 3, 3)
    box(ctx, 120, 506, 1040, 134, hexc('e8e8e0'), 3, 3)
    # baňky
    for i, c in enumerate(['2ecc71', 'e67e22', '9b59b6']):
        x = 820 + i * 90
        ctx.move_to(x - 10, 400)
        ctx.line_to(x + 10, 400)
        ctx.line_to(x + 10, 430)
        ctx.line_to(x + 35, 478)
        ctx.line_to(x - 35, 478)
        ctx.line_to(x - 10, 430)
        ctx.close_path()
        fill_stroke(ctx, (0.9, 0.95, 1.0), 2.5)
        ctx.move_to(x - 25, 460)
        ctx.line_to(x + 25, 460)
        ctx.line_to(x + 35, 478)
        ctx.line_to(x - 35, 478)
        ctx.close_path()
        ctx.set_source_rgb(*hexc(c))
        ctx.fill()


def set_archive(ctx, tod, t):
    wall_floor(ctx, hexc('a89a80'), hexc('6a5a44'))
    rng = random.Random(11)
    for sx in (40, 360, 820, 1080):
        box(ctx, sx, 90, 200, 550, hexc('5a4a36'), 3)
        for j in range(6):
            yy = 120 + j * 86
            box(ctx, sx + 8, yy + 70, 184, 8, hexc('4a3a28'), 1.5)
            bx = sx + 12
            while bx < sx + 180:
                bw = rng.randint(14, 30)
                box(ctx, bx, yy + 10, bw, 60, hexc(rng.choice(['d8c8a0', 'c8b890', 'b0a080', 'e0d4b0'])), 1.5)
                bx += bw + 2
    lamp_glow(ctx, 640, 120, 420, a=0.4)
    ctx.move_to(640, 0)
    ctx.line_to(640, 90)
    ctx.set_source_rgb(*OUT)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.move_to(600, 120)
    ctx.line_to(680, 120)
    ctx.line_to(660, 90)
    ctx.line_to(620, 90)
    ctx.close_path()
    fill_stroke(ctx, hexc('2e5a3a'), 2)
    box(ctx, 380, 520, 520, 22, hexc('6a4a30'), 3, 3)


def set_kunes(ctx, tod, t):
    wall = hexc('d9c4a0') if tod == 'day' else hexc('7a6a50')
    wall_floor(ctx, wall, hexc('7a5a3a'))
    ctx.set_source_rgba(0.6, 0.3, 0.3, 0.12)
    for i in range(-5, 30):
        for j in range(12):
            ctx.save()
            ctx.translate(i * 70 + (j % 2) * 35, j * 52)
            for k in range(5):
                ctx.rotate(math.pi * 2 / 5)
                ctx.arc(0, 7, 5, 0, 6.3)
                ctx.fill()
            ctx.restore()
    window_frame(ctx, 520, 120, 240, 220, tod, t)
    # krajková záclona
    ctx.set_source_rgba(1, 1, 1, 0.35)
    ctx.rectangle(520, 120, 240, 140)
    ctx.fill()
    # obrázky na stěně
    for x, y in ((140, 140), (300, 180), (900, 150), (1080, 190)):
        box(ctx, x, y, 90, 110, hexc('c49a50'), 4, 2)
        ctx.set_source_rgb(*hexc('6a8a6a'))
        ctx.rectangle(x + 10, y + 10, 70, 90)
        ctx.fill()
    # křeslo, stolek, rádio
    box(ctx, 960, 520, 220, 26, hexc('5a3a22'), 3, 4)
    box(ctx, 1010, 470, 110, 50, hexc('8a6a3a'), 3, 6)
    ctx.arc(1040, 495, 14, 0, 6.3)
    fill_stroke(ctx, hexc('3a3a3a'), 2)
    # pes Bobík
    _dog(ctx, 200, 630, 1, t)
    if tod != 'day':
        lamp_glow(ctx, 1065, 420, 300, a=0.35)


def _dog(ctx, x, y, f, t):
    ctx.save()
    ctx.translate(x, y)
    wag = math.sin(t * 10) * 0.4
    c = hexc('c8964a')
    ctx.save()
    ctx.translate(-f * 40, -50)
    ctx.rotate(-f * (0.8 + wag))
    rrect(ctx, -4, -30, 8, 32, 4)
    fill_stroke(ctx, c, 2.5)
    ctx.restore()
    for dx in (-30, -15, 18, 32):
        box(ctx, dx, -30, 10, 30, c, 2.5, 3)
    rrect(ctx, -45, -65, 90, 42, 20)
    fill_stroke(ctx, c, 3)
    ctx.arc(f * 50, -72, 22, 0, 6.3)
    fill_stroke(ctx, c, 3)
    ctx.save()
    ctx.translate(f * 40, -86)
    ctx.rotate(f * 0.4)
    ctx.scale(0.55, 1)
    ctx.arc(0, 0, 14, 0, 6.3)
    ctx.restore()
    fill_stroke(ctx, hexc('8a5a2a'), 2.5)
    ctx.arc(f * 70, -70, 5, 0, 6.3)
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.fill()
    ctx.arc(f * 55, -78, 3.5, 0, 6.3)
    ctx.fill()
    ctx.restore()


def set_garage(ctx, tod, t):
    wall_floor(ctx, hexc('6a6a66'), hexc('4a4a48'), boards=False)
    # beton - skvrny
    rng = random.Random(5)
    for i in range(30):
        ctx.arc(rng.uniform(0, W), rng.uniform(560, 720), rng.uniform(5, 30), 0, 6.3)
        ctx.set_source_rgba(0, 0, 0, 0.08)
        ctx.fill()
    # cihly
    ctx.set_source_rgba(0, 0, 0, 0.12)
    ctx.set_line_width(1.5)
    for j in range(14):
        yy = 40 * j
        ctx.move_to(-400, yy)
        ctx.line_to(W + 400, yy)
        for i in range(-10, 30):
            xx = i * 80 + (j % 2) * 40
            ctx.move_to(xx, yy)
            ctx.line_to(xx, yy + 40)
    ctx.stroke()
    # regály s nářadím
    box(ctx, 60, 160, 260, 10, hexc('5a4a3a'), 2)
    box(ctx, 60, 300, 260, 10, hexc('5a4a3a'), 2)
    for i in range(5):
        box(ctx, 80 + i * 48, 110, 30, 50, hexc(['c0392b', '7f8c8d', 'f39c12', '2c3e50', '16a085'][i]), 2, 4)
    # lopata opřená o zeď
    ctx.save()
    ctx.translate(380, 620)
    ctx.rotate(-0.12)
    box(ctx, -5, -320, 10, 260, hexc('8a6a3a'), 2)
    ctx.move_to(-28, -60)
    ctx.line_to(28, -60)
    ctx.line_to(22, 0)
    ctx.curve_to(10, 14, -10, 14, -22, 0)
    ctx.close_path()
    fill_stroke(ctx, hexc('7a7a80'), 2.5)
    ctx.restore()
    # mapa na zdi (v dálce)
    box(ctx, 560, 130, 330, 230, hexc('efe6c8'), 3, 2)
    ctx.set_source_rgba(0.3, 0.55, 0.3, 0.4)
    for i in range(6):
        ctx.arc(600 + i * 50, 200 + (i % 3) * 40, 35, 0, 6.3)
        ctx.fill()
    for i in range(16):
        ctx.arc(580 + rng.uniform(0, 290), 150 + rng.uniform(0, 190), 4, 0, 6.3)
        ctx.set_source_rgb(0.85, 0.05, 0.05)
        ctx.fill()
    # mrazák vpravo
    box(ctx, 960, 470, 230, 170, hexc('e8ecef'), 3, 8)
    box(ctx, 955, 455, 240, 26, hexc('f4f6f8'), 3, 6)
    box(ctx, 1150, 500, 20, 8, hexc('2ecc71'), 1)
    # kolo pod plachtou
    ctx.move_to(700, 640)
    ctx.curve_to(690, 520, 760, 470, 820, 480)
    ctx.curve_to(880, 470, 930, 540, 920, 640)
    ctx.close_path()
    fill_stroke(ctx, hexc('4a5a6a'), 3)
    ctx.arc(720, 610, 30, 0, 6.3)
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.move_to(712, 590)
    ctx.line_to(740, 600)
    ctx.set_source_rgb(*hexc('c0392b'))
    ctx.set_line_width(6)
    ctx.stroke()
    # žárovka
    ctx.move_to(640, 0)
    ctx.line_to(640, 60)
    ctx.set_source_rgb(0.1, 0.1, 0.1)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.arc(640, 70, 12, 0, 6.3)
    fill_stroke(ctx, hexc('fff4c0'), 2)


def _tree(ctx, x, y, s, col, trunk=None):
    trunk = trunk or shade(col, -0.4)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rectangle(-8, -60, 16, 60)
    ctx.set_source_rgb(*trunk)
    ctx.fill()
    for i, (w, hh) in enumerate(((70, 90), (58, 80), (44, 70), (28, 55))):
        yy = -50 - i * 48
        ctx.move_to(-w, yy)
        ctx.line_to(0, yy - hh)
        ctx.line_to(w, yy)
        ctx.close_path()
        ctx.set_source_rgb(*shade(col, -0.05 * i))
        ctx.fill()
    ctx.restore()


def set_forest(ctx, tod, t):
    ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, hexc('060a14')), (0.6, hexc('101a28')), (1, hexc('1a2418'))]))
    ctx.rectangle(-400, -200, W + 800, H + 400)
    ctx.fill()
    ctx.arc(980, 110, 30, 0, 6.3)
    ctx.set_source_rgba(0.85, 0.88, 0.95, 0.5)
    ctx.fill()
    rng = random.Random(21)
    for layer, (col, sc, yy) in enumerate(((hexc('16222e'), 0.8, 520), (hexc('0f1a22'), 1.1, 580),
                                           (hexc('0a1218'), 1.5, 680))):
        for i in range(24):
            _tree(ctx, -300 + i * 85 + rng.uniform(-30, 30), yy + rng.uniform(-10, 10), sc * rng.uniform(0.8, 1.2),
                  col)
    ctx.set_source(lin(ctx, 0, 560, 0, H, [(0, hexc('1a2418')), (1, hexc('0c120c'))]))
    ctx.rectangle(-400, 600, W + 800, 400)
    ctx.fill()
    # cedulka kontroly (oranžovobílý lampion)
    ctx.save()
    ctx.translate(1040, 470)
    box(ctx, -3, 0, 6, 160, hexc('6a4a2a'), 1.5)
    ctx.move_to(-26, 0)
    ctx.line_to(26, 0)
    ctx.line_to(26, -52)
    ctx.line_to(-26, -52)
    ctx.close_path()
    fill_stroke(ctx, (1, 1, 1), 2)
    ctx.move_to(-26, 0)
    ctx.line_to(26, -52)
    ctx.line_to(-26, -52)
    ctx.close_path()
    ctx.set_source_rgb(*hexc('e8590c'))
    ctx.fill()
    ctx.restore()


def set_street(ctx, tod, t):
    ctx.set_source(lin(ctx, 0, 0, 0, 500, [(0, hexc('070b18')), (1, hexc('1a2440'))]))
    ctx.rectangle(-400, -200, W + 800, 900)
    ctx.fill()
    # panelák
    box(ctx, -100, 60, 640, 560, hexc('3a4256'), 3)
    rng = random.Random(2)
    for j in range(7):
        for i in range(8):
            lit = rng.random() < 0.4
            ctx.rectangle(-70 + i * 76, 90 + j * 72, 44, 46)
            ctx.set_source_rgb(*(hexc('f5d58a') if lit else hexc('1c2232')))
            ctx.fill()
    # vila v dálce
    box(ctx, 760, 330, 360, 250, hexc('cfcfc4'), 3)
    ctx.move_to(740, 340)
    ctx.line_to(940, 220)
    ctx.line_to(1140, 340)
    ctx.close_path()
    fill_stroke(ctx, hexc('6a3a2a'), 3)
    ctx.rectangle(-400, 610, W + 800, 200)
    ctx.set_source_rgb(*hexc('25252a'))
    ctx.fill()
    # lampa
    box(ctx, 640, 260, 10, 380, hexc('2a2a2a'), 2)
    ctx.arc(645, 255, 16, 0, 6.3)
    fill_stroke(ctx, hexc('fff2b0'), 2)
    lamp_glow(ctx, 645, 300, 320, a=0.35)


def set_bunker(ctx, tod, t):
    ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, hexc('2a2a28')), (1, hexc('3a3a34'))]))
    ctx.rectangle(-400, -200, W + 800, H + 400)
    ctx.fill()
    # klenba
    ctx.move_to(-400, 560)
    ctx.line_to(-400, 260)
    ctx.curve_to(100, -60, 1180, -60, 1680, 260)
    ctx.line_to(1680, 560)
    ctx.set_source_rgba(0, 0, 0, 0.0)
    ctx.set_source_rgb(*hexc('4a4a44'))
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ctx.set_line_width(2)
    for i in range(10):
        ctx.move_to(-400 + i * 230, 560)
        ctx.line_to(-400 + i * 230, 200 - abs(i - 4.5) * 10)
    ctx.stroke()
    ctx.rectangle(-400, 560, W + 800, 400)
    ctx.set_source_rgb(*hexc('2a2824'))
    ctx.fill()
    # kapající voda, trubky, nápis
    box(ctx, -100, 120, 1500, 16, hexc('5a4a3a'), 2)
    ctx.set_source_rgba(0.85, 0.85, 0.8, 0.5)
    ctx.select_font_face('DejaVu Sans', 0, 1)
    ctx.set_font_size(36)
    ctx.move_to(420, 260)
    ctx.show_text('KRYT  CO  —  VSTUP ZAKÁZÁN')
    # matrace a lano
    box(ctx, 900, 600, 300, 40, hexc('6a6a5a'), 3, 8)


def set_quarry(ctx, tod, t):
    ctx.set_source(lin(ctx, 0, 0, 0, H, [(0, hexc('05080f')), (1, hexc('141c26'))]))
    ctx.rectangle(-400, -200, W + 800, H + 400)
    ctx.fill()
    rng = random.Random(31)
    for i in range(20):
        _tree(ctx, -300 + i * 100, 420 + rng.uniform(-20, 10), 0.9, hexc('0e161e'))
    # skalní hrana a voda
    ctx.move_to(-400, 640)
    ctx.line_to(760, 640)
    ctx.line_to(800, 660)
    ctx.line_to(840, 720)
    ctx.line_to(-400, 720)
    ctx.close_path()
    ctx.set_source_rgb(*hexc('2a2a2e'))
    ctx.fill()
    ctx.move_to(-400, 640)
    ctx.line_to(760, 640)
    ctx.set_source_rgb(*hexc('4a4a50'))
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.rectangle(820, 680, 900, 100)
    ctx.set_source(lin(ctx, 0, 680, 0, 760, [(0, hexc('1a3a4a')), (1, hexc('061018'))]))
    ctx.fill()
    for i in range(6):
        ctx.move_to(860 + i * 70 + math.sin(t + i) * 10, 690 + i % 2 * 8)
        ctx.line_to(900 + i * 70 + math.sin(t + i) * 10, 690 + i % 2 * 8)
    ctx.set_source_rgba(0.6, 0.8, 0.9, 0.4)
    ctx.set_line_width(2)
    ctx.stroke()
    # kámen s nápisem
    ctx.move_to(780, 640)
    ctx.line_to(800, 610)
    ctx.line_to(850, 615)
    ctx.line_to(860, 640)
    ctx.close_path()
    fill_stroke(ctx, hexc('5a5a60'), 2.5)


def set_videocall(ctx, tod, t):
    ctx.set_source_rgb(0.1, 0.1, 0.12)
    ctx.paint()


SETS = {
    'room': set_room, 'hall': set_hall, 'sborovna': set_sborovna, 'classroom': set_classroom, 'lab': set_lab,
    'chemlab': set_chemlab, 'archive': set_archive, 'kunes': set_kunes, 'garage': set_garage,
    'forest': set_forest, 'street': set_street, 'bunker': set_bunker, 'quarry': set_quarry,
    'office': set_office, 'videocall': set_videocall,
}


def draw_set(ctx, name, tod, t):
    fn = SETS.get(name)
    if fn:
        fn(ctx, tod, t)
    else:
        ctx.set_source_rgb(0.05, 0.05, 0.07)
        ctx.paint()


# výška podlahy (y) a měřítko postav pro každé prostředí
STAGE = {
    'room': (650, 1.0), 'hall': (655, 1.05), 'sborovna': (655, 0.95), 'classroom': (660, 0.95),
    'lab': (655, 1.0), 'chemlab': (660, 1.0), 'archive': (660, 1.0), 'kunes': (660, 1.0), 'garage': (660, 1.0),
    'forest': (680, 0.95), 'street': (660, 1.0), 'bunker': (660, 1.0), 'quarry': (645, 1.0), 'office': (655, 1.0),
}
