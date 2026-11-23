"""gfx_logo.py: the title-screen logo 東京魔人學園 / 符咒封録 / furigana -> TOKYO MAJIN GAKUEN / FUJU HOUROKU /
THE TALISMAN SEALING CHRONICLE (group title_logo, gfx/title_logo.tsv; ruling D17).

The logo is BG0 of the title screen (mode 14), loaded from the title (ptr, size) table at 0xD289E0:
palette 0xD23120 (bank 3, size word 0x30020), raw 4bpp tiles 0xD23140 (0x2520 bytes = 297 tiles, copied to VRAM
0x0600C000) and a 30x20 map 0xD25660 (entries 0x3000 | tile, size word 0xA000F0 = 160 x 240 px). Nothing else in
the ROM points at the tiles. VRAM 0xC000-0xFFFF holds only this layer, so the set may grow to 512 tiles; a set
larger than the old block moves to free space with the pointer and size at 0xD289E8 updated.

Lettering: Permanent Marker (fonts/permanentmarker, Apache 2.0) for the two title lines, Liberation Sans Bold for
the subtitle, drawn in the original palette: fill 12-15 (grey-white with seeded brush grain), soft edge 9-11,
rim 4/5 inside and 1/2 outside. Seeds are fixed, so the output is the same on every build.
Preview: python -X utf8 tools/gfx_logo.py [--out work/qa/logo] (writes logo_en.png over the original's palette).
"""
import random
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import gfx

ROOT = Path(__file__).resolve().parents[1]
MARKER = ROOT / 'fonts' / 'permanentmarker' / 'PermanentMarker-Regular.ttf'
SANS = ROOT / 'fonts' / 'liberation' / 'LiberationSans-Bold.ttf'
TABLE = 0xD289E0          # (palette, size) (tiles, size) (map, size)
PAL = 0xD23120
MAP = 0xD25660
BANK = 3
MAX_TILES = 512           # VRAM 0x0600C000-0x0600FFFF


def text_mask(text, font, cap, max_w, track=1, scale=4, smooth=True):
    """coverage mask (L) of text with capital height ~cap px, squeezed to max_w px wide"""
    probe = ImageFont.truetype(str(font), 200)
    hb = probe.getbbox('H')
    size = round(200 * cap * scale / (hb[3] - hb[1]))
    f = ImageFont.truetype(str(font), size)
    widths = [f.getlength(c) for c in text]
    big = Image.new('L', (int(sum(widths) + track * scale * len(text)) + 40 * scale, size * 2), 0)
    d = ImageDraw.Draw(big)
    if not smooth:
        d.fontmode = '1'
    x = 20 * scale
    for c, w in zip(text, widths):
        d.text((x, size // 2), c, font=f, fill=255)
        x += w + track * scale
    big = big.crop(big.getbbox())
    w, h = round(big.width / scale), round(big.height / scale)
    return big.resize((min(w, max_w), h), Image.LANCZOS if smooth else Image.NEAREST)


def brush(mask, seed, rim):
    """mask -> 2D list of palette indices: dark rim of `rim` px, grey-white fill with horizontal brush grain"""
    rnd = random.Random(seed)
    pad = rim + 1
    m = Image.new('L', (mask.width + 2 * pad, mask.height + 2 * pad), 0)
    m.paste(mask, (pad, pad))
    solid = m.point(lambda v: 255 if v >= 110 else 0)
    outer = solid.filter(ImageFilter.MaxFilter(2 * rim + 1)).load()
    ring = solid.filter(ImageFilter.MaxFilter(3)).load()
    mp, sp = m.load(), solid.load()
    w, h = m.size
    streak = [rnd.random() for _ in range(h)]
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if sp[x, y]:
                v = mp[x, y]
                if v < 200:
                    out[y][x] = 9 + (v - 110) * 3 // 90
                else:
                    lvl = 1.0 - 0.35 * y / h - rnd.random() * 0.25 - streak[y] * 0.15
                    out[y][x] = 15 if lvl > 0.85 else 14 if lvl > 0.72 else 13 if lvl > 0.6 else 12
            elif ring[x, y]:
                out[y][x] = 4 if rnd.random() > 0.3 else 5
            elif outer[x, y]:
                out[y][x] = 1 if rnd.random() > 0.25 else 2
    return out


def paste(canvas, img, x, y):
    for yy, row in enumerate(img):
        for xx, v in enumerate(row):
            if v and 0 <= y + yy < len(canvas) and 0 <= x + xx < len(canvas[0]):
                canvas[y + yy][x + xx] = v


def canvas(r):
    """the gfx/title_logo.tsv row -> 240x160 index canvas"""
    px = [[0] * 240 for _ in range(160)]
    y = int(r['y'])
    lines = [(r['top'], MARKER, 17, 184, 2), (r['main'], MARKER, 36, 212, 3)]
    for seed, (text, font, cap, max_w, rim) in enumerate(lines):
        img = brush(text_mask(text, font, cap, max_w), seed, rim)
        paste(px, img, (240 - len(img[0])) // 2, y)
        y += len(img) - 2
    if r['sub']:
        mask = text_mask(r['sub'], SANS, 7, 220, scale=1).point(lambda v: 255 if v > 100 else 0)
        img = brush(mask, 9, 1)
        paste(px, img, (240 - len(img[0])) // 2, y + 1)
    return px


# title palette -> end card (9 black, 10 fringe, 11-15 grey to white; its 12-14 are darker than the title's)
END_CARD_INK = {1: 9, 2: 9, 4: 10, 5: 10, 9: 11, 10: 12, 11: 13, 12: 14, 13: 14, 14: 15}


def small(w, h):
    """the two title lines without the subtitle, centred in a w x h grid of end-card palette indices (gfx.py edit
    kind `logo`: the 完 end card's 東京魔人學園 / 符咒封録 above "The End")"""
    r = gfx.rows('title_logo')[0]
    imgs = [brush(text_mask(r['top'], MARKER, 11, w - 16), 5, 1), brush(text_mask(r['main'], MARKER, 22, w - 4), 6, 2)]
    out = [[0] * w for _ in range(h)]
    y = (h - sum(len(i) for i in imgs) + 2) // 2
    for img in imgs:
        paste(out, [[END_CARD_INK.get(v, v) for v in row] for row in img], (w - len(img[0])) // 2, y)
        y += len(img) - 2
    return out


def title_logo(rom):
    r = gfx.rows('title_logo')[0]
    tiles, mp = gfx.tile_bg(canvas(r), 30, 20, MAX_TILES, bank=BANK << 12)
    n = max(struct.unpack_from('<H', mp, 2 * i)[0] & 0x3FF for i in range(600)) + 1
    tiles = tiles[:n * 32]
    t0, size = struct.unpack_from('<II', rom, TABLE + 8)
    t0 &= 0x1FFFFFF
    assert struct.unpack_from('<I', rom, TABLE + 16)[0] & 0x1FFFFFF == MAP
    rom[MAP:MAP + len(mp)] = mp
    out = [(MAP, MAP + len(mp))]
    if len(tiles) <= size:
        tiles = tiles.ljust(size, b'\0')
        rom[t0:t0 + size] = tiles
        return out + [(t0, t0 + size)]
    a = gfx.spare(rom, len(tiles))
    rom[a:a + len(tiles)] = tiles
    struct.pack_into('<II', rom, TABLE + 8, 0x08000000 + a, len(tiles))
    return out + [(a, a + len(tiles)), (TABLE + 8, TABLE + 16)]


def preview(out):
    rom = bytearray((ROOT / 'rom' / 'base.gba').read_bytes())
    cols = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in struct.unpack_from('<16H', rom, PAL)]
    cols[0] = (60, 0, 40)
    px = canvas(gfx.rows('title_logo')[0])
    _, mp = gfx.tile_bg(px, 30, 20, MAX_TILES, bank=BANK << 12)
    img = Image.new('RGB', (240, 160))
    img.putdata([cols[v] for row in px for v in row])
    out.mkdir(parents=True, exist_ok=True)
    img.resize((720, 480), Image.NEAREST).save(out / 'logo_en.png')
    print(out / 'logo_en.png', 'tiles', max(struct.unpack_from('<600H', mp)) - (BANK << 12) + 1)


if __name__ == '__main__':
    preview(Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else ROOT / 'work' / 'qa' / 'logo')
