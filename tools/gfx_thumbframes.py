"""gfx_thumbframes.py: English element emblems on the card thumbnail frames (frame table 0xD80BD4 entries 44-87).

Entries 44-87 of the frame table (tools/gfx_frames.py, entries 0-43 = the large card view) are the 48x64 thumbnail
frames drawn as a 64x64 8bpp OBJ (pack-opening screen, battle card panel, card lists): (tiles, palette, map) with
the map pointer shared (0xCF1098) and the tiles linear, 6x8 tiles of 64 B, pixel value = palette index 0x20-0x2F.
Entry 44 + k is the thumbnail of large frame k: 44-79 carry a small disc bottom left (ring 9x9, interior 7x7 around
x 12, y 51), 83-87 a larger one bottom centre (ring 10x10, interior 8x8 around x 23.5, y 51.5), 80-82 none.
The disc interior (flood fill from the centre, bounded by the ring colour read at the ring's top) is refilled with
its commonest dark colour, and the label (D12: Wd Fi Ea Mt Wa, 3x5 pixel font as the large view's small emblems) is
drawn in the brightest colour the kanji used. Rows: gfx/thumb_frames.tsv (frame, jp, en). Found on the
pack-opening screen (`work/qa/p8s29`, findtile.py: OBJ tiles = 0x86611C.. = entry 85).
"""
import struct
from collections import Counter

import gfx
import gfx_frames
import gfx_minilabels

TABLE = 0xD80BD4
W, H = 48, 64
DISC = {'small': (12, 51, 47), 'large': (23, 51, 47)}   # centre x, centre y, ring top row (ring colour read there)


def bitmap(label):
    """3x5 glyphs: the large view's small-emblem font with the mini labels' 3-wide W and M (two letters = 7 px)"""
    font = dict(gfx_frames.SMALL, W=gfx_minilabels.FONT['W'], M=gfx_minilabels.FONT['M'])
    rows = [''] * 5
    for k, ch in enumerate(label):
        for r in range(5):
            rows[r] += ('.' if k else '') + font[ch][r]
    return rows


def ptr(rom, o):
    return struct.unpack_from('<I', rom, o)[0] - 0x08000000


def lum(rom, pal, v):
    c = struct.unpack_from('<H', rom, pal + 2 * v)[0]
    return (c & 31) + (c >> 5 & 31) + (c >> 10 & 31)


def emblem(rom, k, label):
    tiles, pal = ptr(rom, TABLE + 12 * k), ptr(rom, TABLE + 12 * k + 4)

    def at(x, y):
        return tiles + (y // 8 * 6 + x // 8) * 64 + y % 8 * 8 + x % 8

    cx, cy, top = DISC['large' if k >= 83 else 'small']
    ring = rom[at(cx, top)]
    inside = set()
    todo = [(cx + i, cy + j) for j in (0, -1, 1) for i in (0, -1, 1, -2, 2) if rom[at(cx + i, cy + j)] != ring][:1]
    while todo:
        x, y = todo.pop()
        if (x, y) in inside or rom[at(x, y)] == ring:
            continue
        assert abs(x - cx) <= 5 and abs(y - cy) <= 5, f'thumb frame {k}: disc interior leaks at {x},{y}'
        inside.add((x, y))
        todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in {y for _, y in inside}:   # kanji pixels in the ring colour leave holes: close each row's span
        xs = [x for x, yy in inside if yy == y]
        inside |= {(x, y) for x in range(min(xs), max(xs) + 1)}
    vals = Counter(rom[at(x, y)] for x, y in inside)
    ink = max(vals, key=lambda v: lum(rom, pal, v))
    bg = vals.most_common(1)[0][0]
    if bg == ink:
        bg = min(vals, key=lambda v: lum(rom, pal, v))
    for x, y in inside:
        rom[at(x, y)] = bg
    bm = bitmap(label)
    xs = [x for x, _ in inside]
    ys = [y for _, y in inside]
    w, h = len(bm[0]), len(bm)
    sx = min(xs) + (max(xs) - min(xs) + 1 - w) // 2
    sy = min(ys) + (max(ys) - min(ys) + 1 - h) // 2
    for r, line in enumerate(bm):
        for c, ch in enumerate(line):
            if ch == '#':
                # the large discs' rounded corners: a label corner may cover one ring pixel next to the interior
                assert any((sx + c + i, sy + r + j) in inside for i in (-1, 0, 1) for j in (-1, 0, 1)), \
                    f'thumb frame {k}: label {label} leaves the disc'
                rom[at(sx + c, sy + r)] = ink
    touched = sorted({(y // 8 * 6 + x // 8) for x, y in inside})
    return [(tiles + t * 64, tiles + t * 64 + 64) for t in touched]


def thumb_frames(rom):
    out = []
    for r in gfx.rows('thumb_frames'):
        out += emblem(rom, int(r['frame']), r['en'])
    return out
