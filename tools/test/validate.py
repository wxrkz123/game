"""Static checks on YuYin/data:
  * event command lists are well formed (indents, branch terminators)
  * every referenced image / audio file exists
  * every transfer goes to a valid, passable tile
  * every interactable event can be reached from the map's entry points
Run:  python3 tools/test/validate.py
"""
import json
import os
import re
import sys
from collections import deque

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'YuYin'))
DATA = os.path.join(ROOT, 'data')
problems = []


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


tilesets = load('Tilesets.json')
system = load('System.json')
infos = load('MapInfos.json')
maps = {i['id']: load('Map%03d.json' % i['id']) for i in infos if i}


def tile_passable(mp, x, y):
    w, h = mp['width'], mp['height']
    if not (0 <= x < w and 0 <= y < h):
        return False
    flags = tilesets[mp['tilesetId']]['flags']
    for z in (3, 2, 1, 0):
        tid = mp['data'][(z * h + y) * w + x]
        f = flags[tid]
        if f & 0x10:
            continue
        if (f & 0x0F) == 0:
            return True
        if (f & 0x0F) == 0x0F:
            return False
    return False


def all_commands():
    for mid, mp in maps.items():
        for ev in mp['events']:
            if not ev:
                continue
            for pi, pg in enumerate(ev['pages']):
                yield ('map%d %s(%d) p%d' % (mid, ev['name'], ev['id'], pi + 1), pg['list'])
    for ce in load('CommonEvents.json'):
        if ce:
            yield ('common %s' % ce['name'], ce['list'])


# ---- 1. structure ---------------------------------------------------------
OPENERS = {102: (402, 404), 111: (411, 412), 112: (None, 413)}
for where, lst in all_commands():
    if not lst or lst[-1]['code'] != 0 or lst[-1]['indent'] != 0:
        problems.append('%s: list must end with code 0 at indent 0' % where)
    stack = []
    for i, cmd in enumerate(lst):
        c, ind = cmd['code'], cmd['indent']
        if c in OPENERS:
            stack.append((c, ind))
        if c in (402, 404, 411, 412, 413, 403):
            if not stack or stack[-1][1] != ind:
                problems.append('%s: misplaced %d at #%d' % (where, c, i))
            elif c in (404, 412, 413):
                stack.pop()
        if c == 401 and i > 0 and lst[i - 1]['code'] not in (101, 401):
            problems.append('%s: orphan 401 at #%d' % (where, i))
    if stack:
        problems.append('%s: unclosed blocks %s' % (where, stack))

# ---- 2. files ----------------------------------------------------------------
def need(kind, name):
    if not name:
        return
    if kind in ('bgm', 'bgs', 'me', 'se'):
        p = os.path.join(ROOT, 'audio', kind, name + '.ogg')
    else:
        p = os.path.join(ROOT, 'img', kind, name + '.png')
    if not os.path.exists(p):
        problems.append('missing %s/%s' % (kind, name))


for where, lst in all_commands():
    for cmd in lst:
        c, p = cmd['code'], cmd['parameters']
        if c in (241, 245, 249, 250):
            need({241: 'bgm', 245: 'bgs', 249: 'me', 250: 'se'}[c], p[0]['name'])
        if c == 322:
            need('characters', p[1])
        if c == 231:
            need('pictures', p[1])
        if c == 356:
            m = re.match(r'LifeSong (Echo|Feel|Free|Play|Song) (\S+)', p[0])
            if m:
                inst = {'harm': 'Harm', 'gtr': 'Gtr', 'pno': 'Pno', 'box': 'Box', 'rec': 'Rec'}[m.group(2).lower()]
                for n in range(1, 9):
                    need('se', 'YY_%s_%d' % (inst, n))
        if c == 205:
            for mv in p[1]['list']:
                if mv['code'] == 44:
                    need('se', mv['parameters'][0]['name'])
for mid, mp in maps.items():
    for ev in mp['events']:
        if ev:
            for pg in ev['pages']:
                need('characters', pg['image']['characterName'])
for s in system['sounds']:
    need('se', s['name'])
need('bgm', system['titleBgm']['name'])
need('titles1', system['title1Name'])
need('titles2', system['title2Name'])
for ts in tilesets:
    if ts:
        for n in ts['tilesetNames']:
            need('tilesets', n)

# ---- 3. transfers & reachability ---------------------------------------------
entries = {mid: set() for mid in maps}
entries[system['startMapId']].add((system['startX'], system['startY']))
for where, lst in all_commands():
    for cmd in lst:
        if cmd['code'] == 201 and cmd['parameters'][0] == 0:
            _, m, x, y = cmd['parameters'][:4]
            if m not in maps:
                problems.append('%s: transfer to missing map %d' % (where, m))
                continue
            entries[m].add((x, y))
            if m != 10 and not tile_passable(maps[m], x, y):
                problems.append('%s: transfer target (%d,%d) on map %d is not passable' % (where, x, y, m))


def static_blockers(mp):
    """events that block in every state: all pages same-priority, non-through, with an image"""
    out = set()
    for ev in mp['events']:
        if not ev:
            continue
        if all(pg['priorityType'] == 1 and not pg['through'] and
               (pg['image']['characterName'] or pg['image']['tileId']) and pg['moveType'] == 0
               for pg in ev['pages']) and ev['pages']:
            out.add((ev['x'], ev['y']))
    return out


for mid, mp in maps.items():
    if mid == 10:
        continue
    blocked = static_blockers(mp)
    seen = set()
    q = deque(entries[mid])
    seen.update(entries[mid])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in seen:
                continue
            if tile_passable(mp, nx, ny) and (nx, ny) not in blocked:
                seen.add((nx, ny))
                q.append((nx, ny))
    for ev in mp['events']:
        if not ev:
            continue
        interactive = [pg for pg in ev['pages'] if pg['trigger'] in (0, 1, 2) and len(pg['list']) > 1]
        if not interactive:
            continue
        x, y = ev['x'], ev['y']
        below = all(pg['priorityType'] != 1 for pg in interactive)
        if below and (x, y) in seen:
            continue
        if any((x + dx, y + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            continue
        problems.append('map%d: event "%s" at (%d,%d) cannot be reached' % (mid, ev['name'], x, y))

print('\n'.join(problems) if problems else 'all checks passed')
print('%d problem(s)' % len(problems))
sys.exit(1 if problems else 0)
