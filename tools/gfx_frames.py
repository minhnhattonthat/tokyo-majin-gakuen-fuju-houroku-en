"""gfx_frames.py: English element emblems on the 8bpp card frames (S20, table 0xD80BD4, tools/card_art.py).

Frames 0-35 carry a small round emblem bottom left, frames 39-43 a large one bottom centre, each with a kanji of
木火土金水. Each frame is (tiles, palette, map): 8bpp tiles (pixel values 0x81-0x9F index the frame palette
directly), map 14x20 u16 entries (tile | hflip 0x400 | vflip 0x800). The emblem is found from its near-white kanji
pixels (SEARCH area per size); the disc is filled with its commonest dark colour, light kanji tips in the rim are
cleared too, a pixel label (Wd Fi Ea Mt Wa) is drawn in the kanji's ink, and the touched tiles are written back in
place (the build fails if one of them is also used elsewhere on the map, or flipped).
Rows: gfx/frames.tsv (frame, jp, en, font small|large, optional ink = palette value in hex).
"""
import struct
from collections import Counter

import gfx

TABLE = 0xD80BD4
MAPW, MAPH = 14, 20

# 3x5 font for the small emblems, 5x7 (gfx_icons) for the large ones
SMALL = {
    'W': ['#...#', '#...#', '#.#.#', '#.#.#', '.#.#.'],
    'F': ['###', '#..', '##.', '#..', '#..'],
    'E': ['###', '#..', '##.', '#..', '###'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'],
    'd': ['..#', '.##', '#.#', '#.#', '.##'],
    'i': ['#', '.', '#', '#', '#'],
    'a': ['...', '##.', '.##', '#.#', '.##'],
    't': ['.#.', '###', '.#.', '.#.', '..#'],
}


def ptr(rom, o):
    return struct.unpack_from('<I', rom, o)[0] - 0x08000000


def frame(rom, k):
    tiles, pal, mp = (ptr(rom, TABLE + 12 * k + 4 * j) for j in range(3))
    ents = struct.unpack_from(f'<{MAPW * MAPH}H', rom, mp)
    return tiles, ents


def canvas(rom, k):
    """frame k -> (pixel rows of palette values, {(x, y): (tile byte offset of that pixel)})"""
    tiles, ents = frame(rom, k)
    px = [[0] * (MAPW * 8) for _ in range(MAPH * 8)]
    where = {}
    for m, e in enumerate(ents):
        t, hf, vf = e & 0x3FF, e & 0x400, e & 0x800
        for y in range(8):
            for x in range(8):
                sx, sy = (7 - x if hf else x), (7 - y if vf else y)
                o = tiles + t * 64 + sy * 8 + sx
                X, Y = m % MAPW * 8 + x, m // MAPW * 8 + y
                px[Y][X] = rom[o]
                where[(X, Y)] = (o, t, e)
    return px, where, ents


def bitmap(label, font):
    if font == 'large':
        import gfx_icons
        return gfx_icons.bitmap(label)
    rows = [''] * 5
    for k, ch in enumerate(label):
        for r in range(5):
            rows[r] += ('.' if k else '') + SMALL[ch][r]
    return rows


FRINGE = 16   # rim pixels at least this light (min channel, 0-31) are kanji anti-aliasing
SEARCH = {'small': (0, 120, 32, 160, 6.5), 'large': (30, 116, 82, 152, 10.5)}


def rgb(rom, k, v):
    pal = ptr(rom, TABLE + 12 * k + 4)
    c = struct.unpack_from('<H', rom, pal + 2 * v)[0]
    return (c & 31, c >> 5 & 31, c >> 10 & 31)


def locate(rom, k, px, font):
    """centre of the emblem's near-white kanji pixels inside the font's search area"""
    x0, y0, x1, y1, rad = SEARCH[font]
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[y][x] and min(rgb(rom, k, px[y][x])) >= 24]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, rad


def emblem(rom, k, label, font, ink=None):
    px, where, ents = canvas(rom, k)
    cx, cy, rad = locate(rom, k, px, font)
    x0, y0 = int(cx - rad), int(cy - rad)
    x1, y1 = int(cx + rad) + 2, int(cy + rad) + 2
    cells = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad]
    area = Counter(px[y][x] for x, y in cells)
    ink = ink or max(area, key=lambda v: sum(rgb(rom, k, v)))
    bg = next(v for v, _ in area.most_common() if min(rgb(rom, k, v)) < 20)
    x0, y0, x1, y1 = round(cx - rad), round(cy - rad), round(cx + rad) + 1, round(cy + rad) + 1
    new = {}
    for x, y in cells:
        new[(x, y)] = bg
    # kanji tips that reach into the rim
    for y in range(int(cy - rad) - 2, int(cy + rad) + 3):
        for x in range(int(cx - rad) - 2, int(cx + rad) + 3):
            if (x - cx) ** 2 + (y - cy) ** 2 <= (rad + 1.5) ** 2 and px[y][x] and min(rgb(rom, k, px[y][x])) >= FRINGE:
                new[(x, y)] = bg
    bm = bitmap(label, font)
    w, h = len(bm[0]), len(bm)
    sx = x0 + (x1 - x0 - w + 1) // 2
    sy = y0 + (y1 - y0 - h + 1) // 2
    for r, line in enumerate(bm):
        for c, ch in enumerate(line):
            if ch == '#':
                new[(sx + c, sy + r)] = ink
    touched = {where[p][1] for p in new}
    for m, e in enumerate(ents):
        if e & 0x3FF in touched:
            assert e & 0xC00 == 0, f'frame {k}: emblem tile {e & 0x3FF} is flipped'
            assert sum(1 for f in ents if f & 0x3FF == e & 0x3FF) == 1, f'frame {k}: emblem tile shared'
    for p, v in new.items():
        rom[where[p][0]] = v
    tiles = frame(rom, k)[0]
    return [(tiles + t * 64, tiles + t * 64 + 64) for t in touched]


def frames(rom):
    out = []
    for r in gfx.rows('frames'):
        out += emblem(rom, int(r['frame']), r['en'], r['font'], int(r['ink'], 16) if r.get('ink') else None)
    return out
