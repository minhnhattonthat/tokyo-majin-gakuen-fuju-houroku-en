"""gfx_screens.py: render the menu/banner screens of the asset table 0xD7DCC0-0xD81ED8 (docs/re/graphics.md §Screens).

    python -X utf8 tools/gfx_screens.py [ROM] [--out work/gfx/screens]   # one PNG per screen + list.tsv

The table holds runs of u32 ROM pointers; a screen is a (tiles, palette, map) triple with the palette just before
the tiles and the map just after them: tile count = (map - tiles) / 32, palette count = (tiles - palette) / 32,
map = 30x20 u16 entries (tile number from the first tile of the block, palette bank in bits 12-15). The game adds
its own VRAM tile base and palette bank when it copies the map (dungeon menu: base 0x90, bank 11).
"""
import struct
import sys
from pathlib import Path

from PIL import Image

TABLE = (0xD7DCC0, 0xD81ED8)
MAP_W, MAP_H = 30, 20


def screens(d):
    """yield (table offset, tiles, palette, map, ntiles, npal) for every triple in the table (ROM offsets)"""
    w = [struct.unpack_from('<I', d, a)[0] for a in range(TABLE[0], TABLE[1], 4)]
    for i in range(len(w) - 2):
        t, p, m = w[i:i + 3]
        if t and p and m and 0 < t - p <= 0x200 and (t - p) % 32 == 0 and m > t and (m - t) % 32 == 0 \
                and m - t < 0x10000:
            yield TABLE[0] + 4 * i, t & 0x1FFFFFF, p & 0x1FFFFFF, m & 0x1FFFFFF, (m - t) // 32, (t - p) // 32


def tile_px(d, off):
    return [[(d[off + y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]


def render8(d, t, p, m, ntiles):
    """8bpp screen (a 128-colour palette): full-screen room backgrounds such as the dungeon (0xC1B8F8)"""
    cs = struct.unpack_from('<128H', d, p)
    pal = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in cs]
    img = Image.new('RGB', (MAP_W * 8, MAP_H * 8), (40, 40, 90))
    px = img.load()
    for r in range(MAP_H):
        for c in range(MAP_W):
            e = struct.unpack_from('<H', d, m + 2 * (r * MAP_W + c))[0]
            n = e & 0x3FF
            if n >= ntiles // 2:
                continue
            for y in range(8):
                for x in range(8):
                    v = d[t + 64 * n + (7 - y if e & 0x800 else y) * 8 + (7 - x if e & 0x400 else x)]
                    if v:
                        px[c * 8 + x, r * 8 + y] = pal[v & 127]
    return img


def render(d, t, p, m, ntiles, npal):
    if npal == 8:
        return render8(d, t, p, m, ntiles)
    pals = []
    for k in range(npal):
        cs = struct.unpack_from('<16H', d, p + 32 * k)
        pals.append([((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in cs])
    img = Image.new('RGB', (MAP_W * 8, MAP_H * 8), (40, 40, 90))
    px = img.load()
    for r in range(MAP_H):
        for c in range(MAP_W):
            e = struct.unpack_from('<H', d, m + 2 * (r * MAP_W + c))[0]
            n = e & 0x3FF
            if n >= ntiles:
                continue
            pal = pals[(e >> 12) % npal]
            tp = tile_px(d, t + 32 * n)
            for y in range(8):
                for x in range(8):
                    sx = 7 - x if e & 0x400 else x
                    sy = 7 - y if e & 0x800 else y
                    v = tp[sy][sx]
                    if v:
                        px[c * 8 + x, r * 8 + y] = pal[v]
    return img


def main(argv):
    rom = argv[0] if argv and not argv[0].startswith('--') else 'rom/base.gba'
    out = Path(argv[argv.index('--out') + 1]) if '--out' in argv else Path('work/gfx/screens')
    out.mkdir(parents=True, exist_ok=True)
    d = Path(rom).read_bytes()
    lines = ['entry\ttiles\tpal\tmap\tntiles\tnpal']
    for e, t, p, m, nt, npal in screens(d):
        render(d, t, p, m, nt, npal).save(out / f'{t:06X}.png')
        lines.append(f'{e:06X}\t{t:06X}\t{p:06X}\t{m:06X}\t{nt}\t{npal}')
    (out / 'list.tsv').write_text('\n'.join(lines) + '\n', encoding='utf8')
    print(f'{len(lines) - 1} screens -> {out}')


if __name__ == '__main__':
    main(sys.argv[1:])
