"""Small decorations that make the maps feel lived-in: ground details, tree variants,
garden and farm things outside; clutter, lamps and keepsakes inside.

Same conventions as objects_outside / objects_inside: each function returns
(canvas, flags) with one flag char per tile (o passable, x blocked, * above characters).
"""
from pixlib import Canvas, TILE, shade, mix, rng
from draw import blob, leaf_clusters, shadow_ellipse, furniture
from textutil import draw_text
import palette as P

T = TILE
INK = '#3a3540'


# ---------------------------------------------------------------------------
# ground details (passable, drawn under characters)
# ---------------------------------------------------------------------------
def _blade(cv, x, y, h, col, lean=0):
    for k in range(h):
        cv.px(x + (lean if k > h * 0.6 else 0), y - k, col)


def tuft(seed, n=4, hmin=3, hmax=6, cols=(P.GRASS_LO, P.GRASS_DEEP, P.GRASS_HI)):
    """a small clump of grass blades"""
    def make():
        cv = Canvas(24, 24)
        r = rng(seed)
        for _ in range(r.randrange(1, 3)):
            cx, cy = r.randrange(5, 19), r.randrange(10, 21)
            for i in range(n):
                _blade(cv, cx + i - n // 2, cy, r.randrange(hmin, hmax + 1), cols[i % len(cols)],
                       lean=-1 if i < n // 2 else 1)
        return cv, ['o']
    return make


def clover():
    cv = Canvas(24, 24)
    r = rng(41)
    for _ in range(4):
        x, y = r.randrange(4, 19), r.randrange(5, 20)
        for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 1), (2, 1), (0, 2), (1, 2)):
            cv.px(x + dx, y + dy, P.GRASS_DEEP if dy == 2 else P.LEAF_HI if dx in (0, 1) and dy == 0 else P.LEAF)
    return cv, ['o']


def pebbles():
    cv = Canvas(24, 24)
    r = rng(43)
    for _ in range(4):
        x, y = r.randrange(4, 19), r.randrange(6, 20)
        w = r.choice((2, 3, 3, 4))
        cv.rect(x, y + 1, w, 1, (40, 40, 30, 70))
        cv.rect(x, y, w, 1, P.STONE)
        cv.px(x, y, P.STONE_HI)
    return cv, ['o']


def little_flowers(col, centre='#f7d55c', seed=45, n=4):
    def make():
        cv = Canvas(24, 24)
        r = rng(seed)
        for _ in range(n):
            x, y = r.randrange(4, 20), r.randrange(5, 19)
            cv.px(x, y + 2, P.LEAF_LO)
            cv.px(x, y + 3, P.LEAF_LO)
            cv.px(x + 1, y + 3, P.LEAF)
            cv.px(x - 1, y, col)
            cv.px(x + 1, y, col)
            cv.px(x, y - 1, col)
            cv.px(x, y + 1, col)
            cv.px(x, y, centre)
        return cv, ['o']
    return make


def dandelions():
    cv = Canvas(24, 24)
    r = rng(47)
    for i in range(3):
        x, y = r.randrange(5, 19), r.randrange(7, 18)
        _blade(cv, x, y + 5, 5, P.GRASS_LO)
        if i == 1:      # a seed puff
            for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1)):
                cv.px(x + dx, y + dy, P.WHITE)
            cv.px(x, y, '#e8e2d2')
        else:
            cv.rect(x - 1, y - 1, 3, 3, '#f7d55c')
            cv.px(x, y, '#e0a030')
    return cv, ['o']


def mushrooms():
    cv = Canvas(24, 24)
    for (x, y, cap) in ((8, 15, '#c8503c'), (14, 18, '#b08a5a'), (16, 13, '#c8503c')):
        cv.rect(x, y, 2, 3, '#efe4cf')
        cv.rect(x - 2, y - 2, 6, 2, cap)
        cv.hline(x - 1, y - 3, 4, cap)
        cv.px(x - 1, y - 2, P.WHITE)
        cv.px(x + 2, y - 1, P.WHITE)
    return cv, ['o']


def fallen_leaves():
    cv = Canvas(24, 24)
    r = rng(49)
    for _ in range(6):
        x, y = r.randrange(3, 20), r.randrange(4, 20)
        col = r.choice(('#e0843a', '#f3b24c', '#b85a2c', '#d9a33a'))
        cv.rect(x, y, 3, 2, col)
        cv.px(x + 1, y - 1, col)
        cv.px(x + 2, y + 1, shade(col, 0.7))
    return cv, ['o']


def sprouts():
    """rows of seedlings for the vegetable field"""
    cv = Canvas(24, 24)
    for y in (6, 14, 21):
        for x in range(3, 22, 5):
            cv.px(x, y, P.LEAF_LO)
            cv.px(x - 1, y - 1, P.LEAF)
            cv.px(x + 1, y - 1, P.LEAF_HI)
            cv.px(x, y - 2, P.LEAF)
    return cv, ['o']


def cabbages():
    cv = Canvas(24, 24)
    for (x, y) in ((6, 8), (17, 8), (11, 17)):
        shadow_ellipse(cv, x, y + 4, 5, 1.5)
        cv.ellipse(x, y, 5, 4, '#7fbf5a')
        cv.ellipse(x, y, 3, 2.5, '#b4dc84')
        cv.px(x, y, '#d6efb0')
        cv.px(x - 4, y + 2, P.LEAF_LO)
        cv.px(x + 4, y + 2, P.LEAF_LO)
    return cv, ['x']


# ---------------------------------------------------------------------------
# bigger outdoor things
# ---------------------------------------------------------------------------
def _canopy(cv, cx, cy, rx, ry, seed, colors, deep):
    hi, base, lo = colors
    blob(cv, cx, cy, rx, ry, base, hi, lo, seed=seed, bumpy=0.14)
    leaf_clusters(cv, cx, cy, rx, ry, (hi, base, lo), int(rx * ry / 6), seed + 1)
    cv.outline(deep)


def _trunk(cv, x, y, w, h, col=P.WOOD_LO):
    cv.rect(x, y, w, h, col)
    cv.vline(x, y, h, shade(col, 1.2))
    cv.vline(x + w - 1, y, h, shade(col, 0.7))


def tree_variant(seed, colors, deep, fruit=None, rx=20, ry=15):
    def make():
        cv = Canvas(48, 48)
        shadow_ellipse(cv, 24, 44, 15, 3.5)
        _trunk(cv, 21, 28, 6, 16)
        c2 = Canvas(48, 48)
        _canopy(c2, 24, 19, rx, ry, seed, colors, deep)
        if fruit:
            r = rng(seed + 7)
            for _ in range(11):
                x, y = r.randrange(8, 40), r.randrange(8, 30)
                if c2.get(x, y)[3] and c2.get(x + 1, y + 1)[3]:
                    c2.rect(x, y, 2, 2, fruit)
                    c2.px(x, y, shade(fruit, 1.3))
        cv.blit(c2, 0, 0)
        return cv, ['**', 'xx']
    return make


def bamboo():
    cv = Canvas(24, 48)
    shadow_ellipse(cv, 12, 45, 9, 2.5)
    for (x, top, col) in ((6, 6, '#6fa64a'), (12, 2, '#82b85a'), (17, 9, '#5f9342')):
        cv.rect(x, top, 3, 44 - top, col)
        cv.vline(x, top, 44 - top, shade(col, 1.2))
        for y in range(top + 6, 44, 7):
            cv.hline(x, y, 3, shade(col, 0.7))
    r = rng(51)
    for _ in range(14):
        x, y = r.randrange(2, 22), r.randrange(2, 30)
        cv.line(x, y, x + r.choice((-3, 3)), y + 1, r.choice((P.LEAF, P.LEAF_HI, P.LEAF_LO)))
    return cv, ['*', 'x']


def stump():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 19, 9, 2.5)
    cv.rect(5, 9, 14, 9, P.WOOD_LO)
    cv.vline(5, 9, 9, shade(P.WOOD_LO, 1.2))
    cv.vline(18, 9, 9, shade(P.WOOD_LO, 0.7))
    cv.ellipse(12, 9, 7, 3, P.DIRT_HI)
    cv.ellipse(12, 9, 4, 1.5, P.DIRT)
    cv.px(12, 9, P.WOOD_LO)
    cv.px(4, 17, P.WOOD_LO)
    cv.px(19, 17, P.WOOD_LO)
    return cv, ['x']


def log():
    cv = Canvas(48, 24)
    shadow_ellipse(cv, 24, 19, 21, 2.5)
    cv.rect(4, 9, 38, 9, P.WOOD_LO)
    cv.hline(4, 9, 38, shade(P.WOOD_LO, 1.25))
    cv.hline(4, 17, 38, shade(P.WOOD_LO, 0.7))
    for x in range(8, 40, 6):
        cv.px(x, 12, shade(P.WOOD_LO, 0.75))
        cv.px(x + 2, 14, shade(P.WOOD_LO, 0.8))
    cv.ellipse(42, 13, 3, 4.5, P.DIRT_HI)
    cv.ellipse(42, 13, 1.5, 2.5, P.DIRT)
    cv.px(20, 8, P.LEAF)
    cv.px(21, 8, P.LEAF_HI)
    return cv, ['xx']


def hedge():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 11, 2)
    c2 = Canvas(24, 24)
    c2.round_rect(1, 6, 22, 15, P.LEAF, r=3)
    leaf_clusters(c2, 12, 13, 10, 6, (P.LEAF_HI, P.LEAF, P.LEAF_LO), 12, 53)
    c2.outline(P.LEAF_DEEP)
    cv.blit(c2, 0, 0)
    return cv, ['x']


def flowerpot_out(col='#e8584f'):
    def make():
        cv = Canvas(24, 24)
        shadow_ellipse(cv, 12, 21, 7, 2)
        cv.rect(7, 13, 10, 8, '#c46a3a')
        cv.hline(6, 13, 12, '#d8844c')
        cv.hline(7, 20, 10, '#9a4f2a')
        c2 = Canvas(24, 24)
        blob(c2, 12, 9, 7, 5, P.LEAF, P.LEAF_HI, P.LEAF_LO, seed=55, bumpy=0.3)
        c2.outline(P.LEAF_DEEP)
        cv.blit(c2, 0, 0)
        for (x, y) in ((9, 7), (14, 6), (12, 10), (16, 9)):
            cv.rect(x, y, 2, 2, col)
            cv.px(x, y, shade(col, 1.3))
        return cv, ['x']
    return make


def mailbox():
    cv = Canvas(24, 48)
    shadow_ellipse(cv, 12, 45, 6, 2)
    cv.rect(11, 28, 3, 17, P.WOOD_LO)
    cv.round_rect(5, 16, 14, 13, '#3f8a5a', r=2)
    cv.hline(6, 16, 12, '#5aa874')
    cv.rect(8, 20, 8, 2, '#24543a')
    cv.rect(17, 18, 2, 5, '#d0392f')
    return cv, ['*', 'x']


def bicycle():
    cv = Canvas(48, 24)
    shadow_ellipse(cv, 24, 21, 18, 2)
    for cx in (12, 34):
        cv.ellipse(cx, 15, 6, 6, INK)
        cv.ellipse(cx, 15, 5, 5, (0, 0, 0, 0))
        for k in range(-4, 5, 2):
            cv.px(cx + k, 15, '#9a9aa8')
        cv.px(cx, 15, '#c8c8d0')
    cv.line(12, 15, 20, 7, '#2f6aa3')
    cv.line(20, 7, 30, 7, '#2f6aa3')
    cv.line(30, 7, 34, 15, '#2f6aa3')
    cv.line(20, 7, 23, 15, '#2f6aa3')
    cv.line(23, 15, 12, 15, '#2f6aa3')
    cv.hline(17, 5, 5, INK)
    cv.line(30, 7, 31, 3, INK)
    cv.hline(29, 3, 4, INK)
    cv.rect(31, 6, 6, 3, '#b07a45')         # front basket
    return cv, ['xx']


def watering_can():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 20, 7, 2)
    cv.rect(7, 11, 9, 8, '#5f8fb8')
    cv.hline(7, 11, 9, '#86b0d4')
    cv.line(16, 13, 21, 9, '#5f8fb8')
    cv.px(21, 8, '#86b0d4')
    cv.rect(9, 8, 5, 2, '#3f6f98')
    return cv, ['x']


def veg_basket():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 9, 2)
    cv.rect(4, 12, 16, 8, '#c8a060')
    for x in range(5, 20, 3):
        cv.vline(x, 12, 8, '#a8804a')
    cv.hline(4, 12, 16, '#e0bc80')
    for (x, y, c) in ((7, 10, '#e8584f'), (11, 9, '#f08a3a'), (15, 10, '#7fbf5a'), (9, 8, '#7fbf5a')):
        cv.rect(x, y, 3, 3, c)
        cv.px(x, y, shade(c, 1.3))
    return cv, ['x']


def chicken_coop():
    cv = Canvas(48, 48)
    shadow_ellipse(cv, 24, 44, 20, 3)
    cv.rect(6, 22, 36, 20, P.OLDWOOD)
    for x in range(6, 42, 4):
        cv.vline(x, 22, 20, P.OLDWOOD_LO)
    # roof
    for k in range(10):
        cv.hline(4 + k // 2, 13 + k, 40 - k, '#a5733f' if k % 3 else '#7e5530')
    cv.rect(18, 30, 12, 12, '#3a2a22')
    cv.hline(18, 30, 12, P.OLDWOOD_LO)
    cv.rect(8, 40, 10, 3, '#e8d8a0')          # straw
    return cv, ['**', 'xx']


# ---------------------------------------------------------------------------
# inside
# ---------------------------------------------------------------------------
def floor_lamp():
    cv = Canvas(24, 48)
    shadow_ellipse(cv, 12, 45, 6, 1.5)
    cv.rect(8, 43, 8, 2, INK)
    cv.vline(12, 18, 25, '#6a6470')
    # shade
    for k in range(9):
        cv.hline(7 - k // 3, 9 + k, 10 + (k // 3) * 2, '#f3dca0' if k < 7 else '#d8bc80')
    cv.hline(6, 18, 12, '#c8a868')
    return cv, ['*', 'x']


def table_lamp():
    cv = Canvas(24, 24)
    furniture(cv, 4, 12, 16, 3, 9, P.WOOD_HI, P.WOOD)
    cv.rect(11, 6, 2, 6, '#6a6470')
    for k in range(5):
        cv.hline(8 - k // 2, 1 + k, 8 + (k // 2) * 2, '#f3dca0')
    return cv, ['x']


def wall_shelf():
    cv = Canvas(24, 24)
    cv.rect(2, 14, 20, 2, P.WOOD)
    cv.hline(2, 16, 20, (0, 0, 0, 60))
    for (x, h, c) in ((4, 6, '#d8574f'), (7, 7, '#3f6fb0'), (9, 5, '#f7d55c'), (14, 4, '#e8e2d2'), (18, 5, '#8fbf6a')):
        cv.rect(x, 14 - h, 2 if x < 12 else 3, h, c)
    cv.rect(13, 9, 5, 1, '#c8c8d0')
    return cv, ['x']


def fu_poster():
    """the red diamond 福 for good luck"""
    cv = Canvas(24, 24)
    for k in range(9):
        cv.hline(12 - k, 3 + k, 2 * k + 1, '#d0392f')
        cv.hline(12 - k, 19 - k, 2 * k + 1, '#d0392f')
    draw_text(cv, 12, 5, '福', '#f3cf5a', center=True)
    return cv, ['x']


def scroll_painting():
    """hanging scroll: mountains in ink"""
    cv = Canvas(24, 24)
    cv.rect(7, 1, 10, 21, '#f3ead6')
    cv.rect(6, 1, 12, 2, P.WOOD_LO)
    cv.rect(6, 21, 12, 2, P.WOOD_LO)
    cv.line(8, 15, 11, 9, '#6a6470')
    cv.line(11, 9, 13, 13, '#6a6470')
    cv.line(12, 12, 14, 7, '#8a8490')
    cv.line(14, 7, 16, 15, '#8a8490')
    cv.px(9, 5, '#d0392f')
    return cv, ['x']


def corn_string():
    cv = Canvas(24, 24)
    cv.vline(8, 1, 3, P.WOOD_LO)
    for y in range(4, 20, 3):
        cv.rect(6, y, 5, 3, '#f0c040')
        cv.px(6, y, '#f7d870')
    cv.vline(16, 1, 3, P.WOOD_LO)
    for y in range(4, 18, 2):
        cv.px(15 + (y // 2) % 2, y, '#d33a2c')
        cv.px(16 + (y // 2) % 2, y + 1, '#a82a20')
    return cv, ['x']


def thermos():
    """the red flowered hot-water flask every Chinese home has"""
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 5, 1.5)
    cv.rect(9, 6, 7, 15, '#d0392f')
    cv.vline(9, 6, 15, '#e8584f')
    cv.rect(10, 3, 5, 3, '#e8e2d2')
    cv.px(12, 11, '#f3cf5a')
    cv.px(11, 12, '#f3cf5a')
    cv.px(13, 12, '#f3cf5a')
    cv.px(12, 13, '#f3cf5a')
    cv.hline(9, 19, 7, '#8a2a22')
    return cv, ['x']


def washstand():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 22, 8, 1.5)
    for x in (5, 18):
        cv.vline(x, 10, 12, P.WOOD_LO)
    cv.line(5, 21, 18, 14, P.WOOD_DEEP)
    cv.ellipse(12, 9, 8, 3, '#d8dce0')
    cv.ellipse(12, 9, 6, 2, '#9fc6e0')
    cv.rect(17, 2, 3, 6, '#e8584f')      # towel
    return cv, ['x']


def plant_small():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 6, 1.5)
    cv.rect(8, 14, 8, 7, '#e8e2d2')
    cv.hline(8, 14, 8, P.WHITE)
    c2 = Canvas(24, 24)
    for (x, y, rx, ry, s) in ((12, 10, 6, 5, 4), (8, 7, 3, 4, 5), (16, 6, 3, 4, 6)):
        blob(c2, x, y, rx, ry, P.LEAF, P.LEAF_HI, P.LEAF_LO, seed=s, bumpy=0.3)
    c2.outline(P.LEAF_DEEP)
    cv.blit(c2, 0, 0)
    return cv, ['x']


def vase_flowers():
    cv = Canvas(24, 24)
    furniture(cv, 5, 14, 14, 3, 7, P.WOOD_HI, P.WOOD)
    cv.rect(10, 7, 4, 7, '#5f8fb8')
    cv.px(10, 7, '#86b0d4')
    for (x, y, c) in ((9, 3, '#f2a0b8'), (13, 2, '#fbf8f2'), (11, 1, '#f7d55c'), (15, 4, '#f2a0b8')):
        cv.vline(x + 1, y + 2, 3, P.LEAF_LO)
        cv.rect(x, y, 2, 2, c)
    return cv, ['x']


def cushion(col='#d8574f'):
    def make():
        cv = Canvas(24, 24)
        shadow_ellipse(cv, 12, 18, 8, 2)
        cv.round_rect(4, 9, 16, 9, col, r=2)
        cv.hline(5, 9, 14, shade(col, 1.2))
        cv.px(12, 13, shade(col, 0.7))
        return cv, ['o']
    return make


def basket():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 8, 1.5)
    cv.rect(5, 11, 14, 9, '#c8a060')
    for y in range(12, 20, 2):
        cv.hline(5, y, 14, '#a8804a')
    cv.hline(5, 11, 14, '#e0bc80')
    cv.rect(7, 8, 10, 3, '#e8e2d2')     # folded cloth
    return cv, ['x']


def coat_rack():
    cv = Canvas(24, 48)
    shadow_ellipse(cv, 12, 45, 7, 1.5)
    cv.vline(12, 8, 36, P.WOOD_LO)
    cv.hline(7, 44, 11, P.WOOD_LO)
    cv.hline(8, 9, 9, P.WOOD_LO)
    cv.rect(5, 10, 7, 14, '#5f7fa8')     # coat
    cv.hline(5, 10, 7, '#7f9fc8')
    cv.rect(14, 10, 4, 6, '#e8c05a')     # scarf
    cv.vline(15, 16, 6, '#e8c05a')
    return cv, ['*', 'x']


def umbrella_stand():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 5, 1.5)
    cv.rect(8, 12, 8, 9, '#8a8490')
    cv.hline(8, 12, 8, '#aaa4b0')
    cv.line(10, 12, 9, 2, '#3f6fb0')
    cv.line(14, 12, 15, 4, '#d8574f')
    cv.px(8, 2, '#3f6fb0')
    cv.px(16, 4, '#d8574f')
    return cv, ['x']


def slippers():
    cv = Canvas(24, 24)
    for x in (7, 13):
        cv.round_rect(x, 9, 4, 9, '#5f8fb8', r=1)
        cv.rect(x, 9, 4, 3, '#86b0d4')
    return cv, ['o']


def trash_can():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 5, 1.5)
    cv.rect(8, 10, 8, 11, '#9fb38a')
    cv.hline(7, 10, 10, '#b8cca4')
    cv.px(11, 9, '#e8e2d2')
    cv.px(12, 8, '#e8e2d2')
    return cv, ['x']


def books_floor():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 8, 1.5)
    for (y, x, w, c) in ((18, 5, 14, '#3f6fb0'), (15, 6, 12, '#d8574f'), (12, 5, 13, '#f7d55c'), (9, 7, 10, '#8fbf6a')):
        cv.rect(x, y, w, 3, c)
        cv.hline(x, y, w, shade(c, 1.25))
        cv.vline(x + w - 1, y, 3, '#f3ead6')
    return cv, ['x']


def sheet_music():
    cv = Canvas(24, 24)
    r = rng(57)
    for _ in range(3):
        x, y = r.randrange(3, 13), r.randrange(4, 14)
        cv.rect(x, y, 8, 6, '#f6f1e4')
        for k in range(1, 6, 2):
            cv.hline(x + 1, y + k, 6, '#b8b0a0')
        cv.px(x + 3, y + 2, INK)
    return cv, ['o']


def string_lights():
    cv = Canvas(24, 24)
    pts = [(1, 6), (6, 9), (12, 10), (18, 9), (23, 6)]
    for (a, b) in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], '#6a6470')
    for (x, y), c in zip(((4, 9), (9, 11), (15, 11), (20, 9)), ('#ffe08a', '#ffb0c8', '#ffe08a', '#a8e0ff')):
        cv.rect(x, y, 2, 2, c)
    return cv, ['x']


def teddy():
    cv = Canvas(24, 24)
    shadow_ellipse(cv, 12, 21, 6, 1.5)
    bear, lo = '#c8905a', '#a8703e'
    cv.ellipse(12, 15, 5, 5, bear)
    cv.ellipse(12, 8, 4, 4, bear)
    cv.ellipse(8, 5, 1.5, 1.5, lo)
    cv.ellipse(16, 5, 1.5, 1.5, lo)
    cv.px(11, 8, INK)
    cv.px(13, 8, INK)
    cv.rect(11, 10, 3, 1, '#e8c8a0')
    cv.rect(9, 12, 7, 2, '#d8574f')      # ribbon
    return cv, ['x']


def mirror():
    cv = Canvas(24, 24)
    cv.round_rect(7, 2, 10, 18, P.WOOD, r=2)
    cv.round_rect(8, 3, 8, 16, '#c8dce8', r=2)
    cv.line(10, 6, 13, 3, P.WHITE)
    cv.line(10, 9, 14, 5, '#e8f0f6')
    return cv, ['x']


def runner_rug(col='#b85a4a', edge='#e8c05a'):
    def make():
        cv = Canvas(48, 24)
        cv.rect(3, 6, 42, 13, col)
        cv.frame(4, 7, 40, 11, edge)
        for x in range(8, 41, 6):
            cv.px(x, 12, edge)
        for x in range(3, 45, 2):
            cv.px(x, 5, edge)
            cv.px(x, 19, edge)
        return cv, ['oo']
    return make


def crate_stack():
    cv = Canvas(24, 24)
    for (x, y, w, h) in ((3, 11, 11, 10), (12, 13, 9, 8), (6, 3, 9, 8)):
        cv.rect(x, y, w, h, '#c8a06a')
        cv.frame(x, y, w, h, '#8a6243')
        cv.line(x, y, x + w - 1, y + h - 1, '#a8804a')
    return cv, ['x']


OUTSIDE = {
    'tuft_a': tuft(61), 'tuft_b': tuft(62, n=3), 'tuft_c': tuft(63, n=5, hmin=4, hmax=8),
    'tuft_dry': tuft(64, cols=('#b8a860', '#9a8c4a', '#d0c078')),
    'clover': clover, 'pebbles': pebbles,
    'daisies': little_flowers(P.WHITE, seed=45), 'bluebells': little_flowers('#9a8ee0', '#e8e2ff', seed=46),
    'buttercups': little_flowers('#f7d55c', '#e08a3a', seed=48, n=5), 'dandelions': dandelions,
    'mushrooms': mushrooms, 'fallen_leaves': fallen_leaves, 'sprouts': sprouts, 'cabbages': cabbages,
    'tree_round': tree_variant(71, ('#9fd46a', '#6aae4e', '#4a8a40'), '#2c5b33', rx=19, ry=16),
    'tree_dark': tree_variant(73, ('#7ab85a', '#4f8f46', '#356e38'), '#1f4a2c'),
    'tree_persimmon': tree_variant(75, (P.LEAF_HI, P.LEAF, P.LEAF_LO), P.LEAF_DEEP, fruit='#f08a3a'),
    'bamboo': bamboo, 'stump': stump, 'log': log, 'hedge': hedge,
    'flowerpot_red': flowerpot_out('#e8584f'), 'flowerpot_yellow': flowerpot_out('#f7d55c'),
    'mailbox': mailbox, 'bicycle': bicycle, 'watering_can': watering_can, 'veg_basket': veg_basket,
    'chicken_coop': chicken_coop,
}

INSIDE = {
    'floor_lamp': floor_lamp, 'table_lamp': table_lamp, 'wall_shelf': wall_shelf, 'fu': fu_poster,
    'scroll_painting': scroll_painting, 'corn_string': corn_string, 'thermos': thermos,
    'washstand': washstand, 'plant_small': plant_small, 'vase_flowers': vase_flowers,
    'cushion_red': cushion('#d8574f'), 'cushion_blue': cushion('#5f8fb8'), 'basket': basket,
    'coat_rack': coat_rack, 'umbrella_stand': umbrella_stand, 'slippers': slippers,
    'trash_can': trash_can, 'books_floor': books_floor, 'sheet_music': sheet_music,
    'string_lights': string_lights, 'teddy': teddy, 'mirror': mirror,
    'runner_red': runner_rug(), 'runner_green': runner_rug('#5f8a5a', '#e8d8a0'),
    'crate_stack': crate_stack,
}
