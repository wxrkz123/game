"""Export the whole story from YuYin/data into docs/剧本.md (readable script)."""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA = os.path.join(ROOT, 'YuYin', 'data')


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


system = load('System.json')
infos = load('MapInfos.json')
actor = load('Actors.json')[1]['name']
SW = system['switches']
INST = {'Harm': '口琴', 'Gtr': '吉他', 'Pno': '钢琴', 'Box': '八音盒', 'Rec': '竖笛'}


def clean(t):
    t = t.replace('\\N[1]', actor)
    t = re.sub(r'\\[CI]\[\d+\]', '', t)
    t = t.replace('\\V[3]', 'N')
    return t


def cond_text(c):
    parts = []
    if c['switch1Valid']:
        parts.append(SW[c['switch1Id']])
    if c['switch2Valid']:
        parts.append(SW[c['switch2Id']])
    if c['selfSwitchValid']:
        parts.append('（之后）')
    return ' + '.join(parts) if parts else '（任何时候）'


def describe(lst):
    out = []
    i = 0
    while i < len(lst):
        cmd = lst[i]
        code, p, ind = cmd['code'], cmd['parameters'], cmd['indent']
        pad = '  ' * ind
        if code == 101:
            lines = []
            j = i + 1
            while j < len(lst) and lst[j]['code'] == 401:
                lines.append(clean(lst[j]['parameters'][0]))
                j += 1
            text = ' '.join(lines)
            m = re.match(r'^【(.+?)】(.*)$', text)
            if m:
                out.append('%s- **%s**：%s' % (pad, m.group(1), m.group(2)))
            else:
                out.append('%s- *%s*' % (pad, text))
            i = j
            continue
        if code == 102:
            out.append('%s- 〔选择〕%s' % (pad, ' ／ '.join(p[0])))
        elif code == 402:
            out.append('%s- 选「%s」：' % (pad, p[1]))
        elif code == 356:
            m = re.match(r'LifeSong (\w+) ?(\S*) ?(\S*) ?(\S*) ?(.*)', p[0])
            if m:
                sub, inst, a, b, rest = m.groups()
                if sub == 'Chapter':
                    out.append('%s- 🎬 章节标题卡：**%s %s** %s' % (pad, inst, a, (b + ' ' + rest).strip()))
                elif sub in ('Echo', 'Feel'):
                    out.append('%s- 🎵 旋律小游戏（%s，%s）：`%s` —— %s' % (
                        pad, INST.get(inst, inst), '跟着弹' if sub == 'Echo' else '用眼睛“听”', a, rest))
                elif sub == 'Free':
                    out.append('%s- 🎵 自由演奏（%s）：%s' % (pad, INST.get(inst, inst), rest or '随便弹弹'))
                elif sub == 'Play':
                    out.append('%s- 🎶（%s 奏出旋律 `%s`）' % (pad, INST.get(inst, inst), a))
                elif sub == 'Song':
                    out.append('%s- 🎶（钢琴弹完整首歌，加上玩家写的最后一句）' % pad)
        elif code == 126 and p[1] == 0:
            pass
        elif code == 105:
            out.append('%s- 📜 滚动字幕（片尾）' % pad)
        i += 1
    return out


def main():
    lines = ['# 《余音》完整剧本', '',
             '> 这份剧本是从游戏数据（`YuYin/data`）自动导出的，和游戏里的内容完全一致。',
             '> 想改台词？请直接在 RPG Maker MV 里打开对应地图的事件修改（见《新手教程》）。', '']
    order = [10, 1, 3, 2, 4, 5, 6, 7, 9, 8]
    names = {i['id']: i['name'] for i in infos if i}
    for mid in order:
        mp = load('Map%03d.json' % mid)
        lines.append('## 地图 %s' % names[mid])
        lines.append('')
        seen = set()
        for ev in mp['events']:
            if not ev:
                continue
            for pg in ev['pages']:
                body = describe(pg['list'])
                if not any('**' in b or '🎵' in b or '🎬' in b or '*' in b for b in body):
                    continue
                key = (ev['name'], tuple(body))
                if key in seen:
                    continue
                seen.add(key)
                trig = {0: '对话/调查', 1: '走上去', 3: '自动剧情', 4: '自动'}.get(pg['trigger'], '')
                lines.append('### %s 〔%s · %s〕' % (ev['name'], cond_text(pg['conditions']), trig))
                lines.extend(body)
                lines.append('')
    with open(os.path.join(ROOT, 'docs', '剧本.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('docs/剧本.md written:', len(lines), 'lines')


if __name__ == '__main__':
    main()
