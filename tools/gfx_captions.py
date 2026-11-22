"""gfx_captions.py: story-scene location captions (G5/W12, S11 0xBD515C): sprite table entries 74-96 (0xD81840,
12 B each: tiles, palette 0xBD513C, 0) hold 23 captions of 0x300 B: a 16x96 4bpp column (2 tiles a row), drawn as
three 16x32 OBJs at x 216, y 8/40/72 at the top right of a story scene. JP: up to five 16x16 kanji, then a 2 px
vertical line to the bottom (palette 2-8 grey to white, no rim).

English (gfx/captions.tsv: entry, jp, en): the name set sideways, reading top to bottom (rotated 90 degrees
clockwise, as on a book spine), white on the grey ramp with a black rim (index 1) for busy backgrounds, then the
JP line where at least 10 px remain.

    python -X utf8 tools/gfx_captions.py OUT.png     # JP | EN preview of all 23
"""
import sys

from PIL import Image, ImageDraw, ImageFont

import gfx

TILES, PAL, N, SIZE = 0xBD515C, 0xBD513C, 23, 0x300
W, H = 96, 16           # the caption laid flat (before rotation): length x column width
LO, HI, RIM = 3, 8, 1   # ink ramp and rim indices
ROOM = 92               # text length limit; narrower fonts squeeze to fit


def flat(text, size=11):
    """the caption as a W x H strip (text left, then the line), palette indices"""
    font = ImageFont.truetype(str(gfx.FONT), size)
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    _, ct, _, cb = d.textbbox((0, 0), 'Hg', font=font)
    txt = Image.new('L', (r - l + 2, H), 0)
    ImageDraw.Draw(txt).text((1 - l, (H - (cb - ct)) // 2 - ct), text, font=font, fill=255)
    if txt.width > ROOM:
        txt = txt.resize((ROOM, H), Image.LANCZOS)
    img = Image.new('L', (W, H), 0)
    img.paste(txt, (1, 0))
    a = img.load()
    px = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if a[x, y] >= 40:
                px[y][x] = LO + round((a[x, y] - 40) / 215 * (HI - LO))
    for y in range(H):
        for x in range(W):
            if not px[y][x] and any(0 <= y + j < H and 0 <= x + i < W and px[y + j][x + i] >= LO
                                    for j in (-1, 0, 1) for i in (-1, 0, 1) if i or j):
                px[y][x] = RIM
    end = 1 + txt.width + 4
    if W - end >= 10:
        for x in range(end, W):
            px[7][x], px[8][x] = 7, 5
    return px


def column(text):
    """flat strip rotated 90 degrees clockwise -> 16 x 96 pixel rows (top of the letters faces right)"""
    f = flat(text)
    return [[f[H - 1 - x][y] for x in range(H)] for y in range(W)]


def captions(rom):
    out = []
    for r in gfx.rows('captions'):
        k = int(r['entry'])
        a = TILES + k * SIZE
        data = gfx.encode(column(r['en']), 2)
        assert len(data) == SIZE
        rom[a:a + SIZE] = data
        out.append((a, a + SIZE))
    return out


def preview(out):
    import struct
    orig = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
    new = bytearray(orig)
    captions(new)
    pal = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in struct.unpack_from('<16H', orig, PAL)]
    img = Image.new('RGB', (N * 20, 2 * 100 + 4), (40, 40, 90))
    for row, src in enumerate((orig, new)):
        for k in range(N):
            a = TILES + k * SIZE
            px = gfx.decode(src[a:a + SIZE], 2, 24)
            for y in range(96):
                for x in range(16):
                    if px[y][x]:
                        img.putpixel((k * 20 + 2 + x, row * 102 + 2 + y), pal[px[y][x]])
    img.resize((img.width * 3, img.height * 3), Image.NEAREST).save(out)
    print(out)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    preview(sys.argv[1])
