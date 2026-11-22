"""gfx.py: graphics-text redraws (phase 8). Each group reads gfx/<group>.tsv and writes 4bpp tiles into the ROM.

    python -X utf8 tools/gfx.py preview [GROUP ..] [--out work/gfx]   # original | English PNGs per group, zoomed
    build.py calls apply(rom) for the English build (not for the identity or marker build).

Groups (docs/re/graphics.md rows):
- title_menu (G4): 0xD25E50, 6 labels of 64x16 px, each stored as two 32x16 sprite halves (4x2 tiles each, left
  half first), 16 tiles a label. Pixels are a 16-step grey ramp: 0 transparent, low = dark rim, F = white.
  Lettering: Liberation Sans Bold (fonts/liberation, OFL), antialiased onto the ramp with a dark rim (docs/fonts.md).
- menu_labels (W1, W4, W5): 64x16 sprite labels, 8x2 tiles row-major, at gfx/menu_labels.tsv offsets; 6-colour
  ramp (MENU_RAMP), same font at 13 px.
- dungeon_menu (W3): the dungeon menu's BG2 screen (tiles 0xC24E08, map 0xC25DC8) rebuilt from gfx/dungeon_menu.tsv.
"""
import csv
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'fonts' / 'liberation' / 'LiberationSans-Bold.ttf'


def rows(group):
    with open(ROOT / 'gfx' / f'{group}.tsv', encoding='utf8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


# ---- 4bpp tile helpers ----
def decode(data, cols, ntiles):
    """4bpp tiles -> (w, h, pixel rows) with `cols` tiles a row"""
    w, h = cols * 8, (ntiles + cols - 1) // cols * 8
    px = [[0] * w for _ in range(h)]
    for t in range(ntiles):
        tx, ty = t % cols * 8, t // cols * 8
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                px[ty + y][tx + x] = (b >> 4) if x & 1 else b & 15
    return px


def encode(px, cols):
    """pixel rows (multiple of 8 high, cols*8 wide) -> 4bpp tile bytes, row-major tiles"""
    out = bytearray()
    for ty in range(0, len(px), 8):
        for tx in range(0, cols * 8, 8):
            for y in range(8):
                for x in range(0, 8, 2):
                    out.append(px[ty + y][tx + x] | px[ty + y][tx + x + 1] << 4)
    return bytes(out)


def letter(text, w, h, size, dy=0, ramp=(3, 15, 2)):
    """text centred in w x h -> ramp indices: alpha -> lo..hi ink, rim around the ink, 0 = transparent.
    ramp = (lo, hi, rim): (3, 15, 2) for the title menu's 16-step ramp, (2, 5, 1) for the 6-colour menu labels."""
    lo, hi, rim = ramp
    font = ImageFont.truetype(str(FONT), size)
    img = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    while r - l > w - 2 and size > 8:
        size -= 1
        font = ImageFont.truetype(str(FONT), size)
        l, t, r, b = d.textbbox((0, 0), text, font=font)
    x = (w - (r - l)) // 2 - l
    y = (h - (b - t)) // 2 - t + dy
    d.text((x, y), text, font=font, fill=255)
    a = img.load()
    px = [[0] * w for _ in range(h)]
    for yy in range(h):
        for xx in range(w):
            v = a[xx, yy]
            if v >= 40:
                px[yy][xx] = lo + round((v - 40) / 215 * (hi - lo))
    for yy in range(h):
        for xx in range(w):
            if px[yy][xx] == 0 and any(0 <= yy + j < h and 0 <= xx + i < w and px[yy + j][xx + i] >= lo
                                       for j in (-1, 0, 1) for i in (-1, 0, 1)):
                px[yy][xx] = rim
    return px


# ---- groups ----
TITLE_MENU = 0xD25E50


def title_menu_label(text):
    """64x16 label -> 16 tiles: left 32x16 half (4x2 tiles), then the right half"""
    px = letter(text, 64, 16, 13)
    left = [r[:32] for r in px]
    right = [r[32:] for r in px]
    return encode(left, 4) + encode(right, 4)


def title_menu(rom):
    for r in rows('title_menu'):
        i = int(r['item'])
        data = title_menu_label(r['en'])
        assert len(data) == 0x200
        rom[TITLE_MENU + i * 0x200:TITLE_MENU + (i + 1) * 0x200] = data
    return [(TITLE_MENU, TITLE_MENU + 0xC00)]


MENU_RAMP = (2, 5, 1)   # 0 transparent, 1 dark rim, 2-5 grey to white (palette e.g. 0xC24DE8)


def menu_labels(rom):
    """64x16 sprite labels, 8x2 tiles row-major (0x200 bytes) at the tsv's offsets"""
    out = []
    for r in rows('menu_labels'):
        a = int(r['offset'], 16)
        data = encode(letter(r['en'], 64, 16, 13, ramp=MENU_RAMP), 8)
        assert len(data) == 0x200
        rom[a:a + 0x200] = data
        out.append((a, a + 0x200))
    return out


# dungeon menu (BG2): table 0xD81C3C (tiles, palette, map): 126 tiles at 0xC24E08, 30x20 map at 0xC25DC8 whose
# entries are 0xB000 | tile (the game adds VRAM tile base 0x90). Each label owns a 3-tile (24 px) band.
DUNGEON_TILES, DUNGEON_MAP, DUNGEON_NTILES = 0xC24E08, 0xC25DC8, 126


def bg_screen(labels, w=30, h=20, cx=64, span=112):
    """[(top tile row, text)] -> 30x20 pixel canvas with each label centred on x = cx in a span-wide, 24 px band"""
    px = [[0] * (w * 8) for _ in range(h * 8)]
    for row, text in labels:
        lab = letter(text, span, 24, 13, ramp=MENU_RAMP)
        x0 = cx - span // 2
        for y in range(24):
            px[row * 8 + y][x0:x0 + span] = lab[y]
    return px


def tile_bg(px, w, h, ntiles, bank=0xB000):
    """pixel canvas -> (tile bytes padded to ntiles, map bytes): tile 0 blank, identical tiles shared"""
    tiles, index, mp = [bytes(32)], {bytes(32): 0}, bytearray()
    for ty in range(h):
        for tx in range(w):
            t = encode([r[tx * 8:tx * 8 + 8] for r in px[ty * 8:ty * 8 + 8]], 1)
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            mp += (bank | index[t]).to_bytes(2, 'little')
    assert len(tiles) <= ntiles, f'{len(tiles)} tiles > {ntiles}'
    return b''.join(tiles).ljust(ntiles * 32, b'\0'), bytes(mp)


def dungeon_menu(rom):
    labels = [(int(r['row']), r['en']) for r in rows('dungeon_menu')]
    tiles, mp = tile_bg(bg_screen(labels), 30, 20, DUNGEON_NTILES)
    rom[DUNGEON_TILES:DUNGEON_TILES + len(tiles)] = tiles
    rom[DUNGEON_MAP:DUNGEON_MAP + len(mp)] = mp
    return [(DUNGEON_TILES, DUNGEON_TILES + len(tiles)), (DUNGEON_MAP, DUNGEON_MAP + len(mp))]


def room_banners(rom):
    """8bpp room backgrounds (S15, W3-W5): tools/gfx_rooms.py"""
    import gfx_rooms
    by_screen = {}
    for r in rows('room_banners'):
        by_screen.setdefault(int(r['screen'], 16), []).append(
            (int(r['x']), int(r['y']), int(r['w']), int(r['h']), r['dir'] == 'v', r['en'], int(r['size'])))
    out, spare = [], [ROOM_SPARE]
    for tiles, labels in by_screen.items():
        out += gfx_rooms.redraw(rom, tiles, labels, FONT, spare)
    return out


ROOM_SPARE = 0xFD1000   # free 0xFF space for room screens that need tiles of their own (after FLOOR_HOOK)


# Fuin Cave floor number (W3): 0x080597D0 put the floor ([0x03003810] + 1, 1-100) on the plaque as kanji numeral
# sprites (二十三: units obj63 y 93, 十 obj64 y 80, tens obj65 y 67; 百 alone). Sprite slots at 0xC273A8 (11 x 16x16,
# 2x2 tiles, OBJ tiles 0x58 + 4k, bank 12) become the digits 0-9, lettered rotated 90 degrees clockwise like the
# plaque's English, and the routine jumps to FLOOR_HOOK, which stacks the Arabic digits top to bottom (units at y 93,
# tens 85, hundreds 77) and hides the sprites it does not use.
FLOOR_FN, FLOOR_DIGITS, FLOOR_HOOK = 0x0597D0, 0xC273A8, 0xFD0000
FLOOR_ASM = '''
    push {r4, r5, r6, r7, lr}
    ldr r0, =0x03003810
    ldrb r0, [r0]
    adds r0, #1
    movs r5, #0
    movs r6, #0
hund:
    cmp r0, #100
    blt tens
    subs r0, #100
    adds r5, #1
    b hund
tens:
    cmp r0, #10
    blt units
    subs r0, #10
    adds r6, #1
    b tens
units:
    ldr r4, =0x03005868
    movs r1, #93
    bl put
    adds r4, #8
    movs r0, r6
    movs r1, #85
    movs r2, r5
    orrs r2, r6
    bl put_if
    adds r4, #8
    movs r0, r5
    movs r1, #77
    movs r2, r5
    bl put_if
    ldr r0, =0x030035A0
    ldr r1, [r0]
    movs r2, #1
    orrs r1, r2
    str r1, [r0]
    pop {r4, r5, r6, r7}
    pop {r0}
    bx r0
put_if:
    cmp r2, #0
    bne put
    movs r1, #0x80
    lsls r1, r1, #2
    strh r1, [r4]
    bx lr
put:
    strh r1, [r4]
    ldr r1, =0x40D5
    strh r1, [r4, #2]
    lsls r0, r0, #2
    ldr r1, =0xC458
    adds r0, r0, r1
    strh r0, [r4, #4]
    bx lr
'''


def floor_numerals(rom):
    import vwf
    out = []
    for d in range(10):
        px = letter(str(d), 16, 16, 12, ramp=MENU_RAMP)
        rot = [[px[15 - x][y] for x in range(16)] for y in range(16)]   # 90 degrees clockwise
        a = FLOOR_DIGITS + d * 0x80
        rom[a:a + 0x80] = encode(rot, 2)
    out.append((FLOOR_DIGITS, FLOOR_DIGITS + 10 * 0x80))
    code = vwf.assemble(FLOOR_ASM, 0x08000000 + FLOOR_HOOK, thumb=True)
    assert all(b == 0xFF for b in rom[FLOOR_HOOK:FLOOR_HOOK + len(code)]), 'FLOOR_HOOK is not free space'
    rom[FLOOR_HOOK:FLOOR_HOOK + len(code)] = code
    out.append((FLOOR_HOOK, FLOOR_HOOK + len(code)))
    stub = vwf.assemble('ldr r3, [pc, #0]\nbx r3', 0x08000000 + FLOOR_FN, thumb=True) + \
        (0x08000000 + FLOOR_HOOK + 1).to_bytes(4, 'little')
    rom[FLOOR_FN:FLOOR_FN + len(stub)] = stub
    out.append((FLOOR_FN, FLOOR_FN + len(stub)))
    return out


def signs(rom):
    """4bpp sign boards with their own palette (gfx/signs.tsv; detour map W2: tools/gfx_signs.py)"""
    import gfx_signs
    out = []
    for r in rows('signs'):
        a, cols, nrows = int(r['offset'], 16), int(r['cols']), int(r['rows'])
        n = cols * nrows
        px = decode(rom[a:a + 32 * n], cols, n)
        gfx_signs.reletter(px, gfx_signs.pal_rgb(rom, int(r['pal'], 16)), r['en'], r['dir'] == 'v', int(r['size']),
                           FONT, light_ink=r['ink'] == 'light')
        rom[a:a + 32 * n] = encode(px, cols)
        out.append((a, a + 32 * n))
    return out


def letter_levels(text, w, h, size, levels, rim, align='left'):
    """like letter(), but ink alpha picks from `levels` (palette indices dark to bright, need not be contiguous)
    and text sits 1 px from the left edge (align='left') or centred"""
    px = letter(text, w, h, size, ramp=(1, len(levels), 0)) if align == 'center' else None
    if px is None:
        font = ImageFont.truetype(str(FONT), size)
        img = Image.new('L', (w, h), 0)
        d = ImageDraw.Draw(img)
        l, t, r, b = d.textbbox((0, 0), text, font=font)
        while r - l > w - 2 and size > 8:
            size -= 1
            font = ImageFont.truetype(str(FONT), size)
            l, t, r, b = d.textbbox((0, 0), text, font=font)
        d.text((1 - l, (h - (b - t)) // 2 - t), text, font=font, fill=255)
        a = img.load()
        px = [[0 if a[x, y] < 40 else 1 + round((a[x, y] - 40) / 215 * (len(levels) - 1)) for x in range(w)]
              for y in range(h)]
    out = [[levels[v - 1] if v else 0 for v in row] for row in px]
    for y in range(h):
        for x in range(w):
            if not out[y][x] and any(0 <= y + j < h and 0 <= x + i < w and px[y + j][x + i]
                                     for j in (-1, 0, 1) for i in (-1, 0, 1)):
                out[y][x] = rim
    return out


# Settings screen (W7, S21/S22): BG2 screen (palette 0xD19814, 105 tiles 0xD19834, 30x20 map 0xD1A554, pointers at
# 0xD1BB5C/64/6C) holds the 設定 banner and the five labels in white; the selected label is a yellow 64x16 sprite
# pair over it and each value a 32x16 sprite, all at 0xD1AA24 (k * 0x100, 4x2 tiles; palette 0xD1AA04: 1-3 shadow,
# 12-15 yellow, 5-7 green, 8-11 blue). BG labels sit at the sprites' screen positions (x 56, map = screen).
SET_TILES, SET_MAP, SET_PTRS, SET_NTILES = 0xD19834, 0xD1A554, 0xD1BB64, 105
SET_SPR = 0xD1AA24
SET_RAMPS = {'yellow': [12, 13, 14, 15], 'green': [4, 5, 6, 7], 'blue': [8, 9, 10, 11], 'white': [10, 12, 14, 15]}


def settings_screen(rom):
    import gfx_signs
    out = []
    labels = rows('settings')
    for r in labels:
        if r['kind'] == 'sprite':
            k, w = int(r['slot']), int(r['w'])
            px = letter_levels(r['en'], w, 16, 12, SET_RAMPS[r['ramp']], 1)
            data = b''.join(encode([row[x:x + 32] for row in px], 4) for x in range(0, w, 32))
            a = SET_SPR + k * 0x100
            rom[a:a + len(data)] = data
            out.append((a, a + len(data)))
    edits = [r for r in labels if r['kind'] != 'sprite']
    return out + bg4_edit(rom, SET_PTRS, 1, edits, SET_RAMPS['white'])


def bg4_edit(rom, ptrs, bank, edits, white=(10, 12, 14, 15), pal_at=-8):
    """4bpp 30x20 BG screen whose (palette, tiles, map) pointers sit at ptrs + pal_at, ptrs, ptrs + 8 (pal_at 4 for
    the screen table 0xD7DCC0, whose entries are tiles, palette, map): decode it, apply
    edits (rows with kind bg = white label on a clear rect, board = reletter a light-ink board, gfx_signs), retile
    (identical tiles shared, no flips) and write it back in place, or into free space at ROOM_SPARE-managed
    BG4_SPARE with the pointers moved when it needs more tiles than the original block holds"""
    pal, t0, m0 = (struct.unpack_from('<I', rom, ptrs + k)[0] & 0x1FFFFFF for k in (pal_at, 0, 8))
    ntiles = (m0 - t0) // 32
    canvas = screen_canvas(rom[t0:m0], struct.unpack_from('<600H', rom, m0))
    edit_canvas(canvas, edits, rom, pal, white)
    tiles, mp = tile_bg(canvas, 30, 20, 1024, bank=bank << 12)
    tiles = tiles.rstrip(b'\0')
    tiles += bytes(-len(tiles) % 32)
    if len(tiles) <= ntiles * 32:
        tiles = tiles.ljust(ntiles * 32, b'\0')
        rom[t0:t0 + len(tiles)] = tiles
        rom[m0:m0 + len(mp)] = mp
        return [(t0, t0 + len(tiles)), (m0, m0 + len(mp))]
    a = spare(rom, len(tiles) + len(mp))
    rom[a:a + len(tiles)] = tiles
    rom[a + len(tiles):a + len(tiles) + len(mp)] = mp
    struct.pack_into('<I', rom, ptrs, 0x08000000 + a)
    struct.pack_into('<I', rom, ptrs + 8, 0x08000000 + a + len(tiles))
    return [(a, a + len(tiles) + len(mp)), (ptrs, ptrs + 4), (ptrs + 8, ptrs + 12)]


def spare(n):
    """claim n bytes of 0xFF free space at BG4_SPARE (256-aligned blocks)"""
    a = BG4_SPARE[0]
    assert all(b == 0xFF for b in ROM_FREE[0][a:a + n]), f'{a:06X} is not free space'
    BG4_SPARE[0] = (a + n + 0xFF) & ~0xFF
    return a


def screen_canvas(tiles, ents, w=30):
    """4bpp tile bytes + map entries (flips honoured) -> 240-wide pixel canvas of palette indices"""
    canvas = [[0] * (w * 8) for _ in range(len(ents) // w * 8)]
    for i, e in enumerate(ents):
        n = e & 0x3FF
        t = decode(tiles[32 * n:32 * n + 32].ljust(32, b'\0'), 1, 1)
        for y in range(8):
            for x in range(8):
                canvas[i // w * 8 + y][i % w * 8 + x] = t[7 - y if e & 0x800 else y][7 - x if e & 0x400 else x]
    return canvas


def edit_canvas(canvas, edits, rom, pal, white):
    """apply gfx/<group>.tsv rows to a screen canvas. Kinds: bg = white label on a clear rect; board = reletter a
    light-ink board (gfx_signs); patch = cover with a blank stretch of the same texture at (sx, sy), then centred
    white text; label = text on the transparent backdrop (index 0), left-aligned, ink `white`, rim index sx"""
    import gfx_signs
    palrgb = gfx_signs.pal_rgb(rom, pal)
    for r in edits:
        x, y, w, h = int(r['x']), int(r['y']), int(r['w']), int(r['h'])
        if r['kind'] == 'bg':
            px = letter_levels(r['en'], w, h, 12, list(white), 1)
            for yy in range(h):
                canvas[y + yy][x:x + w] = px[yy]
        elif r['kind'] == 'board':
            sub = [row[x:x + w] for row in canvas[y:y + h]]
            gfx_signs.reletter(sub, palrgb, r['en'], False, 13, FONT, light_ink=True, inset=2)
            for yy in range(h):
                canvas[y + yy][x:x + w] = sub[yy]
        elif r['kind'] == 'patch':   # cover with a blank stretch of the same texture (sx, sy), then white text
            sx, sy = int(r['sx']), int(r['sy'])
            src = [row[sx:sx + w] for row in canvas[sy:sy + h]]
            px = letter_levels(r['en'], w, h, 12, list(white), 1, align='center')
            for yy in range(h):
                canvas[y + yy][x:x + w] = [p or s for p, s in zip(px[yy], src[yy])]
        elif r['kind'] == 'label':   # transparent backdrop: clear the rect, then left-aligned text with a rim
            px = letter_levels(r['en'], w, h, int(r['sy'] or 11), list(white), int(r['sx']))
            for yy in range(h):
                canvas[y + yy][x:x + w] = px[yy]
        elif r['kind'] == 'shadow':  # transparent backdrop: centred text (size sy), drop shadow index sx down-right
            canvas_shadow(canvas, x, y, w, h, r['en'], int(r['sy']), list(white), int(r['sx']))


def canvas_shadow(canvas, x, y, w, h, text, size, levels, shade, depth=3):
    """clear the rect, letter `text` centred in `levels`, then a `depth` px drop shadow (index `shade`) to the
    lower right with a 1 px fringe of index shade + 1 (end card 完: ink 11-15, shadow 9, fringe 10)"""
    px = letter(text, w, h, size, ramp=(1, len(levels), 0))
    ink = [[levels[v - 1] if v else 0 for v in row] for row in px]
    out = [row[:] for row in ink]
    for yy in range(h):
        for xx in range(w):
            if not out[yy][xx] and any(0 <= yy - k < h and 0 <= xx - k < w and ink[yy - k][xx - k]
                                       for k in range(1, depth + 1)):
                out[yy][xx] = shade
    for yy in range(h):
        for xx in range(w):
            if not out[yy][xx] and any(0 <= yy + j < h and 0 <= xx + i < w and out[yy + j][xx + i] == shade
                                       for j in (-1, 0, 1) for i in (-1, 0, 1)):
                out[yy][xx] = shade + 1
    for yy in range(h):
        canvas[y + yy][x:x + w] = out[yy]


def lz_screen_edit(rom, entry, bank, edits, white, max_tiles=0):
    """4bpp 30x20 BG screen of the screen table 0xD7DCC0 whose tiles are LZ77 (BIOS LZ77UnComp into WRAM, then
    copied to VRAM) and whose palette and raw map follow at entry + 4 / + 8 (name entry: entry 0xD7DF1C, tiles
    0xBEAC20, palette 0xE51FDA, map 0xE577AA). Edit as bg4_edit, retile, recompress; the stream goes back in place
    when it fits, else into BG4_SPARE with the tiles pointer moved. The map is rewritten in place (same size).
    The loader 0x08003268 takes the size from the LZ77 header (allocates the WRAM buffer, copies that many bytes
    to VRAM), so the set may grow up to max_tiles: keep it below the layer's screen base in VRAM."""
    import lz77
    t0, pal, m0 = (struct.unpack_from('<I', rom, entry + k)[0] & 0x1FFFFFF for k in (0, 4, 8))
    old, end = lz77.decompress(rom, t0)
    canvas = screen_canvas(old, struct.unpack_from('<600H', rom, m0))
    edit_canvas(canvas, edits, rom, pal, white)
    tiles, mp = tile_bg(canvas, 30, 20, max(max_tiles, len(old) // 32), bank=bank << 12)
    tiles = tiles.rstrip(b'\0')
    tiles = tiles.ljust(max(len(old), (len(tiles) + 31) // 32 * 32), b'\0')
    packed = lz77.compress(tiles)
    assert lz77.decompress(packed, 0)[0] == tiles
    rom[m0:m0 + len(mp)] = mp
    out = [(m0, m0 + len(mp))]
    if len(packed) <= end - t0:
        rom[t0:t0 + len(packed)] = packed
        return out + [(t0, t0 + len(packed))]
    a = spare(rom, len(packed))
    rom[a:a + len(packed)] = packed
    struct.pack_into('<I', rom, entry, 0x08000000 + a)
    return out + [(a, a + len(packed)), (entry, entry + 4)]


def spare(rom, n):
    """claim n bytes of 0xFF free space at BG4_SPARE (256-aligned blocks)"""
    a = BG4_SPARE[0]
    assert all(b == 0xFF for b in rom[a:a + n]), f'{a:06X} is not free space'
    BG4_SPARE[0] = (a + n + 0xFF) & ~0xFF
    return a


BG4_SPARE = [0xFD8000]   # reset by apply(): free space for 4bpp screens that outgrow their block


HAIKU_PTRS = 0xD16F9C   # haiku club BG2 (W9): palette 0xD0E300, tiles 0xD0E320, map 0xD0F8C0, bank 9


def haiku_screen(rom):
    return bg4_edit(rom, HAIKU_PTRS, 9, rows('haiku'))


# screen-table entries (tiles, palette, map; bank 13): deck-name entry (G6) and the shop's item list (商品選択)
def deck_name_screen(rom):
    return bg4_edit(rom, 0xD81D68, 13, rows('deck_name'), white=(11, 13, 14, 15), pal_at=4)


def name_entry_screen(rom):
    """player name entry (G6, W15): LZ77 screen-table entry 0xD7DF1C, bank 10; the top captions are on the clear
    backdrop with a brown rim (index 7) like the JP glyphs. BG2 tiles at VRAM 0x0600C000, screen base 0xE800:
    room for 320 tiles (the JP set has 234; 0xDD40-0xE800 holds only stale data on this screen)"""
    return lz_screen_edit(rom, 0xD7DF1C, 10, rows('name_entry'), white=(11, 13, 14, 15), max_tiles=320)


def end_card(rom):
    """ending 完 card (W11): LZ77 screen-table entry 0xD7DF04 (tiles 0xBE6738, palette 0xE2BEBA, map 0xE5D0BA),
    BG2 bank 14, char base 0x0600C000, screen base 0xE800; the title logo above stays (D5), 完 -> The End"""
    return lz_screen_edit(rom, 0xD7DF04, 14, rows('end_card'), white=(11, 12, 13, 14, 15), max_tiles=320)


def shop_list_screen(rom):
    return bg4_edit(rom, 0xD81DBC, 13, rows('shop_list'), white=(10, 13, 14, 15), pal_at=4)


def plaques(rom):
    """small BG plaques with their own map size (pack select header): tools/gfx_plaques.py"""
    import gfx_plaques
    return gfx_plaques.pack_header(rom)


def banners(rom):
    """battle banners 勝負 / 術者交代 / 勝利 / 敗北 (S9): tools/gfx_banners.py"""
    import gfx_banners
    return gfx_banners.banners(rom)


def battle_ui(rom):
    """battle HUD sprites: 先手 / 後手 badges (S6), AP上昇 (S10): tools/gfx_battle.py"""
    import gfx_battle
    return gfx_battle.battle_ui(rom)


def deck_edit(rom):
    """deck editor buttons and category tabs (S19): tools/gfx_deck.py"""
    import gfx_deck
    return gfx_deck.deck_edit(rom)


def captions(rom):
    """story-scene location captions (G5/W12, S11): tools/gfx_captions.py"""
    import gfx_captions
    return gfx_captions.captions(rom)


GROUPS = {'title_menu': title_menu, 'menu_labels': menu_labels, 'dungeon_menu': dungeon_menu,
          'room_banners': room_banners, 'floor_numerals': floor_numerals, 'signs': signs,
          'settings_screen': settings_screen, 'haiku_screen': haiku_screen, 'deck_name_screen': deck_name_screen,
          'name_entry_screen': name_entry_screen, 'shop_list_screen': shop_list_screen, 'deck_edit': deck_edit, 'plaques': plaques,
          'banners': banners, 'battle_ui': battle_ui, 'captions': captions,
          'end_card': end_card}


def apply(rom):
    """write every group into rom (bytearray); return the written (start, end) ranges"""
    out = []
    BG4_SPARE[0] = 0xFD8000
    for fn in GROUPS.values():
        out += fn(rom)
    return out


def preview(groups, out):
    orig = (ROOT / 'rom' / 'base.gba').read_bytes()
    new = bytearray(orig)
    out.mkdir(parents=True, exist_ok=True)
    grey = [(i * 17, i * 17, i * 17) for i in range(16)]
    grey[0] = (40, 40, 90)
    for g in groups:
        for a, b in GROUPS[g](new):
            for name, src in (('jp', orig), ('en', new)):
                # labels as stored: 32x16 halves, show them side by side as the screen does
                n = (b - a) // 32
                tiles = decode(src[a:b], 4, n)
                lab = []
                for k in range(0, len(tiles), 32):
                    half = tiles[k:k + 32]
                    lab += [half[y] + half[16 + y] for y in range(16)]
                img = Image.new('RGB', (64, len(lab)))
                img.putdata([grey[v] for row in lab for v in row])
                img = img.resize((64 * 4, len(lab) * 4), Image.NEAREST)
                p = out / f'{g}_{name}.png'
                img.save(p)
                print(p)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['preview']:
        out = Path('work/gfx')
        if '--out' in args:
            out = Path(args[args.index('--out') + 1])
            args = args[:args.index('--out')] + args[args.index('--out') + 2:]
        preview(args[1:] or list(GROUPS), out)
    else:
        print(__doc__)
