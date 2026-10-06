"""Write every data/*.json file of 《余音》.

    python3 tools/build/build_data.py

WARNING: this regenerates the maps and the database from the Python
source.  Once you start editing the game inside RPG Maker MV, do not run this
script again (it would overwrite your edits).
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import maps as M
import story
from mvdata import build, Cmd, map_json, audio
from story_core import S, V, I, CE, SWITCH_NAMES, VAR_NAMES
from mapgen import META, TILESETS

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'YuYin'))
DATA = os.path.join(ROOT, 'data')


def dump(name, obj):
    with open(os.path.join(DATA, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))


# ---------------------------------------------------------------------------
# database
# ---------------------------------------------------------------------------

def actors():
    return [None, {
        'id': 1, 'battlerName': '', 'characterIndex': 0, 'characterName': '$Yin_Old', 'classId': 1,
        'equips': [0, 0, 0, 0, 0], 'faceIndex': 0, 'faceName': '', 'traits': [], 'initialLevel': 1,
        'maxLevel': 99, 'name': '林音', 'nickname': '清水小学的林老师', 'note': '',
        'profile': '一辈子都放不下音乐的人。',
    }]


def classes():
    params = [[0] + [500 + 50 * l for l in range(1, 100)], [0] + [100 + 10 * l for l in range(1, 100)]]
    for base in (20, 20, 20, 20, 20, 20):
        params.append([0] + [base + 2 * l for l in range(1, 100)])
    return [None, {
        'id': 1, 'expParams': [30, 20, 30, 30], 'traits': [
            {'code': 23, 'dataId': 0, 'value': 1}, {'code': 22, 'dataId': 0, 'value': 0.95},
            {'code': 22, 'dataId': 1, 'value': 0.05}, {'code': 22, 'dataId': 2, 'value': 0.04},
            {'code': 41, 'dataId': 1, 'value': 1}, {'code': 51, 'dataId': 1, 'value': 1},
            {'code': 52, 'dataId': 1, 'value': 1}],
        'learnings': [], 'name': '音乐人', 'note': '', 'params': params,
    }]


def skills():
    def sk(i, name, msg, scope, stype=0, formula='0', dtype=0):
        return {'id': i, 'animationId': -1, 'damage': {'critical': False, 'elementId': 0, 'formula': formula,
                                                         'type': dtype, 'variance': 20},
                'description': '', 'effects': [], 'hitType': 1, 'iconIndex': 0, 'message1': msg, 'message2': '',
                'mpCost': 0, 'name': name, 'note': '', 'occasion': 1, 'repeats': 1, 'requiredWtypeId1': 0,
                'requiredWtypeId2': 0, 'scope': scope, 'speed': 0, 'stypeId': stype, 'successRate': 100,
                'tpCost': 0, 'tpGain': 0}
    return [None, sk(1, '攻击', '的攻击！', 1, formula='a.atk * 4 - b.def * 2', dtype=1),
            sk(2, '防御', '在防御。', 11)]


def items():
    def it(i, name, icon, desc, key=True, ce=0, consumable=False):
        return {'id': i, 'animationId': 0, 'consumable': consumable,
                'damage': {'critical': False, 'elementId': 0, 'formula': '0', 'type': 0, 'variance': 20},
                'description': desc, 'effects': ([{'code': 44, 'dataId': ce, 'value1': 1, 'value2': 0}] if ce else []),
                'hitType': 0, 'iconIndex': icon, 'itypeId': 2 if key else 1, 'name': name, 'note': '',
                'occasion': 2 if ce else 3, 'price': 0, 'repeats': 1, 'scope': 11 if ce else 0, 'speed': 0,
                'successRate': 100, 'tpGain': 0}
    return [None,
            it(1, '爷爷的口琴', 1, '爷爷吹了五十多年的口琴。\n使用：随时拿出来吹一吹。', ce=CE['HARMONICA']),
            it(2, '爷爷的吉他', 2, '爷爷攒了一整年的钱买的吉他。\n使用：拿出来弹一弹。', ce=CE['GUITAR']),
            it(3, '爷爷的字条', 3, '『口琴太小了，快装不下你的歌了。』'),
            it(4, '妈妈的字条', 3, '『琴弦旧了，换一副吧。——妈』'),
            it(5, '阿杰的拨片', 9, '阿杰用了十年的拨片。\n“以后，替我多弹几首。”'),
            it(6, '粉色的糖', 5, '雪夜里，一个小女孩送的糖。\n一直舍不得吃。'),
            it(7, '竖笛', 6, '给清水小学的孩子们准备的竖笛。'),
            it(8, '爷爷的笔记本', 8, '『音乐不光是用耳朵听的。是用心。』'),
            it(9, '冰棍', 14, '卖冰棍的叔叔送的。\n使用：吃掉它。', key=False, ce=CE['POPSICLE'], consumable=True),
            it(10, '又一颗粉色的糖', 5, '四十多年后，小雨还回来的糖。\n是同一个牌子。'),
            it(11, '一束小花', 11, '山坡上摘的野花。')]


def common_events():
    def ce(i, name, fn):
        return {'id': i, 'list': build(fn), 'name': name, 'switchId': 1, 'trigger': 0}

    return [None,
            ce(CE['HARMONICA'], '吹口琴', lambda c: c.plugin('LifeSong Free Harm 0 0 吹吹爷爷的口琴')),
            ce(CE['GUITAR'], '弹吉他', lambda c: c.plugin('LifeSong Free Gtr 0 0 弹一弹吉他')),
            ce(CE['POPSICLE'], '吃冰棍', lambda c: c.text('凉丝丝、甜滋滋的。', '是夏天的味道。')),
            ce(CE['FRAGMENT'], '获得旋律碎片', lambda c: (c.var(V['FRAGMENTS'], 1, '+'), c.me('YY_Fragment'),
                                                       c.flash((255, 240, 180, 120), 40, False)))]


def misc_db():
    weapons = [None, {'id': 1, 'animationId': 0, 'description': '', 'etypeId': 1, 'traits': [], 'iconIndex': 0,
                      'name': '（未使用）', 'note': '', 'params': [0] * 8, 'price': 0, 'wtypeId': 1}]
    armors = [None, {'id': 1, 'atypeId': 1, 'description': '', 'etypeId': 2, 'traits': [], 'iconIndex': 0,
                     'name': '（未使用）', 'note': '', 'params': [0] * 8, 'price': 0}]
    enemies = [None, {'id': 1, 'actions': [{'conditionParam1': 0, 'conditionParam2': 0, 'conditionType': 0,
                                             'rating': 5, 'skillId': 1}],
                      'battlerHue': 0, 'battlerName': '', 'dropItems': [{'dataId': 1, 'denominator': 1, 'kind': 0}] * 3,
                      'exp': 0, 'traits': [], 'gold': 0, 'name': '（未使用）', 'note': '',
                      'params': [100, 0, 10, 10, 10, 10, 10, 10]}]
    troops = [None, {'id': 1, 'members': [], 'name': '（未使用）', 'pages': [{
        'conditions': {'actorHp': 50, 'actorId': 1, 'actorValid': False, 'enemyHp': 50, 'enemyIndex': 0,
                       'enemyValid': False, 'switchId': 1, 'switchValid': False, 'turnA': 0, 'turnB': 0,
                       'turnEnding': False, 'turnValid': False},
        'list': [{'code': 0, 'indent': 0, 'parameters': []}], 'span': 0}]}]
    states = [None, {'id': 1, 'autoRemovalTiming': 0, 'chanceByDamage': 100, 'iconIndex': 0, 'maxTurns': 1,
                     'message1': '倒下了！', 'message2': '倒下了！', 'message3': '', 'message4': '站起来了！',
                     'minTurns': 1, 'motion': 3, 'name': '无法战斗', 'note': '', 'overlay': 0, 'priority': 100,
                     'releaseByDamage': False, 'removeAtBattleEnd': False, 'removeByDamage': False,
                     'removeByRestriction': False, 'removeByWalking': False, 'restriction': 4,
                     'stepsToRemove': 100, 'traits': [{'code': 23, 'dataId': 9, 'value': 0}]}]
    animations = [None, {'id': 1, 'animation1Hue': 0, 'animation1Name': '', 'animation2Hue': 0,
                         'animation2Name': '', 'frames': [[]], 'name': '（未使用）', 'position': 1, 'timings': []}]
    return weapons, armors, enemies, troops, states, animations


def system(map_names):
    sw = [''] * 61
    for k, v in SWITCH_NAMES.items():
        sw[k] = v
    var = [''] * 31
    for k, v in VAR_NAMES.items():
        var[k] = v
    se = lambda n, v=80: audio(n, v)
    empty = audio('', 90)
    sounds = [se('YY_Cursor', 55), se('YY_Decision', 65), se('YY_Cancel', 65), se('YY_Buzzer', 65),
              se('YY_Decision', 60), se('YY_Save', 80), se('YY_Load', 80)] + [empty] * 15 + \
             [se('YY_Item', 70), empty]
    vehicle = lambda: {'bgm': audio('', 90), 'characterIndex': 0, 'characterName': '', 'startMapId': 0,
                       'startX': 0, 'startY': 0}
    return {
        'airship': vehicle(), 'boat': vehicle(), 'ship': vehicle(),
        'armorTypes': ['', '普通'], 'attackMotions': [{'type': 0, 'weaponImageId': 0}] * 13,
        'battleBgm': audio('', 90), 'battleback1Name': '', 'battleback2Name': '', 'battlerHue': 0,
        'battlerName': '', 'currencyUnit': '元', 'defeatMe': audio('', 90), 'editMapId': 2,
        'elements': ['', '物理'], 'equipTypes': ['', '武器', '盾', '头', '身体', '饰品'],
        'gameTitle': '余音', 'gameoverMe': audio('', 90), 'locale': 'zh_CN', 'magicSkills': [1],
        'menuCommands': [True, False, False, False, False, True],
        'optDisplayTp': False, 'optDrawTitle': False, 'optExtraExp': False, 'optFloorDeath': False,
        'optFollowers': False, 'optSideView': False, 'optSlipDeath': False, 'optTransparent': True,
        'partyMembers': [1], 'skillTypes': ['', '技能'], 'sounds': sounds,
        'startMapId': 10, 'startX': 8, 'startY': 6,
        'switches': sw, 'variables': var,
        'terms': {
            'basic': ['等级', 'Lv', 'HP', 'HP', 'MP', 'MP', 'TP', 'TP', '经验', 'EXP'],
            'commands': ['战斗', '逃跑', '攻击', '防御', '物品', '技能', '装备', '状态', '整队', '存档', '结束游戏',
                         '设置', '武器', '防具', '重要物品', '装备', '最强装备', '全部卸下', '新的故事', '继续',
                         None, '回到标题', '取消', None, '购买', '出售'],
            'params': ['最大HP', '最大MP', '攻击力', '防御力', '魔法攻击', '魔法防御', '敏捷', '运气', '命中', '闪避'],
            'messages': {
                'actionFailure': '对%1没有效果。', 'actorDamage': '%1受到了%2点伤害！', 'actorDrain': '%1的%2被吸收了%3！',
                'actorGain': '%1的%2恢复了%3！', 'actorLoss': '%1的%2减少了%3！', 'actorNoDamage': '%1没有受到伤害！',
                'actorNoHit': '没有命中%1！', 'actorRecovery': '%1的%2恢复了%3！', 'alwaysDash': '始终奔跑',
                'bgmVolume': '背景音乐', 'bgsVolume': '环境音', 'buffAdd': '%1的%2提高了！', 'buffRemove': '%1的%2恢复了！',
                'commandRemember': '记住指令', 'counterAttack': '%1反击了！', 'criticalToActor': '暴击！',
                'criticalToEnemy': '暴击！', 'debuffAdd': '%1的%2降低了！', 'defeat': '%1被打败了。',
                'emerge': '%1出现了！', 'enemyDamage': '%1受到了%2点伤害！', 'enemyDrain': '%1的%2被吸收了%3！',
                'enemyGain': '%1的%2恢复了%3！', 'enemyLoss': '%1的%2减少了%3！', 'enemyNoDamage': '%1没有受到伤害！',
                'enemyNoHit': '没有命中%1！', 'enemyRecovery': '%1的%2恢复了%3！', 'escapeFailure': '没能逃走！',
                'escapeStart': '%1逃跑了！', 'evasion': '%1躲开了攻击！', 'expNext': '距离下一个%1',
                'expTotal': '当前%1', 'file': '回忆', 'levelUp': '%1的%2提升到了%3！', 'loadMessage': '要读取哪一段回忆？',
                'magicEvasion': '%1抵消了魔法！', 'magicReflection': '%1反射了魔法！', 'meVolume': '音乐片段',
                'obtainExp': '获得了%1点%2！', 'obtainGold': '获得了%1\\G！', 'obtainItem': '获得了%1！',
                'obtainSkill': '学会了%1！', 'partyName': '%1', 'possession': '持有数', 'preemptive': '%1抢先行动！',
                'saveMessage': '要把这段回忆存在哪里？', 'seVolume': '音效', 'substitute': '%1保护了%2！',
                'surprise': '%1被偷袭了！', 'useItem': '%1使用了%2！', 'victory': '%1胜利了！'},
        },
        'testBattlers': [{'actorId': 1, 'equips': [0, 0, 0, 0, 0], 'level': 1}], 'testTroopId': 1,
        'title1Name': 'YuYin_Title', 'title2Name': 'YuYin_Logo', 'titleBgm': audio('YY_Title', 80),
        'variables': var, 'versionId': random.Random(42).randint(1, 99999999),
        'victoryMe': audio('', 90), 'windowTone': [0, 0, 0, 0],
    }


# ---------------------------------------------------------------------------
# maps
# ---------------------------------------------------------------------------
MAP_DEFS = [
    # id, name, display name, layout fn, events fn
    (M.OLD_HOME, '01 琴房（晚年的家）', '林音的家', M.old_home, story.old_home_events),
    (M.VILLAGE, '02 清水村', '清水村', M.village, story.village_events),
    (M.GRANDPA_HOUSE, '03 爷爷家', '爷爷家', M.grandpa_house, story.grandpa_house_events),
    (M.APARTMENT, '04 城里的家', '家', M.apartment, story.apartment_events),
    (M.SCHOOL, '05 第一中学', '第一中学', M.school_yard, story.school_events),
    (M.MUSIC_ROOM, '06 音乐教室', '音乐教室', M.music_room, story.music_room_events),
    (M.HALL, '07 礼堂', '礼堂', M.hall, story.hall_events),
    (M.CITY, '08 城市·雪夜', '城市', M.city, story.city_events),
    (M.BASEMENT, '09 地下室', '出租屋', M.basement, story.basement_events),
]


def opening_map():
    from mapgen import MapPainter
    m = MapPainter(17, 13, 'inside')
    m.fill(None)
    return m


def build_maps():
    infos = [None]
    order = 1
    for mid, name, disp, layout, evfn in MAP_DEFS:
        m, pts = layout()
        meta = META['outside' if m.tileset_id == 1 else 'inside']
        events = evfn(meta, pts)
        mp = map_json(m.w, m.h, m.tileset_id, m.data(), events, display_name=disp)
        dump('Map%03d.json' % mid, mp)
        infos.append({'id': mid, 'expanded': False, 'name': name, 'order': order, 'parentId': 0,
                      'scrollX': m.w * 24, 'scrollY': m.h * 24})
        order += 1
    m = opening_map()
    events = story.opening_events(META['inside'], {})
    dump('Map010.json', map_json(m.w, m.h, m.tileset_id, m.data(), events, display_name=''))
    infos.append({'id': 10, 'expanded': False, 'name': '00 开场（黑屏）', 'order': 0, 'parentId': 0,
                  'scrollX': 408, 'scrollY': 312})
    # keep map order: opening first
    infos = [None] + sorted([i for i in infos if i], key=lambda i: i['order'])
    for k, i in enumerate(infos[1:], 1):
        i['order'] = k
    by_id = [None] * 11
    for i in infos[1:]:
        by_id[i['id']] = i
    dump('MapInfos.json', by_id)
    return [n for (_, n, _, _, _) in MAP_DEFS]


def main():
    os.makedirs(DATA, exist_ok=True)
    names = build_maps()
    dump('Actors.json', actors())
    dump('Classes.json', classes())
    dump('Skills.json', skills())
    dump('Items.json', items())
    weapons, armors, enemies, troops, states, animations = misc_db()
    dump('Weapons.json', weapons)
    dump('Armors.json', armors)
    dump('Enemies.json', enemies)
    dump('Troops.json', troops)
    dump('States.json', states)
    dump('Animations.json', animations)
    dump('CommonEvents.json', common_events())
    dump('Tilesets.json', [None] + TILESETS)
    dump('System.json', system(names))
    print('data written:', len(os.listdir(DATA)), 'files')


if __name__ == '__main__':
    main()
