"""Ground / floor / wall materials (24 px periodic textures + edge styles)."""
import math

from pixlib import Canvas, TILE, rgba, shade, mix, rng
from autotile import Material
import palette as P

T = TILE


def tex_from_canvas(cv):
    def f(x, y, frame=0):
        c = cv.get(x % cv.w, y % cv.h)
        return c if c[3] else None
    return f


def wrap_px(cv, x, y, c):
    cv.px(x % cv.w, y % cv.h, c)


# ---------------------------------------------------------------------------
# textures
# ---------------------------------------------------------------------------

def grass_tex(seed=1, base=P.GRASS, lo=P.GRASS_LO, hi=P.GRASS_HI, tufts=4, flowers=None):
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, base)
    r = rng(seed)
    # soft mottling
    for _ in range(14):
        wrap_px(cv, r.randrange(T), r.randrange(T), P.GRASS_MID if base == P.GRASS else shade(base, 0.92))
    for _ in range(tufts):
        x, y = r.randrange(T), r.randrange(T)
        # little "v" tuft
        wrap_px(cv, x, y, lo)
        wrap_px(cv, x + 2, y, lo)
        wrap_px(cv, x + 1, y + 1, lo)
        wrap_px(cv, x + 1, y - 1, hi)
    if flowers:
        for col in flowers:
            x, y = r.randrange(T), r.randrange(T)
            wrap_px(cv, x, y, col)
            wrap_px(cv, x + 1, y, shade(col, 1.2))
            wrap_px(cv, x, y + 1, shade(col, 0.8))
    return cv


def dirt_tex(seed=2):
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, P.DIRT)
    r = rng(seed)
    for _ in range(26):
        wrap_px(cv, r.randrange(T), r.randrange(T), P.DIRT_LO)
    for _ in range(14):
        wrap_px(cv, r.randrange(T), r.randrange(T), P.DIRT_HI)
    for _ in range(3):  # pebbles
        x, y = r.randrange(T), r.randrange(T)
        wrap_px(cv, x, y, P.STONE)
        wrap_px(cv, x + 1, y, P.STONE_HI)
        wrap_px(cv, x, y + 1, P.DIRT_DEEP)
    return cv


def cobble_tex(seed=3, base=P.STONE, lo=P.STONE_LO, hi=P.STONE_HI, gap=P.STONE_DEEP):
    """Rounded, slightly irregular cobbles on a 24 px periodic layout."""
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, shade(gap, 1.15))
    stones = [(0, 0, 8, 6), (9, 0, 7, 6), (17, 0, 7, 6),
              (4, 7, 8, 5), (13, 7, 9, 5), (22, 7, 5, 5),
              (0, 13, 6, 5), (7, 13, 8, 5), (16, 13, 7, 5),
              (3, 19, 9, 5), (13, 19, 6, 5), (20, 19, 7, 5)]
    r = rng(seed)
    for (x, y, w, h) in stones:
        c = shade(base, 0.92 + r.random() * 0.14)
        for yy in range(h - 1):
            for xx in range(w - 1):
                if (xx in (0, w - 2)) and (yy in (0, h - 2)):
                    continue
                wrap_px(cv, x + xx, y + yy, c)
        for xx in range(1, w - 2):
            wrap_px(cv, x + xx, y, hi)
        for xx in range(1, w - 2):
            wrap_px(cv, x + xx, y + h - 2, lo)
        wrap_px(cv, x + w - 2, y + 1, lo)
    return cv


def farmland_tex():
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, P.SOIL)
    for y in range(0, T, 8):
        cv.hline(0, y + 5, T, P.SOIL_LO)
        cv.hline(0, y + 6, T, P.SOIL_LO)
        cv.hline(0, y + 1, T, shade(P.SOIL, 1.12))
        for x in range(2, T, 6):  # sprouts
            cv.px(x, y + 2, P.LEAF)
            cv.px(x + 1, y + 1, P.LEAF_HI)
            cv.px(x - 1, y + 1, P.LEAF)
            cv.px(x, y + 3, P.LEAF_LO)
    return cv


def leaves_tex(seed=11):
    """autumn fallen leaves (transparent between leaves)"""
    cv = Canvas(T, T)
    r = rng(seed)
    cols = ['#e0913f', '#c9632f', '#efb24a', '#b5452b']
    for _ in range(16):
        x, y = r.randrange(T), r.randrange(T)
        c = r.choice(cols)
        wrap_px(cv, x, y, c)
        wrap_px(cv, x + 1, y, c)
        wrap_px(cv, x, y + 1, shade(c, 0.8))
    return cv


def asphalt_tex(seed=12):
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, P.ASPHALT)
    r = rng(seed)
    for _ in range(40):
        wrap_px(cv, r.randrange(T), r.randrange(T), r.choice([P.ASPHALT_LO, P.ASPHALT_HI]))
    return cv


def paving_tex(base=P.PAVE, lo=P.PAVE_LO, size=12):
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, base)
    for y in range(0, T, size):
        cv.hline(0, y, T, lo)
    for x in range(0, T, size):
        cv.vline(x, 0, T, lo)
    for y in range(1, T, size):
        cv.hline(1, y, size - 2, shade(base, 1.08))
        cv.hline(size + 1, y, size - 2, shade(base, 1.08))
    return cv


def plaza_tex():
    cv = Canvas(T, T)
    a, b = '#d9cdb8', '#c9b9a0'
    for y in range(T):
        for x in range(T):
            cv.px(x, y, a if ((x // 6) + (y // 6)) % 2 == 0 else b)
    for i in range(0, T, 6):
        cv.hline(0, i, T, shade(b, 0.92))
        cv.vline(i, 0, T, shade(b, 0.92))
    return cv


def planks_tex(base=P.WOOD, lo=P.WOOD_LO, hi=P.WOOD_HI, plank=6, seed=5, vertical=False):
    cv = Canvas(T, T)
    r = rng(seed)
    for i in range(T // plank):
        c = shade(base, 0.95 + 0.08 * r.random())
        for k in range(plank):
            for j in range(T):
                x, y = (i * plank + k, j) if vertical else (j, i * plank + k)
                cv.px(x, y, c)
        # seam
        for j in range(T):
            x, y = (i * plank, j) if vertical else (j, i * plank)
            cv.px(x, y, lo)
            x2, y2 = (i * plank + 1, j) if vertical else (j, i * plank + 1)
            cv.px(x2, y2, hi)
        # butt joints
        off = r.randrange(T)
        for k in range(1, plank):
            x, y = (i * plank + k, off) if vertical else (off, i * plank + k)
            cv.px(x, y, lo)
        # grain
        for _ in range(3):
            g = r.randrange(T)
            k = r.randrange(2, plank)
            for d in range(4):
                x, y = (i * plank + k, (g + d) % T) if vertical else ((g + d) % T, i * plank + k)
                cv.px(x, y, shade(c, 0.9))
    return cv


def tile_floor_tex(a='#e9e4d8', b='#d7d0c0', line='#bdb5a4', size=12):
    cv = Canvas(T, T)
    for y in range(T):
        for x in range(T):
            cv.px(x, y, a if ((x // size) + (y // size)) % 2 == 0 else b)
    for i in range(0, T, size):
        cv.hline(0, i, T, line)
        cv.vline(i, 0, T, line)
    return cv


def carpet_tex(base, lo, hi, pattern='diamond'):
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, base)
    if pattern == 'diamond':
        for y in range(T):
            for x in range(T):
                d = abs((x % 12) - 6) + abs((y % 12) - 6)
                if d == 5:
                    cv.px(x, y, lo)
                elif d == 1:
                    cv.px(x, y, hi)
    else:
        for y in range(0, T, 2):
            for x in range(T):
                if (x + y) % 4 == 0:
                    cv.px(x, y, lo)
    return cv


def concrete_tex(seed=21):
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, '#a8a49c')
    r = rng(seed)
    for _ in range(36):
        wrap_px(cv, r.randrange(T), r.randrange(T), r.choice(['#9a968e', '#b6b2aa']))
    # crack
    x, y = 4, 15
    for i in range(7):
        wrap_px(cv, x + i, y + (i % 3 == 0), '#85817a')
    return cv


def water_tex(frame):
    cv = Canvas(T, T)
    cv.rect(0, 0, T, T, P.WATER)
    ripples = [(2, 3, 5), (14, 6, 6), (7, 12, 4), (18, 15, 5), (3, 19, 6), (12, 21, 4)]
    for i, (x, y, w) in enumerate(ripples):
        dx = (frame * (1 if i % 2 else -1)) % T
        for k in range(w):
            wrap_px(cv, x + dx + k, y, P.WATER_HI)
        wrap_px(cv, x + dx + 1, y + 1, P.WATER_LO)
        wrap_px(cv, x + dx + w - 2, y + 1, P.WATER_LO)
    sparkle = [(5, 8), (17, 11), (9, 17)][frame % 3]
    wrap_px(cv, sparkle[0], sparkle[1], P.FOAM)
    return cv


# ---------------------------------------------------------------------------
# edge styles
# ---------------------------------------------------------------------------

def soft_edge(outer, inner, inner2=None):
    """1px outer rim, 1px inner rim, optional third."""
    def e(d, x, y, frame=0):
        if d == 1:
            return outer
        if d == 2:
            return inner
        if d == 3 and inner2:
            return inner2
        return None
    return e


def ragged(outer, inner, seed=7):
    """an organic, wobbly edge: the boundary randomly eats 0-2 px."""
    r = rng(seed)
    bite = [[r.random() for _ in range(T)] for _ in range(T)]

    def e(d, x, y, frame=0):
        b = bite[y][x]
        if d == 1:
            if b < 0.45:
                return (0, 0, 0, 0)
            return outer
        if d == 2:
            if b < 0.12:
                return (0, 0, 0, 0)
            return inner if b < 0.7 else outer
        return None
    return e


def water_edge(d, x, y, frame=0):
    if d == 1:
        return '#6f8e4a'    # dark wet bank
    if d == 2:
        return P.FOAM if (x + y + frame) % 5 else P.WATER_HI
    if d == 3:
        return P.WATER_HI if (x * 3 + y + frame * 2) % 4 == 0 else None
    return None


def make_materials():
    """Return dict name -> Material."""
    m = {}
    g = grass_tex(1)
    m['grass'] = Material(tex_from_canvas(g), soft_edge(P.GRASS_LO, P.GRASS_MID), radius=3, rim=2)
    g2 = grass_tex(4, base=P.GRASS_MID, lo=P.GRASS_DEEP, hi=P.GRASS, tufts=10,
                   flowers=['#f4f1ea', '#f7d55c', '#f2a0b8'])
    m['meadow'] = Material(tex_from_canvas(g2), ragged(None, P.GRASS_LO, 3), radius=4, rim=2)
    m['dirt'] = Material(tex_from_canvas(dirt_tex()), ragged(P.DIRT_LO, P.DIRT_HI, 8), radius=4, rim=2)
    m['cobble'] = Material(tex_from_canvas(cobble_tex()), soft_edge(P.STONE_DEEP, P.STONE_LO), radius=2, rim=2)
    m['farmland'] = Material(tex_from_canvas(farmland_tex()), soft_edge(P.DIRT_DEEP, P.DIRT_LO), radius=2, rim=2)
    m['leaves'] = Material(tex_from_canvas(leaves_tex()), None, radius=4, rim=0)
    m['asphalt'] = Material(tex_from_canvas(asphalt_tex()), soft_edge('#3d3d46', P.ASPHALT_LO), radius=0, rim=2)
    m['sidewalk'] = Material(tex_from_canvas(paving_tex()), soft_edge('#8f887e', P.PAVE_LO), radius=0, rim=2)
    m['plaza'] = Material(tex_from_canvas(plaza_tex()), soft_edge('#a8987f', '#bfae94'), radius=0, rim=2)
    m['deck'] = Material(tex_from_canvas(planks_tex(seed=6)), soft_edge(P.WOOD_DEEP, P.WOOD_LO), radius=0, rim=2)
    snow = Canvas(T, T)
    snow.rect(0, 0, T, T, '#f4f8fc')
    r = rng(31)
    for _ in range(18):
        wrap_px(snow, r.randrange(T), r.randrange(T), '#dfe8f2')
    m['snow'] = Material(tex_from_canvas(snow), ragged('#c9d6e6', '#e6eef7', 12), radius=5, rim=2)
    m['sand'] = Material(tex_from_canvas(dirt_tex(40)), soft_edge(P.DIRT_LO, P.SAND), radius=4, rim=2)
    # water: animated, 3 frames
    m['water'] = Material(lambda x, y, f: water_tex(f).get(x, y), water_edge, radius=4, rim=3, frames=3)
    # interior floors
    m['wood_floor'] = Material(tex_from_canvas(planks_tex(seed=13)), soft_edge(P.WOOD_DEEP, P.WOOD_LO), radius=0, rim=1)
    m['old_floor'] = Material(tex_from_canvas(planks_tex('#a98a68', '#7d6249', '#c6a886', seed=14)),
                              soft_edge('#5b4636', '#7d6249'), radius=0, rim=1)
    m['tile_floor'] = Material(tex_from_canvas(tile_floor_tex()), soft_edge('#9f978a', None), radius=0, rim=1)
    m['school_floor'] = Material(tex_from_canvas(tile_floor_tex('#d8e3d6', '#c8d6c5', '#aab8a6')),
                                 soft_edge('#8a9886', None), radius=0, rim=1)
    m['carpet_red'] = Material(tex_from_canvas(carpet_tex('#b44a4a', '#8e3438', '#d9725f')),
                               soft_edge('#e3c06a', '#8e3438'), radius=0, rim=2)
    m['carpet_blue'] = Material(tex_from_canvas(carpet_tex('#4a6aa8', '#384f80', '#6f8fc9', 'dots')),
                                soft_edge('#e9e2cf', '#384f80'), radius=1, rim=2)
    m['concrete'] = Material(tex_from_canvas(concrete_tex()), soft_edge('#7c786f', None), radius=0, rim=1)
    m['stage'] = Material(tex_from_canvas(planks_tex('#8a5a3a', '#5e3a24', '#a7744c', seed=15)),
                          soft_edge('#3b2618', '#5e3a24'), radius=0, rim=2)
    m['tatami'] = Material(tex_from_canvas(planks_tex('#cdbf86', '#a99c66', '#ddd29e', plank=4, seed=16, vertical=True)),
                           soft_edge('#4f6b45', '#a99c66'), radius=0, rim=2)
    return m
