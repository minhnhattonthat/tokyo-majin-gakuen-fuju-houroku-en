"""gfx_battle.py: battle HUD sprites (S6, S10), OBJ blocks in 1D tile order (8 tiles a row), group battle_ui
(gfx/battle_ui.tsv: kind, offset, jp, en).

kind `plate`: 64x32 turn-order badges 先手 (0xACE90C) / 後手 (0xACED0C), OBJ bank 10. A 2 px frame around a flat
  interior; the glyphs are one ink colour with anti-alias pixels and a drop shadow to the lower right. Colours are
  read from the block itself: interior = pixel (2, 2); ink = commonest non-interior colour inside; shadow and
  edge from PLATE below.
kind `apup`: 64x64 "AP上昇" blocks (0xB52048 + k*0x800, k 0-3: arrow up / up-lit / down / down-lit), OBJ bank 10.
  The text band (rows with 20+ pixels set, plus the rim row above) is cleared and relettered like
  the JP: a vertical ink ramp 9 8 7 4 (light orange to red), a 2 px white rim (15) and a black drop shadow (1);
  the arrow rows are kept.
"""
import struct

from PIL import Image, ImageDraw, ImageFont

import gfx

FONT = gfx.ROOT / 'fonts' / 'liberation' / 'LiberationSans-Bold.ttf'
PLATE = {0xACE90C: dict(ink=7, edge=8, shadow=11), 0xACED0C: dict(ink=1, edge=3, shadow=4)}


def mask(text, room, tall, maxsize=30):
    """text as a coverage map (0-255) at most `room` px wide, stretched to `tall` px high"""
    size = maxsize
    while True:
        font = ImageFont.truetype(str(FONT), size)
        l, t, r, b = ImageDraw.Draw(Image.new('L', (1, 1))).textbbox((0, 0), text, font=font)
        if r - l <= room or size <= 8:
            break
        size -= 1
    img = Image.new('L', (r - l + 2, b - t + 2), 0)
    ImageDraw.Draw(img).text((1 - l, 1 - t), text, font=font, fill=255)
    img = img.crop(img.getbbox())
    return img.resize((img.width, tall), Image.LANCZOS)


def paste(px, m, x0, y0, put):
    """call put(x, y, coverage) for each covered pixel of mask m placed at (x0, y0)"""
    a = m.load()
    for y in range(m.height):
        for x in range(m.width):
            if a[x, y] and 0 <= y0 + y < len(px) and 0 <= x0 + x < len(px[0]):
                put(x0 + x, y0 + y, a[x, y])


def plate(rom, off, text):
    px = gfx.decode(rom[off:off + 0x400], 8, 32)
    st = PLATE[off]
    bg = px[2][2]
    for y in range(2, 30):
        for x in range(2, 62):
            px[y][x] = bg
    m = mask(text, 52, 18)
    x0, y0 = 32 - m.width // 2 - 1, 16 - m.height // 2 - 1
    body = set()
    paste(px, m, x0, y0, lambda x, y, c: c >= 90 and body.add((x, y)))
    for x, y in body:   # drop shadow first, 1-2 px down-right
        for k in (1, 2):
            if (x + k, y + k) not in body and 2 <= x + k < 62 and 2 <= y + k < 30:
                px[y + k][x + k] = st['shadow']
    paste(px, m, x0, y0, lambda x, y, c: px[y].__setitem__(x, st['ink'] if c >= 170 else
                                                           st['edge'] if c >= 90 else px[y][x]))
    return gfx.encode(px, 8)


AP_RAMP = (9, 8, 7, 7, 4)


def apup(rom, off, text):
    px = gfx.decode(rom[off:off + 0x800], 8, 64)
    rows = [y for y in range(64) if sum(v != 0 for v in px[y]) >= 20]   # arrow rows hold at most 15 pixels
    top, bot = rows[0] - 1, rows[-1]
    for y in range(top, min(bot + 1, 64)):
        px[y] = [0] * 64
    m = mask(text, 44, bot - top - 6)
    rimmed(px, m, 25 - m.width // 2, top + 2, AP_RAMP, 'y', 2, (1, 2))
    return gfx.encode(px, 8)


def rimmed(px, m, x0, y0, ramp, axis, r, shadow, sc=1):
    """letter mask m at (x0, y0): ink graded along `axis` through `ramp`, a white (15) rim of radius r, and a
    drop shadow in colour sc (black 1) at the `shadow` offsets down-right"""
    h, w = len(px), len(px[0])
    a = m.load()
    ink = {(x0 + x, y0 + y) for y in range(m.height) for x in range(m.width) if a[x, y] >= 110}
    rim = {(x + i, y + j) for x, y in ink for j in range(-r, r + 1) for i in range(-r, r + 1)
           if abs(i) + abs(j) <= r + (r > 1)} - ink
    body = ink | rim
    for x, y in body:
        for k in shadow:
            if (x + k, y + k) not in body and 0 <= x + k < w and 0 <= y + k < h:
                px[y + k][x + k] = sc
    for x, y in rim:
        if 0 <= x < w and 0 <= y < h:
            px[y][x] = 15
    span = m.height if axis == 'y' else m.width
    for x, y in ink:
        t = (y - y0) if axis == 'y' else (x - x0)
        px[y][x] = ramp[min(len(ramp) - 1, t * len(ramp) // span)]


VS_RAMP = (2, 3, 7, 8, 9, 10, 11, 12, 13, 14)


def vs(rom, off, text):
    """64x64 対 (0xACCCCC, palette 0xACCCAC): purple-to-blue ink graded left to right, 1 px white rim, black
    shadow 1-3 px down-right; cleared and relettered whole"""
    px = [[0] * 64 for _ in range(64)]
    m = mask(text, 46, 32, maxsize=40)
    rimmed(px, m, 32 - m.width // 2 - 1, 32 - m.height // 2 - 1, VS_RAMP, 'x', 1, (1, 2, 3))
    return gfx.encode(px, 8)


PHASE_RAMP = {'green': (12, 11, 10, 9, 8, 7), 'red': (5, 4, 3, 2, 1)}


def phase(rom, off, text, colour):
    """vertical phase banner, 32x96 (4 tiles a row, 0x600 B, copied whole to OBJ VRAM 0x06017000: 0xB4F808
    配置之間 green, 0xB4FE08 剣戟之間 red; palette 0xB4F7E8; the flying-card sprites follow at 0xB50408/0xB50428):
    the English word as stacked capitals, each graded top to bottom, 2 px white rim, dark grey (6) shadow"""
    px = [[0] * 32 for _ in range(96)]
    step = min(19, 94 // len(text))
    top = (96 - step * len(text)) // 2
    for i, ch in enumerate(text):
        m = mask(ch, 26, step - 4, maxsize=22)
        rimmed(px, m, 15 - m.width // 2, top + i * step + 2, PHASE_RAMP[colour], 'y', 2, (1, 2), sc=6)
    return gfx.encode(px, 4)


NUM_RAMP ={'blue': (3, 2, 2, 2, 2), 'red': (10, 12, 12, 12, 12)}


def numeral(rom, off, text, colour):
    """32x32 OBJ numeral (0xACD4EC + k*0x200: 壱弐参四伍 blue k 0-4, red k 5-9; palette 0xACD4CC): ink 2 (blue)
    or 12 (red), 1 px white rim, black shadow 1-3 px down-right"""
    px = [[0] * 32 for _ in range(32)]
    m = mask(text, 22, 23, maxsize=34)
    rimmed(px, m, 15 - m.width // 2, 4, NUM_RAMP[colour], 'y', 1, (1, 2, 3))
    return gfx.encode(px, 4)


CARD_BOX = (14, 3, 27, 14)   # x0, y0, x1, y1 (exclusive) of the numeral badge, card coordinates


def card_px(rom, off):
    """64x64 8bpp OBJ (8 tiles a row) -> pixel rows"""
    px = [[0] * 64 for _ in range(64)]
    for t in range(64):
        tx, ty = t % 8 * 8, t // 8 * 8
        for y in range(8):
            px[ty + y][tx:tx + 8] = rom[off + t * 64 + y * 8:off + t * 64 + y * 8 + 8]
    return px


def card_bytes(px):
    out = bytearray()
    for t in range(64):
        tx, ty = t % 8 * 8, t // 8 * 8
        for y in range(8):
            out += bytes(px[ty + y][tx:tx + 8])
    return bytes(out)


def cardnum(rom, off, text):
    """turn-order card (8bpp 64x64 OBJ; table 0xD81528: blue set 0xB021EC.., red set 0xAFCC4C..; palette = the
    0xA0 bytes before the tiles, loaded at index 0 (blue) or 0x50 (red)): the kanji numeral badge in the top-left
    corner (CARD_BOX; the enemy's card is shown rotated) is refilled with its light plate colour and the Arabic
    digit drawn in the commonest dark colour there (the glyph's)"""
    px = card_px(rom, off)
    pal = struct.unpack_from('<80H', rom, off - 0xA0)
    base = 0x50 if max(v for row in px for v in row) >= 0x50 else 0
    x0, y0, x1, y1 = CARD_BOX

    def lum(i):
        c = pal[i - base]
        return (c & 31) * 3 + (c >> 5 & 31) * 6 + (c >> 10 & 31)
    box = [px[y][x] for y in range(y0, y1) for x in range(x0, x1)]
    light = max(set(box), key=lambda i: (lum(i) > 150) * box.count(i))
    ink = max(set(box), key=lambda i: (lum(i) <= 150) * box.count(i))   # the glyph's main colour
    for y in range(y0, y1):
        for x in range(x0, x1):
            px[y][x] = light
    m = mask(text, x1 - x0 - 2, y1 - y0 - 2, maxsize=14)
    a = m.load()
    mx, my = x0 + (x1 - x0 - m.width) // 2, y0 + 1
    for y in range(m.height):
        for x in range(m.width):
            if a[x, y] >= 100:
                px[my + y][mx + x] = ink
    return card_bytes(px)


BIG_AREA = (0, 2, 40, 36)   # x0, y0, x1, y1 searched for the numeral on a large card


def bigcard(rom, off, text):
    """large turn-order card (8bpp 112x160 = 14x20 tiles in row order; screen table 0xD815A0..: blue set
    0xAE5FDC.., red set 0xACF24C..; palette right before the tiles, indexed directly): the kanji numeral is
    painted on the art in pure blue (2,12,20) or red (28,3..4,0) with a white (31,31,31) rim. Glyph pixels (ink,
    plus white within 2 px of ink) are filled from the surrounding art, peeling inwards with the commonest
    unmasked neighbour; the Arabic digit is drawn in the same ink with a 1 px white rim, centred on the old glyph"""
    px = [[rom[off + (y // 8 * 14 + x // 8) * 64 + y % 8 * 8 + x % 8] for x in range(112)] for y in range(160)]
    n = BIG_PAL[off]
    pal = struct.unpack_from('<%dH' % n, rom, off - n * 2)

    def rgb(i):
        c = pal[i] if i < n else 0
        return c & 31, c >> 5 & 31, c >> 10 & 31
    ink_cols = {(2, 12, 20), (28, 3, 0), (28, 4, 0)}
    x0, y0, x1, y1 = BIG_AREA
    ink = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if rgb(px[y][x]) in ink_cols}
    ink_i = max(set(px[y][x] for x, y in ink), key=lambda i: sum(px[y][x] == i for x, y in ink))
    near = {(x + dx, y + dy) for x, y in ink for dx in range(-2, 3) for dy in range(-2, 3)}
    near = {(x, y) for x, y in near if 0 <= x < 112 and 0 <= y < 160}
    rim = [px[y][x] for x, y in near if min(rgb(px[y][x])) >= 30]
    white = max(set(rim), key=rim.count)   # the rim colour: (31,31,31), or (31,31,30) on 0xAD3BBC
    masked = near   # ink, its white rim and the blended fringe between rim and art
    gx0, gx1 = min(x for x, _ in ink), max(x for x, _ in ink) + 1
    gy0, gy1 = min(y for _, y in ink), max(y for _, y in ink) + 1
    hole = set(masked)
    while hole:
        fill = {}
        for x, y in hole:
            nb = [px[y + dy][x + dx] for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1))
                  if 0 <= x + dx < 112 and 0 <= y + dy < 160 and (x + dx, y + dy) not in hole]
            if nb:
                fill[x, y] = max(set(nb), key=nb.count)
        for (x, y), v in fill.items():
            px[y][x] = v
        hole -= set(fill)
    m = mask(text, gx1 - gx0 - 2, gy1 - gy0 - 2, maxsize=26)
    a = m.load()
    mx, my = (gx0 + gx1 - m.width) // 2, gy0 + 1
    glyph = {(mx + x, my + y) for y in range(m.height) for x in range(m.width) if a[x, y] >= 100}
    for x, y in glyph:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) not in glyph:
                    px[y + dy][x + dx] = white
    for x, y in glyph:
        px[y][x] = ink_i
    out = bytearray()
    for t in range(280):
        tx, ty = t % 14 * 8, t // 14 * 8
        for y in range(8):
            out += bytes(px[ty + y][tx:tx + 8])
    return bytes(out)


# palette size (colours) of each large card, from the screen table (palette pointer -> tiles pointer)
BIG_PAL = {0xAE5FDC: 80, 0xAEA8AC: 80, 0xAEF17C: 80, 0xAF3A4C: 80, 0xAF831C: 80,
           0xACF24C: 160, 0xAD3BBC: 160, 0xAD852C: 160, 0xADCE9C: 160, 0xAE180C: 160}


def legend(rom, off, text):
    """rarity legend 0xD3C1F8 (64x64 4bpp OBJ, 8x8 tiles in row order, palette 0xD3C1D8; table 0xD63960):
    three lines 高:紫色 / ↕:金色 / 低:銀色 on red marble (1-4). text = 'Hi|Purple/|Gold/Lo|Silver': per line the
    label (empty = keep the original, the arrow) and the colour word. Colons are kept; replaced areas are
    inpainted from the marble, then lettered in the line's original fill with a right/down shadow of 8"""
    px = gfx.decode(rom[off:off + 0x800], 8, 64)
    lines = [(9, 23), (24, 39), (40, 55)]
    fills = [9, 11, 10]
    for (y0, y1), fill, part in zip(lines, fills, text.split('/')):
        lab, word = part.split('|')
        boxes = [(20, 47, word, fill)] + ([(3, 16, lab, 14)] if lab else [])
        for x0, x1, s, ink in boxes:
            hole = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[y][x] > 4}
            while hole:
                fill_ = {}
                for x, y in hole:
                    nb = [px[y + dy][x + dx] for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
                          if (x + dx, y + dy) not in hole and 1 <= px[y + dy][x + dx] <= 4]
                    if nb:
                        fill_[x, y] = max(set(nb), key=nb.count)
                for (x, y), v in fill_.items():
                    px[y][x] = v
                hole -= set(fill_)
            m = mask(s, x1 - x0 - 1, y1 - y0 - 3, maxsize=14)
            a = m.load()
            mx, my = x0 + (x1 - x0 - 1 - m.width) // 2, y0 + 1
            g = {(mx + x, my + y) for y in range(m.height) for x in range(m.width) if a[x, y] >= 110}
            for x, y in g:
                if (x + 1, y + 1) not in g:
                    px[y + 1][x + 1] = 8
            for x, y in g:
                px[y][x] = ink
    return gfx.encode(px, 8)


def panel(rom, off, text):
    """48x48 stone panel 攻撃 / 待機 (0xB54068: 36 tiles, map 0xB544E8 = 6x6 in order, palette 0xB54048 as bank
    13): white (15) glyphs straight on the stone. Each glyph pixel is replaced by the stone pixel 3 to its left
    (or right) that is not a glyph, then the English lines (text split on '/') are drawn in 15 with a 1 px shadow
    of 2, right-aligned to x 43 like the JP"""
    px = gfx.decode(rom[off:off + 0x480], 6, 36)
    glyph = {(x, y) for y in range(4, 44) for x in range(4, 44) if px[y][x] == 15}
    for x, y in sorted(glyph):
        for d in (-3, 3, -6, 6, -1, 1):
            if (x + d, y) not in glyph and 4 <= x + d < 44:
                px[y][x] = px[y][x + d]
                break
    lines = text.split('/')
    for i, line in enumerate(lines):
        m = mask(line, 36, 9, maxsize=12)
        x0, y0 = 43 - m.width, (12, 29)[i]
        a = m.load()
        ink = {(x0 + x, y0 + y) for y in range(m.height) for x in range(m.width) if a[x, y] >= 120}
        for x, y in ink:
            if (x + 1, y + 1) not in ink:
                px[y + 1][x + 1] = 2
        for x, y in ink:
            px[y][x] = 15
    return gfx.encode(px, 6)


def battle_ui(rom):
    out = []
    for r in gfx.rows('battle_ui'):
        off = int(r['offset'], 16)
        if r['kind'] == 'plate':
            data = plate(rom, off, r['en'])
        elif r['kind'] == 'apup':
            data = apup(rom, off, r['en'])
        elif r['kind'] in ('num_blue', 'num_red'):
            data = numeral(rom, off, r['en'], r['kind'][4:])
        elif r['kind'] in ('phase_green', 'phase_red'):
            data = phase(rom, off, r['en'], r['kind'][6:])
        elif r['kind'] == 'cardnum':
            data = cardnum(rom, off, r['en'])
        elif r['kind'] == 'legend':
            data = legend(rom, off, r['en'])
        elif r['kind'] == 'bigcard':
            data = bigcard(rom, off, r['en'])
        elif r['kind'] == 'vs':
            data = vs(rom, off, r['en'])
        elif r['kind'] == 'panel':
            data = panel(rom, off, r['en'])
        else:
            raise ValueError(r['kind'])
        rom[off:off + len(data)] = data
        out.append((off, off + len(data)))
    return out
