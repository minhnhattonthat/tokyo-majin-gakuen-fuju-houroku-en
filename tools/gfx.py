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


GROUPS = {'title_menu': title_menu, 'menu_labels': menu_labels, 'dungeon_menu': dungeon_menu,
          'room_banners': room_banners, 'floor_numerals': floor_numerals}


def apply(rom):
    """write every group into rom (bytearray); return the written (start, end) ranges"""
    out = []
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
