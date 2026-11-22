"""gfx_shopplaques.py: card-pick plaques of the shop / trade screens (S17, group shop_plaques).

Sprite-table entry 0xD81DF8: tiles 0xC381A8, palette 0xC38188. Plaque k (gfx/shop_plaques.tsv slot) is two 64x32
OBJs (8x4 tiles, 1D, 0x400 B each) side by side at 0xC381A8 + k * 0x800: 売り符選択 / 交換符選択 / 捨て符選択; the
売る / 買う labels after them (0xC399A8..) are group menu_labels. The wood plaque spans x 6-89, y 6-25; its interior
(x 8-87, y 8-23) is rebuilt row by row from its own text-free pixels (8 px pattern, as tools/gfx_plaques.py) and the
English is lettered centred in the light inks with a dark rim.

The pink 早 badge (16x16, 2x2 tiles at 0xC6FAC8, sprite-table entry 0xD81D8C, palette 0xC6F928: 5 white, 2 pink)
marks the sell screen's Trade tab, which sells every trade card at once ("Sell all trade cards at once,
unchecked."): it becomes a white fast-forward mark on the plain pink fill.
"""
import gfx

TILES = 0xC381A8
TEXTURE = {2, 3, 4, 5, 6, 7, 8}   # browns of the wood (a-f are the lettering, 1 shadow, 9 rim)
BOX = (8, 8, 80, 16)
WHITE, RIM = (11, 13, 14, 15), 1


def plaque_canvas(rom, a):
    left = gfx.decode(rom[a:a + 0x400], 8, 32)
    right = gfx.decode(rom[a + 0x400:a + 0x800], 8, 32)
    return [lr + rr for lr, rr in zip(left, right)]


def apply(rom):
    out = []
    x, y, w, h = BOX
    for r in gfx.rows('shop_plaques'):
        a = TILES + int(r['slot']) * 0x800
        c = plaque_canvas(rom, a)
        for yy in range(y, y + h):
            pat = [v for v in c[yy][x:x + w] if v in TEXTURE][:8]
            assert len(pat) == 8, f'{a:06X} row {yy}: too little texture'
            c[yy][x:x + w] = [pat[i % 8] for i in range(w)]
        lab = gfx.letter_levels(r['en'], w, h, 12, list(WHITE), RIM, align='center')
        for yy in range(h):
            c[y + yy][x:x + w] = [p or s for p, s in zip(lab[yy], c[y + yy][x:x + w])]
        rom[a:a + 0x400] = gfx.encode([row[:64] for row in c], 8)
        rom[a + 0x400:a + 0x800] = gfx.encode([row[64:] for row in c], 8)
        out.append((a, a + 0x800))
    return out + quick_badge(rom)


QUICK = 0xC6FAC8
FFWD = ['.5....5.....', '.55...55....', '.555..555...', '.5555.5555..',
        '.5555.5555..', '.555..555...', '.55...55....', '.5....5.....']


def quick_badge(rom):
    px = gfx.decode(rom[QUICK:QUICK + 0x80], 2, 4)
    for y in range(2, 14):
        px[y][2:14] = [2] * 12
    for i, row in enumerate(FFWD):
        for j, ch in enumerate(row):
            if ch == '5':
                px[4 + i][3 + j] = 5
    rom[QUICK:QUICK + 0x80] = gfx.encode(px, 2)
    return [(QUICK, QUICK + 0x80)]
