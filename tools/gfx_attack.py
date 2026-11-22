"""gfx_attack.py: the attack-type badges 拳 武 飛 術 氣 (S28, 0xD451F8, palette 0xD451D8, (ptr, size) table 0xD63978).

Five 32x16 4bpp OBJs (1D, 4x2 tiles each): a 16x16 icon on the left, a white kanji (ink 15, shadow 1 one pixel down
and right, clear 0) on the right. English: the kanji half is cleared and the glossary's 4-letter abbreviation
(FIST ARMS RNGD ART KI, rows gfx/attack_types.tsv) is drawn in the 3x5 capital font of tools/gfx_minilabels.py with
the same ink and shadow, centred.
"""
import gfx
import gfx_minilabels

BASE = 0xD451F8
INK, SHADOW = 15, 1


def half(rom, i):
    """tile offsets of OBJ i's right 16x16 half, as (offset, ox, oy)"""
    return [(BASE + (i * 8 + ty * 4 + 2 + tx) * 32, tx * 8, ty * 8) for ty in range(2) for tx in range(2)]


def draw(label):
    px = [[0] * 16 for _ in range(16)]
    rows = [''] * 5
    for k, ch in enumerate(label):
        for r in range(5):
            rows[r] += ('.' if k else '') + gfx_minilabels.FONT[ch][r]
    w = len(rows[0])
    if w + 1 > 16:
        raise SystemExit(f'gfx_attack: {label!r} is {w} px wide, room 15')
    sx, sy = (15 - w) // 2, 5
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == '#':
                px[sy + r + 1][sx + c + 1] = px[sy + r + 1][sx + c + 1] or SHADOW
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == '#':
                px[sy + r][sx + c] = INK
    return px


def attack_types(rom):
    out = []
    for r in gfx.rows('attack_types'):
        i = int(r['index'])
        px = draw(r['en'])
        for t, ox, oy in half(rom, i):
            for y in range(8):
                for x in range(0, 8, 2):
                    rom[t + y * 4 + x // 2] = px[oy + y][ox + x] | px[oy + y][ox + x + 1] << 4
            out.append((t, t + 32))
    return out
