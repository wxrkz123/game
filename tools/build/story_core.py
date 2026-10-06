"""Shared constants and helpers for the 《余音》 story script."""
from mvdata import Cmd, page, event, PLAYER, THIS, DOWN, LEFT, RIGHT, UP
import maps as M

# ---------------------------------------------------------------------------
# switches
# ---------------------------------------------------------------------------
S = dict(
    PRO=1, CH1=2, CH2=3, CH3=4, CH4=5, CH5=6,
    DUODUO_IN=7, PRO_OPENED=8, DUODUO_CALL=9,
    # chapter 1
    SOUND_QUEST=11, SOUNDS_DONE=12, LESSON_DONE=13,
    # chapter 2
    GOT_GUITAR=21, MOM_TALK=22, JOINED_BAND=23, SONG_WRITTEN=24, CAUGHT=25, FESTIVAL=26,
    HOME_NIGHT=27, MOM_AT_HALL=28, CH2_DONE=29,
    # chapter 3
    PHONE=31, OWNER=32, DEMO=33, JIE_BYE=34, BUSKED=35, PHONE_RING=36, JIE_READY=37,
    CASE_OUT=38, PASSERS=39, XIAOYU=40, CANDY=41,
    # chapter 4
    NOTEBOOK=45, COLOR_BACK=46, MET_XIAOHE=47, TEACH=48,
    # chapter 5
    C5_XIAOHE=51, C5_JIE=52, C5_XIAOYU=53, C5_GRAVE=54, CONCERT=55, C5_READY=56, C5_OUT=57,
)
SWITCH_NAMES = {
    1: '序章', 2: '第一章', 3: '第二章', 4: '第三章', 5: '第四章', 6: '第五章',
    7: '序章:朵朵进门', 8: '序章:开场结束', 9: '终章:朵朵来叫',
    11: '一:开始找声音', 12: '一:声音找齐', 13: '一:学会口琴',
    21: '二:拆开包裹', 22: '二:和妈妈谈过', 23: '二:加入乐队', 24: '二:写好了歌', 25: '二:被妈妈发现',
    26: '二:文艺汇演', 27: '二:演出后回家', 28: '二:妈妈在礼堂', 29: '二:本章结束',
    31: '三:接过电话', 32: '三:老板娘', 33: '三:送过小样', 34: '三:阿杰告别', 35: '三:街头唱完',
    36: '三:电话响', 37: '三:阿杰出现', 38: '三:打开琴盒', 39: '三:路人', 40: '三:小雨出现', 41: '三:糖',
    45: '四:读了笔记本', 46: '四:颜色回来了', 47: '四:遇见小禾', 48: '四:答应教书',
    51: '五:小禾', 52: '五:阿杰', 53: '五:小雨', 54: '五:扫墓', 55: '五:音乐会', 56: '五:可以开始',
    57: '五:出门了',
}

# ---------------------------------------------------------------------------
# variables
# ---------------------------------------------------------------------------
V = dict(CHAPTER=1, FRAGMENTS=2, SOUNDS=3, RESULT=11, CH2_CHOICE=12, CH3_CHOICE=13, FINAL=20)
VAR_NAMES = {1: '章节标题', 2: '旋律碎片数', 3: '夏天的声音', 11: '小游戏错误次数', 12: '第二章选择',
             13: '第三章选择', 20: '最后一句（玩家的旋律）'}

# ---------------------------------------------------------------------------
# items
# ---------------------------------------------------------------------------
I = dict(HARMONICA=1, GUITAR=2, GRANDPA_NOTE=3, MOM_NOTE=4, PICK=5, CANDY=6, RECORDER=7,
         NOTEBOOK=8, POPSICLE=9, CANDY2=10, BOUQUET=11)

# common events
CE = dict(HARMONICA=1, GUITAR=2, POPSICLE=3, FRAGMENT=4)

ME = '\\N[1]'   # the heroine's name in messages

# the four learned phrases (jianpu, 8 = high do)
P1 = '3,5,6,5,3,2,1'
P2 = '2,3,5,6,5,3,2'
P3 = '6,8,6,5,3,5,6'
P4 = '5,3,2,1,2,3,1'
P1_RHYTHM = '3:1.5,5:.5,6,5,3,2,1:2'

CHAPTERS = {
    1: dict(switch='CH1', title='第一章 · 蝉鸣 · 八岁的夏天', image='$Yin_Child', nick='最喜欢爷爷的口琴',
            card='第一章 蝉鸣 八岁·夏', to=(M.GRANDPA_HOUSE, 14, 5, DOWN)),
    2: dict(switch='CH2', title='第二章 · 逆风 · 十六岁的秋天', image='$Yin_Teen', nick='瞒着妈妈组乐队',
            card='第二章 逆风 十六岁·秋', to=(M.APARTMENT, 16, 7, UP)),
    3: dict(switch='CH3', title='第三章 · 霓虹 · 二十五岁的冬天', image='$Yin_Adult', nick='在地铁口唱歌的人',
            card='第三章 霓虹 二十五岁·冬', to=(M.BASEMENT, 8, 7, UP)),
    4: dict(switch='CH4', title='第四章 · 无声 · 四十五岁的春天', image='$Yin_Middle', nick='写歌的人',
            card='第四章 无声 四十五岁·春', to=(M.VILLAGE, 26, 30, UP)),
    5: dict(switch='CH5', title='第五章 · 余音 · 七十八岁的秋天', image='$Yin_Old', nick='清水小学的林老师',
            card='第五章 余音 七十八岁·秋', to=(M.OLD_HOME, 8, 7, UP)),
}
PREV = {1: 'PRO', 2: 'CH1', 3: 'CH2', 4: 'CH3', 5: 'CH4'}


def goto_chapter(c, n, lines=()):
    """Fade out, narrate, show the chapter card and move to the chapter's first map."""
    ch = CHAPTERS[n]
    c.fade_bgm(3)
    c.fade_bgs(3)
    c.fadeout()
    c.weather('none', 0, 0)
    c.tint((0, 0, 0, 0), 1, False)
    c.wait(40)
    for ln in lines:
        c.narrate(ln)
    c.switch(S[PREV[n]], False)
    c.switch(S[ch['switch']], True)
    c.plugin('LifeSong SetText %d %s' % (V['CHAPTER'], ch['title']))
    c.actor_image(ch['image'])
    c.nickname(ch['nick'])
    c.plugin('LifeSong Chapter %s' % ch['card'])
    m, x, y, d = ch['to']
    c.transfer(m, x, y, d, fade=2)


def fragment(c, icon, name, notes, line):
    c.common(CE['FRAGMENT'])
    c.text('\\I[%d]\\C[6]旋律碎片「%s」\\C[0]' % (icon, name), '\\C[8]%s\\C[0]' % notes, line, bg=0, pos=1)


class Events:
    def __init__(self):
        self.list = [None]

    def add(self, name, x, y, pages, note=''):
        eid = len(self.list)
        self.list.append(event(eid, name, x, y, pages if isinstance(pages, list) else [pages], note))
        return eid


def inspect(texts):
    """texts: list of (cond_dict, lines) -> list of pages for an invisible look-at event."""
    pages = []
    for cond, lines in texts:
        pages.append(page(lambda c, L=lines: c.text(*L), cond=cond, priority=1))
    return pages


def npc(image, d, texts, move_type=0, step_anime=False, freq=3, speed=3, through=False, priority=1):
    """texts: list of (cond, fn) where fn(c) writes the dialogue."""
    pages = []
    for cond, fn in texts:
        img = image(cond) if callable(image) else (image, d)
        pages.append(page(fn, image=img, cond=cond, move_type=move_type, step_anime=step_anime,
                          move_freq=freq, move_speed=speed, through=through, priority=priority))
    return pages


def door(cond_targets):
    """cond_targets: list of (cond, fn) for a player-touch door."""
    return [page(fn, cond=cond, trigger=1, priority=0) for cond, fn in cond_targets]


def step_back(c, direction='u'):
    c.walk(PLAYER, direction)


def C(*names, **kw):
    """condition helper: C('CH1', 'SOUND_QUEST', self='A', var=(...))"""
    d = {}
    if len(names) > 0:
        d['switch1'] = S[names[0]]
    if len(names) > 1:
        d['switch2'] = S[names[1]]
    d.update(kw)
    return d
