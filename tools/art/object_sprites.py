"""Animated object / animal sprites ('!$' single sheets: 3 frames x 4 rows).

For objects that do not turn, the 4 rows are used as *states*
(an event page picks a state through its image direction:
row 0 = 'down'(2), row 1 = 'left'(4), row 2 = 'right'(6), row 3 = 'up'(8)).
"""
import math

from pixlib import Canvas, shade, rng
from chars import object_sheet
from textutil import draw_text
import palette as P

INK = '#3b2a33'


def _same_rows(frames):
    return object_sheet([frames, frames, frames, frames])


def sparkle():
    fr = []
    for f in range(3):
        cv = Canvas(24, 24)
        s = [2, 4, 3][f]
        c = ['#fff6c8', '#ffffff', '#ffe89a'][f]
        cx, cy = 12, 13
        cv.hline(cx - s, cy, 2 * s + 1, c)
        cv.vline(cx, cy - s, 2 * s + 1, c)
        cv.px(cx, cy, '#ffffff')
        if f == 1:
            for d in (-2, 2):
                cv.px(cx + d, cy + d, '#fff6c8')
                cv.px(cx + d, cy - d, '#fff6c8')
        cv.outline((255, 220, 120, 110))
        fr.append(cv)
    return _same_rows(fr)


def note(color='#f7d55c'):
    rows = []
    for col in (color, '#9ad6f2', '#f2a0b8', '#b6e39a'):
        fr = []
        for f in range(3):
            cv = Canvas(24, 24)
            dy = [0, -1, -2][f]
            y = 8 + dy
            cv.ellipse(9, y + 9, 3, 2.4, col)
            cv.ellipse(16, y + 7, 3, 2.4, col)
            cv.rect(11, y, 2, 9, col)
            cv.rect(18, y - 2, 2, 9, col)
            cv.rect(11, y - 2, 9, 2, col)
            cv.rect(11, y, 9, 1, col)
            cv.outline(shade(col, 0.55))
            fr.append(cv)
        rows.append(fr)
    return object_sheet(rows)


def wind_chime():
    fr = []
    for f in range(3):
        cv = Canvas(24, 24)
        sway = [-1, 0, 1][f]
        cv.vline(12, 0, 4, '#8a8a96')
        cv.ellipse(12, 6, 5, 3, '#5aa0d8')
        cv.hline(7, 7, 11, '#3f7ab0')
        cv.vline(12 + sway, 9, 6, '#d8d4cc')
        cv.rect(10 + sway * 2, 15, 5, 7, '#fbf8f2')
        cv.hline(10 + sway * 2, 15, 5, '#d8302a')
        cv.px(12 + sway * 2, 18, '#d8302a')
        fr.append(cv)
    return _same_rows(fr)


def guitar_case():
    """row0 empty, row1 coins, row2 candy, row3 candy+coins (open case on the ground)"""
    rows = []
    for state in range(4):
        fr = []
        for f in range(3):
            cv = Canvas(24, 24)
            cv.ellipse(8, 14, 6, 6, '#2e2a36')
            cv.ellipse(17, 15, 5, 5, '#2e2a36')
            cv.rect(8, 9, 10, 11, '#2e2a36')
            cv.ellipse(8, 14, 4.5, 4.5, '#b8303a')
            cv.ellipse(17, 15, 3.5, 3.5, '#b8303a')
            cv.rect(8, 11, 9, 7, '#b8303a')
            if state in (1, 3):
                for (x, y) in ((6, 13), (9, 16), (14, 14)):
                    cv.px(x, y, '#f0c040')
                    cv.px(x + 1, y, '#f7e08a' if f == 1 else '#f0c040')
            if state in (2, 3):
                cv.rect(15, 12, 4, 3, '#f2a0b8')
                cv.px(14, 13, '#f7d55c')
                cv.px(19, 13, '#f7d55c')
                if f == 1:
                    cv.px(17, 11, '#ffffff')
            fr.append(cv)
        rows.append(fr)
    return object_sheet(rows)


def phone():
    """row0 idle, row1 ringing (shakes)"""
    rows = []
    for state in range(4):
        fr = []
        for f in range(3):
            cv = Canvas(24, 24)
            dx = 0 if state == 0 else [-1, 1, 0][f]
            cv.rect(8 + dx, 8, 8, 13, '#3a3540')
            cv.rect(9 + dx, 9, 6, 9, '#5a8ac8' if state else '#2a3040')
            cv.px(12 + dx, 19, '#8a8a96')
            if state and f != 2:
                cv.px(5, 9, '#f7d55c')
                cv.px(4, 8, '#f7d55c')
                cv.px(19, 9, '#f7d55c')
                cv.px(20, 8, '#f7d55c')
            fr.append(cv)
        rows.append(fr)
    return object_sheet(rows)


def item_glint(drawer):
    fr = []
    for f in range(3):
        cv = Canvas(24, 24)
        drawer(cv)
        if f == 1:
            cv.px(17, 9, '#ffffff')
            cv.px(16, 9, '#fff6c8')
            cv.px(18, 9, '#fff6c8')
            cv.px(17, 8, '#fff6c8')
            cv.px(17, 10, '#fff6c8')
        fr.append(cv)
    return _same_rows(fr)


def _harmonica(cv):
    cv.rect(6, 13, 13, 5, '#c9c5bc')
    cv.hline(6, 13, 13, '#ecebe6')
    cv.rect(6, 15, 13, 1, '#8a8a96')
    for x in range(7, 18, 2):
        cv.px(x, 16, '#3a3540')
    cv.outline(INK)


def _envelope(cv):
    cv.rect(5, 11, 14, 9, '#f4efe4')
    cv.line(5, 11, 12, 16, '#c9c2b2')
    cv.line(18, 11, 12, 16, '#c9c2b2')
    cv.px(12, 17, '#d8302a')
    cv.outline(INK)


def _recorder(cv):
    cv.line(6, 19, 18, 9, '#f4efe4')
    cv.line(7, 19, 19, 9, '#e8e0cc')
    for (x, y) in ((10, 15), (12, 13), (14, 12)):
        cv.px(x, y, '#3a3540')
    cv.outline(INK)


def _flowers_bouquet(cv):
    cv.line(10, 20, 12, 13, P.LEAF_LO)
    cv.line(14, 20, 12, 13, P.LEAF_LO)
    for (x, y, c) in ((10, 10, '#f4f1ea'), (14, 10, '#f7d55c'), (12, 8, '#f4f1ea'), (12, 12, '#f2a0b8')):
        cv.ellipse(x, y, 2, 2, c)
    cv.outline(INK)


def _lyrics(cv):
    cv.rect(6, 9, 12, 12, '#fbf8f2')
    for y in (11, 13, 15, 17):
        cv.hline(8, y, 8, '#9a9aa8')
    cv.rect(13, 16, 3, 2, '#3a3540')
    cv.outline(INK)


def _photo(cv):
    cv.rect(6, 9, 12, 11, '#fbf8f2')
    cv.rect(7, 10, 10, 7, '#cfe6f2')
    cv.rect(9, 12, 2, 4, '#3a3540')
    cv.rect(13, 13, 2, 3, '#d8574f')
    cv.outline(INK)


def _guitar_new(cv):
    cv.rect(11, 2, 2, 11, P.WOOD_DEEP)
    cv.ellipse(12, 15, 5, 4, '#c97a3a')
    cv.ellipse(12, 19, 6, 4, '#c97a3a')
    cv.ellipse(12, 16, 1.5, 1.5, '#2a1a12')
    cv.outline(INK)


def dragonfly():
    rows = []
    for d in range(4):
        fr = []
        for f in range(3):
            cv = Canvas(24, 24)
            horizontal = d in (1, 2)
            if horizontal:
                cv.hline(6, 12, 12, '#3f86c2')
                cv.px(5 if d == 1 else 18, 12, '#2a5a8a')
                wing = '#dff2ff' if f != 1 else '#bfe0f5'
                wy = 10 if f == 1 else 9
                cv.hline(9, wy, 5, wing)
                cv.hline(9, 24 - wy - 0, 5, wing)
            else:
                cv.vline(12, 6, 12, '#3f86c2')
                wing = '#dff2ff' if f != 1 else '#bfe0f5'
                w = 5 if f == 1 else 6
                cv.hline(12 - w, 9, w, wing)
                cv.hline(13, 9, w, wing)
                cv.hline(12 - w + 1, 11, w - 1, wing)
                cv.hline(13, 11, w - 1, wing)
            fr.append(cv)
        rows.append(fr)
    return object_sheet(rows)


def cat():
    """an orange village cat (walks)"""
    body, lo, hi = '#e8a050', '#c47a34', '#f6c890'
    rows = []
    for d in ('down', 'left', 'right', 'up'):
        fr = []
        for f in range(3):
            cv = Canvas(24, 24)
            step = [-1, 0, 1][f]
            dd = 'left' if d == 'right' else d
            if dd == 'left':
                cv.rect(7, 13, 11, 6, body)
                cv.hline(7, 13, 11, hi)
                cv.rect(4, 9, 7, 6, body)
                cv.px(4, 8, body)
                cv.px(9, 8, body)
                cv.px(5, 11, '#2b2230')
                cv.px(4, 13, '#f2a0b8')
                for i, x in enumerate((8, 15)):
                    cv.rect(x + (step if i == 0 else -step), 19, 2, 3, lo)
                cv.line(18, 14, 21, 9 + (f % 2), body)
                for x in (10, 13, 16):
                    cv.vline(x, 14, 3, lo)
            elif dd == 'down':
                cv.rect(8, 12, 8, 8, body)
                cv.rect(7, 6, 10, 7, body)
                cv.px(7, 5, body)
                cv.px(16, 5, body)
                cv.px(9, 9, '#2b2230')
                cv.px(14, 9, '#2b2230')
                cv.px(11, 11, '#f2a0b8')
                cv.px(12, 11, '#f2a0b8')
                cv.rect(9 + (step < 0), 20, 2, 2, lo)
                cv.rect(13 - (step > 0), 20, 2, 2, lo)
            else:
                cv.rect(8, 12, 8, 8, body)
                cv.rect(7, 6, 10, 7, body)
                cv.px(7, 5, body)
                cv.px(16, 5, body)
                cv.line(12, 19, 14, 22, lo)
                cv.vline(12, 7, 5, lo)
            cv.outline(INK)
            if d == 'right':
                cv = cv.flipped()
            fr.append(cv)
        rows.append(fr)
    return object_sheet(rows)


def sleeping_cat():
    fr = []
    for f in range(3):
        cv = Canvas(24, 24)
        cv.ellipse(12, 16, 7, 4, '#e8a050')
        cv.ellipse(7, 15, 3, 3, '#e8a050')
        cv.px(5, 12, '#e8a050')
        cv.px(8, 12, '#e8a050')
        cv.hline(5, 15, 2, '#2b2230')
        for x in (11, 14, 17):
            cv.vline(x, 13, 2, '#c47a34')
        cv.outline(INK)
        if f == 1:
            draw_text(cv, 17, 0, 'z', '#9ad6f2')
        fr.append(cv)
    return _same_rows(fr)


def chicken():
    body = '#fbf8f2'
    rows = []
    for d in ('down', 'left', 'right', 'up'):
        fr = []
        for f in range(3):
            cv = Canvas(24, 24)
            dd = 'left' if d == 'right' else d
            peck = 1 if f == 1 else 0
            if dd == 'left':
                cv.ellipse(13, 15, 6, 4.5, body)
                cv.ellipse(8, 10 + peck, 3, 3, body)
                cv.px(7, 7 + peck, '#d8302a')
                cv.px(8, 7 + peck, '#d8302a')
                cv.px(5, 10 + peck, '#f0a030')
                cv.px(7, 10 + peck, '#2b2230')
                cv.px(8, 12 + peck, '#d8302a')
                cv.px(18, 12, '#e8e4dc')
                cv.px(19, 11, '#e8e4dc')
                cv.vline(12, 19, 3, '#f0a030')
                cv.vline(15, 19, 3, '#f0a030')
            else:
                cv.ellipse(12, 15, 5, 5, body)
                cv.ellipse(12, 9, 3, 3, body)
                cv.px(12, 6, '#d8302a')
                if dd == 'down':
                    cv.px(11, 9, '#2b2230')
                    cv.px(13, 9, '#2b2230')
                    cv.px(12, 10, '#f0a030')
                cv.vline(10, 19, 3, '#f0a030')
                cv.vline(14, 19, 3, '#f0a030')
            cv.outline(INK)
            if d == 'right':
                cv = cv.flipped()
            fr.append(cv)
        rows.append(fr)
    return object_sheet(rows)


def invisible():
    return _same_rows([Canvas(24, 24)] * 3)


def lantern_glow():
    fr = []
    for f in range(3):
        cv = Canvas(24, 24)
        a = [60, 90, 70][f]
        cv.ellipse(12, 12, 9, 9, (255, 190, 90, a // 2))
        cv.ellipse(12, 12, 4.5, 5, '#e2402f')
        cv.hline(9, 7, 7, '#f0c040')
        cv.hline(9, 17, 7, '#f0c040')
        cv.vline(12, 8, 9, '#f6a03c')
        cv.vline(12, 0, 7, '#3a3540')
        fr.append(cv)
    return _same_rows(fr)


def big_piano():
    """an upright piano as a single 2x2-tile event sprite (48x48 frames)"""
    from objects_inside import piano
    cv, _ = piano()
    out = Canvas(144, 192)
    for r in range(4):
        for c in range(3):
            out.paste(cv, c * 48, r * 48)
    return out


SPRITES = {
    '!$Piano': big_piano,
    '!$Sparkle': sparkle, '!$Note': note, '!$WindChime': wind_chime, '!$GuitarCase': guitar_case,
    '!$Phone': phone, '!$Harmonica': lambda: item_glint(_harmonica), '!$Letter': lambda: item_glint(_envelope),
    '!$Recorder': lambda: item_glint(_recorder), '!$Bouquet': lambda: item_glint(_flowers_bouquet),
    '!$Lyrics': lambda: item_glint(_lyrics), '!$Photo': lambda: item_glint(_photo),
    '!$NewGuitar': lambda: item_glint(_guitar_new),
    '$Dragonfly': dragonfly, '$Cat': cat, '!$CatSleep': sleeping_cat, '$Chicken': chicken,
    '!$Lantern': lantern_glow,
}
