"""gfx_icons.py: English redraws of the 16x16 text icons ({Innn}) on the icon sheet 0xACA06C.

Each icon is 4 tiles (TL TR BL BR, 4bpp, BG bank 15). The kanji icons get their glyph erased to the icon's own
background colour and a hand-drawn 5x7 pixel label (or pictogram) in the glyph's ink colour:
  6-10  white boxed 木火土金水 -> Wd Fi Ea Mt Wa      11-15 round 木火土金水 -> the same
  24 陰 -> crescent moon, 25 陽 -> sun (alignment Yin / Yang)
Rows come from gfx/icons.tsv (kind, index, jp, en); en is a label or `@moon` / `@sun`.
"""
from collections import Counter

import gfx

SHEET = 0xACA06C
POS = ((0, 0), (8, 0), (0, 8), (8, 8))

# 5x7 glyphs (rows top to bottom, '#' = ink); lower case sits on the same baseline
GLYPHS = {
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'],
    'F': ['####', '#...', '#...', '###.', '#...', '#...', '#...'],
    'E': ['####', '#...', '#...', '###.', '#...', '#...', '####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'd': ['...#', '...#', '.###', '#..#', '#..#', '#..#', '.###'],
    'i': ['#', '.', '#', '#', '#', '#', '#'],
    'a': ['....', '....', '.##.', '...#', '.###', '#..#', '.###'],
    't': ['.#.', '.#.', '###', '.#.', '.#.', '.#.', '..#'],
}
PICTS = {
    '@moon': ['....###.', '..###...', '.###....', '.###....', '.###....', '.###....', '..###...', '....###.'],
    '@sun': ['...#....', '.#...#..', '...#....', '#.###.#.', '.#####..', '#.###.#.', '...#....', '.#...#..'],
}


def get(rom, i):
    px = [[0] * 16 for _ in range(16)]
    for j, (ox, oy) in enumerate(POS):
        t = SHEET + (4 * i + j) * 32
        for y in range(8):
            for x in range(8):
                b = rom[t + y * 4 + x // 2]
                px[oy + y][ox + x] = (b >> 4) if x & 1 else b & 15
    return px


def put(rom, i, px):
    for j, (ox, oy) in enumerate(POS):
        t = SHEET + (4 * i + j) * 32
        for y in range(8):
            for x in range(0, 8, 2):
                rom[t + y * 4 + x // 2] = px[oy + y][ox + x] | px[oy + y][ox + x + 1] << 4


def bitmap(label):
    if label in PICTS:
        return PICTS[label]
    rows = [''] * 7
    for k, ch in enumerate(label):
        for r in range(7):
            rows[r] += ('.' if k else '') + GLYPHS[ch][r]
    return rows


def redraw(px, label, inner, shape='rect'):
    """erase the glyph inside `inner` (x0, y0, x1, y1; shape `disc` = only its inscribed circle, so a round icon
    keeps its rim) and draw `label` centred in it"""
    x0, y0, x1, y1 = inner
    cx, cy, rad = (x0 + x1 - 1) / 2, (y0 + y1 - 1) / 2, (x1 - x0) / 2
    cells = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
             if shape == 'rect' or (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad]
    area = Counter(px[y][x] for x, y in cells)
    bg, ink = [c for c, _ in area.most_common(2)]
    for x, y in cells:
        px[y][x] = bg
    bm = bitmap(label)
    w, h = len(bm[0]), len(bm)
    sx = x0 + (x1 - x0 - w) // 2
    sy = y0 + (y1 - y0 - h + 1) // 2
    for r, line in enumerate(bm):
        for c, ch in enumerate(line):
            if ch == '#':
                px[sy + r][sx + c] = ink
    return px


def icons(rom):
    for r in gfx.rows('icons'):
        i = int(r['index'])
        inner = tuple(int(v) for v in r['inner'].split(','))
        put(rom, i, redraw(get(rom, i), r['en'], inner, r['shape']))
    return [(SHEET + 4 * 32 * min(int(r['index']) for r in gfx.rows('icons')),
             SHEET + 4 * 32 * (max(int(r['index']) for r in gfx.rows('icons')) + 1))]
