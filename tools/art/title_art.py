"""Title screen: dusk over 清水村, the old tree, grandpa and little 音.

titles1/YuYin_Title.png  - the scene (816x624)
titles2/YuYin_Logo.png   - title text overlay (transparent)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from pixlib import Canvas, mix, rgba, shade, rng
from chars import draw_frame
from cast import CAST
import palette as P

W, H = 408, 312


def _gradient(cv, stops):
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                c = mix(c0, c1, (t - t0) / (t1 - t0))
                break
        # ordered dithering between bands for a pixel-art sky
        cv.hline(0, y, W, c)


def _hill(cv, base_y, amp, freq, phase, col, seed=0):
    for x in range(W):
        y = base_y + amp * math.sin(x * freq + phase) + amp * 0.4 * math.sin(x * freq * 2.7 + phase * 1.3)
        cv.vline(x, int(y), H - int(y), col)


def scene():
    cv = Canvas(W, H)
    _gradient(cv, [(0.0, rgba('#1e1d3a')), (0.32, rgba('#4a3a6e')), (0.55, rgba('#c0607a')),
                   (0.70, rgba('#f2a066')), (0.78, rgba('#f8d48a')), (1.0, rgba('#f8d48a'))])
    r = rng(5)
    for _ in range(90):
        x, y = r.randrange(W), r.randrange(int(H * 0.35))
        cv.px(x, y, (255, 250, 230, r.randrange(80, 230)))
    for (x, y) in ((60, 30), (300, 22), (350, 60)):
        cv.px(x, y, '#ffffff')
        cv.px(x - 1, y, (255, 255, 255, 120))
        cv.px(x + 1, y, (255, 255, 255, 120))
        cv.px(x, y - 1, (255, 255, 255, 120))
        cv.px(x, y + 1, (255, 255, 255, 120))
    # setting sun
    cv.ellipse(120, 236, 26, 26, (255, 236, 170, 255))
    cv.ellipse(120, 236, 34, 34, (255, 220, 150, 50))
    # distant hills
    _hill(cv, 230, 8, 0.02, 0.5, rgba('#8a5a7a'))
    _hill(cv, 248, 6, 0.035, 2.0, rgba('#6a4466'))
    # river glinting
    for y in range(262, 274):
        for x in range(W):
            if (x + y * 3) % 17 < 9:
                cv.px(x, y, mix('#f6c78a', '#8a5a7a', (y - 262) / 12))
    # foreground meadow
    _hill(cv, 270, 4, 0.03, 1.0, rgba('#2e2540'))
    for x in range(0, W, 2):
        hgt = r.randrange(2, 7)
        cv.vline(x, 270 - hgt + int(4 * math.sin(x * 0.03 + 1)), hgt, '#2e2540')
    # the hill with the old tree
    for x in range(W):
        y = min(272, 228 + int(((x - 320) / 90) ** 2 * 22))
        cv.vline(x, y, H - y, '#2e2540')
    # tree trunk
    for y in range(150, 236):
        t = (y - 150) / 86
        half = int(5 + 6 * t * t)
        cv.hline(318 - half, y, half * 2, '#2a1f30')
    for (x0, y0, x1, y1) in ((318, 165, 286, 130), (318, 160, 352, 128), (318, 158, 320, 110)):
        for k in range(3):
            cv.line(x0 + k - 1, y0, x1 + k - 1, y1, '#2a1f30')
    # canopy: dark clumps with sunset rim light
    clumps = [(318, 112, 52, 34), (276, 128, 28, 20), (362, 126, 30, 20), (300, 94, 30, 22), (338, 92, 30, 22)]
    for (cx, cy, rx, ry) in clumps:
        cv.ellipse(cx, cy, rx, ry, '#2c2a3e')
    for (cx, cy, rx, ry) in clumps:
        for k in range(60):
            a = r.random() * math.pi * 2
            d = 0.8 + r.random() * 0.25
            x, y = int(cx + math.cos(a) * rx * d), int(cy + math.sin(a) * ry * d)
            if cv.get(x, y)[:3] == rgba('#2c2a3e')[:3]:
                lit = math.cos(a) < -0.3 and math.sin(a) > -0.2
                cv.px(x, y, '#6a4a5e' if lit else '#3a3650')
    # tiny blossoms catching light
    for _ in range(50):
        x, y = r.randrange(260, 380), r.randrange(70, 150)
        if cv.get(x, y)[:3] in (rgba('#2c2a3e')[:3], rgba('#3a3650')[:3]):
            cv.px(x, y, '#e8b8a0')
    # grandpa & little 音 (back view, silhouettes with rim light)
    for name, x in (('$Grandpa', 284), ('$Yin_Child', 268)):
        fr = draw_frame(CAST[name], 'up', 1)
        for yy in range(24):
            for xx in range(24):
                c = fr.get(xx, yy)
                if c[3]:
                    edge = fr.get(xx - 1, yy)[3] == 0
                    cv.px(x + xx, 206 + yy + (1 if name == '$Yin_Child' else 0), '#9a6a76' if edge else '#241c2e')
    # floating notes + fireflies
    for (x, y, s) in ((262, 196, 1), (246, 178, 0), (232, 160, 1), (222, 136, 0), (232, 114, 1)):
        col = (255, 222, 150, 230)
        cv.ellipse(x, y, 2.2, 1.7, col)
        cv.vline(x + 2, y - 7, 7, col)
        if s:
            cv.px(x + 3, y - 6, col)
            cv.px(x + 4, y - 5, col)
    for _ in range(26):
        x, y = r.randrange(150, 400), r.randrange(150, 280)
        cv.px(x, y, (255, 240, 140, 220))
        cv.px(x + 1, y, (255, 240, 140, 90))
    return cv


def logo(font_path=None):
    """Title text overlay at full resolution (816x624)."""
    img = Image.new('RGBA', (816, 624), (0, 0, 0, 0))
    if font_path and os.path.exists(font_path):
        f_big = ImageFont.truetype(font_path, 120)
        f_small = ImageFont.truetype(font_path, 34)
    else:
        from textutil import _ttf_path
        f_big = ImageFont.truetype(_ttf_path(), 96)
        f_small = ImageFont.truetype(_ttf_path(), 36)
    d = ImageDraw.Draw(img)
    title, sub = '余音', '— 一生所爱 —'
    x, y = 80, 120
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y), title, font=f_big, fill=(255, 210, 140, 200))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(glow)
    d.text((x + 4, y + 5), title, font=f_big, fill=(40, 26, 50, 200))
    d.text((x, y), title, font=f_big, fill=(255, 246, 228, 255))
    tw = d.textlength(title, font=f_big)
    sw = d.textlength(sub, font=f_small)
    d.text((x + (tw - sw) / 2 + 2, y + 158), sub, font=f_small, fill=(40, 26, 50, 180))
    d.text((x + (tw - sw) / 2, y + 156), sub, font=f_small, fill=(255, 230, 190, 255))
    return img


def build(root, wenkai=None):
    t1 = os.path.join(root, 'img', 'titles1')
    t2 = os.path.join(root, 'img', 'titles2')
    os.makedirs(t1, exist_ok=True)
    os.makedirs(t2, exist_ok=True)
    scene().save(os.path.join(t1, 'YuYin_Title.png'))
    logo(wenkai).save(os.path.join(t2, 'YuYin_Logo.png'))
