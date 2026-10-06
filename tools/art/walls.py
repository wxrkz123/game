"""Interior walls (A4 autotiles): a 'wall top' floor-type autotile plus a
'wall side' wall-type autotile per style.

The wall face block is 48x48 logical: row 0 (12 px) = crown, rows 1-2 = plain
(vertical period 12, so walls of any height tile cleanly), row 3 = wainscot or
baseboard.  Columns 0 and 47 get corner shading.
"""
from pixlib import Canvas, TILE, shade, rng
from autotile import Material
from materials import soft_edge, tex_from_canvas
import palette as P

T = TILE


def _face(style):
    W = H = 48
    cv = Canvas(W, H)
    base, pat, crown, wains, wains_hi, top = style['base'], style['pat'], style['crown'], style['wains'], style['wains_hi'], style['top']
    for y in range(H):
        for x in range(W):
            cv.px(x, y, base)
    # periodic pattern in the plain area (period 24 x 12)
    kind = style.get('pattern', 'dots')
    r = rng(style.get('seed', 1))
    if kind == 'dots':
        for y in range(0, H, 12):
            for x in range(0, W, 12):
                cv.px(x + 5, y + 5, pat)
                cv.px(x + 11, y + 11, pat)
    elif kind == 'stripes':
        for x in range(0, W, 6):
            cv.vline(x, 0, H, pat)
    elif kind == 'stain':
        for _ in range(60):
            x, y = r.randrange(W), r.randrange(12)
            for k in range(4):
                cv.px(x, y + 12 * k, pat)
    elif kind == 'brick':
        for y in range(0, H, 6):
            off = 0 if (y // 6) % 2 == 0 else 6
            cv.hline(0, y, W, pat)
            for x in range(off, W, 12):
                cv.vline(x, y, 6, pat)
    elif kind == 'curtain':
        for x in range(W):
            if (x // 4) % 2:
                cv.vline(x, 0, H, pat)
    # crown (row 0)
    cv.hline(0, 0, W, shade(crown, 0.7))
    cv.hline(0, 1, W, crown)
    cv.hline(0, 2, W, shade(crown, 1.2))
    cv.hline(0, 3, W, shade(base, 0.85))
    # wainscot / baseboard (row 3: y 36..47)
    wy = 48 - style.get('wains_h', 5)
    cv.rect(0, wy, W, 48 - wy, wains)
    cv.hline(0, wy, W, wains_hi)
    if style.get('wains_planks'):
        for x in range(0, W, 6):
            cv.vline(x, wy + 1, 48 - wy - 2, shade(wains, 0.85))
    cv.hline(0, 47, W, shade(wains, 0.6))
    cv.hline(0, wy - 1, W, shade(base, 0.85))
    # corners
    cv.vline(0, 0, H, shade(base, 0.6))
    cv.vline(1, 0, H, shade(base, 0.85))
    cv.vline(47, 0, H, shade(base, 0.6))
    cv.vline(46, 0, H, shade(base, 0.85))
    return cv


def _top_material(col):
    tex = Canvas(T, T)
    tex.rect(0, 0, T, T, col)
    for y in range(0, T, 6):
        for x in range(0, T, 6):
            tex.px(x + (y // 6) % 2 * 3, y, shade(col, 0.92))
    return Material(tex_from_canvas(tex), soft_edge(shade(col, 0.55), shade(col, 1.35)), radius=0, rim=2)


STYLES = [
    dict(name='home', base='#f1e6cf', pat='#e0cfaa', crown='#b89b78', wains=P.WOOD, wains_hi=P.WOOD_HI,
         top='#7a6658', pattern='dots', wains_h=5),
    dict(name='old', base='#ece6d8', pat='#e0d8c6', crown=P.WOOD_LO, wains=P.WOOD_LO, wains_hi=P.WOOD,
         top='#5a4636', pattern='stain', wains_h=12, wains_planks=True, seed=4),
    dict(name='school', base='#f4f2ea', pat='#e8e6dc', crown='#a8b8a4', wains='#9cc094', wains_hi='#b8d8b0',
         top='#7f9480', pattern='stripes', wains_h=12),
    dict(name='basement', base='#a19d94', pat='#949088', crown='#7c786f', wains='#7c786f', wains_hi='#8e8a82',
         top='#55524c', pattern='stain', wains_h=4, seed=9),
    dict(name='hall', base='#6a2c3c', pat='#5a2232', crown='#c9a040', wains='#3a1820', wains_hi='#c9a040',
         top='#2e1a24', pattern='curtain', wains_h=6),
    dict(name='brick', base='#9a5e48', pat='#7e4a38', crown='#4e3a30', wains='#4e3a30', wains_hi='#6a5040',
         top='#3e2e26', pattern='brick', wains_h=4),
    dict(name='night_home', base='#d9cbb0', pat='#c9b894', crown='#9a8060', wains=P.WOOD_LO, wains_hi=P.WOOD,
         top='#5e4c40', pattern='dots', wains_h=5),
]


def make_walls():
    """Return list of (name, top_material, face_canvas)."""
    return [(s['name'], _top_material(s['top']), _face(s)) for s in STYLES]
