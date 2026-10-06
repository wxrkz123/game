"""Tiny pixel-art toolkit used by every art generator in this folder.

All drawing happens at *logical* resolution (one tile = 24 x 24 px) and is
scaled up 2x with nearest-neighbour when saved, so every RPG Maker MV image
ends up at the engine's native 48 px tile size with crisp, chunky pixels.
"""
import random

import numpy as np
from PIL import Image

TILE = 24          # logical tile size
SCALE = 2          # output scale -> 48 px tiles for RPG Maker MV


def rgba(c, a=255):
    """'#rrggbb' / (r,g,b) / (r,g,b,a) -> (r,g,b,a)."""
    if c is None:
        return (0, 0, 0, 0)
    if isinstance(c, str):
        c = c.lstrip('#')
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)
    if len(c) == 3:
        return (c[0], c[1], c[2], a)
    return tuple(c)


def mix(c1, c2, t):
    a, b = rgba(c1), rgba(c2)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def shade(c, f):
    """f < 1 darkens, f > 1 lightens (towards white)."""
    r, g, b, a = rgba(c)
    if f <= 1:
        return (int(r * f), int(g * f), int(b * f), a)
    t = f - 1
    return (int(r + (255 - r) * t), int(g + (255 - g) * t), int(b + (255 - b) * t), a)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), dtype=np.uint8)

    # -- basic pixels -------------------------------------------------------
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            col = rgba(c)
            if col[3] == 255 or col[3] == 0:
                self.a[y, x] = col
            else:  # alpha blend
                base = self.a[y, x].astype(float)
                al = col[3] / 255.0
                out = base[:3] * (1 - al) + np.array(col[:3]) * al
                self.a[y, x, :3] = out.astype(np.uint8)
                self.a[y, x, 3] = max(int(base[3]), col[3])

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return tuple(int(v) for v in self.a[y, x])
        return (0, 0, 0, 0)

    def opaque(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.a[y, x, 3] > 0

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c)

    def frame(self, x, y, w, h, c):
        self.hline(x, y, w, c)
        self.hline(x, y + h - 1, w, c)
        self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c)

    def hline(self, x, y, w, c):
        for xx in range(x, x + w):
            self.px(xx, y, c)

    def vline(self, x, y, h, c):
        for yy in range(y, y + h):
            self.px(x, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, c):
        """Filled ellipse centred on (cx, cy) (floats allowed)."""
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                dx = (x + 0.5 - cx) / max(rx, 0.01)
                dy = (y + 0.5 - cy) / max(ry, 0.01)
                if dx * dx + dy * dy <= 1.0:
                    self.px(x, y, c)

    def round_rect(self, x, y, w, h, c, r=1):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                cx = min(xx - x, x + w - 1 - xx)
                cy = min(yy - y, y + h - 1 - yy)
                if cx < r and cy < r and (r - cx) + (r - cy) > r + 0:
                    if (r - cx - 0.5) ** 2 + (r - cy - 0.5) ** 2 > r * r:
                        continue
                self.px(xx, yy, c)

    def ascii(self, rows, cmap, x=0, y=0):
        """Draw ASCII art.  '.' and ' ' are transparent; other chars via cmap."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in '. ':
                    continue
                if ch not in cmap:
                    raise KeyError('ascii colour %r not in map' % ch)
                if cmap[ch] is not None:
                    self.px(x + i, y + j, cmap[ch])

    def blit(self, other, x, y):
        for yy in range(other.h):
            for xx in range(other.w):
                c = other.a[yy, xx]
                if c[3]:
                    self.px(x + xx, y + yy, tuple(int(v) for v in c))

    def paste(self, other, x, y):
        """Copy including transparency (overwrites)."""
        for yy in range(other.h):
            for xx in range(other.w):
                tx, ty = x + xx, y + yy
                if 0 <= tx < self.w and 0 <= ty < self.h:
                    self.a[ty, tx] = other.a[yy, xx]

    def crop(self, x, y, w, h):
        c = Canvas(w, h)
        c.a[:, :] = self.a[y:y + h, x:x + w]
        return c

    def flipped(self):
        c = Canvas(self.w, self.h)
        c.a = self.a[:, ::-1].copy()
        return c

    def copy(self):
        c = Canvas(self.w, self.h)
        c.a = self.a.copy()
        return c

    def outline(self, c, diagonal=False, only_where=None):
        """Draw an outline in transparent pixels bordering opaque ones."""
        col = rgba(c)
        mask = self.a[:, :, 3] > 0
        out = np.zeros_like(mask)
        offs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonal:
            offs += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in offs:
            sh = np.zeros_like(mask)
            ys = slice(max(dy, 0), self.h + min(dy, 0))
            yd = slice(max(-dy, 0), self.h + min(-dy, 0))
            xs = slice(max(dx, 0), self.w + min(dx, 0))
            xd = slice(max(-dx, 0), self.w + min(-dx, 0))
            sh[ys, xs] = mask[yd, xd]
            out |= sh
        out &= ~mask
        if only_where is not None:
            out &= only_where
        self.a[out] = col

    def selout(self, factor=0.55):
        """Outline every opaque region with a darker copy of its own colour."""
        mask = self.a[:, :, 3] > 0
        src = self.a.copy()
        for y in range(self.h):
            for x in range(self.w):
                if mask[y, x]:
                    continue
                best = None
                for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < self.w and 0 <= yy < self.h and mask[yy, xx]:
                        best = src[yy, xx]
                        break
                if best is not None:
                    self.a[y, x] = shade(tuple(int(v) for v in best), factor)

    def recolor(self, mapping):
        """mapping: {old_rgba: new_rgba}"""
        for old, new in mapping.items():
            o = np.array(rgba(old), dtype=np.uint8)
            m = np.all(self.a == o, axis=2)
            self.a[m] = rgba(new)

    def image(self, scale=SCALE):
        img = Image.fromarray(self.a, 'RGBA')
        if scale != 1:
            img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return img

    def save(self, path, scale=SCALE):
        self.image(scale).save(path)


def rng(seed):
    return random.Random(seed)


def speckle(cv, x, y, w, h, colors, density, seed, avoid=None):
    """Randomly sprinkle single pixels of the given colours."""
    r = rng(seed)
    n = int(w * h * density)
    for _ in range(n):
        xx, yy = x + r.randrange(w), y + r.randrange(h)
        if avoid and avoid(xx, yy):
            continue
        cv.px(xx, yy, r.choice(colors))
