"""gfx_warnbox.py: the warning window's header ⚠警告⚠ -> "Warning" (group warn_box, gfx/warn_box.tsv).

The warning box (detour menu -> 最初から降りる "From Floor 1": "Fuin Cave data will be reset. Are you sure?",
D78E04) is BG0 built at run time from screen-table entry 0xD81690 (tiles 0xC26298, 122 raw 4bpp tiles copied to
VRAM 0x06000000; palette 0xC26278, bank 13; its ROM map 0xC271D8 is not the screen layout). In VRAM map rows 5-6
(cols 6-23) the header strip is tiles 0x05-0x16 over 0x17-0x27, 0x16; the window texture repeats every 8 tiles, so
row 5's texture tiles 0x07, 0x08 (strip x 16-31) and 0x12-0x14 (x 104-127) are shared with row 13 and must keep
their look: everything drawn here stays inside strip x 32-103 on row 5 (tiles 0x09-0x11) and x 8-135 on row 6
(tiles 0x18-0x27). Both ⚠ icons plus "Warning" do not fit centred in that span, so the header is a centred
"Warning" alone. The glyphs are erased with the texture 64 px away (one period), then the word is lettered with
the original white ramp and a dark rim. Tiles are edited in place (indices kept). Found from a PPU dump
(work/qa/p8s33/warn, bglayers.py + vramfind.py); docs/re/graphics.md §session 33.
"""
import gfx

ROW5 = list(range(0x05, 0x17))                 # VRAM map row 5, cols 6-23
ROW6 = list(range(0x17, 0x28)) + [0x16]        # row 6
SHARED = {0x07, 0x08, 0x12, 0x13, 0x14, 0x16, 0x17}
PERIOD = 64
GLYPH = set(range(8, 16)) | {1, 2}             # texture uses 3-7 only


def tile(rom, t0, n):
    return gfx.decode(rom[t0 + 32 * n:t0 + 32 * n + 32], 1, 1)


def strip(rom, t0):
    rows = []
    for line in (ROW5, ROW6):
        ts = [tile(rom, t0, n) for n in line]
        rows += [sum((t[y] for t in ts), []) for y in range(8)]
    return rows


def warn_box(rom):
    out = []
    for r in gfx.rows('warn_box'):
        t0 = int(r['tiles'], 16)
        px = strip(rom, t0)
        w = len(px[0])
        cols = [x for x in range(8, w - 8) if any(px[y][x] in GLYPH for y in range(1, 16))]
        g0, g1 = min(cols) - 1, max(cols) + 1
        assert 32 <= g0 and g1 < 104 + 8, (g0, g1)
        new = [row[:] for row in px]
        for y in range(1, 16):
            for x in range(g0, g1 + 1):
                sx = x + PERIOD if x + PERIOD < w - 8 and not g0 <= x + PERIOD <= g1 else x - PERIOD
                assert 8 <= sx < w - 8 and not g0 <= sx <= g1
                new[y][x] = px[y][sx]
        levels = [int(v, 16) for v in r['levels'].split(',')]
        lw = 72
        lab = gfx.letter_levels(r['en'], lw, 15, int(r['size']), levels, int(r['rim'], 16), align='center')
        x0 = (g0 + g1 + 1) // 2 - lw // 2
        for y in range(15):
            for x in range(lw):
                if lab[y][x]:
                    new[1 + y][x0 + x] = lab[y][x]
        for k, line in enumerate((ROW5, ROW6)):
            for i, n in enumerate(line):
                cell = [row[8 * i:8 * i + 8] for row in new[8 * k:8 * k + 8]]
                if cell == [row[8 * i:8 * i + 8] for row in px[8 * k:8 * k + 8]]:
                    continue
                assert n not in SHARED, f'tile {n:#x} is shared with other rows'
                a = t0 + 32 * n
                rom[a:a + 32] = gfx.encode(cell, 1)
                out.append((a, a + 32))
    return out
