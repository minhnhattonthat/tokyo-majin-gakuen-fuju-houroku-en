"""gfx_zoom.py ROM OUT.png SPEC.. [--zoom N]: render chosen ROM assets as labelled, zoomed tile strips.

SPEC = OFFSET:LEN:COLS[:BPP], hex OFFSET/LEN, COLS may be a comma list (one strip per width) and BPP is 4 (default)
or 8. Prefix OFFSET with 'z' to LZ77-decompress first (LEN then caps the decompressed bytes; 0 = all).
Example: gfx_zoom.py rom/base.gba work/z.png D1B944:200:4,8 zD14834:0:3
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import lz77  # noqa: E402
from gfx_sweep import render, tiles_of  # noqa: E402


def strips(rom, spec):
    parts = spec.split(':')
    off = parts[0]
    lz = off.startswith('z')
    o = int(off.lstrip('z'), 16)
    n = int(parts[1], 16) if len(parts) > 1 else 0
    cols = [int(c) for c in parts[2].split(',')] if len(parts) > 2 else [16]
    bpp = int(parts[3]) if len(parts) > 3 else 4
    if lz:
        c = lz77.decompress(rom, o)
        c = c[:n] if n else c
    else:
        c = rom[o:o + (n or 0x800)]
    tl = tiles_of(c, bpp)
    if not tl:
        print('%s: %d bytes, no whole tile' % (spec, len(c)))
        return
    for w in cols:
        yield '%s len %X w%d %dbpp' % (off.upper(), len(c), w, bpp), render(tl, bpp, w)


def main(argv):
    zoom = 3
    if '--zoom' in argv:
        i = argv.index('--zoom')
        zoom = int(argv[i + 1])
        del argv[i:i + 2]
    rom = open(argv[0], 'rb').read()
    out = argv[1]
    ims = [(lab, im.resize((im.width * zoom, im.height * zoom), Image.NEAREST))
           for spec in argv[2:] for lab, im in strips(rom, spec)]
    W = max(max(im.width for _, im in ims), 200)
    H = sum(im.height + 14 for _, im in ims)
    sheet = Image.new('L', (W, H), 60)
    d = ImageDraw.Draw(sheet)
    y = 0
    for lab, im in ims:
        d.text((2, y), lab, fill=255)
        sheet.paste(im, (0, y + 12))
        y += im.height + 14
    sheet.save(out)
    print(out, sheet.size)


if __name__ == '__main__':
    main(sys.argv[1:])
