"""romblock.py: render a 4bpp tile block with a 16-colour palette stored in the ROM, original | English build.

    python -X utf8 tools/debug/romblock.py OFFSET COLS NTILES PALOFF OUT.png [--zoom 4] [--rom rom/base.gba]
        [--en build/tmgfh_en.gba] [--obj 2x2]

OFFSET / PALOFF hex. Tiles in row-major order, COLS tiles a row (1D OBJ blocks: COLS = width / 8).
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gfx  # noqa: E402


def render(rom, off, cols, n, paloff, obj=None):
    pal = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in struct.unpack_from('<16H', rom, paloff)]
    if obj:   # 1D OBJs of ow x oh tiles, laid out cols OBJs a row
        ow, oh = obj
        per = ow * oh
        tiles = [gfx.decode(rom[off + t * 32:off + t * 32 + 32], 1, 1) for t in range(n)]
        nobj = n // per
        rows = (nobj + cols - 1) // cols
        px = [[0] * (cols * ow * 8) for _ in range(rows * oh * 8)]
        for t in range(nobj * per):
            o, k = divmod(t, per)
            bx = o % cols * ow * 8 + k % ow * 8
            by = o // cols * oh * 8 + k // ow * 8
            for y in range(8):
                px[by + y][bx:bx + 8] = tiles[t][y]
    else:
        px = gfx.decode(rom[off:off + n * 32], cols, n)
    im = Image.new('RGB', (len(px[0]), len(px)))
    im.putdata([pal[v] for row in px for v in row])
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('offset')
    ap.add_argument('cols', type=int)
    ap.add_argument('ntiles', type=int)
    ap.add_argument('paloff')
    ap.add_argument('out')
    ap.add_argument('--zoom', type=int, default=4)
    ap.add_argument('--rom', default='rom/base.gba')
    ap.add_argument('--en', default='build/tmgfh_en.gba')
    ap.add_argument('--obj', help='WxH in tiles: lay the block out as 1D OBJs of that size, COLS OBJs a row')
    a = ap.parse_args()
    obj = tuple(int(v) for v in a.obj.split('x')) if a.obj else None
    ims = [render(Path(p).read_bytes(), int(a.offset, 16), a.cols, a.ntiles, int(a.paloff, 16), obj)
           for p in (a.rom, a.en)]
    w, h = ims[0].size
    out = Image.new('RGB', (w * 2 + 4, h), (60, 60, 60))
    out.paste(ims[0], (0, 0))
    out.paste(ims[1], (w + 4, 0))
    out.resize((out.width * a.zoom, h * a.zoom), Image.NEAREST).save(a.out)
    print(a.out)


if __name__ == '__main__':
    main()
