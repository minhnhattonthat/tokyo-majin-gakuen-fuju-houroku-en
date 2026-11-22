"""gfx_board.py: the sutra board's ten sin labels (mode 7, W13 / S16 0xC1ADF8, group sutra_board, gfx/sutra_board.tsv).

The board is screen-table entry 0xD81B7C: 4bpp BG3 (tiles 0xC165E8, 538; palette 0xC165C8, bank 14; 30x20 map
0xC1A928, map = screen). Its ten brush labels 貪欲 悪口 綺語 瞋恚 .. are the zones the player picks; the picked one is
a red copy drawn over it by a sprite: ten 8-tile strips at 0xC1ADF8 + k * 0x100 (palette 0xC1ADD8: 1-6 black rim
greys, 7-15 red), 32x16 for the top / bottom labels (slots 0-3) and 16x32 for the side ones (4-9), placed exactly on
the BG label (tsv x, y). The board's tiles are retiled without flips, so they outgrow the block: they move to free
space (TILES_AT) and the setup's fixed copy size is raised (SIZE_LIT).

Each label rect (+2 px) is cleared of its ink (dark pixels and their 1 px fringe refilled from neighbouring
parchment, seeded per slot) and the English is lettered in the same box: black core (index 0, as the kanji) with
dark-brown edges; side labels are rotated 90 degrees clockwise (read top to bottom, as the story captions). The
sprite gets the same mask in the red ramp with a black 1 px rim. '/' in `en` breaks the line.
"""
import random
import struct

from PIL import Image, ImageDraw, ImageFont

import gfx

ENTRY = 0xD81B7C
SPR, SPR_N = 0xC1ADF8, 10
# mode-7 setup 0x08056738 calls the screen loader 0x08003224 (layer 3, entry 0x533) with a fixed byte count, the
# literal 0x4340 (538 tiles) at 0x080567E4; BG3 char base 0x8000, screen base 0xE800: room for 832 tiles
SIZE_LIT, MAX_TILES = 0x0567E4, 832
TILES_AT = 0xFC0000   # free 0xFF run 0xF20000-0xFCFFFF (BG4_SPARE at 0xFD8000 is full up to the tab block 0xFDF000)
DARK = {0, 1, 2, 3, 5, 6}


def mask(text, w, h, size, squash=0.7):
    """alpha rows (0-255) of `text` centred in w x h (1 px margin each side for the rim): the font shrinks until
    the lines fit the height, then each line is squeezed horizontally to fit the width (down to `squash`, below
    which the font shrinks further)"""
    lines = text.split('/')
    gap = 1 if len(lines) > 1 else 0
    while True:
        font = ImageFont.truetype(str(gfx.FONT), size)
        d = ImageDraw.Draw(Image.new('L', (1, 1)))
        _, ct, _, cb = d.textbbox((0, 0), 'Hg' if any(c in 'gjpqy' for c in text) else 'H', font=font)
        lh = cb - ct
        boxes = [d.textbbox((0, 0), ln, font=font) for ln in lines]
        tw = max(r - l for l, _, r, _ in boxes)
        th = lh * len(lines) + gap * (len(lines) - 1)
        if (th <= h - 2 and tw * squash <= w - 2) or size <= 7:
            break
        size -= 1
    img = Image.new('L', (w, h), 0)
    y = (h - th) // 2
    for ln, (l, _, r, _) in zip(lines, boxes):
        li = Image.new('L', (r - l + 2, lh), 0)
        ImageDraw.Draw(li).text((1 - l, -ct), ln, font=font, fill=255)
        lw = min(li.width, w - 2)
        if lw < li.width:
            li = li.resize((lw, lh), Image.LANCZOS)
        img.paste(li, ((w - lw) // 2, y))
        y += lh + gap
    a = img.load()
    return [[a[x, yy] for x in range(w)] for yy in range(h)]


def label_mask(r):
    w, h = int(r['w']), int(r['h'])
    if r['orient'] == 'v':   # letter along the long side, then rotate clockwise (top to bottom)
        m = mask(r['en'], h, w, 13)   # w rows of h px
        return [[m[w - 1 - x][y] for x in range(w)] for y in range(h)]
    return mask(r['en'], w, h, 13 if '/' not in r['en'] else 10)


def wipe(canvas, x, y, w, h, seed):
    """refill dark ink (and its 1 px fringe) inside the rect from neighbouring parchment pixels"""
    H, W = len(canvas), len(canvas[0])
    x0, y0, x1, y1 = max(0, x - 2), max(0, y - 2), min(W, x + w + 2), min(H, y + h + 2)
    bad = {(xx, yy) for yy in range(y0, y1) for xx in range(x0, x1) if canvas[yy][xx] in DARK}
    bad |= {(xx + i, yy + j) for xx, yy in bad for i in (-1, 0, 1) for j in (-1, 0, 1)
            if x0 <= xx + i < x1 and y0 <= yy + j < y1}
    rnd = random.Random(seed)
    while bad:
        done = []
        for xx, yy in sorted(bad, key=lambda p: (p[1], p[0])):
            nb = [(xx + i, yy + j) for i in (-1, 0, 1) for j in (-1, 0, 1)
                  if (i or j) and 0 <= xx + i < W and 0 <= yy + j < H and (xx + i, yy + j) not in bad]
            if nb:
                sx, sy = rnd.choice(nb)
                done.append((xx, yy, canvas[sy][sx]))
        for xx, yy, v in done:
            canvas[yy][xx] = v
            bad.discard((xx, yy))


def bg_ink(a):
    return 0 if a >= 150 else 1 if a >= 95 else 3


def apply(rom):
    rows = gfx.rows('sutra_board')
    t0, pal, m0 = (struct.unpack_from('<I', rom, ENTRY + k)[0] & 0x1FFFFFF for k in (0, 4, 8))
    ntiles = (m0 - t0) // 32
    canvas = gfx.screen_canvas(rom[t0:m0], struct.unpack_from('<600H', rom, m0))
    out = []
    for r in rows:
        k, x, y, w, h = (int(r[c]) for c in ('spr', 'x', 'y', 'w', 'h'))
        wipe(canvas, x, y, w, h, k)
        m = label_mask(r)
        for yy in range(h):
            for xx in range(w):
                if m[yy][xx] >= 40:
                    canvas[y + yy][x + xx] = bg_ink(m[yy][xx])
        # sprite: red ramp 9..15 by alpha, black rim 1 around it, 0 transparent
        spr = [[0 if v < 40 else 9 + round((v - 40) / 215 * 6) for v in row] for row in m]
        for yy in range(h):
            for xx in range(w):
                if not spr[yy][xx] and any(0 <= yy + j < h and 0 <= xx + i < w and m[yy + j][xx + i] >= 40
                                           for j in (-1, 0, 1) for i in (-1, 0, 1)):
                    spr[yy][xx] = 1
        a = SPR + k * 0x100
        data = gfx.encode(spr, w // 8)
        assert len(data) == 0x100
        rom[a:a + 0x100] = data
        out.append((a, a + 0x100))
    tiles, mp = gfx.tile_bg(canvas, 30, 20, MAX_TILES, bank=14 << 12)
    tiles = tiles.rstrip(b'\0')
    tiles += bytes(-len(tiles) % 32)
    rom[m0:m0 + len(mp)] = mp
    out.append((m0, m0 + len(mp)))
    if len(tiles) <= m0 - t0:
        tiles = tiles.ljust(m0 - t0, b'\0')
        rom[t0:t0 + len(tiles)] = tiles
        return out + [(t0, t0 + len(tiles))]
    # more tiles than the block holds: move them to free space and raise the setup's copy size
    a = TILES_AT
    assert all(b == 0xFF for b in rom[a:a + len(tiles)]), f'{a:06X} is not free space'
    rom[a:a + len(tiles)] = tiles
    struct.pack_into('<I', rom, ENTRY, 0x08000000 + a)
    assert struct.unpack_from('<I', rom, SIZE_LIT)[0] == m0 - t0
    struct.pack_into('<I', rom, SIZE_LIT, len(tiles))
    return out + [(a, a + len(tiles)), (ENTRY, ENTRY + 4), (SIZE_LIT, SIZE_LIT + 4)]
