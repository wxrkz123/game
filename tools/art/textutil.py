"""Render crisp pixel text with the bundled Fusion Pixel font (OFL)."""
import os
import tempfile

from PIL import Image, ImageDraw, ImageFont

_HERE = os.path.dirname(os.path.abspath(__file__))
WOFF2 = os.path.join(_HERE, '..', '..', 'YuYin', 'fonts', 'FusionPixel12.woff2')
_cache = {}


def _ttf_path():
    out = os.path.join(tempfile.gettempdir(), 'yuyin_fusionpixel12.ttf')
    if not os.path.exists(out):
        from fontTools.ttLib import TTFont
        f = TTFont(WOFF2)
        f.flavor = None
        f.save(out)
    return out


def font(size=12):
    if size not in _cache:
        _cache[size] = ImageFont.truetype(_ttf_path(), size)
    return _cache[size]


def text_canvas(text, color, size=12):
    """Return a PIL RGBA image of the text at logical resolution (no AA)."""
    f = font(size)
    l, t, r, b = f.getbbox(text)
    im = Image.new('RGBA', (r - l + 2, b - t + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((1 - l, 1 - t), text, font=f, fill=color)
    return im


def draw_text(cv, x, y, text, color, size=12, center=False, shadow=None):
    from pixlib import rgba
    im = text_canvas(text, rgba(color), size)
    if center:
        x = x - im.width // 2
    import numpy as np
    arr = np.array(im)
    if shadow:
        for yy in range(arr.shape[0]):
            for xx in range(arr.shape[1]):
                if arr[yy, xx, 3]:
                    cv.px(x + xx + 1, y + yy + 1, shadow)
    for yy in range(arr.shape[0]):
        for xx in range(arr.shape[1]):
            if arr[yy, xx, 3]:
                cv.px(x + xx, y + yy, tuple(int(v) for v in arr[yy, xx]))
    return im.width
