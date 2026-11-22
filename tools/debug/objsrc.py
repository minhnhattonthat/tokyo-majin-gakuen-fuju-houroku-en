"""objsrc.py: for each OBJ of a GBA PPU dump, find where its tiles sit in the ROM (exact 32-byte match per tile).

    python -X utf8 tools/debug/objsrc.py DIR/ppu_000200 [--rom rom/base.gba] [--only 80-96]

Prints, per OBJ: index, x, y, size, first tile, bank and the ROM offset of each of its tiles (1D mapping, 4bpp);
'-' for a tile not found raw in the ROM (decompressed or built at run time), '0' for a blank tile.
"""
import argparse
import struct
from pathlib import Path

SIZES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
         (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('prefix')
    ap.add_argument('--rom', default='rom/base.gba')
    ap.add_argument('--only')
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    vram = Path(a.prefix + '.vram.bin').read_bytes()
    oam = Path(a.prefix + '.oam.bin').read_bytes()
    lo, hi = (map(int, a.only.split('-')) if a.only else (0, 127))
    cache = {}
    for i in range(lo, hi + 1):
        a0, a1, a2 = struct.unpack_from('<3H', oam, i * 8)
        if (a0 >> 8) & 3 == 2:
            continue
        w, h = SIZES.get((a0 >> 14, a1 >> 14), (0, 0))
        if not w:
            continue
        x, y, t0, bank = a1 & 0x1FF, a0 & 0xFF, a2 & 0x3FF, a2 >> 12
        locs = []
        for k in range(w // 8 * (h // 8)):
            t = vram[0x10000 + (t0 + k) * 32:0x10000 + (t0 + k + 1) * 32]
            if not any(t):
                locs.append('0')
                continue
            if t not in cache:
                f = rom.find(t)
                cache[t] = f'{f:06X}' if f >= 0 else '-'
            locs.append(cache[t])
        print(f'obj{i}: x={x} y={y} {w}x{h} tile={t0} bank={bank}  ' + ' '.join(locs))


if __name__ == '__main__':
    main()
