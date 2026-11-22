"""gfx_cards.py: card name labels (S1 0xA4DACC classes, S4 lands, S5 spells / possessions / barriers), the title
strip at the top of the large card view (L in the hand).

Character card records 0xD7ADE8 (0x1C B a card, word 0 = pointer to the class string in the CF string area); the
other kinds have plain u32 lists (KINDS). Entry i of a kind has label i in its block: 112x16 4bpp, 14x2 tiles
row-major (0x380 B), palette 0xB08C6C. JP: black 12 px kanji with grey antialiasing (12 black, 13 dark grey, 14 light grey; 0
transparent, no rim), ink in rows 3-14 from x 2, drawn on the card's light header strip. Shot: the L view of a
hand card shows label 79 大蝙蝠 (`work/qa/cls4`).

English: the `en` of the same class string in script/system/cf.tsv (the panel shows that text in the font), so the
large view and the panel always agree. Liberation Sans Bold 12 px on the same three levels, left at x 2; names wider
than ROOM are squeezed horizontally.

    python -X utf8 tools/gfx_cards.py OUT.png     # JP | EN preview of every label
"""
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

import gfx

PAL, SIZE = 0xB08C6C, 0x380
W, H, COLS = 112, 16, 14
# (kind, name table, stride, count, label block): label i of a kind names entry i of its table; each block ends
# where the next (a 40x8 mini-label block, 0xA0 B a card, not redrawn yet) begins
KINDS = (('character', 0xD7ADE8, 0x1C, 282, 0xA4DACC),   # card records, word 0 = class string
         ('land', 0xD7D2D0, 4, 52, 0xA9660C),
         ('spell', 0xD7D5E0, 4, 83, 0xAA3C8C),
         ('possession', 0xD7D4FC, 4, 27, 0xAB92EC),
         ('barrier', 0xD7D568, 4, 30, 0xAC024C))
# entries that point at a shared 4-letter ability abbreviation: the label gets the full ability name
FULL = {'CF6648': 'Renew', 'CF6550': 'Heresy'}
LEVELS = (14, 13, 12)   # light grey, dark grey, black
ROOM = 102              # visible width of the header strip from x 2


def class_strings():
    """CF string id (hex, upper) -> (jp, en)"""
    out = {}
    with open(gfx.ROOT / 'script' / 'system' / 'cf.tsv', encoding='utf8') as f:
        for line in f:
            c = line.rstrip('\n').split('\t')
            if len(c) >= 5 and c[0] != 'id':
                out[c[0]] = (c[3], c[4])
    return out


def labels(rom=None):
    """[(label ROM offset, jp, en)] for every label of every card kind (a zero list entry has no label). The
    tables are read from the original ROM: the build moves strings that outgrow their slot before gfx runs."""
    rom = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
    strs = class_strings()
    out = []
    for kind, table, stride, n, tiles in KINDS:
        for i in range(n):
            p = struct.unpack_from('<I', rom, table + stride * i)[0] & 0x1FFFFFF
            if not p:
                continue
            k = '%X' % p
            jp, en = strs[k]
            out.append((tiles + i * SIZE, jp, FULL.get(k, en or jp)))
    return out


def strip(text, size=12):
    """the label as W x H palette-index rows"""
    font = ImageFont.truetype(str(gfx.FONT), size)
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    l, _, r, _ = d.textbbox((0, 0), text, font=font)
    _, ct, _, cb = d.textbbox((0, 0), 'H', font=font)
    txt = Image.new('L', (r - l + 2, H), 0)
    # cap tops on row 4, baseline on row 13, as the kanji's ink sits in rows 3-14
    ImageDraw.Draw(txt).text((1 - l, 4 - ct), text, font=font, fill=255)
    if txt.width > ROOM:
        txt = txt.resize((ROOM, H), Image.LANCZOS)
    img = Image.new('L', (W, H), 0)
    img.paste(txt, (1, 0))
    a = img.load()
    px = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            v = a[x, y]
            if v >= 48:
                px[y][x] = LEVELS[min(2, (v - 48) * 3 // 160)]
    return px


def card_classes(rom):
    out = []
    for a, _, en in labels(rom):
        data = gfx.encode(strip(en), COLS)
        assert len(data) == SIZE
        rom[a:a + SIZE] = data
        out.append((a, a + SIZE))
    return out


def preview(out, first=0, count=None):
    orig = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
    new = bytearray(orig)
    offs = [a for a, _, _ in labels(orig)][first:]
    offs = offs[:count]
    count = len(offs)
    card_classes(new)
    pal = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in struct.unpack_from('<16H', orig, PAL)]
    pal[0] = (214, 222, 214)   # the header strip's light grey
    img = Image.new('RGB', (2 * (W + 4), count * (H + 2)), (40, 40, 90))
    for col, src in enumerate((orig, new)):
        for k in range(count):
            a = offs[k]
            px = gfx.decode(src[a:a + SIZE], COLS, 2 * COLS)
            for y in range(H):
                for x in range(W):
                    img.putpixel((col * (W + 4) + x, k * (H + 2) + y), pal[px[y][x]])
    img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(out)
    print(out)


if __name__ == '__main__':
    if len(sys.argv) not in (2, 4):
        sys.exit(__doc__)
    preview(sys.argv[1], *(int(v) for v in sys.argv[2:]))
