"""Tile layouts of every map in 《余音》 (events are added in story.py).

Each function returns (MapPainter, points) where points holds named
coordinates the story needs (doors, NPC spots...).
"""
import math

from mapgen import MapPainter

# map ids
OLD_HOME, VILLAGE, GRANDPA_HOUSE, APARTMENT, SCHOOL, MUSIC_ROOM, HALL, CITY, BASEMENT = range(1, 10)


def _border_trees(m, skip=()):
    w, h = m.w, m.h
    for x in range(0, w - 1, 2):
        if not any(a <= x <= b or a <= x + 1 <= b for (a, b) in skip):
            m.stamp('tree', x, h - 2)
        m.stamp('tree', x, 0)
    for y in range(2, h - 2, 2):
        m.stamp('tree', 0, y)
        m.stamp('tree', w - 2, y)


def village():
    m = MapPainter(40, 32, 'outside')
    m.fill('grass', 0)
    pts = {}
    # river with a lotus pond
    for y in range(0, 32):
        x0 = 5 + (1 if 6 <= y <= 12 else 0)
        m.rect(x0, y, 3, 1, 'water', z=0)
    m.rect(2, 21, 6, 6, 'water', z=0)
    m.rect(5, 20, 2, 1, 'water', z=0)
    # meadow patches
    m.rect(28, 25, 8, 4, 'meadow')
    m.rect(9, 26, 3, 3, 'meadow')
    m.rect(30, 1, 7, 2, 'meadow')
    # ---- paths ---------------------------------------------------------------
    m.vpath(13, 7, 16)                       # grandpa's door -> square
    m.hpath(2, 16, 16)                       # west road across the bridge
    m.rect(16, 14, 10, 5, 'dirt')            # the square under the old tree (packed earth)
    m.vpath(27, 7, 16)                       # granny li
    m.hpath(25, 33, 16)                      # east road
    m.vpath(33, 14, 16)                      # farmer's door
    m.vpath(20, 18, 27)                      # south to the school
    m.hpath(15, 28, 27, width=1)
    m.rect(14, 26, 5, 1, 'dirt')             # school yard
    m.vpath(26, 27, 31)                      # road out of the village
    m.vpath(28, 25, 27)                      # brick house
    m.rect(31, 17, 6, 5, 'farmland')
    m.rect(1, 13, 4, 4, 'sand')              # fishing spot
    # ---- buildings -------------------------------------------------------------
    m.stamp('grandpa_house', 11, 3)
    pts['grandpa_door'] = (13, 6)
    m.stamp('house_wood', 26, 3)
    pts['li_door'] = (27, 6)
    m.stamp('house_red', 32, 10)
    pts['farmer_door'] = (33, 13)
    m.stamp('school_village', 13, 22)
    pts['school_door'] = (16, 25)
    m.stamp('house_brick', 26, 21)
    pts['brick_door'] = (28, 24)
    m.stamp('shed', 36, 10)
    # ---- the old tree and its square --------------------------------------------
    m.stamp('old_tree', 19, 9)
    pts['tree_root_left'] = (19, 13)
    pts['tree_root_right'] = (22, 13)
    m.stamp('bench', 16, 13)
    m.stamp('bench', 24, 13)
    m.stamp('well', 17, 17)
    m.stamp('popsicle_cart', 21, 25)
    pts['cart_front'] = (23, 27)
    # ---- the river side ------------------------------------------------------------
    for x in range(5, 8):
        m.stamp('bridge_h', x, 16)
    for (x, y) in ((8, 4), (8, 10), (8, 20), (4, 11), (1, 19), (8, 27)):
        m.stamp('reeds', x, y)
    for (x, y) in ((3, 22), (5, 24), (2, 25), (6, 22)):
        m.stamp('lily', x, y)
    m.stamp('boat', 5, 18)
    m.stamp('stepping_stone', 3, 17)
    # ---- farm --------------------------------------------------------------------------
    for x in range(30, 38):
        m.stamp('fence_h', x, 22)
    for x in range(30, 33):
        m.stamp('fence_h', x, 16)
    for x in range(34, 38):
        m.stamp('fence_h', x, 16)
    for y in range(17, 22):
        m.stamp('fence_v', 37, y)
    m.stamp('haystack', 36, 14)
    m.stamp('firewood', 31, 13)
    m.stamp('barrel', 36, 12)
    # ---- the hill with the graves (NE) -------------------------------------------------
    for x in range(32, 38):
        m.stamp('fence_h', x, 6)
    for y in range(3, 6):
        m.stamp('fence_v', 31, y)
    m.stamp('pine', 37, 3)
    m.stamp('pine', 32, 2)
    pts['grave_grandpa'] = (34, 4)
    pts['grave_mom'] = (35, 4)
    m.rect(33, 3, 4, 3, 'meadow')
    m.vpath(33, 5, 9)
    m.clear_objects(33, 6)
    m.rect(33, 6, 1, 1, 'dirt')
    m.vpath(33, 7, 10)
    m.hpath(27, 33, 9)
    # ---- greenery ----------------------------------------------------------------------
    _border_trees(m, skip=[(24, 29)])
    for (x, y) in ((9, 8), (16, 8), (23, 2), (30, 7), (10, 22), (22, 21), (36, 24), (12, 28),
                   (32, 27), (2, 7), (2, 2)):
        m.stamp('tree', x, y)
    pts['cicada_tree'] = (17, 9)       # trunk cell of the tree at (16,8)
    for (x, y) in ((24, 7), (10, 13), (30, 19 - 6), (18, 20), (35, 26)):
        m.stamp('tree_small', x, y)
    for (x, y) in ((11, 7), (16, 7), (25, 8), (30, 8), (12, 20), (24, 20), (29, 20), (21, 21)):
        m.stamp('bush' if (x + y) % 3 else 'bush_pink', x, y)
    for (x, y) in ((10, 6), (17, 6), (25, 6), (24, 6), (14, 21), (19, 21), (30, 24), (25, 25),
                   (11, 16), (12, 12), (17, 19), (23, 19), (29, 14), (38, 9 - 0)):
        m.stamp('flowers' if (x * y) % 2 else 'flowers_warm', x, y)
    for (x, y) in ((10, 3), (3, 5), (36, 28), (13, 29), (30, 29)):
        m.stamp('tall_grass', x, y)
    m.stamp('rock', 11, 18)
    m.stamp('rock', 34, 25)
    m.stamp('clothesline', 16, 4)
    m.stamp('sign_village', 24, 28)
    pts['entrance'] = (26, 30)
    pts['bridge'] = (6, 16)
    pts['stream_spot'] = (6, 15)
    pts['chime'] = (29, 7)
    return m, pts



def _furnish_wall(m, items):
    for (name, x, y) in items:
        m.stamp(name, x, y)


def old_home():
    """林音晚年的家 = 爷爷的老房子（序章、终章）"""
    m = MapPainter(17, 13, 'inside')
    floor = m.room(1, 1, 15, 11, 'old', 'old_floor')
    m.rect(6, 6, 5, 3, 'carpet_red', z=0)
    m.door_gap(8, 11, 'old_floor')
    _furnish_wall(m, [
        ('piano', 3, 3), ('bookshelf', 6, 3), ('bookshelf2', 7, 3), ('clock', 9, 2),
        ('photo0', 10, 2), ('photo1', 11, 2), ('photo2', 12, 2), ('photo3', 13, 2),
        ('window_lattice', 5, 2), ('plant', 2, 3), ('bed_old', 14, 3), ('dresser', 2, 6),
        ('altar_table', 2, 8), ('rocking_chair', 12, 7), ('tea_table', 11, 7), ('radio', 14, 8),
        ('small_table', 13, 7), ('harmonica_case', 13, 7), ('notebooks', 8, 4),
        ('plant', 14, 9),
    ])
    m.auto_shadows()
    pts = dict(door=(8, 11), entry=(8, 10), piano=(3, 4), piano2=(4, 4), stand=(4, 5))
    return m, pts


def grandpa_house():
    """爷爷家（1998年）"""
    m = MapPainter(17, 13, 'inside')
    m.room(1, 1, 15, 11, 'old', 'old_floor')
    m.rect(9, 7, 3, 2, 'tatami', z=0)
    m.door_gap(8, 11, 'old_floor')
    _furnish_wall(m, [
        ('wok_stove', 2, 4), ('window_lattice', 5, 2), ('calendar', 7, 2), ('clock', 9, 2),
        ('window_lattice', 12, 2), ('bed_old', 14, 3), ('wardrobe', 13, 3), ('radio', 4, 4),
        ('table', 5, 7), ('chair_down', 5, 6), ('chair_up', 6, 9), ('bookshelf', 10, 3),
        ('boxes', 2, 9), ('plant', 14, 8), ('dresser', 11, 4),
    ])
    m.auto_shadows()
    pts = dict(door=(8, 11), entry=(8, 10), bed=(14, 4), bedside=(14, 6))
    return m, pts


def apartment():
    """第二章：城市里的家（客厅/厨房 + 林音的房间）"""
    m = MapPainter(21, 15, 'inside')
    m.room(1, 1, 19, 13, 'home', 'wood_floor')
    # partition between living room and bedroom
    for y in range(4, 13):
        if y not in (8, 9):
            m.kind[0][y][12] = ('walltop', 'home')
    m.wall_block(12, 1, 1, 3, 'home')
    m.rect(14, 8, 4, 3, 'carpet_blue', z=0)
    m.rect(2, 11, 2, 1, 'carpet_red', z=0)
    m.door_gap(6, 13, 'wood_floor')
    _furnish_wall(m, [
        # kitchen / living room
        ('stove', 2, 4), ('sink', 3, 4), ('fridge', 4, 3), ('window_wall', 7, 2), ('clock', 9, 2),
        ('dining_table', 6, 6), ('chair_down', 6, 5), ('chair_down', 7, 5),
        ('sofa', 2, 10), ('tv', 2, 12), ('plant', 11, 3), ('shoe_rack', 8, 12), ('calendar', 10, 2),
        # bedroom
        ('bed_blue', 18, 3), ('desk', 13, 4), ('chair_up', 13, 5), ('bookshelf', 16, 3),
        ('window_wall', 17, 2), ('poster_star', 13, 2), ('poster_band', 15, 2), ('wardrobe', 18, 10),
        ('dresser', 18, 8 + 0),
    ])
    m.auto_shadows()
    pts = dict(door=(6, 13), entry=(6, 12), desk=(13, 4), bed=(18, 4), kitchen=(4, 6),
               mom_kitchen=(5, 6), bedroom=(15, 7))
    return m, pts


def school_yard():
    """第一中学（校园）"""
    m = MapPainter(25, 18, 'outside')
    m.fill('grass', 0)
    m.rect(2, 6, 21, 10, 'plaza')
    m.vpath(11, 15, 17, 'plaza', width=3)
    m.stamp('school', 8, 1)
    pts = dict(door=(12, 5), gate=(12, 17))
    m.stamp('flagpole', 5, 3)
    m.stamp('bulletin', 17, 4)
    m.stamp('bike_rack', 19, 7)
    m.stamp('bike_rack', 19, 8)
    for (x, y) in ((0, 0), (2, 0), (16, 0), (18, 0), (20, 0), (22, 0), (0, 2), (22, 2), (0, 4), (23, 4)):
        m.stamp('tree', x, y) if x < 23 else m.stamp('tree_small', x, y)
    for (x, y) in ((1, 7), (1, 10), (1, 13), (23, 9), (23, 12), (3, 16), (8, 16), (16, 16), (20, 16)):
        m.stamp('tree_small', x, y) if y < 16 else m.stamp('bush', x, y)
    for (x, y) in ((4, 11), (8, 11), (15, 11), (18, 11)):
        m.stamp('planter_tree', x, y)
    m.stamp('bench', 5, 13)
    m.stamp('bench', 16, 13)
    m.stamp('trash_bin', 14, 13)
    for x in list(range(0, 10)) + list(range(15, 25)):
        m.stamp('fence_h', x, 17)
    for (x, y) in ((6, 9), (9, 14), (13, 8), (21, 14)):
        m.stamp('flowers', x, y)
    return m, pts


def music_room():
    m = MapPainter(17, 13, 'inside')
    m.room(1, 1, 15, 11, 'school', 'school_floor')
    m.rect(5, 6, 7, 3, 'carpet_blue', z=0)
    m.door_gap(8, 11, 'school_floor')
    _furnish_wall(m, [
        ('blackboard', 6, 2), ('piano', 2, 3), ('drum_kit', 12, 3), ('amp', 14, 4),
        ('window_wall', 4, 2), ('window_wall', 10, 2), ('poster_band', 11, 2),
        ('music_stand', 6, 7), ('music_stand', 8, 7), ('music_stand', 10, 7),
        ('keyboard_stand', 3, 8), ('school_chair', 6, 9), ('school_chair', 8, 9), ('school_chair', 10, 9),
        ('guitar_stand', 14, 7), ('bookshelf', 15, 3) if False else ('plant', 15, 8),
    ])
    m.auto_shadows()
    return m, dict(door=(8, 11), entry=(8, 10))


def hall():
    m = MapPainter(21, 15, 'inside')
    m.room(1, 1, 19, 13, 'hall', 'carpet_red')
    m.rect(3, 4, 15, 3, 'stage', z=0)
    m.door_gap(10, 13, 'carpet_red')
    _furnish_wall(m, [
        ('stage_curtain', 2, 3), ('stage_curtain', 18, 3), ('spotlight', 7, 4), ('spotlight', 13, 4),
        ('mic_stand' if False else 'music_stand', 10, 5), ('amp', 4, 5), ('amp', 16, 5),
        ('drum_kit', 13, 3),
    ])
    for y in (8, 10):
        for x in list(range(3, 10)) + list(range(11, 18)):
            m.stamp('audience_chair', x, y)
    m.auto_shadows()
    pts = dict(door=(10, 13), entry=(10, 12), stage=(10, 6), stage_left=(8, 6), stage_right=(12, 6),
               back=(10, 12))
    return m, pts


def city():
    """第三章：雪夜的城市街道"""
    m = MapPainter(34, 16, 'outside')
    m.fill('sidewalk', 0)
    m.rect(0, 9, 34, 3, 'asphalt', z=0)
    m.rect(0, 0, 34, 2, 'night_void', z=0)
    m.rect(9, 2, 4, 0, 'night_void', z=0)
    pts = {}
    m.stamp('record_company', 0, 0)
    pts['record_door'] = (2, 5)
    m.stamp('shop_a', 5, 1)
    m.stamp('cafe', 9, 2)
    pts['cafe_door'] = (11, 5)
    m.stamp('apartment', 13, 1)
    pts['home_door'] = (16, 5)
    m.stamp('convenience', 19, 1)
    m.stamp('shop_b', 23, 1)
    m.stamp('shop_c', 27, 1)
    m.stamp('neon_live', 31, 2)
    m.stamp('neon_bar', 31, 4)
    for x in range(1, 34, 3):
        m.stamp('road_line', x, 10)
    for y in (9, 10, 11):
        m.stamp('crosswalk', 15, y)
        m.stamp('crosswalk', 16, y)
    m.stamp('subway', 21, 12)
    pts['subway'] = (22, 13)
    pts['busk'] = (19, 13)
    for x in (4, 9, 26, 31):
        m.stamp('streetlamp', x, 6)
    for x in (2, 13, 28):
        m.stamp('streetlamp', x, 12)
    m.stamp('vending', 25, 6)
    m.stamp('trash_bin', 27, 7)
    m.stamp('bus_stop', 7, 12)
    m.stamp('bench', 9, 13)
    m.stamp('snowman', 30, 13)
    for x in (0, 4, 11, 16, 25, 33):
        m.stamp('planter_tree', x, 14)
    m.cells([(29, 14), (30, 15), (31, 15), (32, 14), (0, 7), (1, 7), (18, 15), (19, 15), (12, 6),
             (23, 8), (24, 8), (6, 15), (7, 15)], 'snow')
    return m, pts


def basement():
    """第三章：地下室出租屋"""
    m = MapPainter(17, 13, 'inside')
    m.fill(None)
    m.room(3, 1, 11, 10, 'basement', 'concrete')
    m.door_gap(8, 10, 'concrete')
    _furnish_wall(m, [
        ('window_night', 7, 2), ('calendar', 5, 2), ('poster_star', 10, 2),
        ('mattress', 11, 4), ('noodles_table', 9, 5), ('guitar_stand', 4, 3), ('boxes', 4, 8),
        ('boxes', 5, 8), ('cd_stack', 6, 4), ('laundry', 12, 7), ('heater', 10, 8),
    ])
    m.auto_shadows()
    return m, dict(door=(8, 10), entry=(8, 9), phone=(9, 5))


ALL = {
    OLD_HOME: ('琴房', old_home), VILLAGE: ('清水村', village), GRANDPA_HOUSE: ('爷爷家', grandpa_house),
    APARTMENT: ('家', apartment), SCHOOL: ('第一中学', school_yard), MUSIC_ROOM: ('音乐教室', music_room),
    HALL: ('礼堂', hall), CITY: ('城市·雪夜', city), BASEMENT: ('出租屋', basement),
}


if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'art'))
    from mvrender import render_map
    from mapgen import TILESETS
    out = sys.argv[1]
    for mid, (name, fn) in ALL.items():
        m, pts = fn()
        mp = {'width': m.w, 'height': m.h, 'data': m.data()}
        img = render_map(mp, TILESETS[m.tileset_id - 1],
                         os.path.join(os.path.dirname(__file__), '..', '..', 'YuYin', 'img', 'tilesets'))
        img.save(os.path.join(out, 'map%02d.png' % mid))
