"""gfx_emotion.py: the emotion-choice dials of the story scenes (script op 0A, 179 choices; docs/re/text.md).

Table 0xD8172C: (tiles, palette, 0) triples. Entry 0 / 1: the left (悩 悲 冷 怒, OBJ palette 0xBEF388) and right
(愛 友 同 喜, palette 0xBF07A8) dials, each an LZ77 block of four 64x64 4bpp OBJ frames (1D, 64 tiles a frame; frame
3 is the blank glow). Then per dial 9 raw 16x16 icons (128 bytes each): 0-3 the icons as drawn on the dial (top,
right, bottom, left), 4-7 the same lit (white disc, dark ink), 8 a blank lit disc. The dial frames hold icons 0-3
pixel for pixel at (24,4) (44,24) (24,44) (4,24) (found by tools/debug, session 38).

English: each disc's interior is flattened to one colour and the 3-letter abbreviation of gfx/emotion_dial.tsv is
drawn in the 3x5 capital font of tools/gfx_minilabels.py (ink yellow 14 with a dark shadow 1 on the dial icons,
ink 1 on the lit discs); the dial frames get the new icons pasted at the same spots and are recompressed (in place
when they fit, else free space with the table pointer moved).
"""
import struct

import gfx
import gfx_minilabels
import lz77

TABLE = 0xD8172C
ICONS = (0xBF0328, 0xBF16E0)
SPOTS = ((24, 4), (44, 24), (24, 44), (4, 24))
FILL = (1, 1)          # disc fill per dial: near-black 281030 / 001030 (yellow ink on grey read poorly)
INK, SHADOW, LIT_INK, LIT_FILL = 14, 0, 1, 15


def to_px(data, tw, th):
    px = [[0] * (tw * 8) for _ in range(th * 8)]
    for t in range(tw * th):
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                px[(t // tw) * 8 + y][(t % tw) * 8 + x] = (b >> 4) if x & 1 else (b & 15)
    return px


def to_tiles(px, tw, th):
    out = bytearray(tw * th * 32)
    for t in range(tw * th):
        for y in range(8):
            for x in range(0, 8, 2):
                r = (t // tw) * 8 + y
                c = (t % tw) * 8 + x
                out[t * 32 + y * 4 + x // 2] = px[r][c] | px[r][c + 1] << 4
    return out


def inside(x, y):
    """disc interior (the ring and outline stay): 16x16 disc centred at 7.5,7.5"""
    return (x - 7.5) ** 2 + (y - 7.5) ** 2 < 5.6 ** 2


# Pictograms (D16 revised), after the DS remake's emotion blocks (rom/tmgk-en__18412.png): spiral 悩, drop 悲,
# snowflake 冷, flame 怒 / heart 愛, two people 友, linked rings 同, smiley 喜. Keyed by the abbreviation in
# gfx/emotion_dial.tsv; an abbreviation without an icon falls back to the 3x5 letters.
ICON = {
    'WOR': ('.#######.', '#.......#', '#.#####.#', '#.#...#.#', '#.#.#.#.#', '#.#.###.#', '#.#.....#',
            '.#.######'),
    'SAD': ('...#...', '..###..', '..###..', '.#####.', '#######', '##.####', '#.#####', '.#####.', '..###..'),
    'CLM': ('....#....', '.#..#..#.', '..#.#.#..', '...###...', '#########', '...###...', '..#.#.#..',
            '.#..#..#.', '....#....'),
    'ANG': ('....#....', '...##....', '...###...', '..####.#.', '.#######.', '.###.###.', '.##...##.',
            '.##...##.', '..#####..'),
    'LOV': ('..##...##..', '.####.####.', '.#########.', '.#########.', '..#######..', '...#####...',
            '....###....', '.....#.....'),
    'FRN': ('..##...##..', '.####.####.', '..##...##..', '...........', '.####.####.', '#####.#####',
            '#####.#####'),
    'SYM': ('..###.###..', '.#...#...#.', '#...#.#...#', '#...#.#...#', '#...#.#...#', '.#...#...#.',
            '..###.###..'),
    'JOY': ('..#####..', '.#.....#.', '#..#.#..#', '#..#.#..#', '#.......#', '#.#...#.#', '#..###..#',
            '.#.....#.', '..#####..'),
}


def letter(px, text, ink, shadow, fill):
    if text in ICON:
        rows = list(ICON[text])
    else:
        rows = [''] * 5
        for k, ch in enumerate(text):
            for r in range(5):
                rows[r] += ('.' if k else '') + gfx_minilabels.FONT[ch][r]
    w = len(rows[0])
    if w > 11:
        raise SystemExit(f'gfx_emotion: {text!r} is {w} px wide, room 11')
    for y in range(16):
        for x in range(16):
            if inside(x, y):
                px[y][x] = fill
    sx, sy = (16 - w) // 2, (16 - len(rows)) // 2
    if shadow:
        for r, line in enumerate(rows):
            for c, ch in enumerate(line):
                if ch == '#' and inside(sx + c + 1, sy + r + 1):
                    px[sy + r + 1][sx + c + 1] = shadow
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == '#':
                px[sy + r][sx + c] = ink
    return px


def apply(rom):
    out = []
    labels = {}
    for r in gfx.rows('emotion_dial'):
        labels[int(r['dial']), int(r['index'])] = r['en']
    for d in range(2):
        base = ICONS[d]
        new_icons = []
        for i in range(4):
            for k, ink, shadow, fill in ((i, INK, SHADOW, FILL[d]), (i + 4, LIT_INK, 0, LIT_FILL)):
                a = base + k * 128
                px = letter(to_px(rom[a:a + 128], 2, 2), labels[d, i], ink, shadow, fill)
                rom[a:a + 128] = to_tiles(px, 2, 2)
                out.append((a, a + 128))
                if k == i:
                    new_icons.append(px)
        ent = TABLE + d * 12
        t0 = struct.unpack_from('<I', rom, ent)[0] & 0x1FFFFFF
        data, end = lz77.decompress(rom, t0)
        data = bytearray(data)
        for f in range(3):
            fr = to_px(data[f * 2048:(f + 1) * 2048], 8, 8)
            for (ox, oy), ic in zip(SPOTS, new_icons):
                for y in range(16):
                    for x in range(16):
                        if ic[y][x]:
                            fr[oy + y][ox + x] = ic[y][x]
            data[f * 2048:(f + 1) * 2048] = to_tiles(fr, 8, 8)
        packed = lz77.compress(bytes(data))
        assert lz77.decompress(packed, 0)[0] == bytes(data)
        if len(packed) <= end - t0:
            rom[t0:t0 + len(packed)] = packed
            out.append((t0, t0 + len(packed)))
        else:
            a = gfx.spare(rom, len(packed))
            rom[a:a + len(packed)] = packed
            struct.pack_into('<I', rom, ent, 0x08000000 + a)
            out += [(a, a + len(packed)), (ent, ent + 4)]
    return out
