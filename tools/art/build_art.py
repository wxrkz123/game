"""Generate every image of 《余音》 into YuYin/img.

    python3 tools/art/build_art.py [path/to/LXGWWenKai.ttf]

The optional font is only used for the title logo; without it the bundled
pixel font is used instead.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', 'YuYin'))

import build_tilesets
import system_art
import title_art
from chars import sheet
from cast import CAST
from object_sprites import SPRITES


def main():
    build_tilesets.build()
    chars_dir = os.path.join(ROOT, 'img', 'characters')
    os.makedirs(chars_dir, exist_ok=True)
    for name, spec in CAST.items():
        sheet(spec).save(os.path.join(chars_dir, name + '.png'))
    for name, fn in SPRITES.items():
        fn().save(os.path.join(chars_dir, name + '.png'))
    system_art.build(os.path.join(ROOT, 'img', 'system'), os.path.join(ROOT, 'icon'))
    title_art.build(ROOT, sys.argv[1] if len(sys.argv) > 1 else None)
    # empty folders the engine / editor expect
    for d in ('animations', 'battlebacks1', 'battlebacks2', 'enemies', 'faces', 'parallaxes',
              'pictures', 'sv_actors', 'sv_enemies'):
        p = os.path.join(ROOT, 'img', d)
        os.makedirs(p, exist_ok=True)
        keep = os.path.join(p, '.gitkeep')
        if not os.listdir(p):
            open(keep, 'w').close()
    print('art done:', len(CAST), 'characters,', len(SPRITES), 'object sprites')


if __name__ == '__main__':
    main()
