"""sprblock.py: render a ROM block of 4bpp sprite tiles as a row of OBJs (1D mapping), with an OBJ palette bank
taken from a PPU dump, to see which sprite graphics a block holds.

    python -X utf8 tools/debug/sprblock.py ROM OFFSET OBJ_W OBJ_H COUNT PAL_BIN BANK OUT.png [--per-row N] [--zoom 3]

OFFSET hex; OBJ_W/OBJ_H in pixels; PAL_BIN is a ppudump .pal.bin (OBJ palettes at 0x200); BANK 0-15.
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gfx  # noqa: E402


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('offset')
    ap.add_argument('w', type=int)
    ap.add_argument('h', type=int)
    ap.add_argument('count', type=int)
    ap.add_argument('pal')
    ap.add_argument('bank', type=int)
    ap.add_argument('out')
    ap.add_argument('--per-row', type=int, default=4)
    ap.add_argument('--zoom', type=int, default=3)
    a = ap.parse_args(argv)
    rom = Path(a.rom).read_bytes()
    pal = Path(a.pal).read_bytes()[0x200 + a.bank * 32:0x200 + a.bank * 32 + 32]
    rgb = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in struct.unpack('<16H', pal)]
    rgb[0] = (255, 0, 255)
    off = int(a.offset, 16)
    cols, n = a.w // 8, a.w // 8 * (a.h // 8)
    pr = min(a.per_row, a.count)
    img = Image.new('RGB', (pr * (a.w + 2), (a.count + pr - 1) // pr * (a.h + 2)), (0, 0, 0))
    for k in range(a.count):
        px = gfx.decode(rom[off + k * n * 32:off + (k + 1) * n * 32], cols, n)
        ox, oy = k % pr * (a.w + 2), k // pr * (a.h + 2)
        for y in range(a.h):
            for x in range(a.w):
                img.putpixel((ox + x, oy + y), rgb[px[y][x]])
    img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST).save(a.out)
    print(a.out)


if __name__ == '__main__':
    main(sys.argv[1:])
