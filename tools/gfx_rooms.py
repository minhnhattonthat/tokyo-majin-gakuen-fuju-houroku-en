"""gfx_rooms.py: English lettering on the 8bpp full-screen room backgrounds (group room_banners, gfx/room_banners.tsv).

A room screen is a (tiles, palette, map) triple of the screen table (docs/re/graphics.md §Screen table) with a
128-colour palette: 8bpp tiles, 30x20 map (tile index from the block start, flip bits honoured). Each tsv row names
the screen by its tiles offset and a rect in map pixels (the game scrolls BG3 by (-11,-4), so screen = map + (11,4)):
the rect is wiped with the plaque's own wood (per column for a vertical plaque, per row for a horizontal one, from
the pixels that are neither ink nor outline) and the English is lettered white with a dark rim, read top to bottom
on a vertical plaque (rotated 90 degrees clockwise). Pixels map to the nearest colour of the screen's palette.
Edited tiles are rewritten in place; a tile the map also uses outside the edited area stops the build.
"""
import struct

from PIL import Image, ImageDraw, ImageFont

W, H = 30, 20


# 8bpp screens whose palette entry is not 128 colours at BG palette 0: tiles -> (colours, first BG palette index).
# Mode 11 (link trade) loads its 32 colours to BG palette 208 (0x0805BEF6: 0x03005C50 = palette buffer + 0x1A0).
PALS = {0xBFC5F8: (32, 208)}


def screen_entry(rom, tiles):
    """tiles offset -> (palette, map, ntiles, (ncolours, base)) from the screen table (8bpp tiles)"""
    from gfx_screens import screens
    for _, t, p, m, nt, npal in screens(rom):
        if t == tiles:
            ncol, base = PALS.get(tiles, (128, 0))
            assert npal * 16 == ncol, f'{tiles:06X} palette has {npal * 16} colours, expected {ncol}'
            return p, m, nt // 2, (ncol, base)
    raise KeyError(f'{tiles:06X} not in the screen table')


def palette(rom, p, ncol=(128, 0)):
    """BG palette index -> RGB; indices the screen's palette does not load are None"""
    n, base = ncol
    cs = struct.unpack_from(f'<{n}H', rom, p)
    pal = [None] * 256
    for i, c in enumerate(cs):
        pal[base + i] = ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8)
    return pal


def entries(rom, m):
    return [struct.unpack_from('<H', rom, m + 2 * i)[0] for i in range(W * H)]


def decode(rom, t, ents):
    px = [[0] * (W * 8) for _ in range(H * 8)]
    for i, e in enumerate(ents):
        n, c, r = e & 0x3FF, i % W, i // W
        for y in range(8):
            for x in range(8):
                v = rom[t + 64 * n + (7 - y if e & 0x800 else y) * 8 + (7 - x if e & 0x400 else x)]
                px[r * 8 + y][c * 8 + x] = v
    return px


def lum(c):
    return (c[0] * 3 + c[1] * 6 + c[2]) / 10


def nearest(pal, rgb, cache):
    if rgb not in cache:
        cache[rgb] = min((i for i in range(1, len(pal)) if pal[i] is not None), key=lambda i: sum((a - b) ** 2 for a, b in zip(pal[i], rgb)))
    return cache[rgb]


def text_alpha(text, w, h, size, font_path):
    """text centred in w x h (long side first) -> (ink alpha, rim alpha) rows, 0-255"""
    font = ImageFont.truetype(str(font_path), size)
    img = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    while (r - l > w - 2 or b - t > h - 2) and size > 7:
        size -= 1
        font = ImageFont.truetype(str(font_path), size)
        l, t, r, b = d.textbbox((0, 0), text, font=font)
    d.text(((w - (r - l)) // 2 - l, (h - (b - t)) // 2 - t), text, font=font, fill=255)
    rim = Image.new('L', (w, h), 0)
    a = img.load()
    rp = rim.load()
    for y in range(h):
        for x in range(w):
            rp[x, y] = max(a[x + i, y + j] for j in (-1, 0, 1) for i in (-1, 0, 1)
                           if 0 <= x + i < w and 0 <= y + j < h)
    return img, rim


# plaque colour luminance range per screen (default: the brown wood plaques); the link-trade 交換符 band is green
WOOD = {0xBFC5F8: (100, 160)}


def wipe(px, pal, x, y, w, h, vertical, wood_lum=(30, 120)):
    """fill the rect with its wood: per column (vertical) or row, the most common non-ink, non-outline colour"""
    from collections import Counter
    lines = range(x, x + w) if vertical else range(y, y + h)
    lo, hi = wood_lum
    for k in lines:
        cells = [(x2, k) for x2 in range(y, y + h)] if vertical else [(x2, k) for x2 in range(x, x + w)]
        vals = [px[b][a] if not vertical else px[a][b] for a, b in cells]
        wood = [v for v in vals if lo <= lum(pal[v]) < hi] or vals
        fill = Counter(wood).most_common(1)[0][0]
        for a, b in cells:
            if vertical:
                px[a][b] = fill
            else:
                px[b][a] = fill


def letter(px, pal, x, y, w, h, vertical, text, size, font_path):
    ink, rim = text_alpha(text, h if vertical else w, w if vertical else h, size, font_path)
    if vertical:
        ink, rim = ink.rotate(-90, expand=True), rim.rotate(-90, expand=True)
    ia, ra = ink.load(), rim.load()
    cache = {}
    for yy in range(h):
        for xx in range(w):
            a, r = ia[xx, yy] / 255, ra[xx, yy] / 255
            if not r:
                continue
            bg = pal[px[y + yy][x + xx]]
            dark = tuple(int(c * (1 - r) + 16 * r) for c in bg)
            rgb = tuple(int(c * (1 - a) + 248 * a) for c in dark)
            px[y + yy][x + xx] = nearest(pal, (rgb[0] // 8 * 8, rgb[1] // 8 * 8, rgb[2] // 8 * 8), cache)


def redraw(rom, tiles, labels, font_path, spare):
    """labels: [(x, y, w, h, vertical, text, size)] in map pixels -> written ROM ranges.
    Edited tiles are rewritten in place while each is used by one map cell; when a tile repeats (texture tiles), the
    edited cells get tiles of their own appended to the block, and the block (tiles then map) moves to free space at
    spare[0] (advanced past it), with the screen table's tiles and map pointers updated."""
    from gfx_screens import screens
    entry = next(e for e, t, *_ in screens(rom) if t == tiles)
    p, m, nt, ncol = screen_entry(rom, tiles)
    pal, ents = palette(rom, p, ncol), entries(rom, m)
    px = decode(rom, tiles, ents)
    cells = set()
    for x, y, w, h, vertical, text, size in labels:
        wipe(px, pal, x, y, w, h, vertical, WOOD.get(tiles, (30, 120)))
        letter(px, pal, x, y, w, h, vertical, text, size, font_path)
        cells |= {(r, c) for r in range(y // 8, (y + h - 1) // 8 + 1) for c in range(x // 8, (x + w - 1) // 8 + 1)}
    uses = {}
    for e in ents:
        uses[e & 0x3FF] = uses.get(e & 0x3FF, 0) + 1
    block = bytearray(rom[tiles:tiles + 64 * nt])
    out, moved = [], False
    for r, c in sorted(cells):
        e = ents[r * W + c]
        n = e & 0x3FF
        data = bytearray(64)
        for y in range(8):
            for x in range(8):
                data[(7 - y if e & 0x800 else y) * 8 + (7 - x if e & 0x400 else x)] = px[r * 8 + y][c * 8 + x]
        if block[64 * n:64 * n + 64] == data:
            continue
        if uses[n] == 1:
            block[64 * n:64 * n + 64] = data
            continue
        moved = True
        n2 = len(block) // 64
        assert n2 < 1024, f'{tiles:06X}: more than 1024 tiles'
        block += data
        ents[r * W + c] = (e & ~0x3FF) | n2
    if not moved:
        rom[tiles:tiles + len(block)] = block
        return [(tiles, tiles + len(block))]
    mp = b''.join(e.to_bytes(2, 'little') for e in ents)
    a = spare[0]
    assert all(b == 0xFF for b in rom[a:a + len(block) + len(mp)]), f'{a:06X} is not free space'
    rom[a:a + len(block)] = block
    rom[a + len(block):a + len(block) + len(mp)] = mp
    struct.pack_into('<I', rom, entry, 0x08000000 + a)
    struct.pack_into('<I', rom, entry + 8, 0x08000000 + a + len(block))
    spare[0] = (a + len(block) + len(mp) + 0xFF) & ~0xFF
    out += [(a, a + len(block) + len(mp)), (entry, entry + 4), (entry + 8, entry + 12)]
    return out
