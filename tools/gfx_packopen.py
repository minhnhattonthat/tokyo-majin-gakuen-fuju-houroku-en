"""gfx_packopen.py: booster-pack opening screen sprites, rows of gfx/pack_open.tsv (group pack_open).

The pack-opening screen (shop -> Buy -> a pack; also after a battle) shows, OBJ palette 10:
- kind `button`: the 次へ button, a 46x15 plate in two 32x16 OBJs (4x2 tiles, 0x100 B each, contiguous): bright
  0xC37D88 (fill 3, ink f with 8/b edges) and dim 0xC37F88 (fill 9). Interior x 1..43, y 1..12 is refilled with
  `fill` and `en` lettered centred (Liberation Sans Bold, alpha -> `levels`, no rim).
- kind `burst`: the 新 "new card" star, a 32x32 OBJ (two 0x100 halves stacked) at 0xC37988 (yellow, fill c) and
  0xC37B88 (white, fill f): the kanji's box x 1..14, y 9..20 is refilled and `en` drawn in a 5x7 pixel font in
  `levels` (red 2).
Palette 10 (pack screen): 2 red, 3 orange-red, 8 salmon, 9 pink, b peach, c yellow, f white. Found from a PPU dump
of the pack screen (`work/qa/p8s29/pk`, objsrc.py: obj53/54 = 0xC37E88/0xC37D88); docs/re/graphics.md S16.
"""
import gfx

BUTTON = (1, 43, 1, 12)       # x0, x1, y0, y1 inside the 46x15 plate
BURST = (1, 14, 9, 20)        # the kanji's box inside the star
GLYPHS = {
    'N': ['#..#', '##.#', '##.#', '#.##', '#.##', '#..#', '#..#'],
    'E': ['###', '#..', '#..', '###', '#..', '#..', '###'],
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'],
}


def halves(rom, a, n):
    return [gfx.decode(rom[a + k * 0x100:a + (k + 1) * 0x100], 4, 8) for k in range(n)]


def button(rom, a, fill, levels, size, text):
    hs = halves(rom, a, 2)
    px = [hs[0][y] + hs[1][y] for y in range(16)]
    x0, x1, y0, y1 = BUTTON
    w, h = x1 - x0 + 1, y1 - y0 + 1
    lab = gfx.letter_levels(text, w, h, size, levels, fill, align='center')
    for y in range(h):
        for x in range(w):
            px[y0 + y][x0 + x] = lab[y][x] or fill
    data = b''.join(gfx.encode([row[k * 32:k * 32 + 32] for row in px], 4) for k in range(2))
    rom[a:a + len(data)] = data
    return (a, a + len(data))


def burst(rom, a, fill, ink, text):
    hs = halves(rom, a, 2)
    px = hs[0] + hs[1]
    x0, x1, y0, y1 = BURST
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px[y][x] = fill
    rows = [''] * 7
    for k, ch in enumerate(text):
        for r in range(7):
            rows[r] += ('.' if k else '') + GLYPHS[ch][r]
    gx = x0 + (x1 - x0 + 1 - len(rows[0])) // 2
    gy = y0 + (y1 - y0 + 1 - 7) // 2
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == '#':
                px[gy + r][gx + c] = ink
    data = gfx.encode(px[:16], 4) + gfx.encode(px[16:], 4)
    rom[a:a + len(data)] = data
    return (a, a + len(data))


def pack_open(rom):
    out = []
    for r in gfx.rows('pack_open'):
        a, fill = int(r['offset'], 16), int(r['fill'], 16)
        levels = [int(v, 16) for v in r['levels'].split(',')]
        if r['kind'] == 'button':
            out.append(button(rom, a, fill, levels, int(r['size']), r['en']))
        else:
            out.append(burst(rom, a, fill, levels[0], r['en']))
    return out
