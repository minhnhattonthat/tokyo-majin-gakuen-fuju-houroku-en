"""gfx_banners.py: battle banners (S9, 0xB4B7E8): eight 64x64 4bpp OBJ blocks (0x800 B each, 1D tile order, 8
tiles a row), shown as two sprites stacked 48 px apart (top at y 28, bottom at y 76, OBJ palette bank 10):
勝/負 (battle start), 術者/交代 (caster change), 勝/利 (victory), 敗/北 (defeat). Each block holds one word of the
English line (gfx/banners.tsv: block, jp, en), lettered like the JP glyphs: ink with a highlight on the top edge
of each stroke and a dark bottom edge, a 2 px white rim (index 15) and a black drop shadow (index 1) to the lower
right. Ink indices per pair (palette bank 10): 勝負 yellow-red 12-14/2, 術者交代 blues 8-11, 勝利 reds 2-4/14,
敗北 greys 5-7. Victory: state work/states/pack_select_pre.mss is the victory banner itself (docs/re/game.md).
"""
from PIL import Image, ImageDraw, ImageFont

import gfx

BASE = 0xB4B7E8
INK = {0: (14, 2, 13), 1: (14, 2, 13), 2: (10, 8, 11), 3: (10, 8, 11), 4: (2, 3, 4), 5: (2, 3, 4),
       6: (5, 7, 6), 7: (5, 7, 6)}   # block -> (main, dark edge, highlight)
FONT = gfx.ROOT / 'fonts' / 'liberation' / 'LiberationSans-Bold.ttf'


def word(text, ink, w=64, h=64, maxsize=28, room=54, stretch=1.6, tall=34):
    """one word lettered into a w x h block; the glyphs fit `room` px wide, then are stretched vertically by
    `stretch` (at most `tall` px high) for a banner look closer to the JP kanji's height"""
    main, dark, hi = ink
    size = maxsize
    while True:
        font = ImageFont.truetype(str(FONT), size)
        d = ImageDraw.Draw(Image.new('L', (1, 1)))
        l, t, r, b = d.textbbox((0, 0), text, font=font)
        if r - l <= room or size <= 10:
            break
        size -= 1
    txt = Image.new('L', (r - l + 2, b - t + 2), 0)
    ImageDraw.Draw(txt).text((1 - l, 1 - t), text, font=font, fill=255)
    th = min(tall, round(txt.height * stretch))
    txt = txt.resize((txt.width, th), Image.LANCZOS)
    img = Image.new('L', (w, h), 0)
    img.paste(txt, ((w - txt.width) // 2 - 1, (h - th) // 2 - 1))
    a = img.load()
    m = [[a[x, y] >= 110 for x in range(w)] for y in range(h)]

    def on(x, y, g):
        return 0 <= x < w and 0 <= y < h and g[y][x]
    px = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if m[y][x]:
                px[y][x] = hi if not on(x, y - 1, m) else dark if not on(x, y + 1, m) else main
    rim = [[not m[y][x] and any(on(x + i, y + j, m) for j in range(-2, 3) for i in range(-2, 3)
                                if abs(i) + abs(j) <= 3) for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if rim[y][x]:
                px[y][x] = 15
    body = [[px[y][x] != 0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if not body[y][x] and any(on(x - k, y - k, body) for k in (1, 2, 3)):
                px[y][x] = 1
    return px


def banners(rom):
    out = []
    for r in gfx.rows('banners'):
        k = int(r['block'])
        a = BASE + k * 0x800
        rom[a:a + 0x800] = gfx.encode(word(r['en'], INK[k]), 8)
        out.append((a, a + 0x800))
    return out
