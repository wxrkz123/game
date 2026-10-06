"""Interior furniture.  Same conventions as objects_outside:
returns (canvas, flags) with flags chars o / x / * / c.
Tall pieces put their upper tile on '*' so characters walking behind are hidden.
"""
import math

from pixlib import Canvas, TILE, rgba, shade, mix, rng
from draw import furniture, window, door, box, shadow_ellipse, blob
from textutil import draw_text
import palette as P

T = TILE
INK = '#3a3540'


def _floor_shadow(cv, x, y, w):
    cv.hline(x, y, w, (20, 15, 25, 70))


def bed(blanket='#d8574f', pillow=P.WHITE, frame=P.WOOD):
    cv = Canvas(24, 48)
    # headboard
    cv.rect(2, 2, 20, 8, frame)
    cv.hline(2, 2, 20, shade(frame, 1.2))
    cv.rect(2, 10, 20, 34, shade(frame, 0.85))
    # mattress & pillow
    cv.rect(3, 8, 18, 34, '#f4efe4')
    cv.rect(5, 9, 14, 7, pillow)
    cv.hline(5, 15, 14, shade(pillow, 0.85))
    # blanket
    cv.rect(3, 18, 18, 24, blanket)
    cv.hline(3, 18, 18, shade(blanket, 1.25))
    cv.hline(3, 19, 18, P.WHITE)
    for y in range(24, 42, 6):
        cv.hline(4, y, 16, shade(blanket, 0.88))
    cv.rect(2, 42, 20, 3, shade(frame, 0.7))
    _floor_shadow(cv, 2, 45, 20)
    return cv, ['*', 'x']


def bed_old():
    """grandpa's wooden bed with a floral quilt"""
    cv, f = bed(blanket='#3f6fb0', frame=P.WOOD_LO)
    r = rng(3)
    for _ in range(16):
        x, y = r.randrange(4, 20), r.randrange(21, 41)
        cv.px(x, y, '#f2a0b8')
        cv.px(x + 1, y, '#f7d55c')
    return cv, f


def mattress():
    cv = Canvas(24, 48)
    cv.rect(2, 10, 20, 34, '#d9d4c8')
    cv.rect(4, 12, 14, 6, '#efebe2')
    cv.rect(2, 22, 20, 22, '#7f8a96')
    cv.hline(2, 22, 20, '#9aa5b1')
    cv.line(4, 30, 18, 36, '#6b7682')
    _floor_shadow(cv, 2, 44, 20)
    return cv, ['o', 'x']


def table(w=2, h=2, top=P.WOOD_HI, front=P.WOOD):
    W, H = w * T, h * T
    cv = Canvas(W, H)
    furniture(cv, 2, 6, W - 4, H - 18, 6, top, front)
    for x in (3, W - 6):
        cv.rect(x, H - 12, 3, 9, shade(front, 0.75))
    _floor_shadow(cv, 3, H - 3, W - 6)
    return cv, ['x' * w] * h


def dining_table():
    cv, f = table(2, 2)
    # bowls & dishes
    for (x, c) in ((10, '#f4efe4'), (22, '#f4efe4'), (34, '#f4efe4')):
        cv.ellipse(x, 16, 4, 3, c)
        cv.ellipse(x, 15, 2.5, 1.5, ['#e8a050', '#7fb85a', '#d8574f'][(x // 12) % 3])
    cv.rect(18, 24, 12, 2, P.WOOD_DEEP)
    return cv, f


def small_table():
    cv = Canvas(24, 24)
    furniture(cv, 3, 6, 18, 8, 5, P.WOOD_HI, P.WOOD)
    cv.rect(4, 19, 2, 4, P.WOOD_LO)
    cv.rect(18, 19, 2, 4, P.WOOD_LO)
    return cv, ['x']


def tea_table():
    cv, f = small_table()
    cv.ellipse(9, 9, 3, 2, '#e8e4dc')
    cv.rect(8, 7, 3, 2, '#5aa08a')
    for x in (14, 17):
        cv.ellipse(x, 10, 1.5, 1, '#e8e4dc')
    return cv, f


def chair(facing='down'):
    cv = Canvas(24, 24)
    if facing == 'down':
        cv.rect(6, 2, 12, 9, P.WOOD)
        cv.hline(6, 2, 12, P.WOOD_HI)
        cv.vline(8, 3, 7, P.WOOD_LO)
        cv.vline(15, 3, 7, P.WOOD_LO)
        furniture(cv, 5, 11, 14, 4, 3, P.WOOD_HI, P.WOOD_LO)
    else:
        furniture(cv, 5, 6, 14, 4, 3, P.WOOD_HI, P.WOOD_LO)
        cv.rect(6, 12, 12, 6, P.WOOD)
        cv.hline(6, 12, 12, P.WOOD_HI)
    cv.rect(6, 18, 2, 5, P.WOOD_DEEP)
    cv.rect(16, 18, 2, 5, P.WOOD_DEEP)
    return cv, ['x']


def desk(items=True, color=P.WOOD):
    cv = Canvas(48, 24)
    furniture(cv, 2, 2, 44, 9, 11, shade(color, 1.15), color)
    # drawers
    for x in (6, 32):
        cv.rect(x, 13, 10, 7, shade(color, 0.9))
        cv.frame(x, 13, 10, 7, shade(color, 0.7))
        cv.px(x + 5, 16, P.DIRT_HI)
    if items:
        cv.rect(8, 3, 10, 7, '#3f6fb0')       # book
        cv.rect(9, 4, 8, 5, '#f4efe4')
        cv.vline(13, 4, 5, '#c9c2b2')
        cv.rect(34, 2, 2, 7, INK)               # lamp
        cv.rect(31, 1, 8, 3, '#f0c040')
        cv.rect(22, 5, 6, 3, '#e8584f')         # pencil case
    return cv, ['xx']


def bookshelf(seed=1):
    cv = Canvas(24, 48)
    cv.rect(1, 2, 22, 43, P.WOOD_LO)
    cv.rect(1, 2, 22, 3, P.WOOD)
    cv.hline(1, 2, 22, P.WOOD_HI)
    r = rng(seed)
    for sy in (6, 18, 30):
        cv.rect(3, sy, 18, 10, P.WOOD_DEEP)
        x = 3
        while x < 20:
            w = r.choice((2, 2, 3))
            h = r.randrange(7, 10)
            c = r.choice(['#d8574f', '#3f6fb0', '#5a9a5a', '#e8b83a', '#8a5aa6', '#e8e4dc', '#c46a3a'])
            cv.rect(x, sy + 10 - h, w, h, c)
            cv.px(x, sy + 10 - h, shade(c, 1.25))
            x += w
        cv.hline(2, sy + 10, 20, P.WOOD)
    cv.rect(1, 42, 22, 3, P.WOOD)
    _floor_shadow(cv, 1, 45, 22)
    return cv, ['*', 'x']


def wardrobe():
    cv = Canvas(24, 48)
    cv.rect(1, 2, 22, 43, P.WOOD)
    cv.hline(1, 2, 22, P.WOOD_HI)
    cv.vline(12, 5, 37, P.WOOD_LO)
    cv.frame(3, 5, 8, 37, P.WOOD_LO)
    cv.frame(13, 5, 8, 37, P.WOOD_LO)
    cv.px(10, 24, P.DIRT_HI)
    cv.px(14, 24, P.DIRT_HI)
    cv.rect(1, 42, 22, 3, P.WOOD_DEEP)
    _floor_shadow(cv, 1, 45, 22)
    return cv, ['*', 'x']


def dresser():
    cv = Canvas(24, 24)
    furniture(cv, 2, 3, 20, 5, 15, P.WOOD_HI, P.WOOD)
    for y in (10, 15):
        cv.hline(3, y, 18, P.WOOD_LO)
        cv.px(12, y + 2, P.DIRT_HI)
    cv.rect(15, 0, 5, 4, '#f2a0b8')  # little vase
    cv.px(17, 0, P.LEAF)
    return cv, ['x']


def piano():
    """upright piano (2x2)"""
    cv = Canvas(48, 48)
    body = '#3a2a2e'
    cv.rect(2, 4, 44, 40, body)
    cv.hline(2, 4, 44, '#5c4448')
    cv.rect(2, 4, 44, 4, '#4a363a')
    # sheet music
    cv.rect(14, 9, 9, 11, P.WHITE)
    cv.rect(24, 9, 9, 11, '#f4efe4')
    for y in range(11, 19, 2):
        cv.hline(15, y, 7, '#9a9aa8')
        cv.hline(25, y, 7, '#9a9aa8')
    cv.px(17, 12, INK)
    cv.px(19, 14, INK)
    cv.px(27, 13, INK)
    # keyboard
    cv.rect(3, 24, 42, 7, P.WHITE)
    for x in range(3, 45, 3):
        cv.vline(x, 24, 7, '#c9c5bc')
    for x in range(4, 44, 3):
        if (x // 3) % 7 not in (2, 6):
            cv.rect(x + 1, 24, 2, 4, INK)
    cv.hline(3, 31, 42, '#24181b')
    # legs/pedals
    cv.rect(4, 32, 40, 11, '#30222a')
    cv.rect(20, 40, 8, 2, '#d0b060')
    # candle-ish lamp on top
    cv.rect(38, 1, 4, 4, '#f0c040')
    _floor_shadow(cv, 2, 44, 44)
    return cv, ['**', 'xx']


def guitar_stand(body='#c97a3a'):
    cv = Canvas(24, 48)
    # neck
    cv.rect(11, 4, 3, 22, P.WOOD_DEEP)
    cv.rect(10, 2, 5, 5, INK)
    for y in range(8, 25, 4):
        cv.hline(11, y, 3, '#c9c5bc')
    # body
    cv.ellipse(12, 30, 7, 6, body)
    cv.ellipse(12, 38, 9, 7, body)
    cv.ellipse(12, 33, 2.5, 2.5, '#2a1a12')
    cv.ellipse(10, 29, 2, 1.5, shade(body, 1.25))
    cv.rect(9, 40, 7, 2, '#2a1a12')
    # stand
    cv.line(6, 45, 12, 40, INK)
    cv.line(18, 45, 12, 40, INK)
    _floor_shadow(cv, 4, 46, 16)
    return cv, ['*', 'x']


def window_wall(curtain='#e8c8a0', night=False):
    cv = Canvas(24, 24)
    window(cv, 3, 3, 18, 16, frame=P.WOOD_LO, glass='#2f3f66' if night else '#a8d4f0', cross=True, sill=True)
    if not night:
        cv.px(6, 5, P.WHITE)
        cv.px(14, 12, P.WHITE)
    cv.rect(1, 1, 5, 20, curtain)
    cv.rect(18, 1, 5, 20, curtain)
    cv.vline(3, 2, 18, shade(curtain, 0.85))
    cv.vline(20, 2, 18, shade(curtain, 0.85))
    cv.hline(0, 1, 24, P.WOOD_DEEP)
    return cv, ['x']


def lattice_window_wall():
    cv = Canvas(24, 24)
    cv.rect(2, 3, 20, 17, P.WOOD_DEEP)
    cv.rect(3, 4, 18, 15, '#f1e6c8')
    for x in range(5, 21, 3):
        cv.vline(x, 4, 15, P.WOOD_LO)
    for y in range(6, 19, 3):
        cv.hline(3, y, 18, P.WOOD_LO)
    return cv, ['x']


def wall_clock():
    cv = Canvas(24, 24)
    cv.ellipse(12, 11, 7, 7, P.WOOD_LO)
    cv.ellipse(12, 11, 5.5, 5.5, P.WHITE)
    cv.vline(12, 7, 5, INK)
    cv.hline(12, 11, 3, INK)
    return cv, ['x']


def photo_frame(kind=0):
    cv = Canvas(24, 24)
    cv.rect(5, 5, 14, 12, P.WOOD_LO)
    cv.rect(6, 6, 12, 10, ['#cfe6f2', '#f6e3c2', '#d9e8cf', '#e8d8f0'][kind % 4])
    # tiny people silhouettes
    if kind % 2 == 0:
        cv.rect(9, 10, 2, 5, INK)
        cv.px(9, 9, P.SKIN)
        cv.rect(13, 11, 2, 4, '#d8574f')
        cv.px(13, 10, P.SKIN)
    else:
        cv.rect(7, 12, 10, 4, P.LEAF)
        cv.ellipse(14, 9, 2, 2, '#f7d55c')
    return cv, ['x']


def calendar():
    cv = Canvas(24, 24)
    cv.rect(7, 4, 10, 14, P.WHITE)
    cv.rect(7, 4, 10, 4, '#d8574f')
    for y in range(10, 17, 2):
        for x in range(8, 16, 2):
            cv.px(x, y, '#9a9aa8')
    cv.px(12, 3, INK)
    return cv, ['x']


def poster(col='#3f6fb0', accent='#f7d55c'):
    cv = Canvas(24, 24)
    cv.rect(5, 3, 14, 18, col)
    cv.ellipse(12, 10, 4, 4, accent)
    cv.rect(11, 9, 1, 1, col)
    cv.rect(7, 16, 10, 2, P.WHITE)
    cv.px(5, 3, '#c9c5bc')
    cv.px(18, 3, '#c9c5bc')
    return cv, ['x']


def stove():
    cv = Canvas(24, 24)
    furniture(cv, 2, 2, 20, 9, 11, '#d8d4cc', '#b8b4ac')
    for x in (7, 16):
        cv.ellipse(x, 6, 3, 2, INK)
        cv.ellipse(x, 6, 1.5, 1, '#e8584f')
    cv.rect(5, 15, 14, 5, '#55505c')
    return cv, ['x']


def wok_stove():
    """old village stove (灶台) 2x1 brick with a wok"""
    cv = Canvas(48, 24)
    from draw import wall_brick
    wall_brick(cv, 2, 8, 44, 14, base='#b5644c', lo='#8c4838', mortar='#dcc6a6')
    cv.rect(2, 3, 44, 6, '#cfc5b4')
    cv.ellipse(14, 6, 7, 3, INK)
    cv.ellipse(14, 6, 5, 2, '#55505c')
    cv.rect(30, 2, 10, 6, P.WOOD)
    cv.rect(10, 14, 8, 6, '#2a1f1a')
    cv.px(13, 17, '#f08a3a')
    cv.px(14, 18, '#f7d55c')
    return cv, ['xx']


def sink():
    cv = Canvas(24, 24)
    furniture(cv, 2, 2, 20, 9, 11, '#e8e4dc', '#c9c5bc')
    cv.rect(6, 4, 12, 5, '#9fb8c8')
    cv.rect(11, 1, 2, 4, '#9a9aa8')
    return cv, ['x']


def fridge():
    cv = Canvas(24, 48)
    cv.rect(2, 4, 20, 40, '#e9eef1')
    cv.vline(2, 4, 40, '#ffffff')
    cv.vline(21, 4, 40, '#c2cbd1')
    cv.hline(2, 20, 20, '#c2cbd1')
    cv.rect(18, 10, 2, 7, '#9aa5b1')
    cv.rect(18, 24, 2, 9, '#9aa5b1')
    cv.rect(6, 8, 4, 4, '#f2a0b8')  # magnet note
    _floor_shadow(cv, 2, 44, 20)
    return cv, ['*', 'x']


def sofa(color='#7f9a6a'):
    cv = Canvas(48, 24)
    cv.rect(2, 2, 44, 10, shade(color, 0.9))
    cv.hline(2, 2, 44, shade(color, 1.15))
    cv.rect(2, 10, 44, 10, color)
    cv.vline(23, 11, 8, shade(color, 0.85))
    cv.rect(0, 6, 4, 15, shade(color, 0.8))
    cv.rect(44, 6, 4, 15, shade(color, 0.8))
    cv.hline(2, 20, 44, shade(color, 0.7))
    return cv, ['xx']


def tv():
    cv = Canvas(24, 24)
    furniture(cv, 2, 12, 20, 3, 8, P.WOOD_HI, P.WOOD)
    cv.rect(3, 1, 18, 12, INK)
    cv.rect(4, 2, 16, 9, '#4a5a7a')
    cv.px(6, 4, '#8aa0c8')
    return cv, ['x']


def student_desk():
    cv = Canvas(24, 24)
    furniture(cv, 2, 4, 20, 7, 6, '#d9b98a', '#b8925e')
    cv.rect(3, 17, 2, 6, '#7a7a86')
    cv.rect(19, 17, 2, 6, '#7a7a86')
    cv.rect(6, 5, 7, 5, P.WHITE)
    return cv, ['x']


def school_chair():
    cv = Canvas(24, 24)
    furniture(cv, 6, 8, 12, 4, 3, '#d9b98a', '#b8925e')
    cv.rect(6, 15, 12, 4, '#9a9aa8')
    cv.rect(7, 18, 2, 5, '#7a7a86')
    cv.rect(15, 18, 2, 5, '#7a7a86')
    return cv, ['x']


def blackboard():
    cv = Canvas(72, 48)
    cv.rect(2, 4, 68, 36, P.WOOD_LO)
    cv.rect(4, 6, 64, 32, '#2f5a46')
    draw_text(cv, 36, 8, '文艺汇演', '#f4efe4', center=True)
    # staff lines + notes
    for y in (26, 29, 32):
        cv.hline(10, y, 52, '#c9d8cc')
    for (x, y) in ((16, 30), (24, 27), (32, 25), (40, 27), (48, 30)):
        cv.ellipse(x, y, 2, 1.5, '#f4efe4')
        cv.vline(x + 2, y - 6, 6, '#f4efe4')
    cv.rect(4, 38, 64, 3, P.WOOD)
    cv.rect(50, 37, 6, 2, P.WHITE)
    return cv, ['xxx', 'xxx']


def podium():
    cv = Canvas(24, 24)
    furniture(cv, 3, 4, 18, 5, 14, '#c9a070', '#a77a4c')
    cv.rect(9, 12, 6, 4, '#d8302a')
    return cv, ['x']


def drum_kit():
    cv = Canvas(48, 48)
    # cymbals
    cv.ellipse(8, 12, 7, 2, '#e8c860')
    cv.vline(8, 13, 22, '#9a9aa8')
    cv.ellipse(40, 10, 7, 2, '#e8c860')
    cv.vline(40, 11, 24, '#9a9aa8')
    # toms
    for (x, y) in ((18, 18), (30, 18)):
        cv.ellipse(x, y, 6, 3, '#f4efe4')
        cv.rect(x - 6, y, 12, 6, '#c2453f')
    # bass drum
    cv.ellipse(24, 34, 11, 10, '#c2453f')
    cv.ellipse(24, 34, 9, 8, '#f4efe4')
    draw_text(cv, 24, 28, '音', '#c2453f', center=True)
    # snare
    cv.ellipse(10, 34, 5, 2, '#f4efe4')
    cv.rect(5, 34, 10, 5, '#b8b8c2')
    _floor_shadow(cv, 8, 45, 32)
    return cv, ['**', 'xx']


def amp():
    cv = Canvas(24, 24)
    cv.rect(3, 4, 18, 17, '#2a2630')
    cv.rect(4, 5, 16, 3, '#55505c')
    for x in range(6, 18, 3):
        cv.px(x, 6, '#e8c860')
    cv.rect(5, 9, 14, 10, '#45404c')
    for y in range(10, 19, 2):
        cv.hline(5, y, 14, '#3a3540')
    return cv, ['x']


def music_stand():
    cv = Canvas(24, 24)
    cv.rect(5, 3, 14, 9, INK)
    cv.rect(6, 4, 12, 7, P.WHITE)
    for y in (5, 7, 9):
        cv.hline(7, y, 10, '#9a9aa8')
    cv.vline(12, 12, 9, INK)
    cv.line(8, 22, 12, 20, INK)
    cv.line(16, 22, 12, 20, INK)
    return cv, ['x']


def keyboard_stand():
    cv = Canvas(48, 24)
    cv.rect(2, 4, 44, 9, INK)
    cv.rect(4, 6, 40, 5, P.WHITE)
    for x in range(4, 44, 3):
        cv.vline(x, 6, 5, '#c9c5bc')
        if (x // 3) % 7 not in (2, 6):
            cv.rect(x + 1, 6, 2, 3, INK)
    cv.line(8, 22, 16, 13, '#55505c')
    cv.line(16, 22, 8, 13, '#55505c')
    cv.line(32, 22, 40, 13, '#55505c')
    cv.line(40, 22, 32, 13, '#55505c')
    return cv, ['xx']


def stage_curtain():
    cv = Canvas(24, 48)
    for x in range(24):
        c = '#a82a34' if (x // 3) % 2 == 0 else '#8a1f2a'
        cv.vline(x, 0, 46, c)
    cv.rect(0, 0, 24, 5, '#c9a040')
    for x in range(0, 24, 4):
        cv.px(x + 1, 5, '#c9a040')
    return cv, ['*', 'x']


def audience_chair():
    cv = Canvas(24, 24)
    cv.rect(4, 10, 16, 4, '#a82a34')
    cv.rect(4, 4, 16, 7, '#8a1f2a')
    cv.hline(4, 4, 16, '#c43a44')
    cv.rect(4, 14, 16, 3, '#55505c')
    cv.rect(5, 17, 2, 5, '#3a3540')
    cv.rect(17, 17, 2, 5, '#3a3540')
    return cv, ['x']


def spotlight():
    cv = Canvas(24, 24)
    cv.rect(8, 2, 8, 6, INK)
    cv.ellipse(12, 9, 4, 2, '#fff3b8')
    for y in range(11, 24):
        w = (y - 9) // 2 + 3
        for x in range(12 - w, 12 + w):
            cv.px(x, y, (255, 245, 190, 40))
    return cv, ['*']


def boxes():
    cv = Canvas(24, 24)
    furniture(cv, 2, 8, 14, 4, 10, '#d9b98a', '#b8925e')
    cv.vline(9, 8, 4, '#a07a48')
    furniture(cv, 9, 2, 12, 4, 8, '#e2c69a', '#c4a070')
    cv.rect(11, 8, 6, 2, '#f4efe4')
    return cv, ['x']


def noodles_table():
    """low table covered with instant noodle cups and lyric sheets"""
    cv, f = small_table()
    cv.rect(6, 5, 4, 4, '#f4efe4')
    cv.hline(6, 5, 4, '#e8584f')
    cv.rect(12, 7, 7, 5, P.WHITE)
    cv.hline(13, 8, 5, '#9a9aa8')
    cv.hline(13, 10, 4, '#9a9aa8')
    return cv, f


def cd_stack():
    cv = Canvas(24, 24)
    for i in range(6):
        y = 18 - i * 2
        cv.rect(6 + (i % 2), y, 12, 2, ['#3f6fb0', '#e8584f', '#f4efe4'][i % 3])
        cv.hline(6 + (i % 2), y, 12, '#c9c5bc')
    draw_text(cv, 12, 0, '♪', '#e8584f', center=True)
    return cv, ['x']


def heater():
    cv = Canvas(24, 24)
    cv.rect(5, 6, 14, 15, '#c9c5bc')
    for y in range(8, 19, 2):
        cv.hline(7, y, 10, '#f08a3a')
    cv.rect(5, 6, 14, 2, '#9a9aa8')
    return cv, ['x']


def altar_table():
    """供桌 with grandpa's photo, incense and fruit (2x1)"""
    cv = Canvas(48, 24)
    furniture(cv, 2, 6, 44, 6, 12, '#8a3a2a', '#6e2a20')
    cv.rect(18, 0, 12, 10, P.WOOD_DEEP)
    cv.rect(19, 1, 10, 8, '#e8e4dc')
    cv.ellipse(24, 4, 2, 2, '#9a9aa8')
    cv.rect(22, 6, 5, 3, '#6a6a76')
    cv.ellipse(9, 8, 3, 2, '#f08a3a')
    cv.ellipse(38, 8, 3, 2, '#e8584f')
    cv.vline(34, 2, 6, '#c9a070')
    cv.px(34, 1, '#e8584f')
    return cv, ['xx']


def radio():
    cv = Canvas(24, 24)
    cv.rect(3, 6, 18, 12, '#8a5a3a')
    cv.hline(3, 6, 18, '#a8744c')
    cv.rect(5, 8, 8, 8, '#e8d8b0')
    for y in range(9, 16, 2):
        cv.hline(5, y, 8, '#a89870')
    cv.ellipse(17, 10, 2, 2, '#e8c860')
    cv.ellipse(17, 15, 1.5, 1.5, '#e8c860')
    cv.line(8, 6, 14, 1, '#9a9aa8')
    return cv, ['x']


def rocking_chair():
    cv = Canvas(24, 24)
    cv.rect(6, 1, 12, 10, P.WOOD)
    for x in range(7, 18, 3):
        cv.vline(x, 2, 8, P.WOOD_LO)
    furniture(cv, 5, 11, 14, 4, 2, P.WOOD_HI, P.WOOD)
    cv.rect(7, 13, 10, 3, '#d8574f')
    for x in range(3, 22):
        y = 21 - int(2 * math.sin((x - 3) / 18 * math.pi))
        cv.px(x, y, P.WOOD_DEEP)
    cv.vline(7, 17, 4, P.WOOD_LO)
    cv.vline(16, 17, 4, P.WOOD_LO)
    return cv, ['x']


def plant():
    cv = Canvas(24, 48)
    cv.rect(7, 36, 10, 9, '#c46a3a')
    cv.hline(6, 36, 12, '#d8844c')
    c2 = Canvas(24, 48)
    for (x, y, rx, ry, s) in ((12, 26, 8, 9, 1), (8, 18, 5, 6, 2), (16, 16, 5, 7, 3)):
        blob(c2, x, y, rx, ry, P.LEAF, P.LEAF_HI, P.LEAF_LO, seed=s, bumpy=0.25)
    c2.outline(P.LEAF_DEEP)
    cv.blit(c2, 0, 0)
    _floor_shadow(cv, 6, 45, 12)
    return cv, ['*', 'x']


def doormat():
    cv = Canvas(24, 24)
    cv.rect(3, 6, 18, 14, '#a07850')
    cv.frame(3, 6, 18, 14, '#7a5a3a')
    for x in range(5, 19, 2):
        cv.vline(x, 8, 10, '#8a6440')
    return cv, ['o']


def door_wall(col=P.WOOD):
    cv = Canvas(24, 48)
    cv.rect(2, 4, 20, 44, shade(col, 0.6))
    door(cv, 4, 8, 16, 40, col=col)
    return cv, ['x', 'o']


def stairs_down():
    cv = Canvas(24, 24)
    for i, y in enumerate(range(0, 24, 4)):
        c = shade('#9a8a78', 1 - i * 0.1)
        cv.rect(2, y, 20, 4, c)
        cv.hline(2, y, 20, shade(c, 1.2))
    cv.vline(1, 0, 24, P.WOOD_DEEP)
    cv.vline(22, 0, 24, P.WOOD_DEEP)
    return cv, ['o']


def counter():
    cv = Canvas(24, 24)
    furniture(cv, 0, 4, 24, 7, 12, '#d9b98a', P.WOOD)
    return cv, ['c']


def coffee_machine():
    cv = Canvas(24, 24)
    furniture(cv, 0, 4, 24, 7, 12, '#d9b98a', P.WOOD)
    cv.rect(6, 0, 12, 9, '#55505c')
    cv.rect(8, 2, 8, 3, '#9a9aa8')
    cv.rect(10, 6, 4, 2, P.WHITE)
    return cv, ['c']


def harmonica_case():
    """open wooden box holding a harmonica, on a stand"""
    cv = Canvas(24, 24)
    furniture(cv, 4, 8, 16, 7, 6, P.WOOD_HI, P.WOOD)
    cv.rect(6, 9, 12, 4, '#d8302a')
    cv.rect(7, 10, 10, 2, '#c9c5bc')
    for x in range(8, 17, 2):
        cv.px(x, 11, INK)
    return cv, ['x']


def notebooks():
    cv = Canvas(24, 24)
    for i, c in enumerate(('#c46a3a', '#3f6fb0', '#e8b83a', '#5a9a5a')):
        cv.rect(4 + i, 16 - i * 3, 15, 3, c)
        cv.hline(4 + i, 16 - i * 3, 15, shade(c, 1.2))
    return cv, ['x']


def laundry():
    cv = Canvas(24, 48)
    cv.vline(3, 10, 36, '#9a9aa8')
    cv.vline(20, 10, 36, '#9a9aa8')
    cv.hline(3, 12, 18, '#9a9aa8')
    cv.rect(5, 13, 6, 10, '#7fb8d6')
    cv.rect(12, 13, 7, 8, P.WHITE)
    return cv, ['*', 'x']


def shoe_rack():
    cv = Canvas(24, 24)
    furniture(cv, 2, 8, 20, 4, 10, P.WOOD_HI, P.WOOD)
    for (x, c) in ((4, '#d8574f'), (12, INK)):
        cv.rect(x, 4, 6, 4, c)
    return cv, ['x']


def bathtub_less_rug():
    cv = Canvas(24, 24)
    cv.ellipse(12, 12, 10, 7, '#e8c8a0')
    cv.ellipse(12, 12, 7, 4.5, '#d8a878')
    return cv, ['o']


OBJECTS = {
    'bed_red': bed, 'bed_blue': lambda: bed('#3f6fb0'), 'bed_grey': lambda: bed('#8a8a96', frame=P.WOOD_LO),
    'bed_old': bed_old, 'mattress': mattress,
    'dining_table': dining_table, 'table': lambda: table(2, 2), 'small_table': small_table,
    'tea_table': tea_table, 'chair_down': lambda: chair('down'), 'chair_up': lambda: chair('up'),
    'desk': desk, 'desk_plain': lambda: desk(False), 'bookshelf': bookshelf,
    'bookshelf2': lambda: bookshelf(7), 'wardrobe': wardrobe, 'dresser': dresser,
    'piano': piano, 'guitar_stand': guitar_stand, 'window_wall': window_wall,
    'window_night': lambda: window_wall('#9a8ac0', True), 'window_lattice': lattice_window_wall,
    'clock': wall_clock, 'photo0': lambda: photo_frame(0), 'photo1': lambda: photo_frame(1),
    'photo2': lambda: photo_frame(2), 'photo3': lambda: photo_frame(3), 'calendar': calendar,
    'poster_band': poster, 'poster_star': lambda: poster('#8a5aa6', '#f2a0b8'),
    'stove': stove, 'wok_stove': wok_stove, 'sink': sink, 'fridge': fridge, 'sofa': sofa, 'tv': tv,
    'student_desk': student_desk, 'school_chair': school_chair, 'blackboard': blackboard,
    'podium': podium, 'drum_kit': drum_kit, 'amp': amp, 'music_stand': music_stand,
    'keyboard_stand': keyboard_stand, 'stage_curtain': stage_curtain, 'audience_chair': audience_chair,
    'spotlight': spotlight, 'boxes': boxes, 'noodles_table': noodles_table, 'cd_stack': cd_stack,
    'heater': heater, 'altar_table': altar_table, 'radio': radio, 'rocking_chair': rocking_chair,
    'plant': plant, 'doormat': doormat, 'door_wall': door_wall, 'stairs_down': stairs_down,
    'counter': counter, 'coffee_machine': coffee_machine, 'harmonica_case': harmonica_case,
    'notebooks': notebooks, 'laundry': laundry, 'shoe_rack': shoe_rack, 'rug_round': bathtub_less_rug,
}
