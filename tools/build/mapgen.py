"""Paint RPG Maker MV maps from code: ground kinds, rooms, stamped objects.

Layers used:
  z0  base ground / floor / water / walls (autotiles)
  z1  ground overlays (paths, plaza, fields...) - autotiles with transparent edges
  z2  objects (B-E tiles)
  z3  second object layer (used automatically when z2 is taken)
  z4  shadows, z5 regions
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'art'))
from autotile import floor_shape, wall_shape  # noqa: E402

META = json.load(open(os.path.join(HERE, 'tileset_meta.json'), encoding='utf-8'))
TILESETS = json.load(open(os.path.join(HERE, 'tilesets.json'), encoding='utf-8'))


class MapPainter:
    def __init__(self, w, h, tileset='outside'):
        self.w, self.h = w, h
        self.meta = META[tileset]
        self.tileset_id = 1 if tileset == 'outside' else 2
        self.flags = TILESETS[self.tileset_id - 1]['flags']
        self.kind = [[[None] * w for _ in range(h)] for _ in range(2)]   # z0, z1 autotile kinds
        self.raw = [[[0] * w for _ in range(h)] for _ in range(4)]       # explicit tile ids per z
        self.shadow = [[0] * w for _ in range(h)]
        self.region = [[0] * w for _ in range(h)]

    # -- ground ---------------------------------------------------------------
    def fill(self, kind, z=0):
        for y in range(self.h):
            for x in range(self.w):
                self.kind[z][y][x] = kind

    def rect(self, x, y, w, h, kind, z=1):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.kind[z][yy][xx] = kind

    def cells(self, pts, kind, z=1):
        for (x, y) in pts:
            if 0 <= x < self.w and 0 <= y < self.h:
                self.kind[z][y][x] = kind

    def hpath(self, x0, x1, y, kind='dirt', width=1):
        a, b = min(x0, x1), max(x0, x1)
        self.rect(a, y, b - a + 1, width, kind)

    def vpath(self, x, y0, y1, kind='dirt', width=1):
        a, b = min(y0, y1), max(y0, y1)
        self.rect(x, a, width, b - a + 1, kind)

    # -- objects ----------------------------------------------------------------
    def stamp(self, name, x, y, z=None):
        ids = self.meta[name]
        for j, row in enumerate(ids):
            for i, tid in enumerate(row):
                xx, yy = x + i, y + j
                if not (0 <= xx < self.w and 0 <= yy < self.h):
                    continue
                zz = z
                if zz is None:
                    zz = 2 if self.raw[2][yy][xx] == 0 else 3
                self.raw[zz][yy][xx] = tid
        return (x, y, len(ids[0]), len(ids))

    def size(self, name):
        ids = self.meta[name]
        return len(ids[0]), len(ids)

    def put(self, x, y, z, tile_id):
        self.raw[z][y][x] = tile_id

    def clear_objects(self, x, y, w=1, h=1):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.raw[2][yy][xx] = 0
                self.raw[3][yy][xx] = 0

    # -- interiors --------------------------------------------------------------
    def room(self, x, y, w, h, wall, floor, wall_h=2):
        """A room whose outer box is (x,y,w,h) including walls.
        Top: 1 row wall-top + wall_h rows of wall face.  Sides/bottom: wall-top."""
        top = ('walltop', wall)
        side = ('wallside', wall)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                edge = xx in (x, x + w - 1) or yy in (y, y + h - 1)
                if edge:
                    self.kind[0][yy][xx] = top
                elif yy <= y + wall_h:
                    self.kind[0][yy][xx] = side
                else:
                    self.kind[0][yy][xx] = floor
        return (x + 1, y + 1 + wall_h, w - 2, h - 2 - wall_h)   # walkable floor rect

    def door_gap(self, x, y, floor):
        """open the bottom wall at (x,y) and lay a doormat"""
        self.kind[0][y][x] = floor
        self.stamp('doormat', x, y)

    def wall_block(self, x, y, w, h, wall, wall_h=2):
        """an inner partition wall seen in 3/4 view: top rows are wall-top, then wall_h face rows"""
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if yy < y + h - wall_h:
                    self.kind[0][yy][xx] = ('walltop', wall)
                else:
                    self.kind[0][yy][xx] = ('wallside', wall)

    def void(self, x, y, w, h):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.kind[0][yy][xx] = None
                self.kind[1][yy][xx] = None

    # -- resolve ----------------------------------------------------------------
    def _base_id(self, kind):
        if kind is None:
            return 0
        if isinstance(kind, tuple):
            w = self.meta['wall_' + kind[1]]
            return w['top'] if kind[0] == 'walltop' else w['side']
        return self.meta[kind]

    def _tile(self, z, x, y):
        k = self.kind[z][y][x]
        if k is None:
            return 0
        base = self._base_id(k)
        if base < 2048:          # A5 static tile
            return base

        def same(dx, dy):
            xx, yy = x + dx, y + dy
            if not (0 <= xx < self.w and 0 <= yy < self.h):
                return True
            return self.kind[z][yy][xx] == k

        if isinstance(k, tuple) and k[0] == 'wallside':
            return base + wall_shape(same(-1, 0), same(1, 0), same(0, -1), same(0, 1))
        return base + floor_shape(same)

    def auto_shadows(self):
        """MV-style shadow on floor tiles right of a wall-top tile."""
        for y in range(self.h):
            for x in range(1, self.w):
                k = self.kind[0][y][x]
                left = self.kind[0][y][x - 1]
                if isinstance(left, tuple) and not isinstance(k, tuple) and k is not None:
                    above = self.kind[0][y - 1][x - 1] if y > 0 else None
                    if isinstance(above, tuple):
                        self.shadow[y][x] = 5

    def data(self):
        w, h = self.w, self.h
        out = [0] * (w * h * 6)
        for y in range(h):
            for x in range(w):
                for z in (0, 1):
                    tid = self.raw[z][y][x] or self._tile(z, x, y)
                    out[(z * h + y) * w + x] = tid
                for z in (2, 3):
                    out[(z * h + y) * w + x] = self.raw[z][y][x]
                out[(4 * h + y) * w + x] = self.shadow[y][x]
                out[(5 * h + y) * w + x] = self.region[y][x]
        return out

    # -- passability (mirrors Game_Map.checkPassage) ------------------------------
    def passable(self, x, y, data=None):
        data = data or self.data()
        w, h = self.w, self.h
        if not (0 <= x < w and 0 <= y < h):
            return False
        for z in (3, 2, 1, 0):
            tid = data[(z * h + y) * w + x]
            f = self.flags[tid]
            if f & 0x10:
                continue
            if (f & 0x0F) == 0:
                return True
            if (f & 0x0F) == 0x0F:
                return False
        return False
