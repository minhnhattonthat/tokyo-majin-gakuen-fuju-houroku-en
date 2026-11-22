"""gfx_linkerr.py: English wallpaper of the link-error screen (game mode 21, 0x0805A98C; group link_error).

The screen is BG3 = a scrolling 4bpp 256x256 wallpaper (screen-table entry 0xD81C18: tiles 0xC0F358, palette
0xC0F338, 32x32 map 0xC11358 copied whole (0x800 B), bank 14, char base 0x06000000) with 通信エラー (73x12) lettered
over it 16 times in the reds 4/7/8/9, at (3,3) (35,35) (67,67) (99,99) repeated every 128 px both ways, under the
BG0 8bpp overlay 0xC11C58 (the man and the message box, group room_banners). Every pixel in those reds is text: it
is filled from the texture 16 px above or below, then the English is lettered in the same reds with a dark rim
(index 1) at each anchor of gfx/link_error.tsv (top-left of the box, 76x12, wrapping at 256).

The redraw needs more than the original 256 tiles, so bg4-style it moves to free space, and the loader's fixed copy
sizes are raised in tools/patches.py (wallpaper 0x2000 -> 0x2900 = 328 tiles at 0x0805AAA0; overlay 0x4500 -> 0x4800
= 288 tiles at 0x0805AAC4). Both limits are checked here.
"""
import struct

import gfx

ENTRY = 0xD81C18          # tiles, palette, map pointers
INK = (4, 7, 8, 9)        # dark to bright red: the text inks (no texture pixel uses them)
RIM = 1
BOX_W, BOX_H, SIZE = 76, 12, 11
MAX_TILES = 0x2900 // 32  # the loader's copy size after tools/patches.py
W = H = 256


def redraw_canvas(canvas, anchors):
    ink = set(INK)
    mask = [[v in ink for v in row] for row in canvas]
    src = [row[:] for row in canvas]
    for y in range(H):
        for x in range(W):
            if mask[y][x]:
                for k in (16, -16, 24, -24, 32, -32, 8, -8, 40, -40):
                    yy = (y + k) % H
                    if not mask[yy][x]:
                        canvas[y][x] = src[yy][x]
                        break
    for ax, ay, text in anchors:
        px = gfx.letter_levels(text, BOX_W, BOX_H, SIZE, list(INK), RIM)
        for yy in range(BOX_H):
            for xx in range(BOX_W):
                if px[yy][xx]:
                    canvas[(ay + yy) % H][(ax + xx) % W] = px[yy][xx]


def apply(rom):
    t0, pal, m0 = (struct.unpack_from('<I', rom, ENTRY + k)[0] & 0x1FFFFFF for k in (0, 4, 8))
    canvas = gfx.screen_canvas(rom[t0:m0], struct.unpack_from('<1024H', rom, m0), w=32)
    redraw_canvas(canvas, [(int(r['x']), int(r['y']), r['en']) for r in gfx.rows('link_error')])
    tiles, mp = gfx.tile_bg(canvas, 32, 32, 1024, bank=14 << 12)
    tiles = tiles.rstrip(b'\0')
    tiles += bytes(-len(tiles) % 32)
    assert len(tiles) // 32 <= MAX_TILES, f'link-error wallpaper needs {len(tiles) // 32} tiles > {MAX_TILES}'
    a = gfx.spare(rom, len(tiles) + len(mp))
    rom[a:a + len(tiles)] = tiles
    rom[a + len(tiles):a + len(tiles) + len(mp)] = mp
    struct.pack_into('<I', rom, ENTRY, 0x08000000 + a)
    struct.pack_into('<I', rom, ENTRY + 8, 0x08000000 + a + len(tiles))
    return [(a, a + len(tiles) + len(mp)), (ENTRY, ENTRY + 4), (ENTRY + 8, ENTRY + 12)]
