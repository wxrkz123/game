"""《余音》 — the complete story as RPG Maker MV events.

Page order matters: RPG Maker uses the LAST page whose conditions are met,
so pages are listed from the earliest story state to the latest.
"""
from mvdata import Cmd, page, PLAYER, THIS, DOWN, LEFT, RIGHT, UP
from story_core import (S, V, I, CE, ME, P1, P2, P3, P4, P1_RHYTHM, CHAPTERS, goto_chapter, fragment,
                        Events, C, step_back)
import maps as M


def say_me(c, *lines):
    c.say(ME, *lines)


# ===========================================================================
# MAP010  开场（黑屏）
# ===========================================================================

def opening_events(meta, pts):
    ev = Events()

    def opening(c):
        c.wait(60)
        c.narrate('人这一辈子，会遇见很多东西。')
        c.narrate('有的东西，遇见了，就再也放不下了。')
        c.wait(30)
        c.narrate('这是一个关于“放不下”的故事。')
        c.wait(30)
        c.switch(S['PRO'], True)
        c.var_script(V['CHAPTER'], "'序章 · 黄昏 · 七十八岁'")
        c.nickname('清水小学的林老师')
        c.self_switch('A')
        c.transfer(M.OLD_HOME, 6, 7, UP, fade=0)

    ev.add('开场', 8, 6, [page(opening, trigger=3)])
    return ev.list


# ===========================================================================
# MAP001  琴房（林音晚年的家）
# ===========================================================================

def old_home_events(meta, pts):
    ev = Events()

    def env_pro(c):
        c.bgm('YY_Twilight', 70)
        c.tint((34, 0, -34, 0), 1, False)
        c.erase()

    def env_ch5(c):
        c.bgm('YY_Twilight', 70)
        c.tint((51, 0, -51, 17), 1, False)
        c.erase()

    ev.add('环境', 0, 0, [page(env_pro, trigger=4, cond=C('PRO')),
                         page(env_ch5, trigger=4, cond=C('CH5'))])

    duoduo = 3   # event id of 朵朵 (added below as the 3rd event)

    def prologue(c):
        c.transparent(False)
        c.wait(40)
        c.narrate('秋天的傍晚。', '清水村的老槐树，又落了一地的叶子。')
        c.se('YY_Knock', 80)
        c.wait(20)
        c.switch(S['DUODUO_IN'], True)
        c.se('YY_Door', 80)
        c.walk(duoduo, 'u2')
        c.face(PLAYER, DOWN)
        c.say('朵朵', '林奶奶！林奶奶！', '明天的音乐会，真的要在大槐树下面开吗？')
        say_me(c, '是呀。全村的人都会来。')
        c.say('朵朵', '那您要弹什么歌呀？')
        say_me(c, '一首……我写了一辈子的歌。')
        c.balloon(duoduo, '!')
        c.say('朵朵', '一辈子？那得写多长呀！')
        c.balloon(PLAYER, 'note')
        say_me(c, '呵呵。可它呀，还差最后一小段，', '怎么也写不完。')
        c.say('朵朵', '为什么写不完呢？')
        say_me(c, '也许……是因为我还没想明白，', '自己为什么一辈子都放不下它吧。')
        c.balloon(duoduo, '?')
        c.say('朵朵', '……听不懂。', '那我明天一定来听！奶奶再见！')
        c.walk(duoduo, 'd2')
        c.se('YY_Door', 70)
        c.switch(S['DUODUO_IN'], False)
        c.wait(30)
        say_me(c, '……最后一句。')
        c.hint('（四处看看吧。想好了，就到钢琴前按确定键。）')
        c.switch(S['PRO_OPENED'], True)
        c.self_switch('A')

    ev.add('序章开场', 1, 1, [page(prologue, trigger=3, cond=C('PRO'))] +
           [page(None, cond=C('PRO', self='A'))])

    def duo_ch5_call(c):
        pass

    ev.add('朵朵', 8, 10, [
        page(None, cond=C('PRO')),
        page(lambda c: c.say('朵朵', '奶奶明天见！'), image=('$Duoduo', UP), cond=C('PRO', 'DUODUO_IN')),
        page(None, cond=C('CH5')),
        page(lambda c: c.say('朵朵', '快走吧奶奶，大家都在等您！'), image=('$Duoduo', UP),
             cond=C('CH5', 'DUODUO_CALL')),
    ])

    def ch5_open(c):
        c.fadein()
        c.wait(30)
        c.narrate('第二天傍晚。')
        c.se('YY_Knock', 80)
        c.switch(S['DUODUO_CALL'], True)
        c.se('YY_Door', 80)
        c.walk(duoduo, 'u2')
        c.face(PLAYER, DOWN)
        c.say('朵朵', '林奶奶！大家都到了！', '大槐树下面挂满了灯笼，可好看了！')
        say_me(c, '好，好。奶奶这就来。')
        c.say('朵朵', '那我先去占位置！')
        c.walk(duoduo, 'd2')
        c.se('YY_Door', 70)
        c.switch(S['DUODUO_CALL'], False)
        c.hint('（出门，去大槐树下吧。）')
        c.self_switch('A')

    ev.add('终章开场', 1, 2, [page(None, cond=C('PRO')),
                            page(ch5_open, trigger=3, cond=C('CH5')),
                            page(None, cond=C('CH5', self='A'))])

    # ---- the piano: where every memory starts -----------------------------
    def piano_pro(c):
        say_me(c, '……最后一句，到底该怎么写呢。')
        c.wait(20)
        say_me(c, '从头再想一遍吧。', '从……那个夏天开始。')
        c.fade_bgm(2)
        c.me('YY_Memory')
        c.flash((255, 255, 255, 220), 60, True)
        goto_chapter(c, 1, ['……', '那是很久很久以前的事了。'])

    def piano_ch5(c):
        c.text('钢琴盖上，落着一片槐树叶。')
        say_me(c, '……一会儿，就要在大家面前弹了啊。')

    for (x, y) in ((3, 4), (4, 4)):
        ev.add('钢琴', x, y, [page(None, cond=C('PRO')),
                            page(piano_pro, cond=C('PRO', 'PRO_OPENED')),
                            page(piano_ch5, cond=C('CH5'))])

    # ---- things to look at ------------------------------------------------
    looks = [
        ('照片1', 10, 3, ['一张泛黄的照片：', '老槐树下，扎着两个小辫的女孩，', '和一位吹口琴的老人。']),
        ('照片2', 11, 3, ['高中文艺汇演的合影。', '抱着吉他的少女，笑得有点紧张。',
                        '照片的最边上，站着她的妈妈。']),
        ('照片3', 12, 3, ['一张手写的演出海报：『地铁口的歌——林音』。', '边角都磨破了。',
                        '背面，粘着一张粉色的糖纸。']),
        ('照片4', 13, 3, ['清水小学音乐教室的合影。', '一群孩子围着一位短发的老师。',
                        '最前排的小女孩，举着一支竖笛。']),
        ('钟', 9, 3, ['滴答，滴答。', '这只钟，比我还老。']),
        ('窗', 5, 3, ['窗外，就是那棵老槐树。']),
        ('书架', 6, 4, ['一排排手写的乐谱。', '最旧的那一本，封面上歪歪扭扭地写着：', '『小音的歌 · 第一页』']),
        ('书架2', 7, 4, ['乐谱、歌词本、录音带……', '一辈子的声音，都挤在这一格一格里。']),
        ('口琴盒', 13, 7, ['爷爷的口琴的盒子。', '口琴我一直带在身上——', '七十年了，它还在。']),
        ('乐谱', 8, 4, ['写了一半的乐谱。', '最后一页，只有一行字：', '『最后一句，写什么好呢？』']),
        ('供桌', 2, 8, ['墙边的小桌上，摆着爷爷和妈妈的照片。', '照片前的茶，每天都是新泡的。']),
        ('供桌2', 3, 8, ['妈妈的照片是她六十岁那年拍的。', '那天，她第一次说：“我女儿是写歌的。”']),
        ('床', 14, 4, ['爷爷睡过的床。现在是我的了。']),
        ('摇椅', 12, 7, ['摇椅吱呀吱呀地响。', '年纪大了，在这上面一坐就是一下午。']),
        ('收音机', 14, 8, ['老收音机。偶尔还能听到我写的歌。', '……不过，我已经听不太清了。']),
        ('柜子', 2, 6, ['抽屉里放着一副旧吉他弦，', '和一张写着“琴弦旧了，换一副吧”的字条。']),
    ]
    for name, x, y, lines in looks:
        ev.add(name, x, y, [page(lambda c, L=lines: c.text(*L))])

    # ---- the door ---------------------------------------------------------
    def door_pro(c):
        say_me(c, '（天快黑了，明天还有音乐会……今天就不出门了。）')
        step_back(c)

    def door_ch5(c):
        c.se('YY_Door', 70)
        c.switch(S['C5_OUT'], True)
        c.transfer(M.VILLAGE, 13, 7, DOWN, fade=0)

    ev.add('门', 8, 11, [page(door_pro, trigger=1, priority=0, cond=C('PRO')),
                        page(door_ch5, trigger=1, priority=0, cond=C('CH5'))])
    return ev.list


# ===========================================================================
# MAP003  爷爷家（第一章 1998年夏 / 第四章 空房子）
# ===========================================================================

def grandpa_house_events(meta, pts):
    ev = Events()

    def env_ch1(c):
        c.fade_bgm(1)
        c.bgs('YY_Cicadas', 35)
        c.tint((0, 0, 0, 0), 1, False)
        c.erase()

    def env_ch4(c):
        c.if_switch(S['COLOR_BACK'],
                    then=lambda c: (c.bgm('YY_Spring', 60), c.fade_bgs(1), c.tint((0, 0, 0, 0), 1, False)),
                    else_=lambda c: (c.bgm('YY_Silence', 70), c.bgs('YY_Muffled', 35),
                                     c.tint((-17, -17, -17, 200), 1, False)))
        c.erase()

    ev.add('环境', 0, 0, [page(env_ch1, trigger=4, cond=C('CH1')),
                         page(env_ch4, trigger=4, cond=C('CH4'))])

    def ch1_open(c):
        c.fadein()
        c.wait(30)
        c.narrate('一九九八年，夏天。', '爸爸妈妈去城里打工，', '我被送到了清水村的爷爷家。')
        c.balloon(PLAYER, 'sweat')
        say_me(c, '（好热……知了叫得好响。）')
        c.wait(40)
        c.plugin('LifeSong Play Harm %s 22' % P1_RHYTHM)
        c.balloon(PLAYER, '!')
        say_me(c, '……？这是什么声音？', '好好听……')
        c.hint('（声音是从门外传来的。出去看看吧！）')
        c.self_switch('A')

    ev.add('第一章开场', 1, 1, [page(ch1_open, trigger=3, cond=C('CH1')),
                              page(None, cond=C('CH1', self='A'))])

    looks = [
        ((2, 4), ['灶台上温着一碗绿豆汤。', '爷爷说，喝了就不怕热。'], ['灶台早就冷了，上面落满了灰。']),
        ((3, 4), ['锅里煮着玉米，满屋子都是甜甜的味道。'], ['锅已经生锈了。']),
        ((4, 4), ['收音机里咿咿呀呀地唱着戏。', '爷爷说，唱戏的人，用一辈子在唱同一句话。'],
         ['我拧了拧收音机的开关。', '……什么声音也没有。', '是它坏了，还是我听不见了？']),
        ((7, 3), ['墙上的日历：一九九八年七月。', '暑假才刚刚开始。'],
         ['墙上的日历，还停在很多年前——', '爷爷走的那个冬天。']),
        ((5, 3), ['窗外，阳光把老槐树的影子晒得暖洋洋的。'], ['窗户上糊的纸破了，风从洞里钻进来。']),
        ((12, 3), ['从窗户能看见小河。', '河水亮晶晶的，像撒了一把碎镜子。'], ['窗外的小河还在流。']),
        ((9, 3), ['滴答，滴答。爷爷的钟走得很准。'], ['钟停了。']),
        ((10, 4), ['书架上有几本旧书，还有一本没有封面的本子，', '上面全是数字：3 5 6 5 3 2 1……'],
         ['书架上空空的。']),
        ((13, 4), ['衣柜里挂着爷爷的几件旧褂子，都洗得发白了。'], ['衣柜里空荡荡的。']),
        ((11, 4), ['柜子上摆着一张黑白照片：', '年轻时的爷爷，站在矿山前面，手里拿着口琴。'],
         ['柜子上的照片还在。年轻时的爷爷，手里拿着口琴。']),
        ((2, 9), ['墙角堆着几个装满杂物的箱子。'], ['箱子上落满了灰。']),
        ((14, 8), ['一盆长得很旺的吊兰。'], ['吊兰早就枯了。']),
    ]
    for (x, y), ch1, ch4 in looks:
        ev.add('看', x, y, [page(lambda c, L=ch1: c.text(*L), cond=C('CH1')),
                           page(lambda c, L=ch4: c.text(*L), cond=C('CH4'))])

    # grandpa's bed: in chapter 4 the notebook is hidden underneath
    def bed_ch4(c):
        c.text('床底下，有一个落满灰的木盒子。')
        c.se('YY_Paper', 80)
        c.text('里面是一本旧笔记本。', '字迹歪歪扭扭的——是爷爷的字。')
        c.item(I['NOTEBOOK'], 1)
        c.text('\\C[6]『一九七六年 春』\\C[0]', '在矿上干了二十年，耳朵不中用了。',
               '吹口琴的时候，已经听不太清自己吹的是什么。')
        c.text('\\C[6]『可是不要紧。』\\C[0]', '口琴贴在嘴唇上，我能感觉到它在抖。',
               '每一个音，抖得都不一样。')
        c.text('\\C[6]『音乐不光是用耳朵听的。』\\C[0]', '\\C[6]『是用心。』\\C[0]')
        c.balloon(PLAYER, 'tear')
        say_me(c, '……爷爷。', '你那时候……也听不见了吗？')
        say_me(c, '可你还是吹了一辈子。')
        c.wait(30)
        say_me(c, '（我从口袋里拿出那把口琴，', '轻轻地贴在嘴唇上。）')
        c.plugin('LifeSong Feel Harm %s %d 用心去“听”' % (P4, V['RESULT']))
        c.switch(S['NOTEBOOK'], True)
        c.switch(S['COLOR_BACK'], True)
        c.tint((0, 0, 0, 0), 180, False)
        c.fade_bgs(4)
        c.bgm('YY_Spring', 60)
        c.wait(60)
        say_me(c, '……我感觉到了。', '每一个音，都在嘴唇上轻轻地跳。')
        say_me(c, '爷爷……我听见了。')
        fragment(c, 19, '心跳', '5 3 2 1 2 3 1', '音乐不在耳朵里，在心里。')
        c.hint('（窗外好像有孩子在唱歌。出去看看吧。）')

    ev.add('爷爷的床', 14, 4, [
        page(lambda c: c.text('爷爷的床。被子上有晒过太阳的味道。'), cond=C('CH1')),
        page(bed_ch4, cond=C('CH4')),
        page(lambda c: c.text('爷爷的床。', '盒子里的笔记本，我带在身上了。'), cond=C('CH4', 'NOTEBOOK')),
    ])

    def ch4_enter(c):
        c.wait(20)
        c.narrate('爷爷的老房子。', '自从李奶奶走了以后，就再也没有人住过。')
        say_me(c, '（我在门口站了很久。', '屋子里静得像一口井。）')
        c.hint('（看看爷爷留下的东西吧。）')
        c.self_switch('A')

    ev.add('第四章进屋', 1, 2, [page(None, cond=C('CH1')),
                              page(ch4_enter, trigger=3, cond=C('CH4')),
                              page(None, cond=C('CH4', self='A'))])

    def door_out(c):
        c.se('YY_Door', 70)
        c.transfer(M.VILLAGE, 13, 7, DOWN, fade=0)

    ev.add('门', 8, 11, [page(door_out, trigger=1, priority=0)])
    return ev.list


# ===========================================================================
# MAP002  清水村（第一章 夏 / 第四章 春 / 第五章 秋夜）
# ===========================================================================

def village_events(meta, pts):
    ev = Events()

    # ---- environment --------------------------------------------------------
    def env_ch1(c):
        c.bgm('YY_Summer', 70)
        c.bgs('YY_Cicadas', 45)
        c.tint((0, 0, 0, 0), 1, False)
        c.weather('none', 0, 0)
        c.erase()

    def env_ch4(c):
        c.if_switch(S['COLOR_BACK'],
                    then=lambda c: (c.bgm('YY_Spring', 70), c.fade_bgs(1), c.tint((0, 0, 0, 0), 1, False)),
                    else_=lambda c: (c.bgm('YY_Silence', 70), c.bgs('YY_Muffled', 40),
                                     c.tint((-17, -17, -17, 200), 1, False)))
        c.erase()

    def env_ch5(c):
        c.bgm('YY_Twilight', 60)
        c.bgs('YY_Night', 35)
        c.tint((17, -17, 0, 51), 1, False)
        c.erase()

    ev.add('环境', 0, 0, [page(env_ch1, trigger=4, cond=C('CH1')),
                         page(env_ch4, trigger=4, cond=C('CH4')),
                         page(env_ch5, trigger=4, cond=C('CH5'))])

    # ---- 第一章：爷爷 ----------------------------------------------------------
    gx, gy = pts['tree_root_left']

    def grandpa_first(c):
        c.say('爷爷', '哟，小音醒啦？')
        say_me(c, '爷爷！刚才那个好听的声音，是你吹的吗？')
        c.say('爷爷', '是这个。', '口琴。跟了爷爷五十多年喽。')
        c.balloon(PLAYER, 'heart')
        say_me(c, '我也想吹！爷爷教我！教我！')
        c.say('爷爷', '哈哈，先别急。', '吹口琴之前，你得先学会“听”。')
        say_me(c, '听？')
        c.say('爷爷', '这村子里，藏着好多好多声音。', '你去找找看——找到四种“夏天的声音”，', '再回来找爷爷。')
        say_me(c, '四种夏天的声音……好！')
        c.var(V['SOUNDS'], 0)
        c.switch(S['SOUND_QUEST'], True)
        c.hint('（在村子里找找闪闪发光的地方吧。）')

    def grandpa_waiting(c):
        c.say('爷爷', '知了、小河、风……', '这村子里，还有什么会唱歌呢？慢慢找，不着急。')
        c.hint('（已经找到 \\V[3] / 4 种夏天的声音）')

    def grandpa_lesson(c):
        say_me(c, '爷爷！我都找到了！')
        say_me(c, '知了在打拍子，小河在数石头，', '风铃会唱歌，还有冰棍车的铃铛！')
        c.say('爷爷', '哈哈哈！好，好。', '你看，这世上到处都是音乐。')
        c.say('爷爷', '会听的人，就永远不会寂寞。')
        c.say('爷爷', '来，爷爷教你吹。先试三个音。')
        c.plugin('LifeSong Echo Harm 1,2,3 %d 先试三个音：do、re、mi' % V['RESULT'])
        c.say('爷爷', '好！再来一句难点儿的。', '这是爷爷最喜欢的一段，听好了。')
        c.plugin('LifeSong Echo Harm %s %d 跟着爷爷吹一遍' % (P1, V['RESULT']))
        c.if_var(V['RESULT'], '==', 0,
                 then=lambda c: c.say('爷爷', '一次就吹对了！', '我们小音，是长了一对好耳朵的孩子。'),
                 else_=lambda c: c.say('爷爷', '吹错了不要紧。', '喜欢的东西，多吹几遍，就会了。'))
        c.wait(20)
        c.say('爷爷', '……小音，这把口琴，送给你。')
        c.balloon(PLAYER, '!')
        say_me(c, '真的吗？', '可、可这是爷爷最宝贵的东西……')
        c.say('爷爷', '正因为宝贵，才要送给最喜欢它的人。')
        c.item(I['HARMONICA'], 1)
        c.se('YY_Item')
        c.text('\\I[1] 得到了\\C[6]爷爷的口琴\\C[0]！', '\\C[8]（在菜单的「物品」里，可以随时拿出来吹一吹。）\\C[0]')
        fragment(c, 16, '蝉鸣', '3 5 6 5 3 2 1', '这是一切开始的声音。')
        c.switch(S['LESSON_DONE'], True)
        # sunset
        c.fade_bgm(2)
        c.fade_bgs(2)
        c.fadeout()
        c.tint((68, 0, -51, 0), 1, False)
        c.locate(PLAYER, gx, gy + 1, UP)
        c.wait(30)
        c.fadein()
        c.bgm('YY_Harmonica', 70)
        c.narrate('傍晚，我和爷爷坐在老槐树下。', '太阳把小河染成了橘子的颜色。')
        c.say('爷爷', '小音啊，爷爷跟你说句话。', '你现在听不懂，也没关系。')
        c.say('爷爷', '喜欢一样东西，', '不用谁来批准，也不用急着它能换来什么。')
        c.say('爷爷', '你只要一直喜欢下去，', '它就会一直陪着你。')
        say_me(c, '……一直陪着我？')
        c.say('爷爷', '嗯。就像这把口琴，陪了爷爷一辈子。')
        c.balloon(PLAYER, 'music')
        c.wait(40)
        goto_chapter(c, 2, ['那个夏天，我学会了吹好多首歌。',
                            '那是我第一次知道——\n原来心里的声音，是可以吹出来的。',
                            '……',
                            '后来，我回到了城里，上了中学。',
                            '爷爷在我十五岁那年的冬天，走了。'])

    ev.add('爷爷', gx, gy, [
        page(grandpa_first, image=('$Grandpa', DOWN), cond=C('CH1'), step_anime=True),
        page(grandpa_waiting, image=('$Grandpa', DOWN), cond=C('CH1', 'SOUND_QUEST'), step_anime=True),
        page(grandpa_lesson, image=('$Grandpa', DOWN), cond=C('CH1', 'SOUNDS_DONE'), step_anime=True),
        page(lambda c: c.say('爷爷', '天快黑了，回家喝绿豆汤吧。'), image=('$Grandpa', DOWN),
             cond=C('CH1', 'LESSON_DONE')),
    ])

    # ---- 第一章：四种夏天的声音 ------------------------------------------------
    def found(c, se, lines, name):
        c.se(se, 90)
        c.wait(30)
        for ln in lines:
            say_me(c, *ln)
        c.var(V['SOUNDS'], 1, '+')
        c.self_switch('A')
        c.se('YY_Sparkle', 70)
        c.text('\\I[4] 找到了夏天的声音：\\C[6]%s\\C[0]（\\V[3] / 4）' % name)
        c.if_var(V['SOUNDS'], '>=', 4, then=lambda c: (
            c.switch(S['SOUNDS_DONE'], True),
            say_me(c, '四种声音都找到了！', '快去告诉爷爷！')))

    def sound_event(name, x, y, se, lines, idle, label, extra=None):
        pages = [
            page(lambda c: c.text(*idle), cond=C('CH1')),
            page(lambda c: (extra(c) if extra else None, found(c, se, lines, label)),
                 image=('!$Sparkle', DOWN), cond=C('CH1', 'SOUND_QUEST'), step_anime=True),
            page(lambda c: c.text(*idle), cond=C('CH1', 'SOUND_QUEST', self='A')),
        ]
        ev.add(name, x, y, pages)

    cx, cy = pts['cicada_tree']
    sound_event('知了', cx, cy, 'YY_Cicada',
                [['知了——知了——'], ['原来知了是这样叫的。', '一下，一下，像在打拍子。']],
                ['树上的知了叫个不停。'], '知了')
    sx, sy = pts['stream_spot']
    sound_event('小河', sx, sy, 'YY_Stream',
                [['哗啦啦……哗啦啦……'], ['小河在唱歌。', '好像在一颗一颗地数河底的石头。']],
                ['河水清清的，能看见小鱼。'], '小河')

    def bell_vendor(c):
        c.say('卖冰棍的', '冰棍——冰棍——', '五毛钱一根嘞！')

    ev.add('卖冰棍的', pts['cart_front'][0], pts['cart_front'][1], [
        page(lambda c: (c.se('YY_Bell', 80), c.say('卖冰棍的', '冰棍——冰棍——五毛一根！', '小朋友，天热，来一根？')),
             image=('$Vendor', LEFT), cond=C('CH1')),
        page(lambda c: (c.say('卖冰棍的', '找声音？哈哈，那你听这个——'),
                        found(c, 'YY_Bell', [['叮铃铃！叮铃铃！'], ['是夏天最甜的声音！']], '冰棍车的铃铛'),
                        c.say('卖冰棍的', '这根冰棍送你，算是给你的奖品！'),
                        c.item(I['POPSICLE'], 1),
                        c.text('\\I[14] 得到了\\C[6]一根冰棍\\C[0]。')),
             image=('$Vendor', LEFT), cond=C('CH1', 'SOUND_QUEST')),
        page(lambda c: (c.se('YY_Bell', 80), c.say('卖冰棍的', '冰棍好吃不？', '明天再来呀！')),
             image=('$Vendor', LEFT), cond=C('CH1', 'SOUND_QUEST', self='A')),
        page(None, cond=C('CH4')),
        page(None, cond=C('CH5')),
    ])

    # wind chime (decoration in every chapter)
    wx, wy = pts['chime']

    def chime_ch1(c):
        c.se('YY_WindChime', 80)
        c.text('风铃轻轻地晃着。')

    ev.add('风铃', wx, wy, [
        page(chime_ch1, image=('!$WindChime', DOWN), cond=C('CH1'), step_anime=True),
        page(lambda c: found(c, 'YY_WindChime', [['叮——叮铃——'], ['风也会唱歌呢。']], '风铃'),
             image=('!$WindChime', DOWN), cond=C('CH1', 'SOUND_QUEST'), step_anime=True),
        page(chime_ch1, image=('!$WindChime', DOWN), cond=C('CH1', 'SOUND_QUEST', self='A'), step_anime=True),
        page(lambda c: c.text('李奶奶的风铃还挂在那里。', '它在风里晃着……可是我听不见它唱歌。'),
             image=('!$WindChime', DOWN), cond=C('CH4'), step_anime=True),
        page(lambda c: (c.se('YY_WindChime', 80), c.text('叮——叮铃——', '……我听见了。')),
             image=('!$WindChime', DOWN), cond=C('CH4', 'COLOR_BACK'), step_anime=True),
        page(lambda c: (c.se('YY_WindChime', 70), c.text('风铃还在唱。', '六十年了，它从来没有停过。')),
             image=('!$WindChime', DOWN), cond=C('CH5'), step_anime=True),
    ])

    # ---- 第一章：村民 -----------------------------------------------------------
    ev.add('李奶奶', 25, 9, [
        page(lambda c: c.say('李奶奶', '哟，这不是守山家的小孙女嘛！', '你爷爷呀，天天念叨你。'),
             image=('$Granny_Li', DOWN), cond=C('CH1')),
        page(lambda c: c.say('李奶奶', '找会唱歌的东西？', '那你去听听我家门口的风铃——一起风，它就唱。'),
             image=('$Granny_Li', DOWN), cond=C('CH1', 'SOUND_QUEST')),
        page(lambda c: c.say('李奶奶', '你爷爷年轻的时候啊，', '在矿上干活，一下工就坐在大槐树底下吹口琴。',
                             '全村的小孩都围着他转。'),
             image=('$Granny_Li', DOWN), cond=C('CH1', 'SOUNDS_DONE')),
    ])
    ev.add('阿毛', 22, 19, [
        page(lambda c: c.say('阿毛', '小音！来捉蜻蜓呀！'), image=('$Kid_Boy', DOWN), cond=C('CH1'),
             move_type=1, move_freq=3),
        page(lambda c: c.say('阿毛', '在找声音？', '我知道！小河那边的桥上，能听见水哗啦哗啦的！'),
             image=('$Kid_Boy', DOWN), cond=C('CH1', 'SOUND_QUEST'), move_type=1, move_freq=3),
        page(lambda c: c.say('村里的孩子', '（……嗡嗡……）', '（孩子们笑着跑过去了。我听不清他们在喊什么。）'),
             image=('$Kid_Boy', DOWN), cond=C('CH4'), move_type=1, move_freq=3),
        page(lambda c: c.say('村里的孩子', '阿姨阿姨，你是从城里来的吗？', '城里有没有会唱歌的大房子？'),
             image=('$Kid_Boy', DOWN), cond=C('CH4', 'COLOR_BACK'), move_type=1, move_freq=3),
        page(lambda c: c.say('学生', '林老师！我们今晚也要上台！', '我负责打鼓！'), image=('$Kid_Boy', UP), cond=C('CH5')),
    ])
    ev.add('小花', 24, 21, [
        page(lambda c: c.say('小花', '你听，蜻蜓飞的时候，', '翅膀会“嗡嗡”地响哦。'), image=('$Kid_Girl', DOWN),
             cond=C('CH1'), move_type=1, move_freq=3),
        page(lambda c: c.say('小花', '我知道一个声音！', '冰棍车的铃铛！叮铃铃——就在学校门口！'),
             image=('$Kid_Girl', DOWN), cond=C('CH1', 'SOUND_QUEST'), move_type=1, move_freq=3),
        page(lambda c: c.text('一个小女孩冲我挥了挥手。', '……她在说什么呢？'), image=('$Kid_Girl', DOWN),
             cond=C('CH4'), move_type=1, move_freq=3),
        page(lambda c: c.say('村里的孩子', '我们学校没有音乐课。', '唱歌？只有过年的时候，大人们才唱。'),
             image=('$Kid_Girl', DOWN), cond=C('CH4', 'COLOR_BACK'), move_type=1, move_freq=3),
        page(lambda c: c.say('学生', '林老师，我好紧张……', '要是唱错了怎么办？'),
             image=('$Kid_Girl', UP), cond=C('CH5')),
    ])
    for (x, y) in ((24, 23), (11, 24)):
        ev.add('蜻蜓', x, y, [page(None, image=('$Dragonfly', DOWN), cond=C('CH1'), move_type=1, move_freq=5,
                                  move_speed=4, through=True, priority=2, step_anime=True)])
    ev.add('渔夫叔叔', 3, 15, [
        page(lambda c: c.say('渔夫叔叔', '嘘——小声点，鱼要被吓跑了。', '……不过你刚才哼的小调，还挺好听。'),
             image=('$Fisherman', RIGHT), cond=C('CH1')),
        page(lambda c: c.say('渔夫叔叔', '夏天的声音？', '你站到桥上去，闭上眼睛听听小河。'),
             image=('$Fisherman', RIGHT), cond=C('CH1', 'SOUND_QUEST')),
    ])
    ev.add('王伯', 34, 19, [
        page(lambda c: c.say('王伯', '今年雨水足，稻子长得旺。', '秋天的时候，你可要再来吃新米！'),
             image=('$Farmer', DOWN), cond=C('CH1')),
        page(lambda c: c.text('地里的老人抬起头，冲我说了几句话。', '（……我一个字也没听见。）'),
             image=('$Farmer', DOWN), cond=C('CH4')),
        page(lambda c: (c.say('王伯', '你是……守山家的小音丫头？', '都长这么大了！'),
                        c.say('王伯', '你爷爷要是还在，该多高兴。')),
             image=('$Farmer', DOWN), cond=C('CH4', 'COLOR_BACK')),
        page(lambda c: (c.say('王伯', '小音丫头，我九十啦！', '耳朵比你还背。'),
                        c.say('王伯', '可你的歌，我坐在最前面，', '一句一句都“听”得见。')),
             image=('$Farmer', UP), cond=C('CH5')),
    ])
    ev.add('张婶', 18, 5, [
        page(lambda c: c.say('张婶', '小音，帮婶子看着点衣服，', '别让鸡给啄了。'), image=('$Villager_Woman', LEFT),
             cond=C('CH1')),
        page(lambda c: c.say('张婶', '会唱歌的东西？', '鸡算不算？哈哈哈！'), image=('$Villager_Woman', LEFT),
             cond=C('CH1', 'SOUND_QUEST')),
    ])
    for (x, y) in ((30, 14), (31, 15)):
        ev.add('鸡', x, y, [page(lambda c: c.text('咯咯哒！'), image=('$Chicken', DOWN), cond=C('CH1'),
                                move_type=1, move_freq=4)])
    ev.add('橘猫', 15, 10, [page(lambda c: (c.balloon(THIS, 'zzz'), c.text('一只橘猫在树荫下打呼噜。')),
                               image=('!$CatSleep', DOWN), cond=C('CH1'), step_anime=True),
                          page(lambda c: (c.balloon(THIS, 'zzz'), c.text('一只橘猫在晒太阳。', '……是当年那只猫的孙子吗？')),
                               image=('!$CatSleep', DOWN), cond=C('CH4'), step_anime=True)])

    # ---- 永远都在的东西 ------------------------------------------------------
    for x in (20, 21):
        ev.add('老槐树', x, 13, [
            page(lambda c: c.text('老槐树。', '听爷爷说，它比村子还要老。')),
            page(lambda c: c.text('老槐树。', '三十多年过去了，它一点也没变。'), cond=C('CH4')),
            page(lambda c: c.text('老槐树。', '七十年了。', '它听过我所有的歌。'), cond=C('CH5')),
        ])
    ev.add('井', 17, 18, [page(lambda c: c.text('井水凉丝丝的。', '往下看，能看见一小块天。'))])
    for x in (24, 25):
        ev.add('路牌', x, 28, [page(lambda c: c.text('\\C[6]清水村\\C[0]', '往南走三十里，就是县城。'))])

    # ---- doors ----------------------------------------------------------------
    def home_door(c):
        c.se('YY_Door', 70)
        c.if_switch(S['CH5'], then=lambda c: c.transfer(M.OLD_HOME, 8, 10, UP, fade=0),
                    else_=lambda c: c.transfer(M.GRANDPA_HOUSE, 8, 10, UP, fade=0))

    gdx, gdy = pts['grandpa_door']
    ev.add('爷爷家的门', gdx, gdy, [page(home_door, trigger=1, priority=0)])

    def locked(lines):
        def f(c):
            c.text(*lines)
            step_back(c, 'd')
        return f

    for key, lines in (('li_door', ['李奶奶家。门上挂着一串红辣椒。']),
                       ('farmer_door', ['王伯家。门口晒着玉米。']),
                       ('brick_door', ['门关着。屋里传来炒菜的声音。'])):
        x, y = pts[key]
        ev.add('门', x, y, [page(locked(lines), trigger=1, priority=0)])
    x, y = pts['li_door']
    # chapter 4/5 variants for 李奶奶家
    ev.list[-1]['pages'].append(page(locked(['李奶奶家。', '门上贴着褪色的春联。李奶奶已经不在了。']),
                                     trigger=1, priority=0, cond=C('CH4')))
    ev.list[-1]['pages'].append(page(locked(['现在住在这里的，是李奶奶的孙女一家。', '屋里没人——大家都去大槐树下了。']),
                                     trigger=1, priority=0, cond=C('CH5')))
    sx_, sy_ = pts['school_door']
    ev.add('学校的门', sx_, sy_, [
        page(locked(['清水小学。', '放暑假了，校门锁着。']), trigger=1, priority=0, cond=C('CH1')),
        page(locked(['清水小学。', '教室里传来孩子们读书的声音……', '不，是我想象的。我什么也听不见。']),
             trigger=1, priority=0, cond=C('CH4')),
        page(locked(['清水小学。', '我在这里教了二十年音乐。', '今晚，孩子们都去大槐树下了。']),
             trigger=1, priority=0, cond=C('CH5')),
    ])

    ex, ey = pts['entrance']

    def leave_block(c):
        c.if_switch(S['CH1'], then=lambda c: say_me(c, '（爷爷说，小孩子不能一个人跑出村子。）'))
        c.if_switch(S['CH4'], then=lambda c: say_me(c, '（我不想再回城里去了。）'))
        c.if_switch(S['CH5'], then=lambda c: say_me(c, '（今天哪儿也不去。大家都在等我呢。）'))
        step_back(c, 'u')

    ev.add('村口', ex, ey + 1, [page(leave_block, trigger=1, priority=0)])

    # ---- graves on the hill -----------------------------------------------------
    grave_tile = meta['grave'][0][0]
    ggx, ggy = pts['grave_grandpa']
    mgx, mgy = pts['grave_mom']

    def grave_c5(c):
        c.text('\\C[6]林守山之墓\\C[0]　　\\C[6]林淑芬之墓\\C[0]', '爷爷和妈妈，在山坡上挨着。')
        c.if_switch(S['C5_GRAVE'], then=lambda c: c.text('墓碑前的花还很新鲜。'), else_=lambda c: (
            c.text('我把一束小花放在墓碑前。'),
            c.se('YY_Paper', 60),
            say_me(c, '爷爷，妈。', '今天晚上，我要把那首歌唱完了。'),
            say_me(c, '妈，你还记得吗？', '后来我的每一场演出，你都来了。', '总是坐在最后一排。'),
            say_me(c, '这一次……', '你们俩，坐在第一排好不好？'),
            c.balloon(PLAYER, 'flower'),
            c.switch(S['C5_GRAVE'], True)))

    ev.add('爷爷的墓', ggx, ggy, [
        page(None, cond=C('CH1')),
        page(lambda c: c.if_switch(S['COLOR_BACK'], then=lambda c: (
                c.text('\\C[6]林守山之墓\\C[0]'), say_me(c, '爷爷，我听见了。', '是用心听见的。')),
             else_=lambda c: (c.text('\\C[6]林守山之墓\\C[0]'), say_me(c, '爷爷，我回来了。'),
                              say_me(c, '……我听不见了，爷爷。', '我写了一辈子的歌，现在，我听不见了。'))),
             image=grave_tile, cond=C('CH4')),
        page(grave_c5, image=grave_tile, cond=C('CH5')),
    ])
    ev.add('妈妈的墓', mgx, mgy, [page(None, cond=C('CH1')), page(grave_c5, image=grave_tile, cond=C('CH5'))])

    # ---- 第四章 ---------------------------------------------------------------
    def ch4_arrive(c):
        c.fadein()
        c.wait(30)
        say_me(c, '（清水村。', '三十七年了，老槐树还在。）')
        c.wait(20)
        say_me(c, '（村里的人跟我打招呼。', '我只能看见他们的嘴在动，', '声音像是隔着一层厚厚的水。）')
        c.hint('（去爷爷的老房子看看吧——在老槐树的左上方。）')
        c.self_switch('A')

    ev.add('第四章到达', 1, 31, [page(None, cond=C('CH1')),
                               page(ch4_arrive, trigger=3, cond=C('CH4')),
                               page(None, cond=C('CH4', self='A'))])

    hx, hy = pts['tree_root_right']

    def meet_xiaohe(c):
        c.text('一个小女孩一个人坐在树下，', '小声地哼着歌。')
        c.balloon(PLAYER, 'music')
        say_me(c, '（……我听见了。', '是一段没有词的、歪歪扭扭的调子。）')
        say_me(c, '你唱的是什么歌呀？')
        c.balloon(THIS, '!')
        c.say('小女孩', '……没、没什么。', '我瞎哼的。')
        say_me(c, '很好听啊。你叫什么名字？')
        c.say('小禾', '小禾……')
        c.say('小禾', '我们学校没有音乐老师。', '我不会唱歌，就是……喜欢瞎哼。')
        c.say('小禾', '我妈说，哼这个没用。')
        c.wait(20)
        say_me(c, '小禾。', '喜欢一样东西，不用谁来批准哦。')
        c.balloon(THIS, '?')
        say_me(c, '……这是很久很久以前，', '有个人在这棵树下告诉我的。')
        c.switch(S['MET_XIAOHE'], True)
        c.hint('（学校门口好像站着一位老师。）')

    ev.add('小禾', hx, hy, [
        page(None, cond=C('CH1')),
        page(lambda c: c.text('一个小女孩坐在树下，嘴唇轻轻地动着，', '好像在哼歌。', '……可是我什么也听不见。'),
             image=('$Xiaohe_Child', DOWN), cond=C('CH4')),
        page(meet_xiaohe, image=('$Xiaohe_Child', DOWN), cond=C('CH4', 'COLOR_BACK')),
        page(lambda c: c.say('小禾', '林……阿姨？', '你还会来吗？'), image=('$Xiaohe_Child', DOWN),
             cond=C('CH4', 'MET_XIAOHE')),
    ])

    def principal_teach(c):
        c.say('校长', '您……您就是林音？', '那个写歌的林音？', '哎呀，没想到您是咱们清水村出去的！')
        c.say('校长', '不瞒您说，咱们学校好多年没有音乐老师了。', '孩子们连五线谱都没见过……')
        say_me(c, '（我想起了树下那个小声哼歌的小女孩。）')
        c.choices(['让我来教吧。', '我……再想想。'], [
            lambda c: (
                say_me(c, '让我来教吧。'),
                say_me(c, '我的耳朵不太好了。', '可是我想把我知道的东西，都教给他们。'),
                c.say('校长', '真、真的吗！', '孩子们要高兴坏了！'),
                c.switch(S['TEACH'], True),
                c.fade_bgm(3),
                c.fadeout(),
                c.wait(30),
                c.narrate('第二天，我送给小禾一支竖笛。'),
                c.plugin('LifeSong Play Rec 1,2,3,5,3 24'),
                c.narrate('“老师！我、我吹出来了！”'),
                goto_chapter(c, 5, ['那年春天，清水小学有了第一间音乐教室。',
                                    '我在那里教了二十年书。',
                                    '我的耳朵越来越不好了，', '可孩子们的歌声，我一句都没有错过。',
                                    '……',
                                    '又过了很多很多年。'])),
            lambda c: c.say('校长', '不着急，您慢慢想。', '学校的门，随时为您开着。'),
        ])

    ev.add('校长', 17, 26, [
        page(None, cond=C('CH1')),
        page(lambda c: c.text('学校门口站着一位老师。', '她说了很多话。我只听清了“音乐”两个字。'),
             image=('$Villager_Woman', DOWN), cond=C('CH4')),
        page(lambda c: (c.say('校长', '您好！您是来看孩子们的吗？'),
                        c.say('校长', '……唉，我们学校啊，什么都不缺，', '就是缺一位音乐老师。')),
             image=('$Villager_Woman', DOWN), cond=C('CH4', 'COLOR_BACK')),
        page(principal_teach, image=('$Villager_Woman', DOWN), cond=C('CH4', 'MET_XIAOHE')),
    ])

    # ---- 第五章 ---------------------------------------------------------------
    def c5_out(c):
        c.wait(20)
        say_me(c, '（晚风凉凉的。', '大槐树下，已经挤满了人。）')
        c.hint('（和老朋友们说说话吧。准备好了，就走到树下的钢琴前。）')
        c.self_switch('A')

    ev.add('终章出门', 1, 30, [page(None, cond=C('CH1')),
                             page(c5_out, trigger=3, cond=C('CH5', 'C5_OUT')),
                             page(None, cond=C('CH5', self='A'))])

    for (x, y) in ((16, 12), (25, 12), (15, 15), (26, 15), (15, 18), (26, 18), (19, 19), (22, 19),
                   (13, 8), (12, 15)):
        ev.add('灯笼', x, y, [page(None, cond=C('CH1')),
                            page(None, image=('!$Lantern', DOWN), cond=C('CH5'), step_anime=True, priority=2,
                                 through=True)])

    ready_js = '$gameSwitches.value(%d) && $gameSwitches.value(%d) && $gameSwitches.value(%d)' % (
        S['C5_XIAOHE'], S['C5_JIE'], S['C5_XIAOYU'])

    def check_ready(c):
        c.if_script(ready_js, then=lambda c: c.switch(S['C5_READY'], True))

    def xiaohe_c5(c):
        c.say('小禾', '林老师！', '今晚伴奏的乐队，全是您教过的学生。', '我们偷偷练了一个月呢！')
        c.say('小禾', '……老师，', '当年在这棵树下，您跟我说的那句话，', '我一直记着。')
        c.say('小禾', '“喜欢一样东西，不用谁来批准。”', '现在，我也这样告诉我的学生。')
        say_me(c, '小禾……你现在，是清水小学最好的音乐老师了。')
        c.balloon(THIS, 'heart')
        c.switch(S['C5_XIAOHE'], True)
        check_ready(c)

    def jie_c5(c):
        c.say('阿杰', '音音！哈哈，没想到吧？', '我也来了！')
        say_me(c, '阿杰？！你的头发……全白了。')
        c.say('阿杰', '你的也是嘛。')
        c.say('阿杰', '退休以后，我又把吉他捡起来了。', '手指头不灵活了，弹得磕磕绊绊的。')
        c.say('阿杰', '可是这回……我不打算再放下了。')
        c.if_item(I['PICK'], then=lambda c: (
            c.say('阿杰', '对了，那个拨片，还在吗？'),
            say_me(c, '在呢。一直带着。'),
            c.say('阿杰', '那今晚，借我用用？', '我给你伴奏。'),
            c.balloon(THIS, 'music')))
        c.switch(S['C5_JIE'], True)
        check_ready(c)

    def xiaoyu_c5(c):
        c.say('陌生的女士', '您好……', '您还记得我吗？')
        c.say('陌生的女士', '很多年前，一个下雪的晚上，', '在地铁口。')
        c.balloon(PLAYER, '!')
        say_me(c, '……你是，那个给我糖的小姑娘？')
        c.say('小雨', '是我！我叫小雨。')
        c.say('小雨', '那年冬天，我爸爸没能出院。', '可是那天晚上您唱的歌，', '陪我熬过了最难的一年。')
        c.say('小雨', '后来，我当了医生。', '每次累得撑不下去的时候，', '我就哼那首歌。')
        c.say('小雨', '今天，我是来还您那颗糖的。')
        c.item(I['CANDY2'], 1)
        c.se('YY_Item')
        c.text('\\I[5] 小雨递过来一颗粉色的糖。', '……是同一个牌子。', '四十多年了，它居然还在卖。')
        c.balloon(PLAYER, 'tear')
        c.switch(S['C5_XIAOYU'], True)
        check_ready(c)

    ev.add('小禾（大人）', 18, 15, [page(None, cond=C('CH1')),
                                  page(xiaohe_c5, image=('$Xiaohe_Adult', RIGHT), cond=C('CH5')),
                                  page(lambda c: c.say('小禾', '老师，我们都准备好了。'),
                                       image=('$Xiaohe_Adult', RIGHT), cond=C('CH5', 'C5_XIAOHE'))])
    ev.add('阿杰（老年）', 23, 15, [page(None, cond=C('CH1')),
                                  page(jie_c5, image=('$Jie_Old', LEFT), cond=C('CH5')),
                                  page(lambda c: c.say('阿杰', '弹吧，音音。', '这一次，我不会提前走了。'),
                                       image=('$Jie_Old', LEFT), cond=C('CH5', 'C5_JIE'))])
    ev.add('小雨（大人）', 24, 17, [page(None, cond=C('CH1')),
                                  page(xiaoyu_c5, image=('$Xiaoyu_Adult', LEFT), cond=C('CH5')),
                                  page(lambda c: c.say('小雨', '我就坐在最前面听。', '这一次，换我为您停下来。'),
                                       image=('$Xiaoyu_Adult', LEFT), cond=C('CH5', 'C5_XIAOYU'))])
    duo = ev.add('朵朵', 21, 17, [page(None, cond=C('CH1')),
                                 page(lambda c: c.say('朵朵', '奶奶加油！', '我坐在最前面！'),
                                      image=('$Duoduo', UP), cond=C('CH5'))])
    ev.add('村民', 25, 16, [page(None, cond=C('CH1')),
                          page(lambda c: c.say('村民', '林老师，我小时候也是您的学生！', '您还记得我吗？我总是唱跑调的那个！'),
                               image=('$Villager_Woman', LEFT), cond=C('CH5'))])

    # ---- the concert ------------------------------------------------------------
    def concert(c):
        c.fade_bgm(2)
        c.fade_bgs(2)
        c.fadeout()
        c.switch(S['CONCERT'], True)
        c.tint((-85, -68, 0, 34), 1, False)
        c.locate(PLAYER, 20, 16, UP)
        c.locate(duo, 21, 18, UP)
        c.wait(40)
        c.fadein()
        c.bgs('YY_Night', 25)
        c.wait(30)
        c.face(PLAYER, DOWN)
        say_me(c, '谢谢大家，今天来听一个老太太弹琴。')
        say_me(c, '这首歌，我写了一辈子。')
        c.face(PLAYER, UP)
        say_me(c, '第一句，', '是我八岁那年，爷爷在这棵树下教我的。')
        c.plugin('LifeSong Echo Pno %s %d 第一句 · 蝉鸣' % (P1, V['RESULT']))
        say_me(c, '第二句，', '是十六岁那年，我逆着风写的。')
        c.plugin('LifeSong Echo Pno %s %d 第二句 · 逆风' % (P2, V['RESULT']))
        say_me(c, '第三句，', '是写给一个在雪夜里，为我停下脚步的孩子的。')
        c.plugin('LifeSong Echo Pno %s %d 第三句 · 霓虹' % (P3, V['RESULT']))
        say_me(c, '第四句，', '是在我什么都听不见的时候，用心听见的。')
        c.plugin('LifeSong Echo Pno %s %d 第四句 · 心跳' % (P4, V['RESULT']))
        c.wait(20)
        say_me(c, '还有最后一句……', '我想了很多很多年。')
        say_me(c, '现在我知道了。', '最后一句，不用写得多好听，', '只要是自己的声音就好。')
        c.hint('（用你自己的旋律，为这首歌写下最后一句。）')
        c.plugin('LifeSong Free Pno 8 %d 最后一句 · 你的声音' % V['FINAL'])
        say_me(c, '……这就是，我这一辈子的歌。')
        c.text('她从第一句开始，把整首歌又弹了一遍。')
        c.plugin('LifeSong Song Pno 20 %d' % V['FINAL'])
        c.se('YY_Applause', 90)
        c.wait(90)
        c.bgm('YY_Finale', 80)
        c.walk(duo, 'u1')
        c.say('朵朵', '奶奶！奶奶！')
        c.face(PLAYER, DOWN)
        c.say('朵朵', '奶奶，您现在想明白了吗？', '为什么一辈子都放不下它？')
        say_me(c, '嗯。', '……因为喜欢啊。')
        say_me(c, '喜欢一样东西，', '不用谁来批准，也不用它换来什么。')
        say_me(c, '你只要一直喜欢下去，', '它就会一直陪着你。')
        say_me(c, '……来，这个送给你。')
        c.item(I['HARMONICA'], -1)
        c.se('YY_Item')
        c.text('\\I[1] 林音把\\C[6]口琴\\C[0]放进了朵朵的手心。')
        c.say('朵朵', '这是……太爷爷的口琴？')
        say_me(c, '现在，是你的了。')
        c.balloon(duo, 'music')
        c.plugin('LifeSong Play Harm %s 22' % P1_RHYTHM)
        c.balloon(PLAYER, 'heart')
        fragment(c, 20, '余音', '3 5 6 5 3 2 1 ……', '一首歌唱完了。可它的余音，会一直响下去。')
        c.narrate('那天晚上，大槐树下的歌声，', '一直唱到了很晚很晚。')
        c.fadeout()
        c.wait(60)
        c.scroll(['', '《余　音》', '', '—— 一生所爱 ——', '', '', '林音（1990 — ）',
                  '她这一辈子，一直在唱同一首歌。', '', '', '———————————', '',
                  '故事　美术　音乐　程序', '由 Claude 协助制作', '',
                  '引擎　RPG Maker MV Corescript（MIT 许可）', '字体　Fusion Pixel Font（SIL OFL 1.1）', '',
                  '———————————', '', '', '谢谢你，陪她走完这一生。', '', '愿你也有一样东西，',
                  '可以热爱一辈子。', '', '', '', '— 完 —'], speed=2, no_fast=False)
        c.fade_bgm(4)
        c.wait(120)
        c.to_title()

    def piano_not_ready(c):
        say_me(c, '（还有好几个老朋友，想和他们说说话。）')
        c.hint('（和小禾、阿杰，还有那位陌生的女士聊聊吧。）')

    def piano_ready(c):
        say_me(c, '……要开始了吗？')
        c.choices(['开始吧。', '再等一下。'], [concert, None])

    ev.add('钢琴', 20, 15, [page(None, cond=C('CH1')),
                          page(piano_not_ready, image=('!$Piano', DOWN), cond=C('CH5')),
                          page(piano_ready, image=('!$Piano', DOWN), cond=C('CH5', 'C5_READY'))])
    return ev.list


# ===========================================================================
# MAP004  城市里的家（第二章）
# ===========================================================================

def apartment_events(meta, pts):
    ev = Events()

    def env(c):
        c.if_switch(S['HOME_NIGHT'], then=lambda c: (c.fade_bgm(2), c.tint((-68, -51, 0, 17), 1, False)),
                    else_=lambda c: c.if_switch(S['CAUGHT'],
                                                then=lambda c: (c.bgm('YY_Tension', 60), c.tint((-17, -34, -34, 0), 1, False)),
                                                else_=lambda c: (c.bgm('YY_Home', 65), c.tint((0, 0, 0, 0), 1, False))))
        c.fade_bgs(1)
        c.erase()

    ev.add('环境', 0, 0, [page(env, trigger=4, cond=C('CH2'))])

    def ch2_open(c):
        c.fadein()
        c.wait(30)
        c.narrate('二〇〇六年，秋天。', '我十六岁，在城里读高二。')
        c.say('妈妈', '小音——', '村里寄来个包裹，是你李奶奶寄的！', '我放你桌上了！')
        say_me(c, '（李奶奶？）')
        c.hint('（看看书桌上的包裹吧。）')
        c.self_switch('A')

    ev.add('第二章开场', 1, 1, [page(ch2_open, trigger=3, cond=C('CH2')),
                              page(None, cond=C('CH2', self='A'))])

    def open_package(c):
        c.se('YY_Paper', 80)
        c.text('包裹里，是一把旧吉他。', '琴颈上系着一张字条。')
        c.text('\\C[6]『给小音：', '口琴太小了，快装不下你的歌了。', '等你长大，就用它弹吧。', '　　　　　　　　　　　——爷爷』\\C[0]')
        c.text('李奶奶在信里说，', '这是爷爷走之前托她保管的。', '他偷偷攒了一整年的钱。')
        c.balloon(PLAYER, 'tear')
        say_me(c, '……爷爷。')
        c.item(I['GUITAR'], 1)
        c.item(I['GRANDPA_NOTE'], 1)
        c.se('YY_Item')
        c.text('\\I[2] 得到了\\C[6]爷爷的吉他\\C[0]！', '\\C[8]（也可以在菜单里拿出来弹一弹。）\\C[0]')
        c.switch(S['GOT_GUITAR'], True)
        c.wait(20)
        c.say('妈妈', '小音！吃早饭了！')
        c.hint('（去厨房找妈妈。）')

    def night_note(c):
        c.text('桌上放着一副新的吉他弦。', '下面压着一张字条。')
        c.se('YY_Paper', 80)
        c.text('\\C[6]『琴弦旧了，换一副吧。', '　　　　　　　　——妈』\\C[0]')
        c.item(I['MOM_NOTE'], 1)
        c.balloon(PLAYER, 'heart')
        say_me(c, '……妈。')
        c.wait(30)
        c.switch(S['CH2_DONE'], True)
        goto_chapter(c, 3, ['那天以后，妈妈再也没有提过“不许弹琴”。',
                            '后来，我考上了大学。',
                            '毕业那年，我背着吉他，', '一个人来到了这座最大的城市。'])

    dx, dy = pts['desk']
    ev.add('包裹', dx + 1, dy, [
        page(open_package, image=('!$Letter', DOWN), cond=C('CH2')),
        page(lambda c: c.text('拆开的包裹。爷爷的字条，我收在抽屉最里面了。'), cond=C('CH2', 'GOT_GUITAR')),
        page(night_note, image=('!$Letter', DOWN), cond=C('CH2', 'HOME_NIGHT')),
    ])

    def mom_talk(c):
        c.say('妈妈', '包裹里是什么？')
        c.say('妈妈', '……吉他？')
        c.balloon(THIS, '...')
        c.say('妈妈', '小音，下个月就期中考试了。')
        c.say('妈妈', '你爷爷一辈子就爱鼓捣这些。', '吹了一辈子口琴，吹出什么名堂了？')
        say_me(c, '……')
        c.say('妈妈', '先把它收起来。', '等考上大学，你想弹什么都行。')
        c.choices(['……好。', '可是我……'], [
            lambda c: (c.var(V['CH2_CHOICE'], 1), say_me(c, '……好。'),
                       c.narrate('吉他被塞到了床底下。', '可是，心里的声音停不下来。')),
            lambda c: (c.var(V['CH2_CHOICE'], 2), say_me(c, '可是我……真的很喜欢。'),
                       c.say('妈妈', '喜欢能当饭吃吗？', '快去上学，要迟到了。')),
        ])
        c.switch(S['MOM_TALK'], True)
        c.hint('（出门去学校吧。家门在左下方。）')

    mx, my = pts['mom_kitchen']
    ev.add('妈妈', mx - 1, my + 1, [
        page(lambda c: c.say('妈妈', '快去看看包裹呀。'), image=('$Mom', RIGHT), cond=C('CH2')),
        page(mom_talk, image=('$Mom', RIGHT), cond=C('CH2', 'GOT_GUITAR')),
        page(lambda c: c.say('妈妈', '路上小心。', '放学早点回来，别忘了补习班。'), image=('$Mom', RIGHT),
             cond=C('CH2', 'MOM_TALK')),
        page(None, cond=C('CH2', 'CAUGHT')),
    ])

    mom_night = ev.add('妈妈（傍晚）', 17, 6, [
        page(None, cond=C('CH2')),
        page(lambda c: None, image=('$Mom', LEFT), cond=C('CH2', 'CAUGHT')),
        page(None, cond=C('CH2', 'HOME_NIGHT')),
    ])

    def caught(c):
        c.fadein()
        c.wait(30)
        c.narrate('那天傍晚，我一进门，', '就看见妈妈站在我的房间里。', '手里拿着那把吉他。')
        c.say('妈妈', '补习班的老师打电话来，', '说你这个月请了八次假。')
        c.say('妈妈', '你就是去弄这个了？')
        say_me(c, '妈……')
        c.say('妈妈', '你知不知道，妈妈每天加班到几点？', '就是为了让你以后，不用过苦日子！')
        c.say('妈妈', '你爷爷那样的人生，你也想要吗？', '穷了一辈子，到头来只剩一把破口琴！')
        c.choices(['爷爷他……很幸福。', '对不起……'], [
            lambda c: say_me(c, '爷爷他不穷。', '他每天都在吹自己喜欢的歌……', '他很幸福。'),
            lambda c: say_me(c, '对不起……', '可是，我真的放不下。'),
        ])
        c.wait(20)
        say_me(c, '妈，你说爷爷吹了一辈子口琴，', '什么名堂都没吹出来。')
        c.wait(30)
        say_me(c, '……可是，他吹出了我啊。')
        c.balloon(mom_night, '...')
        c.wait(40)
        c.say('妈妈', '…………')
        c.say('妈妈', '……周五，', '就是你们那个什么，演出？')
        say_me(c, '……嗯。')
        c.text('妈妈把吉他轻轻放在床上，', '转身走了出去。')
        c.fade_bgm(3)
        c.fadeout()
        c.narrate('那天晚上，我第一次听见妈妈在房间里，', '很小声地哭。')
        c.wait(30)
        c.narrate('……', '星期五。文艺汇演。')
        c.switch(S['FESTIVAL'], True)
        c.transfer(M.HALL, 10, 6, DOWN, fade=2)

    ev.add('傍晚：争吵', 1, 2, [page(None, cond=C('CH2')),
                             page(caught, trigger=3, cond=C('CH2', 'CAUGHT')),
                             page(None, cond=C('CH2', 'FESTIVAL'))])

    def night_home(c):
        c.fadein()
        c.wait(30)
        c.narrate('演出结束以后，我一个人走回了家。', '妈妈的房门关着，灯已经熄了。')
        c.hint('（回自己的房间看看吧。）')
        c.self_switch('A')

    ev.add('演出后回家', 1, 3, [page(None, cond=C('CH2')),
                             page(night_home, trigger=3, cond=C('CH2', 'HOME_NIGHT')),
                             page(None, cond=C('CH2', self='A'))])

    looks = [
        ((2, 4), ['燃气灶上的锅里，煮着白粥。']),
        ((3, 4), ['水池里泡着两只碗。']),
        ((4, 4), ['冰箱门上贴着一张纸：', '『小音期中考试倒计时：30天』']),
        ((7, 3), ['窗外是一栋一模一样的楼。']),
        ((9, 3), ['七点十五分。']),
        ((10, 3), ['日历上，妈妈用红笔圈出了“期中考试”。']),
        ((16, 4), ['书架上全是参考书。', '最下面一层，藏着几本吉他教材。']),
        ((18, 4), ['我的床。', '床底下……藏着什么呢。']),
        ((15, 3), ['墙上贴着一张乐队海报。', '妈妈说过好几次让我撕掉。']),
        ((17, 3), ['从窗户能看见对面楼的天台。', '那是我偷偷练口琴的地方。']),
        ((2, 12), ['电视里在放晚间新闻。']),
    ]
    for (x, y), lines in looks:
        ev.add('看', x, y, [page(lambda c, L=lines: c.text(*L))])

    def front_door(c):
        c.if_switch(S['MOM_TALK'], then=lambda c: (
            c.se('YY_Door', 70), c.transfer(M.SCHOOL, 12, 16, UP, fade=0)),
            else_=lambda c: (say_me(c, '（先跟妈妈说一声吧。）'), step_back(c)))

    ddx, ddy = pts['door']
    ev.add('家门', ddx, ddy, [page(front_door, trigger=1, priority=0, cond=C('CH2')),
                            page(lambda c: (say_me(c, '（今天哪儿也不去了。）'), step_back(c)), trigger=1, priority=0,
                                 cond=C('CH2', 'CAUGHT'))])
    return ev.list


# ===========================================================================
# MAP005  第一中学（第二章）
# ===========================================================================

def school_events(meta, pts):
    ev = Events()

    def env(c):
        c.bgm('YY_Home', 65)
        c.fade_bgs(1)
        c.tint((0, 0, 0, 0), 1, False)
        c.erase()

    ev.add('环境', 0, 17, [page(env, trigger=4, cond=C('CH2'))])

    def arrive(c):
        c.wait(20)
        say_me(c, '（第一中学。', '公告栏那边，怎么围了那么多人？）')
        c.self_switch('A')

    ev.add('到校', 1, 17, [page(arrive, trigger=3, cond=C('CH2')), page(None, cond=C('CH2', self='A'))])

    poster = ['\\C[6]【第一中学 校园文艺汇演】\\C[0]', '时间：本周五晚上七点', '地点：学校礼堂',
              '欢迎各班踊跃报名！原创节目优先！']
    for x in (17, 18):
        ev.add('公告栏', x, 5, [page(lambda c: c.text(*poster))])

    def jie_recruit(c):
        c.say('阿杰', '喂，林音！', '听说你会吹口琴？')
        say_me(c, '你、你怎么知道……')
        c.say('阿杰', '上周午休，我在天台上听见的。', '超好听！一点都不像课本里的歌。')
        c.say('阿杰', '我想组个乐队，参加文艺汇演。', '吉他、鼓都有了，就差一个会写旋律的人。')
        c.say('阿杰', '来不来？')
        say_me(c, '我……我妈不让我搞这些。')
        c.say('阿杰', '那就偷偷练嘛！', '王老师说了，放学后音乐教室借我们用。')
        c.wait(20)
        say_me(c, '（……喜欢一样东西，不用谁来批准。）')
        c.balloon(PLAYER, 'idea')
        say_me(c, '……好。我来！')
        c.balloon(THIS, 'music')
        c.say('阿杰', '太好了！', '放学后，音乐教室见！就在教学楼里！')
        c.switch(S['JOINED_BAND'], True)
        c.hint('（从教学楼的大门进去，就是音乐教室。）')

    ev.add('阿杰', 16, 6, [
        page(jie_recruit, image=('$Jie_Teen', RIGHT), cond=C('CH2', 'MOM_TALK')),
        page(lambda c: c.say('阿杰', '音乐教室见！'), image=('$Jie_Teen', RIGHT), cond=C('CH2', 'JOINED_BAND')),
    ])
    ev.add('同学', 6, 9, [page(lambda c: c.say('同学', '听说周五的文艺汇演，', '有人要唱自己写的歌！'),
                              image=('$Student_A', DOWN), cond=C('CH2'), move_type=1, move_freq=2)])
    ev.add('同学', 14, 12, [page(lambda c: c.say('同学', '期中考试……完蛋了完蛋了。'),
                                image=('$Student_B', LEFT), cond=C('CH2'))])
    ev.add('同学', 20, 11, [page(lambda c: c.say('同学', '林音，你书包上挂的那个是口琴吗？', '好复古！'),
                                image=('$Student_C', LEFT), cond=C('CH2'))])
    ev.add('王老师', 7, 7, [page(lambda c: c.say('王老师', '林音？阿杰天天跟我念叨你。', '放学后来音乐教室吧。'),
                                image=('$Teacher_Wang', DOWN), cond=C('CH2', 'JOINED_BAND'))])
    ev.add('旗杆', 5, 5, [page(lambda c: c.text('五星红旗在风里哗啦啦地响。'))])

    def school_door(c):
        c.if_switch(S['JOINED_BAND'], then=lambda c: (
            c.se('YY_Door', 70), c.transfer(M.MUSIC_ROOM, 8, 10, UP, fade=0)),
            else_=lambda c: (say_me(c, '（还没到上课时间。', '先去公告栏那边看看吧。）'), step_back(c, 'd')))

    x, y = pts['door']
    ev.add('教学楼大门', x, y, [page(school_door, trigger=1, priority=0, cond=C('CH2'))])
    for gx in (11, 12, 13):
        ev.add('校门', gx, 17, [page(lambda c: (say_me(c, '（还没放学呢。）'), step_back(c)), trigger=1, priority=0)])
    return ev.list


# ===========================================================================
# MAP006  音乐教室（第二章）
# ===========================================================================

def music_room_events(meta, pts):
    ev = Events()

    def env(c):
        c.fade_bgm(2)
        c.tint((17, 0, -17, 0), 1, False)
        c.erase()

    ev.add('环境', 0, 0, [page(env, trigger=4, cond=C('CH2'))])
    wang = ev.add('王老师', 11, 6, [page(lambda c: c.say('王老师', '慢慢来，好的旋律急不得。'),
                                        image=('$Teacher_Wang', DOWN), cond=C('CH2'))])
    jie = ev.add('阿杰', 13, 7, [page(lambda c: c.say('阿杰', '我们的乐队，就叫“逆风”怎么样？'),
                                     image=('$Jie_Teen', LEFT), cond=C('CH2'))])

    def write_song(c):
        c.wait(20)
        c.say('王老师', '你就是林音？', '阿杰天天跟我念叨你。')
        c.say('王老师', '要参加汇演，最好有一首自己的歌。', '你心里，有想写的旋律吗？')
        say_me(c, '有一段……是我爷爷教我的。')
        c.plugin('LifeSong Play Harm %s 22' % P1_RHYTHM)
        say_me(c, '我想……在它后面，接着写下去。')
        c.say('王老师', '好。拿起吉他，', '把心里的声音弹出来试试。')
        c.plugin('LifeSong Echo Gtr %s %d 把心里接下去的旋律弹出来' % (P2, V['RESULT']))
        c.balloon(jie, '!')
        c.say('阿杰', '……哇。', '这段好！有点难过，又有点不服气。')
        c.say('阿杰', '像是……逆着风，也要往前跑。')
        say_me(c, '那这首歌，就叫——', '《逆风》吧。')
        c.balloon(wang, 'note')
        c.fadeout()
        c.bgm('YY_Band', 50)
        c.narrate('那之后的每天放学，', '我们都躲在音乐教室里练习。')
        c.narrate('手指磨出了茧，弦把指尖勒出一道道红印。', '可是我从来没有那么开心过。')
        c.fade_bgm(3)
        c.wait(60)
        c.switch(S['SONG_WRITTEN'], True)
        c.switch(S['CAUGHT'], True)
        c.self_switch('A')
        c.transfer(M.APARTMENT, 15, 6, RIGHT, fade=2)

    ev.add('写歌', 1, 1, [page(write_song, trigger=3, cond=C('CH2', 'JOINED_BAND')),
                        page(None, cond=C('CH2', self='A'))])
    for name, x, y, lines in (('钢琴', 2, 4, ['音乐教室的钢琴。', '有几个琴键已经按不下去了。']),
                              ('钢琴', 3, 4, ['音乐教室的钢琴。', '有几个琴键已经按不下去了。']),
                              ('黑板', 7, 3, ['黑板上写着：“文艺汇演”。', '不知道是谁在下面画了一个笑脸。'])):
        ev.add(name, x, y, [page(lambda c, L=lines: c.text(*L))])

    def leave(c):
        say_me(c, '（还没练完呢。）')
        step_back(c)

    ev.add('门', 8, 11, [page(leave, trigger=1, priority=0)])
    return ev.list


# ===========================================================================
# MAP007  礼堂（第二章：文艺汇演）
# ===========================================================================

def hall_events(meta, pts):
    ev = Events()

    def env(c):
        c.fade_bgm(1)
        c.bgs('YY_Crowd', 45)
        c.tint((-34, -34, -17, 0), 1, False)
        c.erase()

    ev.add('环境', 0, 0, [page(env, trigger=4, cond=C('CH2'))])
    jie = ev.add('阿杰', 12, 6, [page(None, image=('$Jie_Teen', DOWN), cond=C('CH2'))])
    ev.add('鼓手', 15, 5, [page(None, image=('$Student_B', DOWN), cond=C('CH2'))])
    host = ev.add('主持人', 5, 6, [page(None, image=('$Student_C', RIGHT), cond=C('CH2'))])
    audience = [(4, 8, '$Student_A'), (7, 8, '$Passerby_Student'), (12, 8, '$Student_C'), (15, 8, '$Student_B'),
                (5, 10, '$Student_B'), (9, 10, '$Student_A'), (13, 10, '$Passerby_Woman'), (16, 10, '$Student_C')]
    for (x, y, img) in audience:
        ev.add('观众', x, y, [page(None, image=(img, UP), cond=C('CH2'))])
    wang = ev.add('王老师', 2, 11, [page(None, image=('$Teacher_Wang', UP), cond=C('CH2'))])
    mom = ev.add('妈妈', 10, 12, [page(None, cond=C('CH2')),
                                   page(None, image=('$Mom', UP), cond=C('CH2', 'MOM_AT_HALL'))])

    def festival(c):
        c.fadein()
        c.wait(30)
        c.say('主持人', '下一个节目——', '高二（3）班，原创歌曲《逆风》！')
        c.se('YY_Applause', 70)
        c.wait(60)
        c.face(jie, LEFT)
        c.say('阿杰', '（小声）别怕。', '就当是在天台上。')
        c.face(jie, DOWN)
        say_me(c, '（……爷爷，你听好了。）')
        c.fade_bgs(2)
        c.plugin('LifeSong Echo Gtr %s %d 前奏 · 爷爷教我的第一句' % (P1, V['RESULT']))
        c.plugin('LifeSong Echo Gtr %s %d 副歌 · 逆风' % (P2, V['RESULT']))
        c.bgm('YY_Band', 85)
        c.flash((255, 240, 200, 160), 30, False)
        c.narrate('灯光很烫，手心全是汗。')
        c.narrate('可是那一刻，', '我觉得自己好像在飞。')
        c.wait(120)
        c.fade_bgm(3)
        c.se('YY_Applause', 90)
        c.wait(90)
        c.switch(S['MOM_AT_HALL'], True)
        c.wait(20)
        c.balloon(PLAYER, '!')
        c.narrate('礼堂的最后一排，', '站着一个熟悉的身影。')
        say_me(c, '……妈？')
        c.balloon(mom, '...')
        c.walk(mom, 'd1')
        c.switch(S['MOM_AT_HALL'], False)
        c.wait(30)
        fragment(c, 17, '逆风', '2 3 5 6 5 3 2', '逆着风，也要往前跑。')
        c.fadeout()
        c.switch(S['HOME_NIGHT'], True)
        c.transfer(M.APARTMENT, 6, 12, UP, fade=2)

    ev.add('文艺汇演', 1, 1, [page(festival, trigger=3, cond=C('CH2', 'FESTIVAL')),
                            page(None, cond=C('CH2', 'HOME_NIGHT'))])
    return ev.list


# ===========================================================================
# MAP009  地下室出租屋（第三章）
# ===========================================================================

def basement_events(meta, pts):
    ev = Events()

    def env(c):
        c.bgm('YY_Neon', 55)
        c.fade_bgs(1)
        c.weather('none', 0, 0)
        c.tint((-34, -34, -17, 17), 1, False)
        c.erase()

    ev.add('环境', 0, 0, [page(env, trigger=4, cond=C('CH3'))])

    def ch3_open(c):
        c.fadein()
        c.wait(30)
        c.narrate('二〇一五年，冬天。', '我二十五岁。', '住在这座城市的一间地下室里。')
        say_me(c, '（今天，也要去地铁口唱歌。）')
        c.wait(20)
        c.switch(S['PHONE_RING'], True)
        c.se('YY_Phone', 70)
        c.balloon(PLAYER, '!')
        c.hint('（电话响了。）')
        c.self_switch('A')

    ev.add('第三章开场', 1, 1, [page(ch3_open, trigger=3, cond=C('CH3')),
                              page(None, cond=C('CH3', self='A'))])

    def phone_call(c):
        c.se('YY_Decision', 60)
        c.say('妈妈', '喂？小音啊。', '吃饭了没有？')
        c.balloon(PLAYER, 'sweat')
        say_me(c, '吃了吃了。吃得可好了。')
        c.text('（我看了一眼桌上的泡面。）')
        c.say('妈妈', '钱够不够花？', '不够就跟妈说。')
        say_me(c, '够的，妈。', '我这边……挺好的。')
        c.say('妈妈', '那就好。', '……唱歌的事，还顺利吗？')
        say_me(c, '嗯！快了。', '就快了。')
        c.say('妈妈', '别太累了。', '妈……等着听你的唱片。')
        c.wait(30)
        say_me(c, '……')
        c.switch(S['PHONE'], True)
        c.switch(S['PHONE_RING'], False)
        c.hint('（出门吧。门在下方。）')

    px, py = pts['phone']
    ev.add('电话', px, py, [
        page(lambda c: c.text('桌上的泡面已经凉了。'), cond=C('CH3')),
        page(phone_call, image=('!$Phone', LEFT), cond=C('CH3', 'PHONE_RING'), step_anime=True),
        page(lambda c: c.text('妈妈的电话。', '她的声音，好像比去年老了一点。'), image=('!$Phone', DOWN),
             cond=C('CH3', 'PHONE')),
    ])
    looks = [
        ((6, 4), ['自己录的小样CD。', '一共寄出去了三十七张。', '回音：零。']),
        ((7, 3), ['地下室的小窗户，只能看见路人的脚。', '今天的脚，都踩着雪。']),
        ((5, 3), ['日历：二〇一五年十二月。', '房租的日子用红笔圈着。']),
        ((4, 4), ['空空的琴架。吉他背在我身上。']),
        ((11, 5), ['薄薄的床垫。', '冬天睡在上面，能感觉到地板的凉气。']),
        ((10, 8), ['小电暖器。', '为了省电，只在最冷的时候开一会儿。']),
        ((12, 8), ['晾着的衣服，三天了还没干。']),
        ((4, 8), ['纸箱里装着寄不出去的CD。']),
        ((5, 8), ['纸箱里装着写满歌词的本子。']),
        ((10, 3), ['墙上贴着一张演唱会海报。', '总有一天……']),
    ]
    for (x, y), lines in looks:
        ev.add('看', x, y, [page(lambda c, L=lines: c.text(*L))])

    def go_out(c):
        c.if_switch(S['PHONE'], then=lambda c: (
            c.se('YY_Door', 70), c.transfer(M.CITY, 16, 6, DOWN, fade=0)),
            else_=lambda c: (say_me(c, '（电话还在响……）'), step_back(c)))

    dx, dy = pts['door']
    ev.add('门', dx, dy, [page(go_out, trigger=1, priority=0)])
    return ev.list


# ===========================================================================
# MAP008  城市·雪夜（第三章）
# ===========================================================================

def city_events(meta, pts):
    ev = Events()

    def env(c):
        c.bgm('YY_Neon', 70)
        c.bgs('YY_CityNight', 45)
        c.tint((-68, -51, 0, 34), 1, False)
        c.weather('snow', 5, 1, False)
        c.erase()

    ev.add('环境', 0, 15, [page(env, trigger=4, cond=C('CH3'))])

    ready_js = '$gameSwitches.value(%d) && $gameSwitches.value(%d)' % (S['OWNER'], S['DEMO'])

    def check_jie(c):
        c.if_script(ready_js, then=lambda c: (
            c.switch(S['JIE_READY'], True),
            c.hint('（地铁口那边，好像有人在找你。）')))

    def owner_talk(c):
        c.say('老板娘', '小林，今天下班这么早？', '又去地铁口唱歌啊？')
        c.say('老板娘', '哎，我说你一个大学生，', '这么冷的天在外面唱歌，图啥呢？')
        c.say('老板娘', '我有个朋友的公司在招行政，', '朝九晚五，有五险一金。', '要不要去试试？')
        c.choices(['谢谢您，我去试试。', '谢谢……可我想再坚持一下。'], [
            lambda c: (c.var(V['CH3_CHOICE'], 1),
                       say_me(c, '谢谢您。我去试试。', '白天上班，晚上唱歌，也挺好的。'),
                       c.say('老板娘', '这就对了！', '喜欢的事，又不是非得当饭吃。')),
            lambda c: (c.var(V['CH3_CHOICE'], 2),
                       say_me(c, '谢谢您……', '可我想再坚持一年。'),
                       c.say('老板娘', '你这孩子，倔得很。', '今天剩的面包你拿着，别饿着。')),
        ])
        c.switch(S['OWNER'], True)
        check_jie(c)

    cx, cy = pts['cafe_door']
    ev.add('老板娘', cx - 1, cy + 1, [
        page(owner_talk, image=('$Cafe_Owner', DOWN), cond=C('CH3')),
        page(lambda c: c.say('老板娘', '早点回去，别冻着。'), image=('$Cafe_Owner', DOWN), cond=C('CH3', 'OWNER')),
    ])
    ev.add('咖啡馆的门', cx, cy, [page(lambda c: (c.text('咖啡馆已经打烊了。', '我白天在这里打工。'), step_back(c, 'd')),
                                     trigger=1, priority=0)])

    def demo(c):
        c.se('YY_Door', 60)
        c.text('我推开唱片公司的玻璃门。')
        c.say('前台', '小样放这儿吧。', '我们会听的。')
        say_me(c, '上次那张……你们听了吗？')
        c.say('前台', '这个……', '我们每天收到几百张，会尽量听的。')
        c.text('（她身后的纸箱里，塞满了没拆封的CD。）')
        say_me(c, '……谢谢。')
        c.switch(S['DEMO'], True)
        step_back(c, 'd')
        check_jie(c)

    rx, ry = pts['record_door']
    ev.add('唱片公司', rx, ry, [
        page(demo, trigger=1, priority=0, cond=C('CH3')),
        page(lambda c: (c.text('星海唱片。', '门卫说，今天不收小样了。'), step_back(c, 'd')), trigger=1, priority=0,
             cond=C('CH3', 'DEMO')),
    ])
    hx, hy = pts['home_door']
    ev.add('回家', hx, hy, [page(lambda c: (c.se('YY_Door', 60), c.transfer(M.BASEMENT, 8, 9, UP, fade=0)),
                               trigger=1, priority=0)])

    # 阿杰 says goodbye
    def jie_bye(c):
        c.say('阿杰', '音音！', '我找了你好久。')
        say_me(c, '阿杰？', '你怎么穿成这样……')
        c.say('阿杰', '我……找了份工作。明天就入职了。')
        c.say('阿杰', '乐队的事，我不能再陪你了。')
        c.say('阿杰', '我爸病了，家里需要钱。', '而且……我也想明白了。')
        c.say('阿杰', '我没有你那么喜欢。', '喜欢到饿着肚子也不在乎的那种……我做不到。')
        c.wait(30)
        say_me(c, '……我知道。', '没关系的，阿杰。')
        c.say('阿杰', '这个给你。', '我用它弹了十年。以后，替我多弹几首。')
        c.item(I['PICK'], 1)
        c.se('YY_Item')
        c.text('\\I[9] 得到了\\C[6]阿杰的拨片\\C[0]。')
        c.say('阿杰', '……音音，你一定要唱下去啊。')
        c.route(THIS, ['through_on', 'left', 'left', 'left', 'left', 'left', 'left', 'left', 'left'], wait=True)
        c.switch(S['JIE_BYE'], True)
        c.hint('（去地铁口吧。今天，也要唱歌。）')

    ev.add('阿杰', 21, 8, [page(None, cond=C('CH3')),
                         page(jie_bye, image=('$Jie_Adult', LEFT), cond=C('CH3', 'JIE_READY')),
                         page(None, cond=C('CH3', 'JIE_BYE'))])

    # passers-by
    walkers = [('$Passerby_Suit', 2, 14, ['right'] * 20 + ['left'] * 20, 'CH3'),
               ('$Passerby_Woman', 30, 7, ['left'] * 22 + ['right'] * 22, 'CH3'),
               ('$Passerby_Student', 8, 15, ['right'] * 18 + ['left'] * 18, 'CH3')]
    for (img, x, y, route, sw) in walkers:
        ev.add('路人', x, y, [page(lambda c: c.text('路人匆匆地走过去了。'), image=(img, DOWN), cond=C(sw),
                                  route=route, through=True, move_speed=3, move_freq=5)])

    bx, by = pts['busk']
    case = ev.add('琴盒', bx, by + 1, [page(None, cond=C('CH3')),
                                       page(None, image=('!$GuitarCase', DOWN), cond=C('CH3', 'CASE_OUT')),
                                       page(None, image=('!$GuitarCase', RIGHT), cond=C('CH3', 'CANDY'))])
    yu = ev.add('小女孩', 28, 14, [page(None, cond=C('CH3')),
                                   page(None, image=('$Xiaoyu_Child', LEFT), cond=C('CH3', 'XIAOYU'))])
    yumom = ev.add('小女孩的妈妈', 29, 14, [page(None, cond=C('CH3')),
                                           page(None, image=('$Xiaoyu_Mom', LEFT), cond=C('CH3', 'XIAOYU'))])

    def busk(c):
        c.face(PLAYER, DOWN)
        c.switch(S['CASE_OUT'], True)
        c.se('YY_Strum', 70)
        c.narrate('我打开琴盒，开始唱歌。')
        c.fade_bgm(4)
        c.wait(60)
        c.narrate('一个小时。', '两个小时。', '雪越下越大。')
        c.weather('snow', 8, 60, False)
        c.narrate('来来往往的人那么多，', '却没有一个人停下来。')
        c.wait(30)
        say_me(c, '（……也许，我真的不适合吧。）')
        say_me(c, '（收拾东西，回家吧。）')
        c.wait(30)
        c.switch(S['XIAOYU'], True)
        c.route(yu, ['left'] * 7 + ['turn_left'], wait=False)
        c.route(yumom, ['left'] * 7, wait=True)
        c.say('小女孩', '妈妈，等一下！', '我想听姐姐唱歌。')
        c.say('小女孩的妈妈', '雨雨，太晚了，', '明天还要去医院看爸爸……')
        c.say('小女孩', '就听一首！就一首！')
        c.face(PLAYER, RIGHT)
        c.say('小女孩', '姐姐，你能再唱一首吗？')
        c.wait(20)
        say_me(c, '……好。', '姐姐给你唱一首新写的。')
        c.plugin('LifeSong Echo Gtr %s %d 为她唱一首歌' % (P3, V['RESULT']))
        c.bgm('YY_Harmonica', 50)
        c.say('小女孩', '……真好听。')
        c.say('小女孩', '姐姐，这个给你。', '这是我最喜欢的糖。')
        c.switch(S['CANDY'], True)
        c.item(I['CANDY'], 1)
        c.se('YY_Coin', 70)
        c.text('\\I[5] 小女孩把一颗\\C[6]粉色的糖\\C[0]，', '轻轻放进了琴盒里。')
        c.say('小女孩的妈妈', '……谢谢你。', '她爸爸住院了，', '她已经好久没有笑过了。')
        c.say('小女孩', '姐姐，你以后一定会变成大明星的！', '拜拜！')
        c.route(yu, ['through_on'] + ['right'] * 9, wait=False)
        c.route(yumom, ['through_on'] + ['right'] * 9, wait=True)
        c.switch(S['XIAOYU'], False)
        c.wait(30)
        c.narrate('那天晚上，', '我握着那颗糖，在雪地里站了很久。')
        c.narrate('我突然明白了——')
        c.narrate('就算只有一个人在听，', '也值得。')
        fragment(c, 18, '霓虹', '6 1 6 5 3 5 6', '城市的灯那么多，总有一盏，是为你亮的。')
        c.switch(S['BUSKED'], True)
        lines_a = ['后来，我白天在公司上班，', '晚上和周末，继续在街头唱歌。', '日子很累，可我从来没有停下来。']
        lines_b = ['后来，我又在街头唱了很多年。', '日子很穷，可我从来没有停下来。']
        common = ['三十岁那年，一位音乐人在地铁口听见了我的歌。',
                  '从那以后，我开始给别人写歌。', '写了很多很多首。', '……',
                  '二〇三五年，春天。我四十五岁。', '一天早上醒来，世界忽然安静了。',
                  '\\C[6]【医生】\\C[0]突发性耳聋。', '右耳的听力，恐怕很难恢复了。',
                  '左耳也会慢慢受影响……', '高音，你会越来越听不清。',
                  '\\C[6]【林音】\\C[0]……那我，还能写歌吗？',
                  '医生没有回答。', '我回到了清水村。', '回到了那个，我学会“听”的地方。']
        c.if_var(V['CH3_CHOICE'], '==', 1,
                 then=lambda c: goto_chapter(c, 4, lines_a + common),
                 else_=lambda c: goto_chapter(c, 4, lines_b + common))

    ev.add('卖唱的地方', bx, by, [page(None, cond=C('CH3')),
                               page(lambda c: (say_me(c, '（就在这里唱吧。）'),
                                               c.hint('（不过……先四处走走吧。今天还有些事要做。）')),
                                    image=('!$Sparkle', DOWN), cond=C('CH3', 'PHONE'), step_anime=True, priority=0,
                                    trigger=1),
                               page(busk, image=('!$Sparkle', DOWN), cond=C('CH3', 'JIE_BYE'), step_anime=True,
                                    priority=0, trigger=1),
                               page(None, cond=C('CH3', 'CASE_OUT'))])

    def flavor(name, x, y, lines):
        ev.add(name, x, y, [page(lambda c: c.text(*lines))])

    flavor('雪人', 30, 14, ['不知道是谁堆的雪人。', '围巾比我的还新。'])
    flavor('自动售货机', 25, 7, ['热饮：三块五。', '……还是算了。'])
    flavor('公交站', 7, 13, ['末班车已经开走了。'])
    flavor('长椅', 9, 13, ['长椅上落满了雪。'])
    flavor('长椅', 10, 13, ['长椅上落满了雪。'])

    def subway(c):
        say_me(c, '（今天不坐地铁。', '就在这里唱。）')
        step_back(c, 'd')

    sx, sy = pts['subway']
    ev.add('地铁口', sx, sy, [page(subway, trigger=1, priority=0)])
    return ev.list
