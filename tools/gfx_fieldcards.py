"""gfx_fieldcards.py: English battle-tutorial field cards (group fieldcards).

The battle tutorial draws its field cards from pre-drawn 64x64 8bpp OBJs (1D tile order, 64 tiles), not from the
card renderer: entries in the (ptr, size) table 0xD63A38.. (palette = the 0x80 bytes before the first card of each
block). Each card has a 5-row name strip (rows 1-5, between border rows 0 and 6) with a kanji name and a small
round element emblem with a kanji. Opponent cards are drawn upside down (the whole 64x64 rotated 180): they are
rotated upright, edited the same way, and rotated back.

Name strip: ink pixels (darker than the strip's own top row) are replaced by that row's colour in the same
column, then the English name is drawn in the strip's commonest ink colour with the 3x5 capital font of
gfx_minilabels, centred. Emblem: the light kanji pixels are found in the lower-left corner, the disc (radius 4.5
around them) is filled with its commonest dark colour, and a 3x5 label (Wd Fi Ea Mt Wa, gfx_frames.SMALL) is
drawn in the kanji's colour. Tile bytes change in place; nothing moves.
"""
from collections import Counter

import gfx
import gfx_frames
import gfx_minilabels

# (tiles, palette, upside down, name, element label); 0xD3EB78 is a 0x2000 block of two frames of the same card
CARDS = [
    (0xD3CA78, 0xD3C9F8, False, 'LIGHTNING', 'Mt'),   # 神速の剣士 Lightning Blade, 金
    (0xD3EB78, 0xD3EAF8, False, 'FIGHTER', 'Wd'),     # 格闘家, 木
    (0xD3FB78, 0xD3EAF8, False, 'FIGHTER', 'Wd'),
    (0xD3DAF8, 0xD3DA78, True, 'BLADE', 'Fi'),        # opponent ○○の剣士 (name 4 px tall, unreadable), 火
    (0xD40BF8, 0xD40B78, True, 'BLADE', 'Mt'),        # opponent ○○の剣士, 金
]
SEARCH = (8, 42, 32, 62)   # x0, y0, x1, y1 of the emblem kanji in the upright card
RAD = 4.5


def read(rom, t):
    px = [[0] * 64 for _ in range(64)]
    for i in range(64):
        for y in range(8):
            for x in range(8):
                px[i // 8 * 8 + y][i % 8 * 8 + x] = rom[t + i * 64 + y * 8 + x]
    return px


def write(rom, t, px):
    for i in range(64):
        for y in range(8):
            for x in range(8):
                rom[t + i * 64 + y * 8 + x] = px[i // 8 * 8 + y][i % 8 * 8 + x]


def flip(px):
    return [r[::-1] for r in px[::-1]]


def lum(rom, pal, v):
    c = int.from_bytes(rom[pal + 2 * (v % 64):pal + 2 * (v % 64) + 2], 'little')
    return (c & 31, c >> 5 & 31, c >> 10 & 31)


def strip(rom, pal, px, name):
    edge = px[0]
    xs = [x for x in range(64) if edge[x] and px[6][x] == edge[x] and px[1][x] != edge[x]]
    x0, x1 = min(xs), max(xs) + 1
    top = {x: px[1][x] for x in range(x0, x1)}
    floor = min(sum(lum(rom, pal, v)) for v in top.values())
    ink = Counter()
    for y in range(1, 6):
        for x in range(x0, x1):
            if sum(lum(rom, pal, px[y][x])) < floor - 6:
                ink[px[y][x]] += 1
                px[y][x] = top[x]
    colour = ink.most_common(1)[0][0]
    w = gfx_minilabels.width(name)
    assert w <= x1 - x0 - 2, f'{name}: {w} px, strip {x1 - x0}'
    x = x0 + (x1 - x0 - w + 1) // 2
    for c in name:
        g = gfx_minilabels.FONT[c]
        for dy, row in enumerate(g):
            for dx, ch in enumerate(row):
                if ch == '#':
                    px[1 + dy][x + dx] = colour
        x += len(g[0]) + 1


def emblem(rom, pal, px, label):
    sx0, sy0, sx1, sy1 = SEARCH
    pts = [(x, y) for y in range(sy0, sy1) for x in range(sx0, sx1) if min(lum(rom, pal, px[y][x])) >= 24]
    assert pts, 'no emblem kanji found'
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    cells = [(x, y) for y in range(int(cy) - 5, int(cy) + 6) for x in range(int(cx) - 5, int(cx) + 6)
             if (x - cx) ** 2 + (y - cy) ** 2 <= RAD * RAD]
    area = Counter(px[y][x] for x, y in cells)
    light = max(area, key=lambda v: sum(lum(rom, pal, v)))
    dark = next(v for v, _ in area.most_common() if min(lum(rom, pal, v)) < 20)
    for x, y in cells:
        px[y][x] = dark
    bm = gfx_frames.bitmap(label, 'small')
    w, h = len(bm[0]), len(bm)
    ox, oy = round(cx - (w - 1) / 2), round(cy - (h - 1) / 2)
    for r, line in enumerate(bm):
        for c, ch in enumerate(line):
            if ch == '#':
                px[oy + r][ox + c] = light


def fieldcards(rom):
    out = []
    for t, pal, upside, name, label in CARDS:
        px = read(rom, t)
        if upside:
            px = flip(px)
        strip(rom, pal, px, name)
        emblem(rom, pal, px, label)
        if upside:
            px = flip(px)
        write(rom, t, px)
        out.append((t, t + 0x1000))
    return out
