"""Render RPG Maker MV autotile blocks from a simple 'material' description.

A material is a tile-periodic texture plus an edge style.  We render small
scenarios (an isolated tile, a plus-shaped cross, a 2x2 island) and crop them
into the layout RPG Maker expects, so the engine can recombine the quarters
into all 47 shapes.
"""
import numpy as np

from pixlib import Canvas, TILE, rgba

T = TILE


def _occupancy_mask(grid):
    """grid: list of strings, '#' = occupied.  Returns bool array (px)."""
    gh, gw = len(grid), len(grid[0])
    m = np.zeros((gh * T, gw * T), dtype=bool)
    for j in range(gh):
        for i in range(gw):
            if grid[j][i] == '#':
                m[j * T:(j + 1) * T, i * T:(i + 1) * T] = True
    return m


def _round_convex(mask, r):
    """Cut convex corners of the occupied region with radius r."""
    if r <= 0:
        return mask
    h, w = mask.shape
    out = mask.copy()

    def run(x, y, sx, sy):
        n = 0
        while True:
            xx, yy = x + sx * (n + 1), y + sy * (n + 1)
            if not (0 <= xx < w and 0 <= yy < h) or not mask[yy, xx]:
                return n
            n += 1

    for y in range(h):
        for x in range(w):
            if not mask[y, x]:
                continue
            for sx in (-1, 1):
                for sy in (-1, 1):
                    bx = run(x, y, sx, 0)   # occupied pixels beyond us horizontally
                    by = run(x, y, 0, sy)   # ... and vertically
                    if bx < r and by < r:
                        dx = r - bx - 0.5
                        dy = r - by - 0.5
                        if dx * dx + dy * dy > r * r:
                            out[y, x] = False
    return out


def _distance_to_void(mask):
    """Chebyshev-ish distance (in px) from each inside pixel to the nearest void pixel."""
    h, w = mask.shape
    INF = 999
    d = np.where(mask, INF, 0).astype(int)
    # two-pass chamfer (8-neighbour, integer)
    for y in range(h):
        for x in range(w):
            if d[y, x]:
                best = d[y, x]
                for dx, dy in ((-1, 0), (0, -1), (-1, -1), (1, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h:
                        best = min(best, d[yy, xx] + 1)
                    else:
                        best = min(best, INF)
                d[y, x] = best
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            if d[y, x]:
                best = d[y, x]
                for dx, dy in ((1, 0), (0, 1), (1, 1), (-1, 1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h:
                        best = min(best, d[yy, xx] + 1)
                d[y, x] = best
    return d


class Material:
    """texture(x, y, frame) -> rgba for interior pixels (x, y are 0..23 within a tile)
    edge(dist, x, y, frame) -> rgba or None for pixels near the boundary
    (dist = 1 for the outermost inside pixel).  Return None to fall back to texture.
    """

    def __init__(self, texture, edge=None, radius=3, rim=3, frames=1):
        self.texture = texture
        self.edge = edge
        self.radius = radius
        self.rim = rim
        self.frames = frames

    def render(self, grid, frame=0):
        mask = _round_convex(_occupancy_mask(grid), self.radius)
        dist = _distance_to_void(mask)
        h, w = mask.shape
        cv = Canvas(w, h)
        for y in range(h):
            for x in range(w):
                if not mask[y, x]:
                    continue
                c = None
                dd = dist[y, x]
                if self.edge and dd <= self.rim:
                    c = self.edge(dd, x % T, y % T, frame)
                if c is None:
                    c = self.texture(x % T, y % T, frame)
                if c is not None:
                    cv.px(x, y, c)
        return cv


def floor_block(mat, frame=0):
    """Return a 2x3-tile canvas (48 x 72 logical) in MV floor autotile layout."""
    block = Canvas(2 * T, 3 * T)
    iso = mat.render(['...', '.#.', '...'], frame).crop(T, T, T, T)
    cross = mat.render(['.#.', '###', '.#.'], frame).crop(T, T, T, T)
    big = mat.render(['....', '.##.', '.##.', '....'], frame).crop(T, T, 2 * T, 2 * T)
    block.paste(iso, 0, 0)
    block.paste(cross, T, 0)
    block.paste(big, 0, T)
    return block


def wall_block(face):
    """face(x, y, w, h) -> canvas: draw a 2x2 tile wall face with all four edges.

    Returns a 48 x 48 logical canvas in MV wall autotile layout."""
    return face(2 * T, 2 * T)


# ---------------------------------------------------------------------------
# Shape computation for the map builder
# ---------------------------------------------------------------------------

def floor_shape(same):
    """same(dx, dy) -> bool, whether the neighbour belongs to the same autotile."""
    L, R, U, D = same(-1, 0), same(1, 0), same(0, -1), same(0, 1)
    UL, UR, DL, DR = same(-1, -1), same(1, -1), same(-1, 1), same(1, 1)
    missing = (not L, not R, not U, not D)
    n = sum(missing)
    if n == 0:
        return (not UL) * 1 + (not UR) * 2 + (not DR) * 4 + (not DL) * 8
    if n == 1:
        if not L:
            return 16 + (not UR) * 1 + (not DR) * 2
        if not U:
            return 20 + (not DR) * 1 + (not DL) * 2
        if not R:
            return 24 + (not DL) * 1 + (not UL) * 2
        return 28 + (not UL) * 1 + (not UR) * 2
    if n == 2:
        if not L and not R:
            return 32
        if not U and not D:
            return 33
        if not U and not L:
            return 34 + (not DR)
        if not U and not R:
            return 36 + (not DL)
        if not R and not D:
            return 38 + (not UL)
        return 40 + (not UR)  # D and L missing
    if n == 3:
        if D:
            return 42
        if R:
            return 43
        if U:
            return 44
        return 45  # only L present
    return 46


def wall_shape(same_l, same_r, same_u, same_d):
    return (not same_l) * 1 + (not same_u) * 2 + (not same_r) * 4 + (not same_d) * 8
