"""gfx.py: graphics-text redraws (phase 8). Each group reads gfx/<group>.tsv and writes 4bpp tiles into the ROM.

    python -X utf8 tools/gfx.py preview [GROUP ..] [--out work/gfx]   # original | English PNGs per group, zoomed
    build.py calls apply(rom) for the English build (not for the identity or marker build).

Groups (docs/re/graphics.md rows):
- title_menu (G4): 0xD25E50, 6 labels of 64x16 px, each stored as two 32x16 sprite halves (4x2 tiles each, left
  half first), 16 tiles a label. Pixels are a 16-step grey ramp: 0 transparent, low = dark rim, F = white.
  Lettering: Liberation Sans Bold (fonts/liberation, OFL), antialiased onto the ramp with a dark rim (docs/fonts.md).
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


def letter(text, w, h, size, dy=0):
    """text centred in w x h -> ramp indices: alpha -> 3..F ink, 2 = rim around the ink, 0 = transparent"""
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
                px[yy][xx] = 3 + round((v - 40) / 215 * 12)
    for yy in range(h):
        for xx in range(w):
            if px[yy][xx] == 0 and any(0 <= yy + j < h and 0 <= xx + i < w and px[yy + j][xx + i] >= 3
                                       for j in (-1, 0, 1) for i in (-1, 0, 1)):
                px[yy][xx] = 2
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


GROUPS = {'title_menu': title_menu}


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
