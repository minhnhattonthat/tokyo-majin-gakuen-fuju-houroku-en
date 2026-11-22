"""cardnums.py: the ten turn-order cards' numeral corners (8bpp, table 0xD81528), original row over English row.

    python -X utf8 tools/debug/cardnums.py OUT.png [--zoom 4]
"""
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import gfx_battle  # noqa: E402

CARDS = [0xB021EC, 0xB0328C, 0xB0432C, 0xB053CC, 0xB0646C, 0xAFCC4C, 0xAFDD8C, 0xAFEECC, 0xB0000C, 0xB0114C]


def corner(rom, off):
    px = gfx_battle.card_px(rom, off)
    pal = struct.unpack_from('<80H', rom, off - 0xA0)
    base = 0x50 if max(v for row in px for v in row) >= 0x50 else 0
    im = Image.new('RGB', (40, 24))
    for y in range(24):
        for x in range(40):
            c = pal[px[y][x + 8] - base] if px[y][x + 8] >= base else 0
            im.putpixel((x, y), ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8))
    return im


def main():
    out, zoom = sys.argv[1], int(sys.argv[sys.argv.index('--zoom') + 1]) if '--zoom' in sys.argv else 4
    roms = [(ROOT / p).read_bytes() for p in ('rom/base.gba', 'build/tmgfh_en.gba')]
    sheet = Image.new('RGB', (len(CARDS) * 42, 50), (60, 60, 60))
    for i, off in enumerate(CARDS):
        for j, rom in enumerate(roms):
            sheet.paste(corner(rom, off), (i * 42, j * 26))
    sheet.resize((sheet.width * zoom, sheet.height * zoom), Image.NEAREST).save(out)
    print(out)


if __name__ == '__main__':
    main()
