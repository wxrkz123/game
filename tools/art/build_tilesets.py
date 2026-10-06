"""Assemble the tileset images for 《余音》 and emit:
  YuYin/img/tilesets/*.png
  tools/build/tileset_meta.json   (names -> tile ids, used by the map builder)
  tools/build/tilesets.json       (data for data/Tilesets.json)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pixlib import Canvas, TILE
from autotile import floor_block
from materials import make_materials
from walls import make_walls
import objects_outside as OO
import objects_inside as OI

T = TILE
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
IMG = os.path.join(ROOT, 'YuYin', 'img', 'tilesets')
BUILD = os.path.join(ROOT, 'tools', 'build')

FLAG = {'o': 0x0, 'x': 0xF, '*': 0x10, 'b': 0x40, 'c': 0x80 | 0xF}
A1_BASE, A2_BASE, A3_BASE, A4_BASE, A5_BASE = 2048, 2816, 4352, 5888, 1536


class NormalSheet:
    """B/C/D/E sheet: 16x16 tiles; ids 0-127 in the left half, 128-255 right."""

    def __init__(self, index):
        self.index = index            # 0=B,1=C,2=D,3=E
        self.base = index * 256
        self.cv = Canvas(16 * T, 16 * T)
        self.used = [[False] * 16 for _ in range(16)]
        if index == 0:
            self.used[0][0] = True    # B tile 0 must stay empty

    def tile_id(self, col, row):
        half = 1 if col >= 8 else 0
        return self.base + half * 128 + row * 8 + (col % 8)

    def place(self, w, h):
        for half in (0, 1):
            for row in range(16 - h + 1):
                for c0 in range(8 - w + 1):
                    col = half * 8 + c0
                    if all(not self.used[row + j][col + i] for j in range(h) for i in range(w)):
                        for j in range(h):
                            for i in range(w):
                                self.used[row + j][col + i] = True
                        return col, row
        return None


def pack_objects(objects, sheet_indices, flags, meta):
    """objects: dict name->fn.  Packs larger objects first."""
    drawn = []
    for name, fn in objects.items():
        cv, fl = fn()
        w, h = len(fl[0]), len(fl)
        assert cv.w == w * T and cv.h == h * T, name
        drawn.append((name, cv, fl, w, h))
    drawn.sort(key=lambda d: (-d[4] * d[3], -d[4]))
    sheets = [NormalSheet(i) for i in sheet_indices]
    for name, cv, fl, w, h in drawn:
        for sh in sheets:
            pos = sh.place(w, h)
            if pos:
                break
        else:
            raise RuntimeError('no room for ' + name)
        col, row = pos
        sh.cv.paste(cv, col * T, row * T)
        ids = []
        for j in range(h):
            r_ = []
            for i in range(w):
                tid = sh.tile_id(col + i, row + j)
                flags[tid] = FLAG[fl[j][i]]
                r_.append(tid)
            ids.append(r_)
        meta[name] = ids
    return sheets


def a2_sheet(mats, names, flags, meta, impassable=()):
    sheet = Canvas(8 * 2 * T, 4 * 3 * T)
    for k, n in enumerate(names):
        blk = floor_block(mats[n])
        sheet.paste(blk, (k % 8) * 2 * T, (k // 8) * 3 * T)
        kind = 16 + k
        base = A1_BASE + kind * 48
        for s in range(48):
            flags[base + s] = 0xF if n in impassable else 0x0
        meta[n] = base
    return sheet


def a1_sheet(mat, flags, meta, name='water'):
    """A1 with only kind 0 (animated water, 3 frames)."""
    sheet = Canvas(8 * 2 * T, 4 * 3 * T)
    for f in range(3):
        sheet.paste(floor_block(mat, f), f * 2 * T, 0)
    for s in range(48):
        flags[A1_BASE + s] = 0xF | 0x200
    meta[name] = A1_BASE
    return sheet


def a4_sheet(walls, flags, meta):
    sheet = Canvas(8 * 2 * T, 15 * T)
    for i, (name, top_mat, face) in enumerate(walls):
        sheet.paste(floor_block(top_mat), i * 2 * T, 0)
        sheet.paste(face, i * 2 * T, 3 * T)
        top_id = A4_BASE + i * 48
        side_id = A4_BASE + (8 + i) * 48
        for s in range(48):
            flags[top_id + s] = 0xF
            flags[side_id + s] = 0xF
        meta['wall_' + name] = {'top': top_id, 'side': side_id}
    return sheet


def a5_sheet(entries, flags, meta):
    """entries: list of (name, colour or canvas, flag)."""
    sheet = Canvas(8 * T, 16 * T)
    for i, (name, c, fl) in enumerate(entries):
        x, y = (i % 8) * T, (i // 8) * T
        if isinstance(c, Canvas):
            sheet.paste(c, x, y)
        else:
            sheet.rect(x, y, T, T, c)
        tid = A5_BASE + i
        flags[tid] = FLAG[fl]
        meta[name] = tid
    return sheet


def build():
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    mats = make_materials()
    tilesets = []
    all_meta = {}

    # ---------------- Outside (village + city) -----------------------------
    flags = [0] * 8192
    flags[0] = 0x10
    meta = {}
    a1 = a1_sheet(mats['water'], flags, meta)
    a2 = a2_sheet(mats, ['grass', 'meadow', 'dirt', 'cobble', 'farmland', 'sand', 'leaves', 'snow',
                         'asphalt', 'sidewalk', 'plaza', 'deck'], flags, meta)
    a5 = a5_sheet([('void', '#000000', 'x'), ('night_void', '#141826', 'x')], flags, meta)
    village_props = {k: v for k, v in OO.OBJECTS.items()
                     if k not in ('grandpa_house', 'house_red', 'house_brick', 'house_wood',
                                  'school_village', 'shed')}
    buildings = {k: OO.OBJECTS[k] for k in ('grandpa_house', 'house_red', 'house_brick', 'house_wood',
                                            'school_village', 'shed')}
    sB = pack_objects(village_props, [0], flags, meta)
    sC = pack_objects(buildings, [1], flags, meta)
    sD = pack_objects(OO.CITY_OBJECTS, [2], flags, meta)
    names = ['YY_Outside_A1', 'YY_Outside_A2', '', '', 'YY_Outside_A5', 'YY_Outside_B', 'YY_Outside_C',
             'YY_Outside_D', '']
    a1.save(os.path.join(IMG, names[0] + '.png'))
    a2.save(os.path.join(IMG, names[1] + '.png'))
    a5.save(os.path.join(IMG, names[4] + '.png'))
    sB[0].cv.save(os.path.join(IMG, names[5] + '.png'))
    sC[0].cv.save(os.path.join(IMG, names[6] + '.png'))
    sD[0].cv.save(os.path.join(IMG, names[7] + '.png'))
    tilesets.append({'id': 1, 'flags': flags, 'mode': 1, 'name': '屋外（村庄与城市）', 'note': '',
                     'tilesetNames': names})
    all_meta['outside'] = meta

    # ---------------- Inside -----------------------------------------------
    flags = [0] * 8192
    flags[0] = 0x10
    meta = {}
    a2 = a2_sheet(mats, ['wood_floor', 'old_floor', 'tile_floor', 'school_floor', 'carpet_red', 'carpet_blue',
                         'concrete', 'stage', 'tatami'], flags, meta)
    a4 = a4_sheet(make_walls(), flags, meta)
    a5 = a5_sheet([('void', '#000000', 'x')], flags, meta)
    sB = pack_objects(OI.OBJECTS, [0, 1], flags, meta)
    names = ['', 'YY_Inside_A2', '', 'YY_Inside_A4', 'YY_Inside_A5', 'YY_Inside_B', 'YY_Inside_C', '', '']
    a2.save(os.path.join(IMG, names[1] + '.png'))
    a4.save(os.path.join(IMG, names[3] + '.png'))
    a5.save(os.path.join(IMG, names[4] + '.png'))
    sB[0].cv.save(os.path.join(IMG, names[5] + '.png'))
    sB[1].cv.save(os.path.join(IMG, names[6] + '.png'))
    tilesets.append({'id': 2, 'flags': flags, 'mode': 1, 'name': '室内', 'note': '', 'tilesetNames': names})
    all_meta['inside'] = meta

    with open(os.path.join(BUILD, 'tileset_meta.json'), 'w') as f:
        json.dump(all_meta, f, ensure_ascii=False, indent=1)
    with open(os.path.join(BUILD, 'tilesets.json'), 'w') as f:
        json.dump(tilesets, f, ensure_ascii=False)
    print('tilesets built:', [t['name'] for t in tilesets])


if __name__ == '__main__':
    build()
