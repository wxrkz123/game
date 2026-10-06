"""Minimal re-implementation of RPG Maker MV's tile drawing, for map previews."""
from PIL import Image

FLOOR = [
    [[2,4],[1,4],[2,3],[1,3]],[[2,0],[1,4],[2,3],[1,3]],
    [[2,4],[3,0],[2,3],[1,3]],[[2,0],[3,0],[2,3],[1,3]],
    [[2,4],[1,4],[2,3],[3,1]],[[2,0],[1,4],[2,3],[3,1]],
    [[2,4],[3,0],[2,3],[3,1]],[[2,0],[3,0],[2,3],[3,1]],
    [[2,4],[1,4],[2,1],[1,3]],[[2,0],[1,4],[2,1],[1,3]],
    [[2,4],[3,0],[2,1],[1,3]],[[2,0],[3,0],[2,1],[1,3]],
    [[2,4],[1,4],[2,1],[3,1]],[[2,0],[1,4],[2,1],[3,1]],
    [[2,4],[3,0],[2,1],[3,1]],[[2,0],[3,0],[2,1],[3,1]],
    [[0,4],[1,4],[0,3],[1,3]],[[0,4],[3,0],[0,3],[1,3]],
    [[0,4],[1,4],[0,3],[3,1]],[[0,4],[3,0],[0,3],[3,1]],
    [[2,2],[1,2],[2,3],[1,3]],[[2,2],[1,2],[2,3],[3,1]],
    [[2,2],[1,2],[2,1],[1,3]],[[2,2],[1,2],[2,1],[3,1]],
    [[2,4],[3,4],[2,3],[3,3]],[[2,4],[3,4],[2,1],[3,3]],
    [[2,0],[3,4],[2,3],[3,3]],[[2,0],[3,4],[2,1],[3,3]],
    [[2,4],[1,4],[2,5],[1,5]],[[2,0],[1,4],[2,5],[1,5]],
    [[2,4],[3,0],[2,5],[1,5]],[[2,0],[3,0],[2,5],[1,5]],
    [[0,4],[3,4],[0,3],[3,3]],[[2,2],[1,2],[2,5],[1,5]],
    [[0,2],[1,2],[0,3],[1,3]],[[0,2],[1,2],[0,3],[3,1]],
    [[2,2],[3,2],[2,3],[3,3]],[[2,2],[3,2],[2,1],[3,3]],
    [[2,4],[3,4],[2,5],[3,5]],[[2,0],[3,4],[2,5],[3,5]],
    [[0,4],[1,4],[0,5],[1,5]],[[0,4],[3,0],[0,5],[1,5]],
    [[0,2],[3,2],[0,3],[3,3]],[[0,2],[1,2],[0,5],[1,5]],
    [[0,4],[3,4],[0,5],[3,5]],[[2,2],[3,2],[2,5],[3,5]],
    [[0,2],[3,2],[0,5],[3,5]],[[0,0],[1,0],[0,1],[1,1]]
]
WALL = [
    [[2,2],[1,2],[2,1],[1,1]],[[0,2],[1,2],[0,1],[1,1]],
    [[2,0],[1,0],[2,1],[1,1]],[[0,0],[1,0],[0,1],[1,1]],
    [[2,2],[3,2],[2,1],[3,1]],[[0,2],[3,2],[0,1],[3,1]],
    [[2,0],[3,0],[2,1],[3,1]],[[0,0],[3,0],[0,1],[3,1]],
    [[2,2],[1,2],[2,3],[1,3]],[[0,2],[1,2],[0,3],[1,3]],
    [[2,0],[1,0],[2,3],[1,3]],[[0,0],[1,0],[0,3],[1,3]],
    [[2,2],[3,2],[2,3],[3,3]],[[0,2],[3,2],[0,3],[3,3]],
    [[2,0],[3,0],[2,3],[3,3]],[[0,0],[3,0],[0,3],[3,3]]
]

TW = 48


def load_sheets(names, imgdir):
    sheets = []
    for n in names:
        if n:
            try:
                sheets.append(Image.open('%s/%s.png' % (imgdir, n)).convert('RGBA'))
            except FileNotFoundError:
                sheets.append(None)
        else:
            sheets.append(None)
    return sheets


def draw_tile(out, sheets, tile_id, dx, dy, frame=0):
    if tile_id <= 0:
        return
    h1 = w1 = TW // 2
    if tile_id >= 2048:  # autotile
        kind = (tile_id - 2048) // 48
        shape = (tile_id - 2048) % 48
        tx, ty = kind % 8, kind // 8
        table = FLOOR
        if tile_id < 2816:
            setn = 0
            wsi = [0, 1, 2, 1][frame % 4]
            if kind == 0:
                bx, by = wsi * 2, 0
            elif kind == 1:
                bx, by = wsi * 2, 3
            elif kind == 2:
                bx, by = 6, 0
            elif kind == 3:
                bx, by = 6, 3
            else:
                bx = (tx // 4) * 8
                by = ty * 6 + (tx // 2) % 2 * 3
                if kind % 2 == 0:
                    bx += wsi * 2
                else:
                    bx += 6
                    by += frame % 3
                    table = None  # waterfall not supported in preview
        elif tile_id < 4352:
            setn = 1
            bx, by = tx * 2, (ty - 2) * 3
        elif tile_id < 5888:
            setn = 2
            bx, by = tx * 2, (ty - 6) * 2
            table = WALL
        else:
            setn = 3
            bx = tx * 2
            import math
            by = math.floor((ty - 10) * 2.5 + (0.5 if ty % 2 == 1 else 0))
            if ty % 2 == 1:
                table = WALL
        src = sheets[setn]
        if src is None or table is None:
            return
        q = table[shape]
        for i in range(4):
            qsx, qsy = q[i]
            sx1 = (bx * 2 + qsx) * w1
            sy1 = (by * 2 + qsy) * h1
            piece = src.crop((sx1, sy1, sx1 + w1, sy1 + h1))
            out.alpha_composite(piece, (dx + (i % 2) * w1, dy + (i // 2) * h1))
    else:
        if 1536 <= tile_id < 2048:
            setn = 4
            idx = tile_id - 1536
            sx = (idx % 8) * TW
            sy = (idx // 8) * TW
        else:
            setn = 5 + tile_id // 256
            sx = ((tile_id // 128) % 2 * 8 + tile_id % 8) * TW
            sy = ((tile_id % 256) // 8 % 16) * TW
        src = sheets[setn] if setn < len(sheets) else None
        if src is None:
            return
        out.alpha_composite(src.crop((sx, sy, sx + TW, sy + TW)), (dx, dy))


def render_map(mp, tileset, imgdir, frame=0, flags=None, events=None, charimgs=None):
    w, h = mp['width'], mp['height']
    data = mp['data']
    sheets = load_sheets(tileset['tilesetNames'], imgdir)
    flags = tileset['flags']
    lower = Image.new('RGBA', (w * TW, h * TW), (0, 0, 0, 255))
    upper = Image.new('RGBA', (w * TW, h * TW), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            for z in range(4):
                tid = data[(z * h + y) * w + x]
                if not tid:
                    continue
                is_star = flags[tid] & 0x10
                target = upper if is_star else lower
                draw_tile(target, sheets, tid, x * TW, y * TW, frame)
            sh = data[(4 * h + y) * w + x]
            if sh:
                for i in range(4):
                    if sh & (1 << i):
                        ov = Image.new('RGBA', (TW // 2, TW // 2), (0, 0, 0, 128))
                        lower.alpha_composite(ov, (x * TW + (i % 2) * TW // 2, y * TW + (i // 2) * TW // 2))
    if events and charimgs:
        for ev in events:
            if not ev:
                continue
            pg = ev['pages'][0]
            img = pg['image']
            if img['tileId']:
                draw_tile(lower, sheets, img['tileId'], ev['x'] * TW, ev['y'] * TW, frame)
            elif img['characterName']:
                sprite = charimgs(img['characterName'], img['characterIndex'], img['direction'], img['pattern'])
                if sprite:
                    big = img['characterName'].startswith('$') or img['characterName'].startswith('!$')
                    obj = img['characterName'].startswith('!')
                    sw, sh_ = sprite.size
                    px = ev['x'] * TW + TW // 2 - sw // 2
                    py = ev['y'] * TW + TW - sh_ - (0 if obj else 6)
                    lower.alpha_composite(sprite, (px, max(py, 0)))
    lower.alpha_composite(upper)
    return lower
