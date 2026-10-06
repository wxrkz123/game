"""Outdoor objects for the village 清水村 and the city.

Every function returns (canvas, flags) where canvas is (w*24) x (h*24)
logical pixels and flags is a list of h strings with one char per tile:
  o passable, x blocked, * above characters (star), b bush, c counter
"""
import math

from pixlib import Canvas, TILE, rgba, shade, mix, rng
from draw import (blob, leaf_clusters, window, lattice_window, door, tile_roof,
                  wall_plaster, wall_brick, shadow_ellipse, furniture, box)
from textutil import draw_text
import palette as P

T = TILE
LEAVES = (P.LEAF_HI, P.LEAF, P.LEAF_LO)


def _canopy(cv, cx, cy, rx, ry, seed, colors=None, deep=P.LEAF_DEEP):
    hi, base, lo = colors or LEAVES
    blob(cv, cx, cy, rx, ry, base, hi, lo, seed=seed, bumpy=0.12)
    leaf_clusters(cv, cx, cy, rx, ry, (hi, base, lo), int(rx * ry / 6), seed + 1)
    # outline
    tmp = Canvas(cv.w, cv.h)
    tmp.a = cv.a.copy()
    cv.outline(deep)


def _trunk(cv, x, y, w, h, col=P.WOOD_LO):
    cv.rect(x, y, w, h, col)
    cv.vline(x, y, h, shade(col, 1.2))
    cv.vline(x + w - 1, y, h, shade(col, 0.7))
    for yy in range(y + 2, y + h, 4):
        cv.px(x + w // 2, yy, shade(col, 0.75))


def tree():
    cv = Canvas(48, 48)
    shadow_ellipse(cv, 24, 44, 15, 3.5)
    _trunk(cv, 20, 28, 7, 16)
    cv.px(19, 43, P.WOOD_LO)
    cv.px(27, 43, P.WOOD_LO)
    c2 = Canvas(48, 48)
    _canopy(c2, 24, 18, 21, 16, seed=3)
    cv.blit(c2, 0, 0)
    return cv, ['**', 'xx']


def tree_autumn():
    cv = Canvas(48, 48)
    shadow_ellipse(cv, 24, 44, 15, 3.5)
    _trunk(cv, 20, 28, 7, 16)
    c2 = Canvas(48, 48)
    _canopy(c2, 24, 18, 21, 16, seed=5, colors=('#f3b24c', '#e0843a', '#b85a2c'), deep='#7a3a22')
    cv.blit(c2, 0, 0)
    return cv, ['**', 'xx']


def tree_small():
    cv = Canvas(24, 48)
    shadow_ellipse(cv, 12, 44, 8, 2.5)
    _trunk(cv, 10, 30, 4, 14)
    c2 = Canvas(24, 48)
    _canopy(c2, 12, 19, 10, 13, seed=7)
    cv.blit(c2, 0, 0)
    return cv, ['*', 'x']


def pine():
    cv = Canvas(24, 48)
    shadow_ellipse(cv, 12, 44, 8, 2.5)
    _trunk(cv, 10, 36, 4, 8)
    c2 = Canvas(24, 48)
    for i, (y, w) in enumerate([(4, 4), (9, 7), (15, 9), (21, 10), (28, 11)]):
        for k in range(7):
            ww = int(w * (k + 1) / 7)
            col = P.LEAF if k < 4 else P.LEAF_LO
            c2.hline(12 - ww, y + k, ww * 2, col)
            c2.px(12 - ww, y + k, P.LEAF_HI if k < 5 else P.LEAF)
    c2.outline(P.LEAF_DEEP)
    cv.blit(c2, 0, 0)
    return cv, ['*', 'x']


def old_tree():
    """老槐树 - the great old pagoda tree in the village centre (4x5)."""
    W, H = 96, 120
    cv = Canvas(W, H)
    shadow_ellipse(cv, 48, 112, 40, 7, alpha=80)
    # roots
    bark = '#7a5638'
    for (x0, x1, y) in [(30, 40, 110), (56, 68, 110), (24, 34, 113), (62, 74, 113)]:
        cv.rect(x0, y - 3, x1 - x0, 4, bark)
        cv.hline(x0, y - 3, x1 - x0, shade(bark, 1.2))
    # trunk: wide, gnarled
    for y in range(58, 112):
        t = (y - 58) / 54
        half = int(9 + 5 * t * t + 2 * math.sin(y * 0.35))
        cx = 48 + int(2 * math.sin(y * 0.12))
        for x in range(cx - half, cx + half):
            u = (x - (cx - half)) / (2 * half)
            if u < 0.2:
                c = shade(bark, 1.25)
            elif u > 0.75:
                c = shade(bark, 0.7)
            else:
                c = bark
            if (x * 7 + y * 3) % 11 == 0 or (y % 6 == 0 and (x + y) % 3 == 0):
                c = shade(c, 0.78)
            cv.px(x, y, c)
    # a hollow knot
    cv.ellipse(44, 84, 3, 4, '#3e2a1c')
    cv.px(43, 81, shade(bark, 1.3))
    # main branches
    for (x0, y0, x1, y1) in [(42, 62, 24, 40), (54, 62, 74, 38), (48, 60, 48, 30)]:
        for k in range(4):
            cv.line(x0 + k - 2, y0, x1 + k - 2, y1, shade(bark, 0.95 if k else 1.2))
    # canopy: several overlapping clumps
    c2 = Canvas(W, H)
    clumps = [(48, 34, 40, 26, 11), (22, 46, 20, 15, 12), (74, 46, 20, 15, 13),
              (34, 22, 22, 16, 14), (62, 22, 22, 16, 15), (48, 52, 26, 12, 16)]
    for (cx, cy, rx, ry, s) in clumps:
        blob(c2, cx, cy, rx, ry, P.LEAF, P.LEAF_HI, P.LEAF_LO, seed=s, bumpy=0.15)
    for (cx, cy, rx, ry, s) in clumps:
        leaf_clusters(c2, cx, cy, rx, ry, LEAVES, int(rx * ry / 7), s + 20)
    # tiny white pagoda-tree blossoms
    r = rng(77)
    for _ in range(40):
        x, y = r.randrange(12, 86), r.randrange(8, 60)
        if c2.get(x, y)[3] and c2.get(x - 1, y - 1)[3]:
            c2.px(x, y, '#f6f4dc')
    c2.outline(P.LEAF_DEEP)
    # punch a few holes so branches show through
    for (x, y) in [(40, 54), (58, 55), (30, 50)]:
        for k in range(3):
            c2.px(x + k, y, (0, 0, 0, 0))
    cv.blit(c2, 0, 0)
    return cv, ['****', '****', '****', '*xx*', 'oxxo']


def bush():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 20, 10, 3)
    c2 = Canvas(24, 24)
    blob(c2, 12, 13, 10, 8, P.LEAF, P.LEAF_HI, P.LEAF_LO, seed=21, bumpy=0.2)
    leaf_clusters(c2, 12, 13, 10, 8, LEAVES, 10, 22)
    c2.outline(P.LEAF_DEEP)
    cv.blit(c2, 0, 0)
    return cv, ['x']


def flower_bush(col='#f2a0b8'):
    cv, f = bush()
    r = rng(hash(col) % 1000)
    for _ in range(9):
        x, y = r.randrange(5, 19), r.randrange(7, 18)
        if cv.get(x, y)[3]:
            cv.px(x, y, col)
            cv.px(x + 1, y, shade(col, 1.25))
    return cv, f


def flowers(cols=('#f4f1ea', '#f7d55c', '#f2a0b8', '#a98ee0')):
    cv = Canvas(24, 24)
    r = rng(sum(map(ord, ''.join(cols))))
    for i in range(7):
        x, y = r.randrange(3, 20), r.randrange(3, 20)
        c = cols[i % len(cols)]
        cv.px(x, y + 1, P.LEAF_LO)
        cv.px(x, y + 2, P.LEAF_LO)
        cv.px(x - 1, y, c)
        cv.px(x + 1, y, c)
        cv.px(x, y - 1, c)
        cv.px(x, y + 0, '#f7d55c' if c != '#f7d55c' else '#e08a3a')
    return cv, ['o']


def tall_grass():
    cv = Canvas(24, 24)
    r = rng(5)
    for i in range(14):
        x = r.randrange(2, 22)
        h = r.randrange(6, 13)
        col = r.choice([P.GRASS_LO, P.GRASS_DEEP, P.GRASS_MID])
        for k in range(h):
            cv.px(x + (1 if k > h * 0.7 and i % 2 else 0), 22 - k, col)
    return cv, ['b']


def rock():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 19, 10, 3)
    c2 = Canvas(24, 24)
    blob(c2, 12, 14, 9, 7, P.STONE, P.STONE_HI, P.STONE_LO, seed=31, bumpy=0.15)
    c2.outline(P.STONE_DEEP)
    cv.blit(c2, 0, 0)
    return cv, ['x']


def fence_h():
    cv = Canvas(24, 24)
    for x in (5, 17):
        cv.rect(x, 6, 3, 15, P.WOOD)
        cv.vline(x, 6, 15, P.WOOD_HI)
        cv.vline(x + 2, 6, 15, P.WOOD_LO)
        cv.px(x + 1, 5, P.WOOD_HI)
    for y in (9, 15):
        cv.rect(0, y, 24, 2, P.WOOD)
        cv.hline(0, y, 24, P.WOOD_HI)
        cv.hline(0, y + 2, 24, P.WOOD_DEEP)
    cv.hline(0, 21, 24, (30, 40, 30, 60))
    return cv, ['x']


def fence_v():
    cv = Canvas(24, 24)
    for y in (2, 14):
        cv.rect(10, y, 4, 8, P.WOOD)
        cv.vline(10, y, 8, P.WOOD_HI)
        cv.vline(13, y, 8, P.WOOD_LO)
        cv.hline(10, y, 4, P.WOOD_HI)
    cv.rect(11, 0, 2, 24, P.WOOD_LO)
    for y in (2, 14):
        cv.rect(10, y, 4, 8, P.WOOD)
        cv.vline(10, y, 8, P.WOOD_HI)
        cv.hline(10, y, 4, P.WOOD_HI)
        cv.vline(13, y, 8, P.WOOD_DEEP)
    return cv, ['x']


def bridge_h():
    """bridge for walking left-right across a north-south river"""
    cv = Canvas(24, 24)
    for x in range(0, 24, 4):
        cv.rect(x, 3, 4, 18, shade(P.WOOD, 0.96 + (x % 8) / 80))
        cv.vline(x, 3, 18, P.WOOD_LO)
    cv.rect(0, 1, 24, 3, P.WOOD_LO)
    cv.hline(0, 1, 24, P.WOOD)
    cv.rect(0, 20, 24, 3, P.WOOD_DEEP)
    cv.hline(0, 20, 24, P.WOOD_LO)
    for x in (2, 14):
        cv.rect(x, 0, 2, 3, P.WOOD_DEEP)
    return cv, ['o']


def bridge_v():
    cv = Canvas(24, 24)
    for y in range(0, 24, 4):
        cv.rect(3, y, 18, 4, shade(P.WOOD, 0.96 + (y % 8) / 80))
        cv.hline(3, y, 18, P.WOOD_LO)
    cv.rect(1, 0, 3, 24, P.WOOD_LO)
    cv.rect(20, 0, 3, 24, P.WOOD_DEEP)
    return cv, ['o']


def _house_base(w_tiles, h_tiles, roof_h, roof, wall='plaster', seed=0):
    W, H = w_tiles * T, h_tiles * T
    cv = Canvas(W, H)
    wall_y = roof_h
    if wall == 'plaster':
        wall_plaster(cv, 2, wall_y, W - 4, H - wall_y - 1, seed=seed)
    elif wall == 'white':
        wall_plaster(cv, 2, wall_y, W - 4, H - wall_y - 1, base='#f3f0e8', lo='#cfcac0', seed=seed)
    elif wall == 'brick':
        wall_brick(cv, 2, wall_y, W - 4, H - wall_y - 1)
        cv.rect(2, H - 4, W - 4, 3, P.STONE)
        cv.hline(2, H - 4, W - 4, P.STONE_HI)
    elif wall == 'wood':
        cv.rect(2, wall_y, W - 4, H - wall_y - 1, P.OLDWOOD)
        for x in range(2, W - 2, 4):
            cv.vline(x, wall_y, H - wall_y - 1, P.OLDWOOD_LO)
            cv.vline(x + 1, wall_y, H - wall_y - 1, P.OLDWOOD_HI)
        cv.hline(2, wall_y, W - 4, shade(P.OLDWOOD_LO, 0.7))
    # wall side shading
    cv.vline(2, wall_y, H - wall_y - 1, (0, 0, 0, 30))
    cv.vline(W - 3, wall_y, H - wall_y - 1, (0, 0, 0, 50))
    # ground shadow line
    cv.hline(1, H - 1, W - 2, (30, 40, 30, 80))
    base, hi, lo = roof
    tile_roof(cv, 0, 2, W, roof_h - 2, base, hi, lo)
    # eave shadow on wall
    cv.hline(2, roof_h, W - 4, (0, 0, 0, 60))
    cv.hline(2, roof_h + 1, W - 4, (0, 0, 0, 30))
    return cv


def grandpa_house():
    """爷爷家: grey-tiled roof, whitewashed walls, red couplets (5x4)."""
    cv = _house_base(5, 4, 46, (P.ROOF_TILE, P.ROOF_TILE_HI, P.ROOF_TILE_LO), wall='white', seed=3)
    W = 120
    # upturned ridge ends
    for (x, d) in ((0, 1), (W - 1, -1)):
        cv.rect(min(x, x + d * 5), 0, 6, 3, P.ROOF_TILE_LO)
        cv.px(x, 0, P.ROOF_TILE_LO)
        cv.px(x + d * 1, 0, P.ROOF_TILE_LO)
        cv.px(x, 1, P.ROOF_TILE_LO)
    cv.rect(4, 1, W - 8, 3, P.ROOF_TILE_LO)
    cv.hline(4, 1, W - 8, shade(P.ROOF_TILE_LO, 1.25))
    # door (centre tile = x 48..72), double wooden door
    door(cv, 53, 64, 14, 31, col='#8c3b2c', double=True, knob='#e8c05a')
    # couplets
    for x in (48, 69):
        cv.rect(x, 62, 3, 26, '#d0392f')
        for y in range(64, 86, 4):
            cv.px(x + 1, y, '#f3cf5a')
    cv.rect(52, 57, 16, 4, '#d0392f')
    for x in range(54, 66, 3):
        cv.px(x, 58, '#f3cf5a')
    # step
    cv.rect(50, 93, 20, 3, P.STONE)
    cv.hline(50, 93, 20, P.STONE_HI)
    lattice_window(cv, 12, 60, 22, 16)
    lattice_window(cv, 86, 60, 22, 16)
    # a hanging dried-corn bunch & red pepper string for village flavour
    cv.rect(38, 56, 3, 12, '#f0c040')
    cv.px(39, 55, P.WOOD_LO)
    for y in range(57, 72, 2):
        cv.px(80, y, '#d33a2c')
        cv.px(81, y + 1, '#d33a2c')
    flags = ['xxxxx', 'xxxxx', 'xxxxx', 'xxoxx']
    return cv, flags


def house_red():
    cv = _house_base(4, 4, 44, (P.ROOF_RED, P.ROOF_RED_HI, P.ROOF_RED_LO), wall='plaster', seed=5)
    door(cv, 29, 64, 14, 31, col=P.WOOD)
    window(cv, 56, 60, 18, 14, frame=P.WOOD_LO)
    # flower box
    cv.rect(55, 75, 20, 3, P.WOOD_LO)
    for x in range(56, 74, 3):
        cv.px(x, 74, '#f2a0b8')
        cv.px(x + 1, 74, P.LEAF)
    return cv, ['xxxx', 'xxxx', 'xxxx', 'xoxx']


def house_brick():
    cv = _house_base(4, 4, 44, (P.ROOF_TILE, P.ROOF_TILE_HI, P.ROOF_TILE_LO), wall='brick', seed=6)
    door(cv, 53, 64, 14, 31, col='#5c4a3a')
    window(cv, 12, 60, 20, 14, frame=P.WOOD_DEEP)
    return cv, ['xxxx', 'xxxx', 'xxxx', 'xxox']


def house_wood():
    """李奶奶家 — old wooden house with a porch (4x4)."""
    cv = _house_base(4, 4, 44, ('#7f8c5a', '#9aa86e', '#5f6a42'), wall='wood', seed=7)
    door(cv, 29, 64, 14, 31, col=P.WOOD_LO)
    window(cv, 56, 60, 18, 14, frame=P.WOOD_DEEP)
    # porch posts
    for x in (24, 46):
        cv.rect(x, 50, 2, 45, P.WOOD_DEEP)
    return cv, ['xxxx', 'xxxx', 'xxxx', 'xoxx']


def school_village():
    """清水小学 (7x4)."""
    cv = _house_base(7, 4, 40, ('#6d86b0', '#8aa2c8', '#4f6690'), wall='white', seed=8)
    W = 168
    door(cv, 75, 62, 18, 33, col='#5d7fa8', double=True, knob=P.WHITE)
    for x in (10, 40, 110, 140):
        window(cv, x, 56, 20, 16, frame='#5d7fa8')
    # sign board
    cv.rect(57, 41, 54, 15, '#fbf8f2')
    cv.frame(56, 40, 56, 17, P.WOOD_DEEP)
    draw_text(cv, 84, 41, '清水小学', '#c0392b', center=True)
    return cv, ['xxxxxxx', 'xxxxxxx', 'xxxxxxx', 'xxxoxxx']


def shed():
    cv = _house_base(3, 3, 32, ('#a5733f', '#c08a50', '#7e5530'), wall='wood', seed=9)
    cv.rect(28, 46, 16, 25, P.WOOD_DEEP)
    cv.line(28, 46, 43, 70, P.WOOD_LO)
    cv.line(43, 46, 28, 70, P.WOOD_LO)
    return cv, ['xxx', 'xxx', 'xxx']


def well():
    cv = Canvas(24, 48)
    # roof
    cv.rect(2, 6, 20, 6, P.ROOF_TILE)
    cv.hline(2, 6, 20, P.ROOF_TILE_HI)
    cv.hline(2, 11, 20, P.ROOF_TILE_LO)
    cv.rect(4, 12, 2, 18, P.WOOD_LO)
    cv.rect(18, 12, 2, 18, P.WOOD_LO)
    cv.hline(6, 16, 12, P.WOOD_DEEP)
    cv.vline(12, 16, 9, '#c9b48a')
    cv.rect(10, 25, 4, 4, P.WOOD)
    # stone ring
    cv.ellipse(12, 34, 10, 5, P.STONE)
    cv.ellipse(12, 33, 7, 3, '#2f4a6a')
    cv.rect(2, 34, 20, 9, P.STONE)
    for x in range(3, 22, 5):
        cv.vline(x, 35, 8, P.STONE_LO)
    cv.hline(2, 42, 20, P.STONE_DEEP)
    shadow_ellipse(cv, 12, 44, 11, 2.5)
    return cv, ['*', 'x']


def signpost(text='清水村'):
    cv = Canvas(48, 24)
    for x in (8, 38):
        cv.rect(x, 14, 2, 9, P.WOOD_LO)
    cv.rect(2, 0, 44, 16, P.WOOD)
    cv.frame(2, 0, 44, 16, P.WOOD_DEEP)
    cv.hline(3, 1, 42, P.WOOD_HI)
    if text:
        draw_text(cv, 24, 1, text, P.WOOD_DEEP, center=True)
    shadow_ellipse(cv, 24, 22, 18, 1.5)
    return cv, ['xx']


def bench():
    cv = Canvas(48, 24)
    cv.rect(4, 8, 40, 4, P.WOOD)
    cv.hline(4, 8, 40, P.WOOD_HI)
    cv.rect(4, 13, 40, 3, P.WOOD_LO)
    for x in (6, 40):
        cv.rect(x, 16, 2, 6, P.WOOD_DEEP)
    shadow_ellipse(cv, 24, 21, 20, 2)
    return cv, ['xx']


def haystack():
    cv = Canvas(48, 48)
    shadow_ellipse(cv, 24, 42, 20, 4)
    c2 = Canvas(48, 48)
    blob(c2, 24, 26, 19, 16, '#e3c25e', '#f3dc86', '#bf9a3c', seed=41, bumpy=0.1)
    r = rng(42)
    for _ in range(60):
        x, y = r.randrange(8, 40), r.randrange(12, 40)
        if c2.get(x, y)[3]:
            c2.px(x, y, '#c9a443')
            c2.px(x + 1, y - 1, '#f6e39a')
    c2.outline('#8c6f2a')
    cv.blit(c2, 0, 0)
    return cv, ['**', 'xx']


def crate():
    cv = Canvas(24, 24)
    furniture(cv, 3, 5, 18, 5, 13, P.WOOD_HI, P.WOOD)
    cv.line(4, 11, 19, 22, P.WOOD_LO)
    cv.frame(3, 5, 18, 18, P.WOOD_DEEP)
    return cv, ['x']


def barrel():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 9, 2)
    cv.rect(5, 6, 14, 15, P.WOOD)
    cv.ellipse(12, 6, 7, 3, P.WOOD_LO)
    cv.ellipse(12, 6, 5, 2, '#3a5a7a')
    for y in (9, 17):
        cv.hline(5, y, 14, P.STONE_DEEP)
    cv.vline(5, 6, 15, P.WOOD_HI)
    cv.vline(18, 6, 15, P.WOOD_LO)
    return cv, ['x']


def firewood():
    cv = Canvas(24, 24)
    for row, y in enumerate((14, 10, 6)):
        n = 3 - row
        for i in range(n):
            x = 4 + row * 3 + i * 6
            cv.ellipse(x + 3, y + 3, 3, 3, P.WOOD)
            cv.ellipse(x + 3, y + 3, 1.5, 1.5, P.WOOD_HI)
            cv.px(x + 3, y + 3, P.WOOD_LO)
    return cv, ['x']


def popsicle_cart():
    """卖冰棍的小推车 with a parasol (2x2)."""
    cv = Canvas(48, 48)
    shadow_ellipse(cv, 24, 44, 18, 3)
    # parasol
    for y in range(4, 16):
        w = int((y - 3) * 1.8)
        for x in range(24 - w, 24 + w):
            stripe = ((x - 24) // 5) % 2
            cv.px(x, y, '#e8584f' if stripe else '#fbf8f2')
    cv.hline(3, 15, 42, '#b8433b')
    cv.vline(24, 16, 14, P.STONE_DEEP)
    # box
    furniture(cv, 8, 28, 32, 5, 11, '#e6f2f7', '#7fb8d6')
    for i, c in enumerate(('#f2a0b8', '#f7d55c', '#9ad6f2')):
        x = 15 + i * 7
        cv.rect(x, 34, 4, 5, c)
        cv.hline(x, 34, 4, shade(c, 1.2))
        cv.vline(x + 1, 39, 2, P.WOOD_HI)
    for x in (12, 36):
        cv.ellipse(x, 42, 3, 3, BLACKISH)
        cv.px(x, 42, P.STONE)
    return cv, ['**', 'xx']


BLACKISH = '#3a3540'


def grave():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 9, 2)
    cv.rect(6, 4, 12, 17, P.STONE)
    cv.ellipse(12, 5, 6, 3, P.STONE)
    cv.vline(6, 4, 17, P.STONE_HI)
    cv.vline(17, 4, 17, P.STONE_LO)
    cv.rect(9, 8, 6, 8, P.STONE_LO)
    cv.rect(4, 19, 16, 3, P.STONE_LO)
    return cv, ['x']


def boat():
    cv = Canvas(48, 24)
    pts = []
    for x in range(4, 44):
        t = (x - 4) / 39
        depth = int(6 * math.sin(t * math.pi))
        cv.vline(x, 10, 3 + depth // 2, P.WOOD)
        cv.px(x, 10, P.WOOD_HI)
        cv.px(x, 12 + depth // 2, P.WOOD_DEEP)
    cv.rect(10, 11, 28, 2, P.WOOD_LO)
    for x in (16, 30):
        cv.vline(x, 9, 4, P.WOOD_DEEP)
    return cv, ['xx']


def lily():
    cv = Canvas(24, 24)
    for (x, y, r_) in ((7, 8, 4), (16, 15, 5)):
        cv.ellipse(x, y, r_, r_ * 0.7, P.LEAF)
        cv.ellipse(x - 1, y - 1, r_ - 2, r_ * 0.5, P.LEAF_HI)
        cv.line(x, y, x + r_, y, P.LEAF_LO)
    cv.px(16, 13, '#f7c6d6')
    cv.px(17, 13, '#f2a0b8')
    cv.px(16, 12, '#f7c6d6')
    return cv, ['*']


def reeds():
    cv = Canvas(24, 24)
    r = rng(51)
    for i in range(9):
        x = r.randrange(2, 22)
        h = r.randrange(10, 20)
        for k in range(h):
            cv.px(x + (k > h - 4), 23 - k, P.GRASS_LO if i % 2 else P.GRASS_DEEP)
        cv.rect(x, 23 - h - 2, 2, 4, '#8c6440')
    return cv, ['*']


def lantern_string():
    cv = Canvas(24, 24)
    for x in range(24):
        y = 3 + int(3 * math.sin(x / 24 * math.pi))
        cv.px(x, y, '#3a3540')
    cv.ellipse(12, 11, 4, 4.5, '#e2402f')
    cv.hline(9, 6, 7, '#f0c040')
    cv.hline(9, 15, 7, '#f0c040')
    cv.vline(12, 7, 9, '#f6a03c')
    cv.vline(12, 16, 3, '#f0c040')
    return cv, ['*']


def lantern_post():
    cv = Canvas(24, 48)
    cv.rect(11, 14, 3, 32, P.WOOD_DEEP)
    cv.hline(6, 14, 13, P.WOOD_DEEP)
    cv.ellipse(8, 22, 4, 5, '#e2402f')
    cv.hline(5, 17, 7, '#f0c040')
    cv.hline(5, 26, 7, '#f0c040')
    cv.vline(8, 18, 8, '#f6a03c')
    shadow_ellipse(cv, 12, 46, 6, 1.5)
    return cv, ['*', 'x']


def stool():
    cv = Canvas(24, 24)
    furniture(cv, 6, 8, 12, 4, 3, P.WOOD_HI, P.WOOD)
    for x in (7, 16):
        cv.rect(x, 15, 2, 6, P.WOOD_LO)
    return cv, ['x']


def mic_stand():
    cv = Canvas(24, 24)
    cv.vline(12, 4, 17, '#555560')
    cv.ellipse(12, 4, 2, 2, '#3a3a42')
    cv.px(11, 3, '#9a9aa8')
    cv.line(8, 21, 16, 21, '#3a3a42')
    cv.line(12, 20, 8, 22, '#3a3a42')
    cv.line(12, 20, 16, 22, '#3a3a42')
    return cv, ['x']


def clothesline():
    cv = Canvas(48, 48)
    for x in (4, 43):
        cv.rect(x, 10, 2, 34, P.WOOD_LO)
    cv.line(5, 12, 43, 12, '#d8d0c0')
    for (x, c) in ((10, '#e8584f'), (20, '#7fb8d6'), (31, '#f7d55c')):
        cv.rect(x, 13, 8, 10, c)
        cv.hline(x, 13, 8, shade(c, 1.2))
        cv.rect(x + 2, 23, 4, 4, c)
    return cv, ['**', 'xx']


def stepping_stone():
    cv = Canvas(24, 24)
    for (x, y) in ((7, 7), (16, 16)):
        cv.ellipse(x, y, 5, 3.5, P.STONE)
        cv.ellipse(x - 1, y - 1, 3, 2, P.STONE_HI)
    return cv, ['o']


# ---------------------------------------------------------------------------
# City
# ---------------------------------------------------------------------------

def _building(w_tiles, h_tiles, body, trim, rows, lit_seed, shop=None, roof=True):
    W, H = w_tiles * T, h_tiles * T
    cv = Canvas(W, H)
    cv.rect(1, 0, W - 2, H - 1, body)
    cv.vline(1, 0, H - 1, shade(body, 1.1))
    cv.vline(W - 2, 0, H - 1, shade(body, 0.75))
    if roof:
        cv.rect(0, 0, W, 5, trim)
        cv.hline(0, 0, W, shade(trim, 1.2))
        cv.hline(0, 4, W, shade(trim, 0.7))
    r = rng(lit_seed)
    for ry in rows:
        for x in range(8, W - 12, 16):
            lit = r.random() < 0.45
            window(cv, x, ry, 10, 12, frame=shade(body, 0.6), glass=P.WIN_DARK, lit=lit, cross=False, sill=False)
            cv.hline(x - 1, ry + 12, 12, shade(body, 0.8))
    cv.hline(0, H - 1, W, (20, 20, 30, 110))
    return cv


def apartment():
    """林音家 (ch2): residential block (6x5)."""
    cv = _building(6, 5, '#d8c9b0', '#b9a888', [12, 36, 60, 84], 3)
    W, H = 144, 120
    # entrance
    cv.rect(58, 96, 28, 23, '#8a7a66')
    door(cv, 62, 100, 20, 19, col=P.GLASS, double=True, knob=P.STONE_LO, frame='#6a5a48')
    cv.rect(52, 92, 40, 4, '#a07850')
    flags = ['xxxxxx'] * 4 + ['xxxoxx']
    return cv, flags


def school():
    """高中教学楼 (8x5)."""
    W, H = 192, 120
    cv = _building(8, 5, '#eceae2', '#c25843', [26, 52, 78], 9)
    # clock
    cv.ellipse(96, 12, 8, 8, P.WHITE)
    cv.ellipse(96, 12, 8, 8, P.WHITE)
    cv.px(96, 7, BLACKISH)
    cv.vline(96, 7, 6, BLACKISH)
    cv.hline(96, 12, 4, BLACKISH)
    # entrance
    cv.rect(80, 92, 32, 27, '#c9c5b8')
    door(cv, 84, 98, 24, 21, col=P.GLASS, double=True, knob=P.STONE_LO, frame='#7a756a')
    cv.rect(66, 76, 60, 15, '#c25843')
    cv.frame(65, 75, 62, 17, shade('#c25843', 0.7))
    draw_text(cv, 96, 77, '第一中学', P.WHITE, center=True)
    flags = ['xxxxxxxx'] * 4 + ['xxxxoxxx']
    return cv, flags


def cafe():
    """小咖啡馆 (4x4) with striped awning."""
    W, H = 96, 96
    cv = Canvas(W, H)
    wall_brick(cv, 1, 0, W - 2, H - 1, base='#8f5a44', lo='#6e4434', mortar='#c9b49a')
    cv.rect(0, 0, W, 4, '#4e3a30')
    window(cv, 10, 8, 24, 14, frame='#3d2e26', glass=P.WIN_DARK, lit=True, cross=True, sill=False)
    window(cv, 62, 8, 24, 14, frame='#3d2e26', glass=P.WIN_DARK, lit=True, cross=True, sill=False)
    # sign
    cv.rect(26, 25, 44, 15, '#3d2e26')
    cv.frame(25, 24, 46, 17, '#2a1f1a')
    draw_text(cv, 48, 26, '咖啡馆', '#f7d58c', center=True)
    # awning
    for x in range(2, W - 2):
        c = '#2f7a5a' if (x // 6) % 2 == 0 else '#f3efe6'
        for y in range(43, 52):
            cv.px(x, y, c)
        if (x % 6) in (2, 3):
            cv.px(x, 52, c)
    cv.hline(2, 43, W - 4, shade('#2f7a5a', 0.7))
    # big window + door
    window(cv, 6, 58, 38, 24, frame='#3d2e26', glass=P.WIN_DARK, lit=True, cross=False, sill=True)
    door(cv, 53, 62, 14, 33, col='#3d2e26', knob='#f0c040')
    # chalkboard
    cv.rect(72, 66, 16, 20, '#2a2a2a')
    cv.frame(72, 66, 16, 20, P.WOOD_LO)
    for y in (70, 74, 78):
        cv.hline(75, y, 10, '#e8e4dc')
    return cv, ['xxxx', 'xxxx', 'xxxx', 'xxox']


def record_company():
    """唱片公司 (5x6) glass tower."""
    W, H = 120, 144
    cv = Canvas(W, H)
    cv.rect(1, 0, W - 2, H - 1, '#5d6a80')
    for y in range(6, 104, 14):
        for x in range(6, W - 8, 12):
            lit = (x * 7 + y * 3) % 5 == 0
            cv.rect(x, y, 10, 11, P.WIN_LIT if lit else '#7d93b3')
            cv.px(x + 1, y + 1, '#c6d8ee')
    cv.rect(0, 0, W, 4, '#3d4658')
    cv.rect(24, 102, 72, 15, '#20242e')
    draw_text(cv, 60, 103, '星海唱片', '#f7d58c', center=True)
    cv.rect(36, 118, 48, 25, '#3d4658')
    door(cv, 50, 122, 20, 21, col='#9fc6e0', double=True, knob=P.WHITE, frame='#2a3040')
    cv.hline(0, H - 1, W, (20, 20, 30, 110))
    return cv, ['xxxxx'] * 5 + ['xxoxx']


def shop_block(color='#c9b38f', seed=1, sign=None, sign_col='#e8584f'):
    """generic city building (4x5) with a ground floor shop window."""
    cv = _building(4, 5, color, shade(color, 0.7), [10, 36], seed)
    W, H = 96, 120
    cv.rect(4, 84, W - 8, 35, '#3a3540')
    window(cv, 8, 90, 40, 24, frame='#2a2630', glass=P.WIN_DARK, lit=True, cross=False, sill=False)
    door(cv, 58, 92, 16, 27, col='#2a2630', knob=P.STONE)
    if sign:
        cv.rect(8, 69, W - 16, 15, sign_col)
        draw_text(cv, W // 2, 70, sign, P.WHITE, center=True)
    return cv, ['xxxx'] * 5


def convenience():
    cv, f = shop_block('#e9e4da', 4, '便利店', '#2f8f5a')
    return cv, f


def subway_entrance():
    """地铁站入口 (3x2): stairs going down."""
    W, H = 72, 48
    cv = Canvas(W, H)
    cv.rect(2, 10, W - 4, H - 12, '#9a9aa4')
    for i, y in enumerate(range(14, H - 2, 4)):
        c = shade('#55555f', 1 - i * 0.08)
        cv.rect(8, y, W - 16, 3, c)
        cv.hline(8, y, W - 16, shade(c, 1.3))
    cv.rect(2, 10, 6, H - 12, '#b4b4be')
    cv.rect(W - 8, 10, 6, H - 12, '#b4b4be')
    cv.rect(0, 0, W, 10, '#2a5aa8')
    draw_text(cv, W // 2, -1, '地铁 M', P.WHITE, center=True)
    return cv, ['xxx', 'xox']


def streetlamp():
    cv = Canvas(24, 48)
    cv.rect(11, 10, 3, 36, '#3e4250')
    cv.vline(11, 10, 36, '#5a5f70')
    cv.rect(6, 4, 13, 6, '#3e4250')
    cv.rect(7, 9, 11, 3, '#fff3b8')
    cv.rect(9, 44, 7, 3, '#3e4250')
    return cv, ['*', 'x']


def vending():
    cv = Canvas(24, 48)
    cv.rect(3, 6, 18, 38, '#d8453f')
    cv.vline(3, 6, 38, '#ec6a60')
    cv.rect(5, 9, 14, 18, '#e8eef3')
    for y in range(11, 26, 5):
        for x in range(6, 18, 4):
            cv.rect(x, y, 3, 4, ['#3f8fd0', '#f0c040', '#5ab05a', '#e8584f'][(x + y) % 4])
    cv.rect(5, 31, 14, 4, '#3a3540')
    cv.rect(15, 37, 3, 4, '#3a3540')
    cv.hline(2, 44, 20, (20, 20, 30, 110))
    return cv, ['*', 'x']


def trash_bin():
    cv = Canvas(24, 24)
    cv.rect(7, 8, 10, 13, '#4f7f5f')
    cv.rect(6, 6, 12, 3, '#3d6a4d')
    for x in (9, 12, 15):
        cv.vline(x, 10, 9, '#3d6a4d')
    return cv, ['x']


def planter_tree():
    cv, f = tree_small()
    cv.rect(5, 38, 14, 8, '#9a8a78')
    cv.hline(5, 38, 14, '#b8a894')
    return cv, ['*', 'x']


def bus_stop():
    cv = Canvas(24, 48)
    cv.vline(12, 8, 38, '#55555f')
    cv.ellipse(12, 8, 7, 7, '#2a5aa8')
    draw_text(cv, 12, 2, '站', P.WHITE, center=True)
    return cv, ['*', 'x']


def snowman():
    cv = Canvas(24, 48)
    shadow_ellipse(cv, 12, 45, 9, 2)
    cv.ellipse(12, 36, 9, 8, '#f4f8fc')
    cv.ellipse(12, 22, 6, 6, '#f4f8fc')
    cv.outline('#b8c8dc')
    cv.px(10, 21, BLACKISH)
    cv.px(14, 21, BLACKISH)
    cv.px(12, 23, '#f08a3a')
    cv.px(13, 23, '#f08a3a')
    cv.rect(6, 27, 12, 3, '#d8453f')
    cv.rect(14, 28, 3, 6, '#d8453f')
    cv.rect(8, 13, 8, 4, BLACKISH)
    cv.rect(6, 16, 12, 2, BLACKISH)
    return cv, ['*', 'x']


def crosswalk():
    cv = Canvas(24, 24)
    for y in range(2, 24, 6):
        cv.rect(1, y, 22, 3, '#e9e6e0')
    return cv, ['o']


def road_line():
    cv = Canvas(24, 24)
    cv.rect(2, 11, 12, 2, '#e8c84a')
    return cv, ['o']


def flagpole():
    cv = Canvas(24, 72)
    cv.vline(6, 4, 66, '#b8b8c2')
    cv.vline(7, 4, 66, '#8a8a96')
    cv.rect(8, 6, 14, 9, '#d8302a')
    cv.px(10, 8, '#f3cf5a')
    cv.px(13, 9, '#f3cf5a')
    cv.rect(3, 68, 8, 3, P.STONE_LO)
    return cv, ['*', '*', 'x']


def bike_rack():
    cv = Canvas(48, 24)
    for x in (6, 18, 30, 42):
        cv.ellipse(x, 14, 5, 6, (0, 0, 0, 0))
    cv.hline(2, 20, 44, '#8a8a96')
    for x in (8, 22, 36):
        for (dx, c) in ((0, '#3f6fb0'), (6, '#3f6fb0')):
            cv.ellipse(x + dx, 15, 4, 4, '#3a3540')
            cv.ellipse(x + dx, 15, 2.5, 2.5, (0, 0, 0, 0))
        cv.line(x, 15, x + 6, 11, '#d8453f')
        cv.line(x + 3, 11, x + 6, 15, '#d8453f')
    return cv, ['xx']


def bulletin():
    cv = Canvas(48, 48)
    cv.rect(4, 6, 40, 26, P.WOOD_LO)
    cv.rect(6, 8, 36, 22, '#c9a878')
    for (x, y, w, h, c) in ((8, 10, 10, 12, P.WHITE), (20, 11, 9, 10, '#f7d55c'), (31, 9, 9, 14, '#bfe0f0'),
                            (12, 23, 12, 6, '#f2a0b8')):
        cv.rect(x, y, w, h, c)
        cv.px(x + w // 2, y, '#d8302a')
    for x in (8, 38):
        cv.rect(x, 32, 3, 14, P.WOOD_DEEP)
    return cv, ['**', 'xx']


def stage_speaker():
    cv = Canvas(24, 48)
    cv.rect(4, 12, 16, 32, '#2a2630')
    cv.vline(4, 12, 32, '#45404c')
    cv.ellipse(12, 22, 5, 5, '#55505c')
    cv.ellipse(12, 22, 2, 2, '#2a2630')
    cv.ellipse(12, 35, 6, 6, '#55505c')
    cv.ellipse(12, 35, 3, 3, '#2a2630')
    return cv, ['*', 'x']


def neon_sign(text='LIVE', col=P.NEON_PINK):
    cv = Canvas(48, 24)
    cv.rect(2, 4, 44, 16, '#22202a')
    w = draw_text(cv, 24, 4, text, col, center=True)
    cv.frame(2, 4, 44, 16, col)
    return cv, ['**']


OBJECTS = {
    # name: function  (village)
    'tree': tree, 'tree_autumn': tree_autumn, 'tree_small': tree_small, 'pine': pine,
    'old_tree': old_tree, 'bush': bush, 'bush_pink': lambda: flower_bush('#f2a0b8'),
    'bush_white': lambda: flower_bush('#fbf8f2'), 'flowers': flowers,
    'flowers_warm': lambda: flowers(('#e8584f', '#f7d55c', '#f08a3a')),
    'tall_grass': tall_grass, 'rock': rock, 'fence_h': fence_h, 'fence_v': fence_v,
    'bridge_h': bridge_h, 'bridge_v': bridge_v, 'grandpa_house': grandpa_house,
    'house_red': house_red, 'house_brick': house_brick, 'house_wood': house_wood,
    'school_village': school_village, 'shed': shed, 'well': well,
    'sign_village': lambda: signpost('清水村'), 'sign_blank': lambda: signpost(''),
    'bench': bench, 'haystack': haystack, 'crate': crate, 'barrel': barrel,
    'firewood': firewood, 'popsicle_cart': popsicle_cart, 'grave': grave, 'boat': boat,
    'lily': lily, 'reeds': reeds, 'lantern_string': lantern_string, 'lantern_post': lantern_post,
    'stool': stool, 'mic_stand': mic_stand, 'clothesline': clothesline, 'stepping_stone': stepping_stone,
    'speaker': stage_speaker,
}

CITY_OBJECTS = {
    'apartment': apartment, 'school': school, 'cafe': cafe, 'record_company': record_company,
    'shop_a': lambda: shop_block('#c9b38f', 1, '书店', '#3f6fb0'),
    'shop_b': lambda: shop_block('#9fb3c8', 2, '花店', '#d86a8a'),
    'shop_c': lambda: shop_block('#b8a0a0', 3, None),
    'convenience': convenience, 'subway': subway_entrance, 'streetlamp': streetlamp,
    'vending': vending, 'trash_bin': trash_bin, 'planter_tree': planter_tree,
    'bus_stop': bus_stop, 'snowman': snowman, 'crosswalk': crosswalk, 'road_line': road_line,
    'flagpole': flagpole, 'bike_rack': bike_rack, 'bulletin': bulletin,
    'neon_live': lambda: neon_sign('LIVE', P.NEON_PINK),
    'neon_bar': lambda: neon_sign('BAR', P.NEON_CYAN),
}
