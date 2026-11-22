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

# Objects that give off light, read by LifeSong_Atmosphere.js from the map note.
# name -> list of (dx, dy, radius, colour, strength, flicker): the glow's centre in tiles
# from the object's top-left corner.  Windows on an inside wall get a sun shaft instead.
WARM, CANDLE, COOL, MOON = '#ffd894', '#ff9a52', '#cfe6ff', '#9fc0ff'
OBJECT_LIGHTS = {
    # village
    'grandpa_house': [(0.96, 2.83, 1.6, WARM, 0.7, False), (4.04, 2.83, 1.6, WARM, 0.7, False)],
    'house_red': [(2.71, 2.79, 1.6, WARM, 0.7, False)],
    'house_brick': [(0.92, 2.79, 1.6, WARM, 0.7, False)],
    'house_wood': [(2.71, 2.79, 1.6, WARM, 0.7, False)],
    'school_village': [(x, 2.67, 1.3, WARM, 0.5, False) for x in (0.83, 2.08, 5.0, 6.25)],
    'lantern_post': [(0.4, 0.7, 2.0, CANDLE, 1.0, True)],
    'lantern_string': [(0.5, 0.6, 1.5, CANDLE, 0.9, True)],
    # city
    'streetlamp': [(0.52, 0.44, 2.8, '#ffe6a8', 1.0, False)],
    'cafe': [(1.04, 2.92, 2.6, '#ffc27a', 0.9, False), (0.92, 0.63, 1.2, WARM, 0.5, False),
             (3.08, 0.63, 1.2, WARM, 0.5, False)],
    'shop_a': [(1.17, 4.25, 2.4, WARM, 0.7, False)],
    'shop_b': [(1.17, 4.25, 2.4, '#ffc8d8', 0.7, False)],
    'shop_c': [(1.17, 4.25, 2.2, WARM, 0.5, False)],
    'convenience': [(1.17, 4.25, 2.8, COOL, 0.9, False)],
    'vending': [(0.5, 1.0, 1.6, COOL, 0.8, False)],
    'bus_stop': [(0.5, 0.6, 1.5, COOL, 0.6, False)],
    'subway': [(1.5, 0.9, 2.0, '#bcdcff', 0.6, False)],
    'neon_live': [(1.0, 0.5, 2.4, '#ff5fa8', 1.0, True)],
    'neon_bar': [(1.0, 0.5, 2.4, '#4fd8ff', 1.0, True)],
    # inside
    'window_night': [(0.5, 0.5, 1.8, MOON, 0.6, False)],
    'tv': [(0.5, 0.5, 1.4, '#a8d4ff', 0.7, True)],
    'heater': [(0.5, 0.6, 1.8, '#ff8a40', 0.9, True)],
    'desk': [(1.55, 0.2, 1.8, '#ffe4a8', 0.8, False)],
    'radio': [(0.5, 0.5, 0.9, '#ffcf80', 0.5, False)],
    'spotlight': [(0.5, 2.2, 2.6, '#fff2c8', 1.0, False)],
    'floor_lamp': [(0.5, 0.5, 2.4, '#ffe0a0', 0.9, False)],
    'table_lamp': [(0.5, 0.2, 1.6, '#ffe0a0', 0.8, False)],
    'string_lights': [(0.5, 0.45, 1.5, '#ffd6c8', 0.7, True)],
}
SUN_WINDOWS = ('window_wall', 'window_lattice')


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
        self.notes = []          # map note lines (atmosphere, lights) for LifeSong_Atmosphere.js

    # -- atmosphere ---------------------------------------------------------------
    def atmos(self, effects, switch=0):
        """effects: 'leaves clouds' ...; switch: only while this switch is ON (0 = always)"""
        self.notes.append('<atmos%s: %s>' % ('@%d' % switch if switch else '', effects))

    def light(self, x, y, radius, colour, strength=1.0, flicker=False, switch=0):
        self.notes.append('<light%s: %g %g %g %s %g%s>' % (
            '@%d' % switch if switch else '', round(x, 2), round(y, 2), radius, colour, strength,
            ' flicker' if flicker else ''))

    def beam(self, x, y, length=4):
        self.notes.append('<beam: %d %d %d>' % (x, y, length))

    def vignette(self, v):
        self.notes.append('<vignette: %g>' % v)

    def note(self):
        return '\n'.join(self.notes)

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
        for (dx, dy, r, col, k, fl) in OBJECT_LIGHTS.get(name, ()):
            self.light(x + dx, y + dy, r, col, k, fl)
        if name in SUN_WINDOWS:
            self.beam(x, y)
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
