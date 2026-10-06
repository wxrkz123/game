"""Reusable drawing helpers for objects (top-down 3/4 RPG perspective)."""
import math

from pixlib import Canvas, rgba, shade, mix, rng
import palette as P


def box(cv, x, y, w, h, fill, light=None, dark=None, outline=None):
    """A flat box with 1px light top/left and dark bottom/right bevel."""
    cv.rect(x, y, w, h, fill)
    if light:
        cv.hline(x, y, w, light)
    if dark:
        cv.hline(x, y + h - 1, w, dark)
        cv.vline(x + w - 1, y, h, dark)
    if outline:
        cv.frame(x - 1, y - 1, w + 2, h + 2, outline)


def furniture(cv, x, y, w, top_h, front_h, top, front, edge=None):
    """Block seen from 3/4 view: top surface (top_h) above a front face (front_h)."""
    cv.rect(x, y, w, top_h, top)
    cv.hline(x, y, w, shade(top, 1.12))
    cv.rect(x, y + top_h, w, front_h, front)
    cv.hline(x, y + top_h, w, edge or shade(front, 0.8))
    cv.hline(x, y + top_h + front_h - 1, w, shade(front, 0.75))


def blob(cv, cx, cy, rx, ry, base, hi, lo, seed=0, light_dx=-0.35, light_dy=-0.45, bumpy=0.0):
    """Shaded round blob (tree canopy, bush) with a top-left light."""
    r = rng(seed)
    for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
        for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
            dx = (x + 0.5 - cx) / rx
            dy = (y + 0.5 - cy) / ry
            ang = math.atan2(dy, dx)
            wob = 1.0 + bumpy * math.sin(ang * 7 + seed) * 0.5 + bumpy * math.sin(ang * 11 + seed * 2) * 0.3
            d = math.sqrt(dx * dx + dy * dy)
            if d <= wob:
                # lighting
                l = -(dx * light_dx + dy * light_dy) / max(d, 0.001) * min(d, 1.0)
                v = l * 0.6 + (1 - d) * 0.5
                if v > 0.42:
                    c = hi
                elif v < -0.1 or d > wob - 0.12 and (dx + dy) > 0.2:
                    c = lo
                else:
                    c = base
                cv.px(x, y, c)


def leaf_clusters(cv, cx, cy, rx, ry, colors, n, seed, size=3):
    """Scatter small clumps for leafy texture inside an ellipse."""
    r = rng(seed)
    hi, base, lo = colors
    for _ in range(n):
        a = r.random() * 2 * math.pi
        d = math.sqrt(r.random()) * 0.85
        x = int(cx + math.cos(a) * rx * d)
        y = int(cy + math.sin(a) * ry * d)
        # bright clump on upper-left, dark on lower-right
        up = (math.cos(a) * -0.6 + math.sin(a) * -0.8) * d
        col = hi if up > 0.25 else (lo if up < -0.35 else base)
        for k in range(size):
            cv.px(x + k - 1, y, col)
        cv.px(x, y - 1, col)
        cv.px(x, y + 1, shade(col, 0.85))


def window(cv, x, y, w, h, frame=P.WOOD_LO, glass=P.GLASS, lit=False, cross=True, sill=True):
    cv.rect(x, y, w, h, frame)
    g = P.WIN_LIT if lit else glass
    cv.rect(x + 1, y + 1, w - 2, h - 2, g)
    # reflection
    cv.px(x + 2, y + 2, shade(g, 1.25))
    cv.px(x + 3, y + 2, shade(g, 1.25))
    cv.px(x + 2, y + 3, shade(g, 1.25))
    if cross:
        cv.vline(x + w // 2, y + 1, h - 2, frame)
        cv.hline(x + 1, y + h // 2, w - 2, frame)
    if sill:
        cv.hline(x - 1, y + h, w + 2, shade(frame, 0.8))


def lattice_window(cv, x, y, w, h):
    """Traditional Chinese wooden lattice window."""
    cv.rect(x, y, w, h, P.WOOD_DEEP)
    cv.rect(x + 1, y + 1, w - 2, h - 2, '#e8dcc0')
    for xx in range(x + 2, x + w - 1, 3):
        cv.vline(xx, y + 1, h - 2, P.WOOD_LO)
    for yy in range(y + 2, y + h - 1, 3):
        cv.hline(x + 1, yy, w - 2, P.WOOD_LO)


def door(cv, x, y, w, h, col=P.WOOD, double=False, knob=P.DIRT_HI, frame=None):
    cv.rect(x - 1, y - 1, w + 2, h + 1, frame or shade(col, 0.6))
    cv.rect(x, y, w, h, col)
    cv.hline(x, y, w, shade(col, 1.15))
    for xx in range(x + 2, x + w - 1, 3):
        cv.vline(xx, y + 2, h - 3, shade(col, 0.88))
    if double:
        cv.vline(x + w // 2, y, h, shade(col, 0.6))
        cv.px(x + w // 2 - 2, y + h // 2, knob)
        cv.px(x + w // 2 + 1, y + h // 2, knob)
    else:
        cv.px(x + w - 3, y + h // 2, knob)


def tile_roof(cv, x, y, w, h, base, hi, lo, row=4, eave=True, ridge=True):
    """Clay tile roof: horizontal rows of scalloped tiles."""
    cv.rect(x, y, w, h, base)
    for yy in range(y, y + h):
        k = (yy - y) % row
        for xx in range(x, x + w):
            if k == 0:
                cv.px(xx, yy, lo)
            elif k == 1 and (xx + (yy - y) // row * 2) % 4 == 0:
                cv.px(xx, yy, hi)
            if (xx - x + ((yy - y) // row) * 2) % 4 == 0 and k > 0:
                cv.px(xx, yy, shade(base, 0.9))
    if ridge:
        cv.rect(x, y, w, 2, lo)
        cv.hline(x, y, w, shade(lo, 0.8))
    if eave:
        cv.hline(x, y + h - 1, w, shade(lo, 0.7))


def wall_plaster(cv, x, y, w, h, base=P.PLASTER, lo=P.PLASTER_LO, seed=0, base_band=True):
    cv.rect(x, y, w, h, base)
    r = rng(seed)
    for _ in range(w * h // 25):
        cv.px(x + r.randrange(w), y + r.randrange(h), shade(base, 0.96))
    cv.hline(x, y, w, shade(lo, 0.85))  # shadow under eaves
    cv.hline(x, y + 1, w, lo)
    if base_band:
        cv.rect(x, y + h - 3, w, 3, P.STONE)
        cv.hline(x, y + h - 3, w, P.STONE_HI)
        cv.hline(x, y + h - 1, w, P.STONE_LO)


def wall_brick(cv, x, y, w, h, base=P.BRICK, lo=P.BRICK_LO, mortar=P.MORTAR):
    cv.rect(x, y, w, h, mortar)
    for row, yy in enumerate(range(y, y + h, 3)):
        off = 0 if row % 2 == 0 else 3
        for xx in range(x - 6 + off, x + w, 6):
            for bx in range(5):
                for by in range(2):
                    if x <= xx + bx < x + w and yy + by < y + h:
                        cv.px(xx + bx, yy + by, base if by == 0 else lo)
    cv.hline(x, y, w, shade(lo, 0.7))


def shadow_ellipse(cv, cx, cy, rx, ry, alpha=70):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            dx = (x + 0.5 - cx) / rx
            dy = (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1:
                if cv.get(x, y)[3] == 0:
                    cv.px(x, y, (30, 40, 30, alpha))


def text_pixels(cv, x, y, glyphs, color):
    """Draw tiny hand-made glyphs (3x5) for signs.  glyphs: list of 5-row strings."""
    for g in glyphs:
        for j, row in enumerate(g):
            for i, ch in enumerate(row):
                if ch == '#':
                    cv.px(x + i, y + j, color)
        x += len(g[0]) + 1
