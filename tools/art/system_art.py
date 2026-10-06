"""img/system/* : window skin, icons, balloons and the engine's required images."""
import math
import os

from PIL import Image

from pixlib import Canvas, shade, mix, rgba, rng
from textutil import draw_text
import palette as P

INK = '#3b2a33'


# ---------------------------------------------------------------------------
# Window.png (drawn at 96x96 logical, saved 2x = 192x192)
# ---------------------------------------------------------------------------
TEXT_COLORS = [
    '#fff8ec', '#8fd0ff', '#ff9a7a', '#9be38a', '#8aa8ff', '#e0a0ff', '#ffd98a', '#b8b0b8',
    '#d8d0d8', '#6aa8e0', '#e06a50', '#6ab060', '#6080d0', '#b070d0', '#e8c060', '#202028',
    '#ffd890', '#ffe060', '#ff6060', '#20202a', '#e08040', '#f0c060', '#4080e0', '#80c0ff',
    '#80ff80', '#c06060', '#d89cff', '#b080ff', '#60c060', '#a0e060', '#c8a0a0', '#f0e8d8',
]


def window_skin():
    cv = Canvas(96, 96)
    # background (0,0,48,48): warm night gradient
    top, bot = rgba('#33304a'), rgba('#1e1c2c')
    for y in range(48):
        c = mix(top, bot, y / 47)
        cv.hline(0, y, 48, c)
    # pattern (0,48,48,48): faint music staff lines
    for y in range(48, 96):
        k = (y - 48) % 24
        if k in (4, 7, 10, 13, 16):
            cv.hline(0, y, 48, (255, 240, 210, 14))
    for (x, y) in ((10, 48 + 9), (31, 48 + 12)):
        cv.ellipse(x, y, 1.6, 1.2, (255, 240, 210, 18))
        cv.vline(x + 1, y - 5, 5, (255, 240, 210, 18))
    # frame (48,0,48,48) corners 12x12
    gold, gold_lo = rgba('#e9cf9a'), rgba('#a8875a')
    fx, fy, fw = 48, 0, 48
    for i in range(fw):
        for (y, c) in ((1, gold_lo), (2, gold)):
            if 3 <= i <= fw - 4:
                cv.px(fx + i, fy + y, c)
                cv.px(fx + i, fy + fw - 1 - y, c)
                cv.px(fx + y, fy + i, c)
                cv.px(fx + fw - 1 - y, fy + i, c)
    # rounded corners
    for (cx, cy, sx, sy) in ((fx + 3, fy + 3, 1, 1), (fx + fw - 4, fy + 3, -1, 1),
                             (fx + 3, fy + fw - 4, 1, -1), (fx + fw - 4, fy + fw - 4, -1, -1)):
        cv.px(cx - sx * 1, cy, gold)
        cv.px(cx, cy - sy * 1, gold)
        cv.px(cx - sx * 0, cy - sy * 0, gold_lo)
        # tiny note ornament
        cv.px(cx + sx * 3, cy + sy * 3, gold)
        cv.px(cx + sx * 4, cy + sy * 3, gold)
        cv.px(cx + sx * 4, cy + sy * 2, gold)
    # cursor (48,48,24,24)
    cx, cy = 48, 48
    for y in range(24):
        for x in range(24):
            edge = x in (0, 23) or y in (0, 23)
            if (x in (0, 23) and y in (0, 23)):
                continue
            cv.px(cx + x, cy + y, (255, 226, 160, 200) if edge else (255, 220, 150, 60))
    # scroll arrows live inside the frame block: up (66,12,12,6), down (66,30,12,6)
    for i in range(4):
        cv.hline(72 - i - 1, 12 + 1 + i, 2 * i + 2, gold)        # up: narrow at top
        cv.hline(72 - (3 - i) - 1, 30 + 1 + i, 2 * (3 - i) + 2, gold)  # down: wide at top
    # pause sign (72,48,24,24): 4 frames of 12x12, a bouncing note
    for f in range(4):
        ox = 72 + (f % 2) * 12
        oy = 48 + (f // 2) * 12
        dy = [0, -1, -1, 0][f]
        cv.ellipse(ox + 5, oy + 8 + dy, 2, 1.6, gold)
        cv.vline(ox + 6, oy + 3 + dy, 5, gold)
        cv.px(ox + 7, oy + 3 + dy, gold)
        cv.px(ox + 8, oy + 4 + dy, gold)
    img = cv.image(2)
    # text colours (96,144) 12x12 swatches at full res
    px = img.load()
    for n, c in enumerate(TEXT_COLORS):
        col = rgba(c)
        x0 = 96 + (n % 8) * 12
        y0 = 144 + (n // 8) * 12
        for y in range(y0, y0 + 12):
            for x in range(x0, x0 + 12):
                px[x, y] = col
    return img


# ---------------------------------------------------------------------------
# IconSet.png : 16 x 16 logical icons, 16 per row, saved 2x (32 px)
# ---------------------------------------------------------------------------

def _icon_harmonica(cv):
    cv.rect(1, 6, 14, 5, '#c9c5bc')
    cv.hline(1, 6, 14, '#f0efea')
    cv.hline(1, 8, 14, '#8a8a96')
    for x in range(2, 14, 2):
        cv.px(x, 9, INK)
    cv.outline(INK)


def _icon_guitar(cv):
    cv.line(10, 1, 7, 7, P.WOOD_DEEP)
    cv.line(11, 1, 8, 7, P.WOOD_DEEP)
    cv.rect(10, 0, 3, 2, INK)
    cv.ellipse(6, 9, 3.5, 3, '#c97a3a')
    cv.ellipse(5, 12, 4, 3, '#c97a3a')
    cv.px(6, 10, '#2a1a12')
    cv.outline(INK)


def _icon_letter(cv):
    cv.rect(2, 4, 12, 9, '#f4efe4')
    cv.line(2, 4, 8, 9, '#c9c2b2')
    cv.line(13, 4, 8, 9, '#c9c2b2')
    cv.px(8, 10, '#d8302a')
    cv.outline(INK)


def _icon_note(cv, col='#f7d55c'):
    cv.ellipse(5, 12, 2.6, 2, col)
    cv.ellipse(11, 11, 2.6, 2, col)
    cv.rect(7, 3, 1, 9, col)
    cv.rect(13, 2, 1, 9, col)
    cv.rect(7, 2, 7, 2, col)
    cv.outline(shade(col, 0.5))


def _icon_candy(cv):
    cv.ellipse(8, 8, 3.5, 3, '#f2a0b8')
    cv.px(7, 7, '#ffffff')
    for (x, y) in ((2, 6), (2, 10), (3, 8), (14, 6), (14, 10), (13, 8)):
        cv.px(x, y, '#f7d55c')
    cv.outline(INK)


def _icon_recorder(cv):
    cv.line(3, 13, 12, 3, '#f4efe4')
    cv.line(4, 13, 13, 3, '#e0d6c0')
    cv.px(6, 10, INK)
    cv.px(8, 8, INK)
    cv.px(10, 6, INK)
    cv.outline(INK)


def _icon_photo(cv):
    cv.rect(2, 3, 12, 10, '#fbf8f2')
    cv.rect(3, 4, 10, 7, '#cfe6f2')
    cv.rect(5, 7, 2, 4, INK)
    cv.rect(9, 8, 2, 3, '#d8574f')
    cv.outline(INK)


def _icon_notebook(cv):
    cv.rect(3, 2, 10, 12, '#8a5a3a')
    cv.rect(4, 3, 8, 10, '#c49a6a')
    cv.rect(6, 5, 5, 3, '#f4efe4')
    cv.vline(3, 2, 12, '#5a3a2a')
    cv.outline(INK)


def _icon_pick(cv):
    for y in range(4, 13):
        w = max(1, 5 - (y - 4) // 2)
        cv.hline(8 - w, y, 2 * w, '#e8584f')
    cv.px(6, 5, '#ff9a8a')
    cv.outline(INK)


def _icon_lyrics(cv):
    cv.rect(3, 2, 10, 12, '#fbf8f2')
    for y in (4, 6, 8, 10):
        cv.hline(5, y, 6, '#9a9aa8')
    cv.outline(INK)


def _icon_flower(cv):
    for (x, y) in ((8, 4), (5, 7), (11, 7), (6, 10), (10, 10)):
        cv.ellipse(x, y, 2, 2, '#f2a0b8')
    cv.ellipse(8, 7, 1.5, 1.5, '#f7d55c')
    cv.vline(8, 11, 4, P.LEAF_LO)
    cv.outline(INK)


def _icon_heart(cv):
    cv.ellipse(5.5, 6, 3, 3, '#e8584f')
    cv.ellipse(10.5, 6, 3, 3, '#e8584f')
    for y in range(7, 14):
        w = 13 - y
        cv.hline(8 - w, y, 2 * w, '#e8584f')
    cv.px(5, 5, '#ff9a8a')
    cv.outline(INK)


def _icon_star(cv):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 6.5 if i % 2 == 0 else 3
        pts.append((8 + r * math.cos(a), 8 + r * math.sin(a)))
    for y in range(16):
        for x in range(16):
            inside = False
            j = len(pts) - 1
            for i in range(len(pts)):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if ((yi > y + 0.5) != (yj > y + 0.5)) and (x + 0.5 < (xj - xi) * (y + 0.5 - yi) / (yj - yi) + xi):
                    inside = not inside
                j = i
            if inside:
                cv.px(x, y, '#f7d55c')
    cv.outline(INK)


def _icon_popsicle(cv):
    cv.rect(5, 2, 6, 9, '#9ad6f2')
    cv.rect(5, 2, 6, 3, '#f2a0b8')
    cv.px(6, 3, '#ffffff')
    cv.rect(7, 11, 2, 4, '#d9b98a')
    cv.outline(INK)


ICONS = {
    14: _icon_popsicle,
    1: _icon_harmonica, 2: _icon_guitar, 3: _icon_letter, 4: _icon_note, 5: _icon_candy,
    6: _icon_recorder, 7: _icon_photo, 8: _icon_notebook, 9: _icon_pick, 10: _icon_lyrics,
    11: _icon_flower, 12: _icon_heart, 13: _icon_star,
    16: lambda cv: _icon_note(cv, '#ff8a6a'), 17: lambda cv: _icon_note(cv, '#ffc060'),
    18: lambda cv: _icon_note(cv, '#7ac0ff'), 19: lambda cv: _icon_note(cv, '#8ae08a'),
    20: lambda cv: _icon_note(cv, '#d090ff'),
}


def iconset():
    cv = Canvas(16 * 16, 4 * 16)
    for idx, fn in ICONS.items():
        ic = Canvas(16, 16)
        fn(ic)
        cv.paste(ic, (idx % 16) * 16, (idx // 16) * 16)
    return cv.image(2)


# ---------------------------------------------------------------------------
# Balloon.png : 8 frames x 15 rows of 24x24 logical
# ---------------------------------------------------------------------------

def _bubble(cv, scale=1.0):
    w, h = int(10 * scale), int(8 * scale)
    if w < 2:
        return
    cv.ellipse(12, 10, w, h, '#fbf8f2')
    cv.px(9, 10 + h, '#fbf8f2')
    cv.px(8, 11 + h, '#fbf8f2')
    cv.outline(INK)


def _sym(cv, kind, f):
    c = INK
    if kind == 1:   # !
        cv.rect(11, 4, 2, 7, '#d8302a')
        cv.rect(11, 13, 2, 2, '#d8302a')
    elif kind == 2:  # ?
        cv.hline(10, 4, 4, '#3f6fb0')
        cv.px(14, 5, '#3f6fb0')
        cv.px(14, 6, '#3f6fb0')
        cv.px(13, 7, '#3f6fb0')
        cv.px(12, 8, '#3f6fb0')
        cv.px(12, 9, '#3f6fb0')
        cv.rect(12, 12, 2, 2, '#3f6fb0')
        cv.px(9, 5, '#3f6fb0')
    elif kind == 3:  # music note
        dy = [0, -1, 0, 1][f % 4]
        col = '#e8584f'
        cv.ellipse(10, 13 + dy, 2.2, 1.7, col)
        cv.vline(12, 5 + dy, 8, col)
        cv.px(13, 6 + dy, col)
        cv.px(14, 7 + dy, col)
        cv.px(14, 8 + dy, col)
    elif kind == 4:  # heart
        s = 1 if f % 2 else 0
        cv.ellipse(10, 8, 2.4 + s * 0.4, 2.4 + s * 0.4, '#e8584f')
        cv.ellipse(14, 8, 2.4 + s * 0.4, 2.4 + s * 0.4, '#e8584f')
        for y in range(9, 15):
            w = 15 - y
            cv.hline(12 - w, y, 2 * w, '#e8584f')
    elif kind == 5:  # anger
        col = '#d8302a'
        for (x, y) in ((9, 7), (14, 7), (9, 12), (14, 12)):
            cv.px(x, y, col)
        cv.hline(9, 9, 2, col)
        cv.hline(13, 9, 2, col)
        cv.vline(11, 6, 2, col)
        cv.vline(11, 11, 2, col)
    elif kind == 6:  # sweat
        cv.ellipse(12, 11, 2.5, 3, '#7fc4ec')
        cv.px(12, 6, '#7fc4ec')
        cv.px(12, 7, '#7fc4ec')
        cv.px(11, 10, '#e3f6ff')
    elif kind == 7:  # frustration scribble
        for i in range(5):
            cv.line(7 + i * 2, 6 + (i % 2) * 6, 9 + i * 2, 12 - (i % 2) * 6, INK)
    elif kind == 8:  # ...
        n = min(3, f // 2 + 1)
        for i in range(n):
            cv.rect(8 + i * 3, 10, 2, 2, INK)
    elif kind == 9:  # light bulb
        cv.ellipse(12, 8, 3.5, 3.5, '#f7d55c')
        cv.rect(10, 11, 4, 3, '#c9c5bc')
        if f % 2:
            for (x, y) in ((6, 6), (18, 6), (12, 2)):
                cv.px(x, y, '#f7d55c')
    elif kind == 10:  # Zzz
        draw_text(cv, 12, 2, 'Zz', '#3f6fb0', center=True)
    elif kind == 11:  # sparkle / inspiration
        s = [1, 2, 3, 2][f % 4]
        cv.hline(12 - s, 10, 2 * s + 1, '#f0b030')
        cv.vline(12, 10 - s, 2 * s + 1, '#f0b030')
        cv.px(7, 6, '#f0b030')
        cv.px(16, 13, '#f0b030')
    elif kind == 12:  # tear
        dy = f % 3
        cv.ellipse(12, 9 + dy, 2, 2.5, '#5aa9dc')
        cv.px(12, 5 + dy, '#5aa9dc')
    elif kind == 13:  # warm flower
        for (x, y) in ((12, 6), (9, 9), (15, 9), (10, 12), (14, 12)):
            cv.ellipse(x, y, 1.8, 1.8, '#f2a0b8')
        cv.ellipse(12, 9.5, 1.4, 1.4, '#f7d55c')
    elif kind == 14:  # two notes (playing music)
        dy = [0, -1, 0, 1][f % 4]
        for (x, col, o) in ((8, '#3f6fb0', 0), (14, '#e8584f', 1)):
            yy = 12 + (dy if o == 0 else -dy)
            cv.ellipse(x, yy, 1.8, 1.4, col)
            cv.vline(x + 1, yy - 6, 6, col)
            cv.px(x + 2, yy - 5, col)
    elif kind == 15:  # silence (wavy lines struck through)
        for y in (8, 12):
            for x in range(7, 17):
                cv.px(x, y + (x % 2), '#9a9aa8')
        cv.line(7, 15, 17, 5, '#d8302a')


def balloons():
    cv = Canvas(8 * 24, 15 * 24)
    for row in range(15):
        for f in range(8):
            fr = Canvas(24, 24)
            sc = [0.35, 0.7, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0][f]
            _bubble(fr, sc)
            if f >= 2:
                _sym(fr, row + 1, f - 2)
            cv.paste(fr, f * 24, row * 24)
    return cv.image(2)


def shadow(w, h):
    cv = Canvas(w, h)
    cv.ellipse(w / 2, h / 2, w / 2 - 1, h / 2 - 2, (0, 0, 0, 90))
    return cv.image(2)


def blank(wf, hf):
    return Image.new('RGBA', (wf, hf), (0, 0, 0, 0))


def damage():
    img = Image.new('RGBA', (320, 160), (0, 0, 0, 0))
    cv = Canvas(160, 80)
    for row, col in enumerate(('#fbf8f2', '#9be38a', '#ffd98a', '#8fd0ff', '#ff9a7a')):
        for d in range(10):
            draw_text(cv, d * 16 + 8, row * 16, str(d), col, center=True)
    return cv.image(2)


def button_set():
    cv = Canvas(168, 48)
    for i, (x, w, label) in enumerate(((24, 24, '▼'), (48, 24, '▲'), (96, 48, 'OK'))):
        for hot in (0, 1):
            y = hot * 24
            cv.rect(x + 1, y + 1, w - 2, 22, '#4a4568' if not hot else '#6a6598')
            cv.frame(x + 1, y + 1, w - 2, 22, '#e9cf9a')
            draw_text(cv, x + w // 2, y + 5, label, '#fff8ec', center=True)
    return cv.image(2)


def build(out_dir, icon_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(icon_dir, exist_ok=True)
    window_skin().save(os.path.join(out_dir, 'Window.png'))
    iconset().save(os.path.join(out_dir, 'IconSet.png'))
    balloons().save(os.path.join(out_dir, 'Balloon.png'))
    shadow(24, 24).save(os.path.join(out_dir, 'Shadow1.png'))
    shadow(24, 12).save(os.path.join(out_dir, 'Shadow2.png'))
    damage().save(os.path.join(out_dir, 'Damage.png'))
    blank(768, 960).save(os.path.join(out_dir, 'States.png'))
    for i in (1, 2, 3):
        blank(576, 576).save(os.path.join(out_dir, 'Weapons%d.png' % i))
    button_set().save(os.path.join(out_dir, 'ButtonSet.png'))
    ld = Canvas(160, 40)
    from textutil import draw_text as _dt
    _dt(ld, 80, 12, '读取中……', '#d9b26a', center=True)
    ld.image(2).save(os.path.join(out_dir, 'Loading.png'))
    go = Image.new('RGBA', (816, 624), (20, 18, 30, 255))
    go.save(os.path.join(out_dir, 'GameOver.png'))
    # app icon: a golden note on night blue
    ic = Canvas(32, 32)
    ic.round_rect(0, 0, 32, 32, '#2a2740', r=6)
    big = Canvas(16, 16)
    _icon_note(big, '#f7d55c')
    for y in range(16):
        for x in range(16):
            c = big.get(x, y)
            if c[3]:
                ic.rect(x * 2 - 0, y * 2 - 0, 2, 2, c)
    ic.image(8).save(os.path.join(icon_dir, 'icon.png'))
