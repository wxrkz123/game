"""Helpers that produce RPG Maker MV data structures (events, pages, maps...).

The Cmd class is a small DSL for event command lists:

    c = Cmd()
    c.say('爷爷', '小音，你听——')
    c.choices(['好', '不要'], [lambda c: c.text('...'), lambda c: c.text('...')])
    c.if_switch(11, then=lambda c: c.se('YY_Item'))
"""
import copy

PLAYER, THIS = -1, 0
DOWN, LEFT, RIGHT, UP = 2, 4, 6, 8

# move route command codes
MV = dict(down=1, left=2, right=3, up=4, dl=5, dr=6, ul=7, ur=8, random=9, toward=10, away=11,
          forward=12, backward=13, jump=14, wait=15, turn_down=16, turn_left=17, turn_right=18,
          turn_up=19, turn_toward=25, turn_away=26, speed=29, freq=30, walk_on=31, walk_off=32,
          step_on=33, step_off=34, dirfix_on=35, dirfix_off=36, through_on=37, through_off=38,
          transparent_on=39, transparent_off=40, image=41, opacity=42, se=44, script=45)

MAX_LINE = 26   # CJK characters per message line (24px font, 780px window)


def audio(name, volume=90, pitch=100, pan=0):
    return {'name': name, 'volume': volume, 'pitch': pitch, 'pan': pan}


def _visual_len(s):
    n = 0
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == '\\':
            # skip escape codes like \N[1] \C[6] \I[4] \. \|
            j = i + 1
            while j < len(s) and s[j].isalpha():
                j += 1
            if j < len(s) and s[j] == '[':
                k = s.find(']', j)
                if k < 0:
                    break
                if s[i + 1:j] in ('N', 'n'):
                    n += 2 * 2  # a name is about 2 CJK chars
                elif s[i + 1:j] in ('I', 'i'):
                    n += 2
                i = k + 1
                continue
            i = j if j > i + 1 else i + 2
            continue
        n += 1 if ord(ch) > 0x2E80 else 0.5
        i += 1
    return n


def wrap(line, width=MAX_LINE):
    """Soft-wrap a long line at CJK punctuation if possible."""
    if _visual_len(line) <= width:
        return [line]
    out = []
    cur = ''
    for ch in line:
        cur += ch
        if _visual_len(cur) >= width - 1 and ch in '，。！？…、；：）」』—~ ':
            out.append(cur)
            cur = ''
        elif _visual_len(cur) >= width + 2:
            out.append(cur)
            cur = ''
    if cur:
        out.append(cur)
    return out


class Cmd:
    def __init__(self, indent=0):
        self.list = []
        self.indent = indent

    # -- low level ------------------------------------------------------------
    def add(self, code, params=None):
        self.list.append({'code': code, 'indent': self.indent, 'parameters': params if params is not None else []})
        return self

    def _block(self, fn):
        """run fn one indent deeper and close the block with the editor's code-0 line."""
        self.indent += 1
        if fn:
            if callable(fn):
                fn(self)
            else:
                for f in fn:
                    f(self)
        self.add(0, [])
        self.indent -= 1

    def end(self):
        self.list.append({'code': 0, 'indent': self.indent, 'parameters': []})
        return self.list

    # -- messages ---------------------------------------------------------------
    def text(self, *lines, pos=2, bg=0, face='', face_index=0):
        flat = []
        for ln in lines:
            for part in str(ln).split('\n'):
                flat.extend(wrap(part))
        for i in range(0, len(flat), 4):
            self.add(101, [face, face_index, bg, pos])
            for ln in flat[i:i + 4]:
                self.add(401, [ln])
        return self

    def say(self, name, *lines, **kw):
        lines = list(lines)
        first = '【%s】%s' % (name, lines[0] if lines else '')
        flat = []
        for part in [first] + lines[1:]:
            for p in str(part).split('\n'):
                flat.extend(wrap(p))
        # keep the speaker tag on every page
        pages = [flat[i:i + 4] for i in range(0, len(flat), 4)]
        for k, page in enumerate(pages):
            if k > 0 and not page[0].startswith('【'):
                page[0] = '【%s】%s' % (name, page[0])
            self.add(101, [kw.get('face', ''), kw.get('face_index', 0), kw.get('bg', 0), kw.get('pos', 2)])
            for ln in page:
                self.add(401, [ln])
        return self

    def narrate(self, *lines):
        """centred-ish narration on a dim background"""
        return self.text(*lines, bg=1, pos=1)

    def hint(self, *lines):
        return self.text(*['\\C[8]' + ln + '\\C[0]' for ln in lines], bg=1, pos=2)

    def scroll(self, lines, speed=2, no_fast=False):
        self.add(105, [speed, no_fast])
        for ln in lines:
            self.add(405, [ln])
        return self

    def choices(self, options, branches, cancel=-2, default=0, pos=2, bg=0):
        """branches: list of callables, one per option (None = empty)."""
        cancel_type = cancel if cancel != -2 else -1
        self.add(102, [list(options), cancel_type, default, pos, bg])
        for i, opt in enumerate(options):
            self.add(402, [i, opt])
            self._block(branches[i] if i < len(branches) else None)
        if cancel_type == len(options):
            self.add(403, [6, None])
            self._block(branches[len(options)] if len(branches) > len(options) else None)
        self.add(404, [])
        return self

    # -- flow -------------------------------------------------------------------
    def _if(self, params, then, else_):
        self.add(111, params)
        self._block(then)
        if else_ is not None:
            self.add(411, [])
            self._block(else_)
        self.add(412, [])
        return self

    def if_switch(self, sid, on=True, then=None, else_=None):
        return self._if([0, sid, 0 if on else 1], then, else_)

    def if_var(self, vid, op, value, then=None, else_=None):
        ops = {'==': 0, '>=': 1, '<=': 2, '>': 3, '<': 4, '!=': 5}
        return self._if([1, vid, 0, value, ops[op]], then, else_)

    def if_self(self, ch, on=True, then=None, else_=None):
        return self._if([2, ch, 0 if on else 1], then, else_)

    def if_item(self, item_id, then=None, else_=None):
        return self._if([8, item_id], then, else_)

    def if_script(self, js, then=None, else_=None):
        return self._if([12, js], then, else_)

    def loop(self, body):
        self.add(112, [])
        self._block(body)
        self.add(413, [])
        return self

    def break_loop(self):
        return self.add(113, [])

    def exit(self):
        return self.add(115, [])

    def common(self, cid):
        return self.add(117, [cid])

    def label(self, name):
        return self.add(118, [name])

    def jump(self, name):
        return self.add(119, [name])

    # -- game state ---------------------------------------------------------------
    def switch(self, sid, on=True):
        return self.add(121, [sid, sid, 0 if on else 1])

    def var(self, vid, value, op='='):
        ops = {'=': 0, '+': 1, '-': 2, '*': 3, '/': 4, '%': 5}
        return self.add(122, [vid, vid, ops[op], 0, value])

    def var_script(self, vid, js):
        return self.add(122, [vid, vid, 0, 4, js])

    def self_switch(self, ch='A', on=True):
        return self.add(123, [ch, 0 if on else 1])

    def item(self, item_id, n=1):
        return self.add(126, [item_id, 0 if n >= 0 else 1, 0, abs(n)])

    def menu_access(self, on):
        return self.add(135, [1 if on else 0])

    def save_access(self, on):
        return self.add(134, [1 if on else 0])

    # -- movement ---------------------------------------------------------------
    def transfer(self, map_id, x, y, d=0, fade=0):
        return self.add(201, [0, map_id, x, y, d, fade])

    def locate(self, char_id, x, y, d=0):
        return self.add(203, [char_id, 0, x, y, d])

    def route(self, char_id, moves, wait=True, repeat=False, skip=True):
        """moves: list of names from MV (or (name, params) tuples)."""
        lst = []
        for m in moves:
            if isinstance(m, tuple):
                name, prm = m[0], list(m[1:])
            else:
                name, prm = m, []
            if name == 'se':
                prm = [audio(*prm)] if isinstance(prm[0], str) else prm
            lst.append({'code': MV[name], 'indent': None, 'parameters': prm})
        lst.append({'code': 0, 'parameters': []})
        self.add(205, [char_id, {'list': lst, 'repeat': repeat, 'skippable': skip, 'wait': wait}])
        for mv in lst[:-1]:
            self.add(505, [mv])
        return self

    def walk(self, char_id, path, wait=True, speed=None, through=False):
        """path like 'uuurr' or 'u3 r2'."""
        moves = []
        if speed:
            moves.append(('speed', speed))
        if through:
            moves.append('through_on')
        letters = {'u': 'up', 'd': 'down', 'l': 'left', 'r': 'right'}
        import re
        for (ch, num) in re.findall(r'([udlr])(\d*)', path):
            moves.extend([letters[ch]] * (int(num) if num else 1))
        if through:
            moves.append('through_off')
        return self.route(char_id, moves, wait=wait)

    def face(self, char_id, d):
        name = {2: 'turn_down', 4: 'turn_left', 6: 'turn_right', 8: 'turn_up'}[d]
        return self.route(char_id, [name], wait=True)

    def wait_route(self):
        return self.add(209, [])

    def transparent(self, on):
        return self.add(211, [0 if on else 1])

    def balloon(self, char_id, bid, wait=True):
        ids = {'!': 1, '?': 2, 'note': 3, 'heart': 4, 'anger': 5, 'sweat': 6, 'mess': 7, '...': 8,
               'idea': 9, 'zzz': 10, 'sparkle': 11, 'tear': 12, 'flower': 13, 'music': 14, 'silence': 15}
        return self.add(213, [char_id, ids.get(bid, bid), wait])

    def erase(self):
        return self.add(214, [])

    # -- screen -----------------------------------------------------------------
    def fadeout(self):
        return self.add(221, [])

    def fadein(self):
        return self.add(222, [])

    def tint(self, tone, frames=60, wait=True):
        return self.add(223, [list(tone), frames, wait])

    def flash(self, color=(255, 255, 255, 170), frames=30, wait=True):
        return self.add(224, [list(color), frames, wait])

    def shake(self, power=5, speed=5, frames=30, wait=True):
        return self.add(225, [power, speed, frames, wait])

    def wait(self, frames):
        return self.add(230, [frames])

    def weather(self, kind='none', power=5, frames=60, wait=False):
        return self.add(236, [kind, power, frames, wait])

    def picture(self, pid, name, x=0, y=0, opacity=255, origin=0):
        return self.add(231, [pid, name, origin, 0, x, y, 100, 100, opacity, 0])

    def erase_picture(self, pid):
        return self.add(235, [pid])

    # -- audio --------------------------------------------------------------------
    def bgm(self, name, volume=80, pitch=100):
        return self.add(241, [audio(name, volume, pitch)])

    def fade_bgm(self, seconds=2):
        return self.add(242, [seconds])

    def bgs(self, name, volume=70, pitch=100):
        return self.add(245, [audio(name, volume, pitch)])

    def fade_bgs(self, seconds=2):
        return self.add(246, [seconds])

    def me(self, name, volume=90):
        return self.add(249, [audio(name, volume)])

    def se(self, name, volume=90, pitch=100):
        return self.add(250, [audio(name, volume, pitch)])

    # -- actors / system --------------------------------------------------------
    def actor_image(self, char_name, char_index=0, face='', face_index=0, actor=1):
        return self.add(322, [actor, char_name, char_index, face, face_index, ''])

    def nickname(self, nick, actor=1):
        return self.add(324, [actor, nick])

    def map_name(self, on):
        return self.add(281, [0 if on else 1])

    def to_title(self):
        return self.add(354, [])

    def plugin(self, text):
        return self.add(356, [text])

    def script(self, js):
        lines = js.strip().split('\n')
        self.add(355, [lines[0]])
        for ln in lines[1:]:
            self.add(655, [ln])
        return self


def build(fn):
    """fn(Cmd) -> finalized command list"""
    c = Cmd()
    if fn:
        fn(c)
    return c.end()


# ---------------------------------------------------------------------------
# events
# ---------------------------------------------------------------------------

def page(commands=None, image=None, trigger=0, priority=1, cond=None, move_type=0, move_speed=3,
         move_freq=3, walk_anime=True, step_anime=False, dir_fix=False, through=False, route=None):
    """cond: dict with any of switch1, switch2, var=(id, value), self='A', item=id, actor=id"""
    cond = cond or {}
    img = {'tileId': 0, 'characterName': '', 'direction': 2, 'pattern': 1, 'characterIndex': 0}
    if image:
        if isinstance(image, int):
            img['tileId'] = image
            img['pattern'] = 0
        else:
            name = image[0]
            img['characterName'] = name
            img['direction'] = image[1] if len(image) > 1 else 2
            img['characterIndex'] = image[2] if len(image) > 2 else 0
            img['pattern'] = image[3] if len(image) > 3 else 1
    if image is None and commands is None and trigger in (0, 1, 2):
        priority = 0          # an empty placeholder page must never block the player
    var = cond.get('var')
    mr = {'list': [{'code': 0, 'parameters': []}], 'repeat': True, 'skippable': False, 'wait': False}
    if route:
        lst = []
        for m in route:
            if isinstance(m, tuple):
                lst.append({'code': MV[m[0]], 'indent': None, 'parameters': list(m[1:])})
            else:
                lst.append({'code': MV[m], 'indent': None, 'parameters': []})
        lst.append({'code': 0, 'parameters': []})
        mr = {'list': lst, 'repeat': True, 'skippable': True, 'wait': False}
        move_type = 3
    return {
        'conditions': {
            'actorId': cond.get('actor', 1), 'actorValid': 'actor' in cond,
            'itemId': cond.get('item', 1), 'itemValid': 'item' in cond,
            'selfSwitchCh': cond.get('self', 'A'), 'selfSwitchValid': 'self' in cond,
            'switch1Id': cond.get('switch1', 1), 'switch1Valid': 'switch1' in cond,
            'switch2Id': cond.get('switch2', 1), 'switch2Valid': 'switch2' in cond,
            'variableId': var[0] if var else 1, 'variableValid': bool(var),
            'variableValue': var[1] if var else 0,
        },
        'directionFix': dir_fix,
        'image': img,
        'list': build(commands) if (commands is None or callable(commands)) else commands,
        'moveFrequency': move_freq,
        'moveRoute': mr,
        'moveSpeed': move_speed,
        'moveType': move_type,
        'priorityType': priority,
        'stepAnime': step_anime,
        'through': through,
        'trigger': trigger,
        'walkAnime': walk_anime,
    }


def event(eid, name, x, y, pages, note=''):
    return {'id': eid, 'name': name, 'note': note, 'pages': pages, 'x': x, 'y': y}


def map_json(w, h, tileset_id, data, events, display_name='', bgm=None, bgs=None, note='', parallax=''):
    return {
        'autoplayBgm': bool(bgm), 'autoplayBgs': bool(bgs),
        'battleback1Name': '', 'battleback2Name': '',
        'bgm': audio(bgm or '', 80), 'bgs': audio(bgs or '', 70),
        'disableDashing': False, 'displayName': display_name,
        'encounterList': [], 'encounterStep': 30,
        'height': h, 'note': note,
        'parallaxLoopX': False, 'parallaxLoopY': False, 'parallaxName': parallax,
        'parallaxShow': True, 'parallaxSx': 0, 'parallaxSy': 0,
        'scrollType': 0, 'specifyBattleback': False,
        'tilesetId': tileset_id, 'width': w,
        'data': data, 'events': events,
    }
