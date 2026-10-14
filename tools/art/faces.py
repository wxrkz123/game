"""Dialogue portraits (img/faces) drawn from the same Spec as the walking sprites.

Each portrait is 72 x 72 logical px (144 x 144 in game).  A face sheet holds
up to 8 portraits, 4 across and 2 down (576 x 288), the RPG Maker MV layout.
"""
import math

from pixlib import Canvas, rgba, shade
from chars import OUT, EYE
from cast import CAST
from face_sheets import SHEETS
import palette as P

SIZE = 72
IRIS = '#6a4636'
MOUTH = '#b8615a'

GEOM = {
    #           head centre / radii     eyes: y offset, gap, w, h     shoulders: y, half width
    'adult': dict(cx=36, cy=33, rx=16, ry=17, ey=3, eg=6, ew=3, eh=5, sy=53, sw=22),
    'child': dict(cx=36, cy=35, rx=17, ry=17, ey=3, eg=6, ew=4, eh=6, sy=56, sw=17),
    'old':   dict(cx=36, cy=33, rx=16, ry=17, ey=3, eg=6, ew=4, eh=2, sy=53, sw=22),
}


# ---------------------------------------------------------------------------
# shapes
# ---------------------------------------------------------------------------

def _head_rows(g):
    """half widths of the head shape per row: round on top, a soft chin below."""
    cx, cy, rx, ry = g['cx'], g['cy'], g['rx'], g['ry']
    rows = {}
    for y in range(cy - ry, cy + ry + 1):
        t = (y + 0.5 - cy) / ry
        if abs(t) > 1:
            continue
        w = rx * math.sqrt(1 - t * t)
        if t > 0:
            w *= 1 - 0.22 * t
        rows[y] = (int(round(cx - w)), int(round(cx + w)) - 1)
    return rows


def _fill(cv, rows, c, ymin=-999, ymax=999):
    for y, (a, b) in rows.items():
        if ymin <= y <= ymax:
            cv.hline(a, y, b - a + 1, c)


def _ellipse_rows(cx, cy, rx, ry):
    rows = {}
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        t = (y + 0.5 - cy) / ry
        if abs(t) >= 1:
            continue
        w = rx * math.sqrt(1 - t * t)
        rows[y] = (int(round(cx - w)), int(round(cx + w)) - 1)
    return rows


# ---------------------------------------------------------------------------
# body
# ---------------------------------------------------------------------------

def _body(cv, sp, g):
    cx, sy, sw = g['cx'], g['sy'], g['sw']
    skin = sp.skin
    coat = sp.coat if isinstance(sp.coat, str) else None
    outer = coat or sp.top
    # neck
    cv.rect(cx - 4, g['cy'] + g['ry'] - 4, 8, sy - (g['cy'] + g['ry'] - 4) + 2, shade(skin, 0.9))
    # shoulders: a rounded block down to the bottom edge
    for y in range(sy, SIZE):
        k = y - sy
        inset = max(0, 7 - k * 2) if k < 4 else 0
        w = sw - inset
        cv.hline(cx - w, y, 2 * w, outer)
    # side shading
    for y in range(sy + 3, SIZE):
        cv.px(cx + sw - 1, y, shade(outer, 0.82))
        cv.px(cx + sw - 2, y, shade(outer, 0.88))
    if coat:
        # open coat showing the shirt underneath
        for y in range(sy, SIZE):
            w = min(6, 2 + (y - sy) // 2)
            cv.hline(cx - w, y, 2 * w, sp.top)
        for y in range(sy, SIZE):
            w = min(6, 2 + (y - sy) // 2)
            cv.px(cx - w - 1, y, shade(coat, 0.75))
            cv.px(cx + w, y, shade(coat, 0.75))
    else:
        trim = sp.top2 if sp.top2 and sp.top2 != sp.top else shade(sp.top, 0.85)
        # round collar
        cv.hline(cx - 6, sy, 12, trim)
        cv.hline(cx - 5, sy + 1, 10, trim)
        cv.px(cx - 6, sy + 1, trim)
        cv.px(cx + 5, sy + 1, trim)
    # neck opening
    cv.hline(cx - 3, sy, 6, shade(skin, 0.85))
    cv.hline(cx - 2, sy + 1, 4, shade(skin, 0.85))


def _acc_body(cv, sp, g):
    cx, sy, sw = g['cx'], g['sy'], g['sw']
    acc, col = sp.acc, sp.acc_col
    if 'stripe' in acc:
        sc = col.get('stripe', '#3f6fb0')
        for y in range(sy + 3, SIZE):
            cv.px(cx - sw + 3, y, sc)
            cv.px(cx + sw - 4, y, sc)
        cv.vline(cx, sy + 2, SIZE - sy - 2, shade(sp.top, 0.85))
    if 'apron' in acc:
        ac = col.get('apron', P.WHITE)
        cv.rect(cx - 9, sy + 7, 18, SIZE - sy - 7, ac)
        cv.vline(cx - 9, sy + 1, 6, ac)
        cv.vline(cx + 8, sy + 1, 6, ac)
        cv.hline(cx - 9, sy + 10, 18, shade(ac, 0.9))
    if 'tie' in acc:
        tc = col.get('tie_col', '#d8302a')
        cv.hline(cx - 3, sy, 6, P.WHITE)
        cv.rect(cx - 1, sy + 1, 2, 3, tc)
        cv.rect(cx - 2, sy + 4, 4, 8, tc)
        cv.rect(cx - 1, sy + 12, 2, 1, tc)
    if 'guitar' in acc:
        gc = col.get('guitar', '#2e2a36')
        # strap across the chest and the neck of the gig bag over the shoulder
        for i in range(SIZE - sy):
            cv.px(cx - sw + 4 + i, sy + i, shade(gc, 1.25))
            cv.px(cx - sw + 5 + i, sy + i, gc)
        cv.rect(cx + sw - 6, sy - 10, 5, 13, gc)
        cv.hline(cx + sw - 6, sy - 6, 5, shade(gc, 1.35))
    if 'bag' in acc:
        bc = col.get('bag', '#8a5a3a')
        for i in range(SIZE - sy):
            cv.px(cx + sw - 6 - i // 2, sy + i, shade(bc, 0.85))
    if 'scarf' in acc:
        sc = col.get('scarf', '#d8302a')
        for y in range(sy - 4, sy + 3):
            w = 9 if y < sy + 1 else 8
            cv.hline(cx - w, y, 2 * w, sc)
        cv.hline(cx - 8, sy - 1, 16, shade(sc, 0.85))
        cv.rect(cx - 7, sy + 3, 4, 9, sc)
        cv.vline(cx - 5, sy + 3, 9, shade(sc, 0.85))
        cv.hline(cx - 7, sy + 11, 4, shade(sc, 1.3))
    if 'shawl' in acc:
        sc = col.get('shawl', '#8a6aa6')
        # a band over the shoulders, its two ends hanging down in front
        for y in range(sy - 1, SIZE):
            k = y - sy
            w = sp_w(g, k)
            if k < 5:
                cv.hline(cx - w, y, 2 * w, sc)
            else:
                cv.hline(cx - w, y, w - 4, sc)
                cv.hline(cx + 4, y, w - 4, sc)
        cv.hline(cx - sp_w(g, 4), sy + 4, 2 * sp_w(g, 4), shade(sc, 0.82))
        for y in range(sy + 5, SIZE):
            cv.px(cx - 5, y, shade(sc, 0.75))
            cv.px(cx + 4, y, shade(sc, 0.75))
        cv.ellipse(cx, sy + 2, 2, 2, col.get('hairpin', '#e8c860'))


def sp_w(g, k):
    return g['sw'] - (max(0, 7 - k * 2) if k < 4 else 0) + 1


# ---------------------------------------------------------------------------
# hair
# ---------------------------------------------------------------------------

def _hair_back(cv, sp, g):
    H = sp.hair
    lo = shade(H, 0.78)
    cx, cy, rx, ry = g['cx'], g['cy'], g['rx'], g['ry']
    st = sp.hair_style
    if st == 'bald':
        return
    if st == 'bun':
        cv.ellipse(cx, cy - ry - 1, 8, 6, H)
        cv.ellipse(cx - 2, cy - ry - 3, 3, 2, shade(H, 1.25))
    if st == 'buns':
        for sx in (-12, 12):
            cv.ellipse(cx + sx, cy - ry + 2, 6, 6, H)
            cv.ellipse(cx + sx - 2, cy - ry, 2, 2, shade(H, 1.25))
    if st == 'twintails':
        tie = sp.acc_col.get('tie', '#d8574f')
        for sx in (-1, 1):
            tx = cx + sx * (rx + 5)
            cv.ellipse(tx, cy + 9, 5.5, 13, H)
            cv.ellipse(tx, cy + 18, 4, 5, lo)
            cv.ellipse(cx + sx * (rx + 2), cy - 5, 3, 3, tie)
    if st == 'ponytail':
        tie = sp.acc_col.get('tie', '#d8574f')
        tx = cx + rx + 4
        cv.ellipse(tx, cy + 4, 5, 12, H)
        cv.ellipse(tx + 1, cy + 12, 3.5, 5, lo)
        cv.rect(cx + rx - 1, cy - 7, 4, 3, tie)
    depth = {'bob': cy + 11, 'long': SIZE, 'short': cy - 2}.get(st, cy + 1)
    rows = _ellipse_rows(cx, cy - 1, rx + 3, ry + 2)
    for y, (a, b) in rows.items():
        if y <= depth:
            cv.hline(a, y, b - a + 1, H)
    if st in ('bob', 'long'):
        for y in range(cy, depth + 1):
            w = rx + 3 + (1 if st == 'long' and y > cy + 12 else 0)
            if y in rows and y <= depth:
                continue
            cv.hline(cx - w, y, 2 * w, H)
        last = min(depth, SIZE - 1)
        cv.hline(cx - rx - 3, last, 2 * (rx + 3), lo)
        if st == 'bob':
            cv.hline(cx - rx - 2, last + 1, 2 * (rx + 2), lo)


def _hair_front(cv, sp, g):
    H = sp.hair
    hi = shade(H, 1.35)
    lo = shade(H, 0.78)
    cx, cy, rx, ry = g['cx'], g['cy'], g['rx'], g['ry']
    st, fr = sp.hair_style, sp.fringe
    top = cy - ry
    if st == 'bald':
        # tufts above the ears and a shiny scalp
        for sx in (-1, 1):
            cv.ellipse(cx + sx * (rx - 1), cy - 1, 3, 5, H)
            cv.ellipse(cx + sx * (rx - 1), cy - 3, 2, 2, shade(H, 1.08))
        cv.ellipse(cx - 6, top + 5, 3, 2, shade(sp.skin, 1.18))
        return
    hairline = top + 8 if fr != 'none' else top + 6
    cap = _ellipse_rows(cx, cy - 1, rx + 3, ry + 2)
    for y, (a, b) in cap.items():
        if y < hairline:
            cv.hline(a, y, b - a + 1, H)
    # sides framing the face
    side_to = {'short': cy - 1, 'bob': cy + 10, 'long': cy + 14}.get(st, cy + 6)
    if fr == 'none':
        side_to = cy - 2
    for y in range(hairline, side_to + 1):
        if y in cap:
            a, b = cap[y]
            cv.hline(a, y, 4, H)
            cv.hline(b - 3, y, 4, H)
    for y in range(cy + 1, side_to + 1):
        if y in cap:
            a, b = cap[y]
            cv.px(a + 3, y, lo)
            cv.px(b - 3, y, lo)
    fb = cy - 3                     # bottom of the fringe
    if fr in ('full', 'spiky'):
        for y in range(hairline, fb + 1):
            a, b = cap.get(y, (cx - rx, cx + rx))
            cv.hline(a + 2, y, b - a - 3, H)
        step = 4 if fr == 'full' else 5
        for x in range(cx - rx + 1, cx + rx, step):
            for k in range(3 if fr == 'full' else 4):
                w = step - 1 - k if fr == 'full' else max(1, step - 2 * k - 1)
                off = 0 if fr == 'full' else k
                cv.hline(x + off, fb + 1 + k, max(1, w), H)
        if fr == 'spiky':
            for x in range(cx - rx + 2, cx + rx - 2, 5):
                cv.px(x + 1, top - 2, H)
                cv.hline(x, top - 1, 3, H)
                cv.hline(x - 1, top, 5, H)
    elif fr == 'side':
        # a sweep from the parting on the right down across the left brow
        for y in range(hairline, fb + 4):
            k = y - hairline
            right = cx + rx - 2 - k * 2
            a, b = cap.get(y, (cx - rx - 2, cx + rx + 1))
            if right > a + 2:
                cv.hline(a + 2, y, right - a - 2, H)
        for y in range(hairline, hairline + 4):
            a, b = cap.get(y, (cx - rx, cx + rx))
            cv.hline(cx + 4, y, b - cx - 5, H)
    elif fr == 'parted':
        for y in range(hairline, fb + 2):
            k = y - hairline
            a, b = cap.get(y, (cx - rx - 2, cx + rx + 1))
            gap = 1 + k
            cv.hline(a + 2, y, max(0, cx - gap - a - 2), H)
            cv.hline(cx + gap, y, max(0, b - 1 - cx - gap), H)
    elif fr == 'none':
        for y in range(hairline, hairline + 2):
            a, b = cap.get(y, (cx - rx, cx + rx))
            cv.hline(a + 2, y, b - a - 3, H)
    # shine: a band following the curve of the head
    for x in range(cx - 11, cx + 3):
        t = (x + 0.5 - cx) / (rx + 3)
        y = int(round(cy - 1 - (ry + 2) * math.sqrt(max(0, 1 - t * t)))) + 4
        cv.px(x, y, hi)
        if cx - 8 <= x <= cx:
            cv.px(x, y + 1, shade(H, 1.18))
    # shadow under the fringe
    if fr in ('full', 'spiky', 'side', 'parted'):
        for x in range(cx - rx + 3, cx + rx - 2):
            y = fb + 1
            while y < cy + 2 and cv.get(x, y)[:3] == _rgb(H):
                y += 1
            if cv.get(x, y)[:3] == _rgb(sp.skin):
                cv.px(x, y, shade(sp.skin, 0.9))


def _rgb(c):
    return rgba(c)[:3]


# ---------------------------------------------------------------------------
# face
# ---------------------------------------------------------------------------

def _face(cv, sp, g):
    cx, cy, rx, ry = g['cx'], g['cy'], g['rx'], g['ry']
    skin = sp.skin
    rows = _head_rows(g)
    # ears
    for sx in (-1, 1):
        cv.ellipse(cx + sx * rx, cy + 4, 2.5, 3.5, skin)
        cv.px(cx + sx * rx, cy + 4, shade(skin, 0.85))
    _fill(cv, rows, skin)
    # soft shade on the right cheek and under the chin
    for y, (a, b) in rows.items():
        if y > cy - 6:
            cv.px(b, y, shade(skin, 0.92))
    ey = cy + g['ey']
    old = sp.body == 'old'
    for sx in (-1, 1):
        ex = cx + sx * g['eg'] - g['ew'] // 2
        if old:
            # gentle, smiling closed eyes
            cv.px(ex, ey + 2, EYE)
            cv.hline(ex + 1, ey + 1, g['ew'] - 2, EYE)
            cv.px(ex + g['ew'] - 1, ey + 2, EYE)
            cv.px(ex + (g['ew'] if sx > 0 else -1), ey + 3, shade(skin, 0.86))
        else:
            cv.rect(ex, ey, g['ew'], g['eh'], EYE)
            cv.rect(ex, ey + g['eh'] - 2, g['ew'], 2, IRIS)
            cv.px(ex, ey + 1, P.WHITE)
            if g['ew'] > 3:
                cv.px(ex + 1, ey + 1, P.WHITE)
            # lash
            cv.px(ex + (-1 if sx < 0 else g['ew']), ey, EYE)
        # brow
        bx = ex - (1 if sx < 0 else 0)
        cv.hline(bx, ey - 4, g['ew'] + 1, shade(sp.hair, 0.8))
    # nose
    cv.px(cx, ey + g['eh'] + 1, shade(skin, 0.86))
    # mouth: a small smile
    my = ey + g['eh'] + 4
    cv.px(cx - 2, my, MOUTH)
    cv.hline(cx - 1, my + 1, 2, MOUTH)
    cv.px(cx + 1, my, MOUTH)
    if sp.blush:
        for sx in (-1, 1):
            bx = cx + sx * (g['eg'] + 3) - 1
            cv.hline(bx, ey + g['eh'] + 1, 3, P.BLUSH)
    if old:
        for sx in (-1, 1):
            # laugh lines
            cv.px(cx + sx * 5, my - 1, shade(skin, 0.86))
            cv.px(cx + sx * 5, my, shade(skin, 0.86))


def _acc_head(cv, sp, g):
    cx, cy, rx, ry = g['cx'], g['cy'], g['rx'], g['ry']
    acc, col = sp.acc, sp.acc_col
    ey = cy + g['ey']
    if 'glasses' in acc:
        gc = col.get('glasses', '#7a6a5a')
        for sx in (-1, 1):
            ex = cx + sx * g['eg'] - g['ew'] // 2
            cv.frame(ex - 2, ey - 2, g['ew'] + 4, 7, gc)
            cv.px(ex - 1, ey - 1, (255, 255, 255, 90))
        cv.hline(cx - 2, ey, 4, gc)
    if 'beard' in acc:
        bc = col.get('beard', '#e8e4dc')
        my = ey + g['eh'] + 4
        rows = _head_rows(g)
        for y in range(my - 2, cy + ry + 4):
            a, b = rows.get(y, (cx - 7, cx + 6))
            k = y - (my - 2)
            w = max(3, min(b - a + 1, 16) // 2 - max(0, k - 5))
            cv.hline(cx - w, y, 2 * w, bc)
        cv.hline(cx - 4, my - 3, 8, bc)
        cv.hline(cx - 2, my, 4, MOUTH)
        for y in range(my + 2, cy + ry + 3, 2):
            cv.px(cx - 2 + (y % 4), y, shade(bc, 0.88))
    if 'grey_streak' in acc:
        for i in range(8):
            cv.px(cx - 9 + i, cy - ry + 3 + i // 2, '#d8d4cc')
    if 'hairclip' in acc:
        hc = col.get('hairclip', '#f7d55c')
        cv.rect(cx + 8, cy - 8, 4, 2, hc)
        cv.px(cx + 9, cy - 9, hc)
    if 'hairpin' in acc:
        hp = col.get('hairpin', '#e8c860')
        cv.line(cx + 3, cy - ry - 5, cx + 9, cy - ry - 1, '#8a6a3a')
        cv.ellipse(cx + 9, cy - ry - 1, 2, 2, hp)
    if 'straw_hat' in acc:
        hc = '#e8c860'
        cv.ellipse(cx, cy - ry + 6, rx + 10, 4, hc)
        cv.hline(cx - rx - 8, cy - ry + 8, 2 * rx + 16, shade(hc, 0.8))
        for y in range(cy - ry - 4, cy - ry + 5):
            cv.hline(cx - 11, y, 22, hc)
        cv.hline(cx - 11, cy - ry + 2, 22, '#c0392b')
        cv.hline(cx - 11, cy - ry + 3, 22, '#c0392b')
        for x in range(cx - 10, cx + 10, 3):
            cv.px(x, cy - ry - 2, shade(hc, 0.88))
    if 'cap' in acc:
        cc = col.get('cap', '#3f6fb0')
        for y, (a, b) in _ellipse_rows(cx, cy - 4, rx + 2, ry - 2).items():
            if y < cy - 8:
                cv.hline(a, y, b - a + 1, cc)
        cv.hline(cx - rx - 4, cy - 8, 2 * rx + 6, shade(cc, 0.75))
        cv.hline(cx - rx - 6, cy - 7, 2 * rx + 4, shade(cc, 0.75))
        cv.ellipse(cx - 4, cy - ry + 2, 4, 2, shade(cc, 1.3))
    if 'knit_hat' in acc:
        cc = col.get('knit_hat', '#d8302a')
        for y, (a, b) in _ellipse_rows(cx, cy - 2, rx + 3, ry + 1).items():
            if y < cy - 7:
                cv.hline(a, y, b - a + 1, cc)
        for x in range(cx - rx, cx + rx, 3):
            cv.vline(x, cy - ry + 2, 7, shade(cc, 0.85))
        cv.rect(cx - rx - 2, cy - 9, 2 * rx + 4, 3, P.WHITE)
        cv.ellipse(cx, cy - ry - 3, 4, 4, P.WHITE)
    if 'headphones' in acc:
        hc = '#3a3540'
        for y, (a, b) in _ellipse_rows(cx, cy - 1, rx + 4, ry + 3).items():
            if y < cy - 10:
                cv.px(a, y, hc)
                cv.px(b, y, hc)
        top = cy - ry - 1
        cv.hline(cx - 8, top - 1, 16, hc)
        for sx in (-1, 1):
            cv.rect(cx + sx * (rx + 2) - 2, cy - 2, 5, 9, '#d8302a')
            cv.vline(cx + sx * (rx + 2) - 2 + (4 if sx < 0 else 0), cy - 2, 9, shade('#d8302a', 0.7))


def portrait(sp):
    g = GEOM[sp.body]
    cv = Canvas(SIZE, SIZE)
    _hair_back(cv, sp, g)
    _body(cv, sp, g)
    _acc_body(cv, sp, g)
    _face(cv, sp, g)
    _hair_front(cv, sp, g)
    _acc_head(cv, sp, g)
    cv.outline(OUT)
    return cv


def face_sheet(names):
    out = Canvas(SIZE * 4, SIZE * 2)
    for i, name in enumerate(names):
        out.paste(portrait(CAST[name]), (i % 4) * SIZE, (i // 4) * SIZE)
    return out


def build(faces_dir):
    for sheet, names in SHEETS.items():
        face_sheet(names).save('%s/%s.png' % (faces_dir, sheet))
