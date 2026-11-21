"""card_art.py ROM OUT.png IDX[,IDX..] [MAPW]: render entries of the 8bpp art table at 0xD80BD4.

The table holds (tiles, palette, map) ROM pointer triples (12 bytes each; the second half of the table, from
0xD80DE4, holds pairs with a zero third word and is not rendered here). Tiles are 8bpp with pixel values
0x81-0x9F (0 = transparent), indexing the 0x140-byte palette (0xA0 colours) directly. The map is 0x230 bytes of u16 BG entries
(tile | hflip 0x400 | vflip 0x800), MAPW (default 14) entries per row. See docs/re/graphics.md (0x7ED50C row).
"""
import struct
import sys

from PIL import Image

TABLE = 0xD80BD4


def ptr(d, o):
    return struct.unpack_from('<I', d, o)[0] - 0x08000000


def render(d, k, w):
    t, p, m = (ptr(d, TABLE + k * 12 + 4 * i) for i in range(3))
    pal = [struct.unpack_from('<H', d, p + 2 * i)[0] for i in range(0xA0)]
    rgb = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in pal]
    ents = struct.unpack_from('<%dH' % (0x230 // 2), d, m)
    h = (len(ents) + w - 1) // w
    im = Image.new('RGB', (w * 8, h * 8))
    px = im.load()
    for i, e in enumerate(ents):
        base = t + (e & 0x3FF) * 64
        for y in range(8):
            for x in range(8):
                xx = 7 - x if e & 0x400 else x
                yy = 7 - y if e & 0x800 else y
                c = d[base + yy * 8 + xx]
                px[(i % w) * 8 + x, (i // w) * 8 + y] = rgb[c] if 0 <= c < 0xA0 else (255, 0, 255)
    print(k, 'tiles %X pal %X map %X' % (t, p, m))
    return im


def main(argv):
    d = open(argv[0], 'rb').read()
    w = int(argv[3]) if len(argv) > 3 else 14
    ks = argv[2].split('-')
    ks = range(int(ks[0]), int(ks[1]) + 1) if len(ks) == 2 else [int(k) for k in argv[2].split(',')]
    ims = [render(d, k, w) for k in ks]
    per = 11  # frames per sheet row
    cw, ch = max(i.width for i in ims) + 4, max(i.height for i in ims) + 4
    rows = (len(ims) + per - 1) // per
    sheet = Image.new('RGB', (min(len(ims), per) * cw, rows * ch))
    for n, i in enumerate(ims):
        sheet.paste(i, ((n % per) * cw, (n // per) * ch))
    sheet.save(argv[1])


if __name__ == '__main__':
    main(sys.argv[1:])
