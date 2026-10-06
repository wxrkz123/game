"""Parametric chibi character sprites for RPG Maker MV.

Each character is a '$' single sheet: 3 walk frames x 4 directions of 24x24
logical px (48x48 in game).  Row order: down, left, right, up.
"""
from pixlib import Canvas, rgba, shade, mix
import palette as P

OUT = '#3b2a33'      # outline colour
EYE = '#2b2230'

DIRS = ['down', 'left', 'right', 'up']


class Spec:
    def __init__(self, **kw):
        self.body = kw.get('body', 'adult')          # adult | child | old
        self.skin = kw.get('skin', P.SKIN)
        self.hair = kw.get('hair', '#4a3428')
        self.hair_style = kw.get('hair_style', 'short')   # see hair()
        self.fringe = kw.get('fringe', 'full')       # full | side | parted | none | spiky
        self.top = kw.get('top', '#d8574f')          # shirt / dress colour
        self.top2 = kw.get('top2', None)             # sleeves / trim colour
        self.bottom = kw.get('bottom', '#3f5a8a')    # pants / skirt colour
        self.legwear = kw.get('legwear', 'pants')    # pants | skirt | dress | longskirt
        self.shoes = kw.get('shoes', '#5a3a2a')
        self.coat = kw.get('coat', False)            # longer top
        self.acc = kw.get('acc', [])                 # list of accessory names
        self.acc_col = kw.get('acc_col', {})
        self.blush = kw.get('blush', True)


# ---------------------------------------------------------------------------
# geometry per body type
# ---------------------------------------------------------------------------
GEOM = {
    #          head x,y     torso y0,y1   legs y0,y1  torso x0,w
    'adult': dict(hx=6, hy=1, ty0=12, ty1=18, ly0=19, ly1=22, tx=8, tw=8),
    'child': dict(hx=6, hy=5, ty0=16, ty1=19, ly0=20, ly1=22, tx=8, tw=8),
    'old':   dict(hx=6, hy=2, ty0=13, ty1=19, ly0=20, ly1=22, tx=8, tw=8),
}

HEAD = {
    'down': [
        "..SSSSSSSS..",
        ".SSSSSSSSSS.",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSESSSSESSS",
        "SSSESSSSESSS",
        "SSRSSSSSSRSS",
        ".SSSSSSSSSS.",
        "..ssssssss..",
    ],
    'left': [
        "..SSSSSSSS..",
        ".SSSSSSSSSS.",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSESSSSSSSSS",
        "SSESSSSSSSSS",
        "SSSRSSSSSSSs",
        ".SSSSSSSSSs.",
        "..sssssssss.",
    ],
    'up': [
        "..SSSSSSSS..",
        ".SSSSSSSSSS.",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        "SSSSSSSSSSSS",
        ".SSSSSSSSSS.",
        "..ssssssss..",
    ],
}


def _draw_head(cv, sp, d, hx, hy):
    rows = HEAD['left' if d in ('left', 'right') else d]
    cmap = {'S': sp.skin, 's': shade(sp.skin, 0.9), 'E': EYE,
            'R': P.BLUSH if sp.blush else sp.skin}
    cv.ascii(rows, cmap, hx, hy)


# ---------------------------------------------------------------------------
# hair (procedural, in frame coordinates)
# ---------------------------------------------------------------------------

def _hair(cv, sp, d, hx, hy):
    H = sp.hair
    hi = shade(H, 1.35)
    lo = shade(H, 0.75)
    st = sp.hair_style
    fr = sp.fringe
    x0, y0 = hx, hy

    def p(x, y, c=H):
        cv.px(x, y, c)

    def row(y, xa, xb, c=H):
        for x in range(xa, xb + 1):
            p(x, y, c)

    if st == 'bald':
        # grandpa: hair only on the sides/back, shiny scalp
        if d == 'down':
            for y in range(y0 + 3, y0 + 7):
                p(x0 - 0, y)
                p(x0 + 11, y)
                p(x0 + 1, y, lo)
                p(x0 + 10, y, lo)
            cv.px(x0 + 4, y0 + 1, shade(sp.skin, 1.12))
            cv.px(x0 + 5, y0 + 1, shade(sp.skin, 1.12))
        elif d == 'up':
            for y in range(y0 + 3, y0 + 10):
                row(y, x0, x0 + 11)
            row(y0 + 10, x0 + 2, x0 + 9, lo)
        else:
            for y in range(y0 + 3, y0 + 10):
                row(y, x0 + 6, x0 + 11)
            cv.px(x0 + 4, y0 + 1, shade(sp.skin, 1.12))
        return

    # ---- cap (top of the head) -----------------------------------------
    cap = [(y0 - 1, x0 + 2, x0 + 9), (y0, x0, x0 + 11), (y0 + 1, x0 - 1, x0 + 12),
           (y0 + 2, x0 - 1, x0 + 12), (y0 + 3, x0 - 1, x0 + 12)]
    if fr == 'spiky':
        cap[0] = (y0 - 1, x0 + 1, x0 + 10)
    if fr == 'none' and d != 'up':
        cap = cap[:3] + [(y0 + 2, x0 - 1, x0 + 12)]
        for y in range(y0 + 3, y0 + 7):
            p(x0 - 1, y)
            p(x0, y, lo)
            if d == 'down':
                p(x0 + 12, y)
                p(x0 + 11, y, lo)
    for (y, a, b) in cap:
        row(y, a, b)
    if fr == 'spiky':
        for x in range(x0, x0 + 12, 3):
            p(x, y0 - 2)
            p(x + 1, y0 - 2)
    # highlight
    if d in ('down', 'up'):
        row(y0 + 1, x0 + 2, x0 + 4, hi)
        p(x0 + 3, y0 + 2, hi)
    elif d == 'left':
        row(y0 + 1, x0 + 4, x0 + 7, hi)

    # ---- front / fringe -------------------------------------------------
    if d == 'down':
        if fr in ('full', 'spiky'):
            row(y0 + 4, x0, x0 + 11)
            for x in range(x0 + 1, x0 + 11, 3):
                p(x, y0 + 5, H)
        elif fr == 'side':
            row(y0 + 4, x0, x0 + 11)
            for i in range(6):
                p(x0 + 1 + i, y0 + 5, H)
            p(x0 + 1, y0 + 6)
            p(x0 + 2, y0 + 6)
        elif fr == 'parted':
            row(y0 + 4, x0, x0 + 4)
            row(y0 + 4, x0 + 7, x0 + 11)
            p(x0 + 5, y0 + 3, sp.skin)
            p(x0 + 6, y0 + 3, sp.skin)
            p(x0, y0 + 5)
            p(x0 + 11, y0 + 5)
        # sideburns
        for y in (range(y0 + 4, y0 + 8) if fr != 'none' else ()):
            p(x0 - 1, y)
            p(x0 + 12, y)
            p(x0, y, lo)
            p(x0 + 11, y, lo)
    elif d in ('left', 'right'):
        # face side is on the left (mirrored later for right)
        if fr in ('full', 'spiky', 'side'):
            row(y0 + 4, x0, x0 + 5)
            p(x0, y0 + 5)
            p(x0 + 3, y0 + 5)
        elif fr == 'parted':
            row(y0 + 4, x0 + 1, x0 + 3)
        for y in range(y0 + 4, y0 + 9):
            row(y, x0 + 6, x0 + 12)
        row(y0 + 9, x0 + 7, x0 + 11)
        # ear
        p(x0 + 6, y0 + 7, sp.skin)
        p(x0 + 6, y0 + 6, shade(sp.skin, 0.9))
    elif d == 'up':
        for y in range(y0 + 4, y0 + 10):
            row(y, x0 - 1, x0 + 12)
        row(y0 + 10, x0 + 1, x0 + 10, lo)

    # ---- length -----------------------------------------------------------
    if st in ('bob', 'long', 'ponytail', 'twintails', 'bun', 'buns'):
        if st == 'bob':
            depth = y0 + 10
        elif st == 'long':
            depth = y0 + 15
        else:
            depth = y0 + 8
        if d == 'down':
            for y in range(y0 + 5, depth + 1):
                p(x0 - 1, y)
                p(x0, y, lo if y > y0 + 7 else H)
                p(x0 + 12, y)
                p(x0 + 11, y, lo if y > y0 + 7 else H)
                if st == 'long' and y > y0 + 10:
                    p(x0 - 2, y, lo)
                    p(x0 + 13, y, lo)
        elif d in ('left', 'right'):
            for y in range(y0 + 5, depth + 1):
                row(y, x0 + 6, x0 + 12)
            if st == 'long':
                for y in range(y0 + 10, depth + 1):
                    row(y, x0 + 7, x0 + 13, lo if y > depth - 2 else H)
        elif d == 'up':
            for y in range(y0 + 5, depth + 1):
                row(y, x0 - 1, x0 + 12, H if y < depth else lo)
            if st == 'long':
                for y in range(y0 + 10, depth + 1):
                    row(y, x0 - 2, x0 + 13, H if y < depth - 1 else lo)

    # ---- extras -------------------------------------------------------------
    if st == 'ponytail':
        if d == 'up':
            for y in range(y0 + 4, y0 + 12):
                row(y, x0 + 5, x0 + 6, H)
            row(y0 + 12, x0 + 5, x0 + 6, lo)
            p(x0 + 5, y0 + 4, sp.acc_col.get('tie', '#d8574f'))
            p(x0 + 6, y0 + 4, sp.acc_col.get('tie', '#d8574f'))
        elif d in ('left', 'right'):
            for i, y in enumerate(range(y0 + 3, y0 + 11)):
                row(y, x0 + 12, x0 + 13 + (1 if 2 < i < 6 else 0), H if i < 6 else lo)
            p(x0 + 12, y0 + 3, sp.acc_col.get('tie', '#d8574f'))
        elif d == 'down':
            p(x0 + 13, y0 + 6, H)
            p(x0 + 13, y0 + 7, lo)
    elif st == 'twintails':
        tie = sp.acc_col.get('tie', '#d8574f')
        if d in ('down', 'up'):
            for (sx, dirx) in ((x0 - 2, -1), (x0 + 13, 1)):
                for i, y in enumerate(range(y0 + 4, y0 + 11)):
                    w = 2 if 1 < i < 6 else 1
                    for k in range(w):
                        p(sx + dirx * k, y, H if i < 5 else lo)
                p(sx - dirx * 1, y0 + 4, tie)
        else:
            for i, y in enumerate(range(y0 + 4, y0 + 11)):
                row(y, x0 + 12, x0 + 13, H if i < 5 else lo)
            p(x0 + 12, y0 + 4, tie)
    elif st == 'bun':
        if d == 'up':
            cv.ellipse(x0 + 6, y0 + 1, 3.2, 2.6, H)
            row(y0, x0 + 4, x0 + 6, hi)
        elif d in ('left', 'right'):
            cv.ellipse(x0 + 11, y0 + 1, 2.6, 2.6, H)
            p(x0 + 10, y0, hi)
        else:
            cv.ellipse(x0 + 6, y0 - 2, 3, 2.2, H)
            p(x0 + 5, y0 - 3, hi)
        if 'hairpin' in sp.acc:
            p(x0 + 8, y0 - 2 if d == 'down' else y0, sp.acc_col.get('hairpin', '#e8c860'))
    elif st == 'buns':
        for (bx, by) in ((x0, y0 - 1), (x0 + 11, y0 - 1)):
            if d in ('left', 'right') and bx == x0:
                continue
            cv.ellipse(bx + 0.5, by + 0.5, 2.4, 2.4, H)
            p(bx, by - 1, hi)


# ---------------------------------------------------------------------------
# body
# ---------------------------------------------------------------------------

def _body(cv, sp, d, f, g):
    """f: 0 left step, 1 stand, 2 right step."""
    tx, tw, ty0, ty1, ly0, ly1 = g['tx'], g['tw'], g['ty0'], g['ty1'], g['ly0'], g['ly1']
    top, top2 = sp.top, sp.top2 or sp.top
    bot = sp.bottom
    shoe = sp.shoes
    skin = sp.skin
    legs_skin = sp.legwear in ('skirt', 'dress')
    leg_col = skin if legs_skin else bot
    longwear = sp.legwear in ('longskirt',) or sp.coat
    step = {0: -1, 1: 0, 2: 1}[f]

    if d in ('down', 'up'):
        # legs
        lx = [tx + 1, tx + tw - 3]
        for i, x in enumerate(lx):
            lift = 1 if (step == -1 and i == 0) or (step == 1 and i == 1) else 0
            for y in range(ly0, ly1 - lift):
                cv.rect(x, y, 2, 1, leg_col)
            cv.rect(x, ly1 - lift, 2, 1, shoe)
            if d == 'down':
                cv.px(x + (0 if i == 0 else 1), ly1 - lift, shade(shoe, 1.3))
        # skirt / long garments
        if sp.legwear in ('skirt', 'dress'):
            cv.rect(tx - 1, ty1, tw + 2, 2, bot if sp.legwear == 'skirt' else top)
            cv.hline(tx - 1, ty1 + 1, tw + 2, shade(bot if sp.legwear == 'skirt' else top, 0.8))
        if longwear:
            col = sp.coat if isinstance(sp.coat, str) else (bot if sp.legwear == 'longskirt' else top)
            cv.rect(tx - 1, ty1, tw + 2, ly1 - ty1 - 1, col)
            cv.hline(tx - 1, ly1 - 2, tw + 2, shade(col, 0.8))
            if isinstance(sp.coat, str) and d == 'down':
                cv.vline(tx + tw // 2, ty1, ly1 - ty1 - 1, shade(col, 0.8))
        # torso
        tcol = sp.coat if isinstance(sp.coat, str) else top
        cv.rect(tx, ty0, tw, ty1 - ty0 + 1, tcol)
        cv.vline(tx + tw - 1, ty0, ty1 - ty0 + 1, shade(tcol, 0.82))
        if d == 'down':
            # collar/neck
            cv.px(tx + tw // 2 - 1, ty0, shade(skin, 0.9))
            cv.px(tx + tw // 2, ty0, shade(skin, 0.9))
            if top2 != top and not isinstance(sp.coat, str):
                cv.hline(tx + 1, ty0, tw - 2, top2)
        # arms
        swing = step
        for side, ax in ((0, tx - 1), (1, tx + tw)):
            s = swing if side == 0 else -swing
            sleeve = top2 if not isinstance(sp.coat, str) else sp.coat
            ya = ty0 + (1 if g is GEOM['child'] else 0)
            hand_y = ty1 - 1 + (1 if s > 0 else 0) - (1 if s < 0 else 0)
            cv.vline(ax, ya, hand_y - ya, sleeve)
            cv.px(ax, hand_y, skin)
        if d == 'down' and sp.legwear == 'pants' and not longwear:
            cv.hline(tx, ty1, tw, shade(bot, 0.85))
    else:  # left (right is mirrored)
        cx = tx + 1
        tw2 = tw - 2
        # legs: front leg and back leg
        if step == 0:
            legs = [(cx + 1, 0), (cx + 3, 0)]
        else:
            legs = [(cx, 0), (cx + 4, 0)]
        for (x, lift) in legs:
            for y in range(ly0, ly1):
                cv.rect(x, y, 2, 1, leg_col)
            cv.rect(x - 1 if x <= cx + 1 else x, ly1, 3 if x <= cx + 1 else 2, 1, shoe)
        if sp.legwear in ('skirt', 'dress'):
            cv.rect(cx - 1, ty1, tw2 + 2, 2, bot if sp.legwear == 'skirt' else top)
        if longwear:
            col = sp.coat if isinstance(sp.coat, str) else (bot if sp.legwear == 'longskirt' else top)
            cv.rect(cx - 1, ty1, tw2 + 2, ly1 - ty1 - 1, col)
        tcol = sp.coat if isinstance(sp.coat, str) else top
        cv.rect(cx, ty0, tw2, ty1 - ty0 + 1, tcol)
        cv.vline(cx + tw2 - 1, ty0, ty1 - ty0 + 1, shade(tcol, 0.82))
        # arm swings forward/back
        sleeve = top2 if not isinstance(sp.coat, str) else sp.coat
        ax = cx + 2 + (-1 if step == -1 else (1 if step == 1 else 0))
        ya = ty0 + 1
        cv.vline(ax, ya, ty1 - ya - 1, shade(sleeve, 0.9))
        cv.px(ax, ty1 - 1, skin)


# ---------------------------------------------------------------------------
# accessories
# ---------------------------------------------------------------------------

def _acc_back(cv, sp, d, f, g):
    """things drawn behind the body"""
    if 'guitar' in sp.acc:
        gx = g['tx'] + g['tw'] // 2
        col = sp.acc_col.get('guitar', '#3a3540')  # gig bag
        if d == 'up':
            cv.rect(gx - 3, g['ty0'] - 1, 6, 9, col)
            cv.rect(gx - 1, g['ty0'] - 5, 2, 5, col)
            cv.hline(gx - 3, g['ty0'] + 3, 6, shade(col, 1.3))
        elif d == 'left':
            cv.rect(gx + 2, g['ty0'] - 1, 3, 9, col)
            cv.rect(gx + 3, g['ty0'] - 5, 2, 5, col)
        elif d == 'down':
            cv.rect(gx - 1, g['ty0'] - 4, 2, 3, col)
    if 'cane' in sp.acc and d != 'up':
        x = g['tx'] - 2 if d == 'down' else g['tx'] - 1
        cv.vline(x, g['ty0'] + 3, g['ly1'] - g['ty0'] - 2, P.WOOD_LO)


def _acc_front(cv, sp, d, f, g):
    hx, hy = g['hx'], g['hy']
    tx, tw, ty0, ty1 = g['tx'], g['tw'], g['ty0'], g['ty1']
    if 'glasses' in sp.acc:
        gc = sp.acc_col.get('glasses', '#7a6a5a')
        if d == 'down':
            for ex in (hx + 3, hx + 8):
                cv.hline(ex - 1, hy + 5, 3, gc)
                cv.px(ex - 1, hy + 6, gc)
                cv.px(ex + 1, hy + 6, gc)
            cv.hline(hx + 5, hy + 6, 2, gc)
        elif d == 'left':
            cv.hline(hx + 1, hy + 5, 3, gc)
            cv.px(hx + 1, hy + 6, gc)
            cv.px(hx + 3, hy + 6, gc)
            cv.hline(hx + 4, hy + 6, 2, gc)
    if 'beard' in sp.acc and d != 'up':
        bc = sp.acc_col.get('beard', '#e8e4dc')
        if d == 'down':
            cv.rect(hx + 3, hy + 9, 6, 2, bc)
            cv.rect(hx + 4, hy + 11, 4, 1, bc)
            cv.hline(hx + 4, hy + 8, 4, bc)
        else:
            cv.rect(hx + 1, hy + 9, 4, 2, bc)
            cv.px(hx + 2, hy + 11, bc)
    if 'mustache' in sp.acc and d != 'up':
        bc = sp.acc_col.get('beard', '#3a3540')
        if d == 'down':
            cv.hline(hx + 4, hy + 9, 4, bc)
        else:
            cv.hline(hx + 1, hy + 9, 2, bc)
    if 'scarf' in sp.acc:
        sc = sp.acc_col.get('scarf', '#d8302a')
        if d in ('down', 'up'):
            cv.hline(tx - 1, ty0, tw + 2, sc)
            cv.hline(tx, ty0 + 1, tw, shade(sc, 0.85))
            if d == 'down':
                cv.rect(tx + 1, ty0 + 2, 2, 3, sc)
        else:
            cv.hline(tx, ty0, tw - 1, sc)
            cv.rect(tx + tw - 3, ty0 + 1, 2, 3, sc)
    if 'neckerchief' in sp.acc and d == 'down':
        sc = sp.acc_col.get('neckerchief', '#d8302a')
        cv.px(tx + tw // 2 - 1, ty0 + 1, sc)
        cv.px(tx + tw // 2, ty0 + 1, sc)
        cv.px(tx + tw // 2 - 1, ty0 + 2, sc)
    if 'stripe' in sp.acc:   # tracksuit stripe on sleeves/sides
        sc = sp.acc_col.get('stripe', '#3f6fb0')
        if d in ('down', 'up'):
            cv.vline(tx - 1, ty0 + 1, ty1 - ty0 - 1, sc)
            cv.vline(tx + tw, ty0 + 1, ty1 - ty0 - 1, sc)
        if d == 'down':
            cv.vline(tx + tw // 2, ty0 + 1, ty1 - ty0, shade(sp.top, 0.85))
    if 'apron' in sp.acc and d == 'down':
        ac = sp.acc_col.get('apron', P.WHITE)
        cv.rect(tx + 1, ty0 + 2, tw - 2, ty1 - ty0 + 2, ac)
        cv.hline(tx + 1, ty0 + 4, tw - 2, shade(ac, 0.9))
    if 'tie' in sp.acc and d == 'down':
        tc = sp.acc_col.get('tie_col', '#d8302a')
        cv.vline(tx + tw // 2, ty0 + 1, 4, tc)
        cv.px(tx + tw // 2 - 1, ty0 + 1, P.WHITE)
        cv.px(tx + tw // 2 + 1, ty0 + 1, P.WHITE)
    if 'straw_hat' in sp.acc:
        hc = '#e8c860'
        if d == 'down' or d == 'up':
            cv.hline(hx - 3, hy + 3, 18, hc)
            cv.hline(hx - 2, hy + 4, 16, shade(hc, 0.8))
            cv.rect(hx + 1, hy - 1, 10, 4, hc)
            cv.hline(hx + 1, hy + 2, 10, '#c0392b')
        else:
            cv.hline(hx - 3, hy + 3, 18, hc)
            cv.rect(hx + 2, hy - 1, 9, 4, hc)
            cv.hline(hx + 2, hy + 2, 9, '#c0392b')
    if 'cap' in sp.acc:
        cc = sp.acc_col.get('cap', '#3f6fb0')
        cv.rect(hx, hy - 1, 12, 4, cc)
        cv.hline(hx + 2, hy - 1, 6, shade(cc, 1.3))
        if d == 'down':
            cv.hline(hx + 1, hy + 3, 10, shade(cc, 0.75))
        elif d == 'left':
            cv.hline(hx - 3, hy + 3, 6, shade(cc, 0.75))
    if 'knit_hat' in sp.acc:
        cc = sp.acc_col.get('knit_hat', '#d8302a')
        cv.rect(hx - 1, hy - 1, 14, 5, cc)
        cv.hline(hx - 1, hy + 3, 14, P.WHITE)
        cv.ellipse(hx + 6, hy - 2, 2, 2, P.WHITE)
    if 'shawl' in sp.acc and d != 'up':
        sc = sp.acc_col.get('shawl', '#8a6aa6')
        cv.rect(tx - 1, ty0, tw + 2, 3, sc)
        cv.px(tx + tw // 2, ty0 + 3, sc)
        cv.hline(tx - 1, ty0 + 2, tw + 2, shade(sc, 0.8))
    if 'headphones' in sp.acc and d != 'up':
        hc = '#3a3540'
        cv.hline(hx + 1, hy - 1, 10, hc)
        if d == 'down':
            cv.rect(hx - 1, hy + 5, 2, 3, '#d8302a')
            cv.rect(hx + 11, hy + 5, 2, 3, '#d8302a')
        else:
            cv.rect(hx + 5, hy + 5, 2, 3, '#d8302a')
    if 'hairclip' in sp.acc and d == 'down':
        cv.px(hx + 9, hy + 3, sp.acc_col.get('hairclip', '#f7d55c'))
        cv.px(hx + 10, hy + 3, sp.acc_col.get('hairclip', '#f7d55c'))
    if 'bag' in sp.acc and d != 'up':
        bc = sp.acc_col.get('bag', '#8a5a3a')
        if d == 'down':
            cv.line(tx, ty0, tx + tw - 1, ty1 - 2, shade(bc, 0.8))
            cv.rect(tx + tw - 2, ty1 - 2, 3, 3, bc)
        else:
            cv.rect(tx + 2, ty1 - 2, 3, 3, bc)
    if 'grey_streak' in sp.acc and d == 'down':
        cv.px(hx + 3, hy + 1, '#d8d4cc')
        cv.px(hx + 4, hy + 2, '#d8d4cc')


def draw_frame(sp, d, f):
    g = GEOM[sp.body]
    cv = Canvas(24, 24)
    draw_d = 'left' if d == 'right' else d
    bob = 1 if f != 1 else 0
    gg = dict(g)
    gg['hy'] = g['hy'] + bob * 0
    if draw_d == 'up':
        _hair_back_extras = True
    _acc_back(cv, sp, draw_d, f, gg)
    _body(cv, sp, draw_d, f, gg)
    _draw_head(cv, sp, draw_d, gg['hx'], gg['hy'])
    _hair(cv, sp, draw_d, gg['hx'], gg['hy'])
    _acc_front(cv, sp, draw_d, f, gg)
    if draw_d == 'up' and 'guitar' in sp.acc:
        _acc_back(cv, sp, 'up', f, gg)
    cv.outline(OUT)
    if d == 'right':
        cv = cv.flipped()
    return cv


def sheet(sp):
    out = Canvas(72, 96)
    for r, d in enumerate(DIRS):
        for f in range(3):
            out.paste(draw_frame(sp, d, f), f * 24, r * 24)
    return out


def object_sheet(frames_by_row):
    """frames_by_row: list of 4 rows x 3 canvases -> 72x96 sheet."""
    out = Canvas(72, 96)
    for r, row in enumerate(frames_by_row):
        for c, cv in enumerate(row):
            out.paste(cv, c * 24, r * 24)
    return out
