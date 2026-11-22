"""gfx_deck.py: deck editor sprite labels (S19), rows of gfx/deck_edit.tsv.

Sheets (sprite table 0xD81CC0 / 0xD81CCC, entries tiles, palette, 0):
- buttons 0xC66C18, OBJ bank 3 (grey ramp 1 dark .. 15 white, background 6): 32x16 halves (4x2 tiles, 0x100 B),
  a button is `halves` consecutive halves. Frame: row 0 and col 0 light, row 15 and the right columns dark.
- category tabs 0xC67D38, OBJ bank 13 (amber ramp, background 7): 13 entries of 0x200 B, each a 32x16 left half and
  a 32x16 right half (diagonal stripes from x ~45). In OBJ VRAM the left halves sit at tiles 494 + 8k and ONE right
  half at 598, which every tab's OAM uses (tried: making the right halves differ in ROM changes nothing, the game
  still shows tab 0's). Tabs 0-3 carry a 16x16 全 badge at x 48-63 (separate OBJ). Rows of kind tab_todo wait for
  that loader/OAM code to be found.

Each row: clear the interior x0..x1, rows 1..14, to the background colour (tabs keep the stripe run at the right
end of each row), then letter `en` centred in it with gfx.letter (Liberation Sans Bold, dark rim).
"""
import gfx

SIZE = 12
BTN = dict(bg=6, ramp=(11, 15, 1))
TAB = dict(bg=7, ramp=(12, 15, 1))


def halves_px(rom, a, n):
    hs = [gfx.decode(rom[a + k * 0x100:a + (k + 1) * 0x100], 4, 8) for k in range(n)]
    return [sum((h[y] for h in hs), []) for y in range(16)]


def px_halves(px, n):
    return b''.join(gfx.encode([row[k * 32:k * 32 + 32] for row in px], 4) for k in range(n))


def redraw(px, x0, x1, text, bg, ramp, keep_stripes=False):
    w = x1 - x0 + 1
    for y in range(1, 15):
        end = x1 + 1
        if keep_stripes:   # stripe run at the row's right end: indices 4/7 up to the frame column
            end = len(px[y]) - 1
            while end > x0 and px[y][end - 1] in (4, 7):
                end -= 1
            end = min(end, x1 + 1) if end > x1 else end
        for x in range(x0, end):
            px[y][x] = bg
    lab = shadowed(text, w, 14, SIZE, ramp)
    for y in range(14):
        for x in range(w):
            if lab[y][x]:
                px[1 + y][x0 + x] = lab[y][x]
    return px


def shadowed(text, w, h, size, ramp):
    """text centred in w x h: ink alpha -> ramp lo..hi, then a 1 px shadow (ramp's dark index) right, below and
    diagonal of the ink, like the Japanese labels (no outline on the top/left side)"""
    from PIL import Image, ImageDraw, ImageFont
    lo, hi, dark = ramp
    while True:
        font = ImageFont.truetype(str(gfx.FONT), size)
        img = Image.new('L', (w, h), 0)
        d = ImageDraw.Draw(img)
        l, t, r, b = d.textbbox((0, 0), text, font=font)
        if r - l <= w - 2 or size <= 8:
            break
        size -= 1
    d.text(((w - 1 - (r - l)) // 2 - l, (h - 1 - (b - t)) // 2 - t), text, font=font, fill=255)
    a = img.load()
    ink = [[a[x, y] >= 80 for x in range(w)] for y in range(h)]
    px = [[lo + round(max(0, a[x, y] - 80) / 175 * (hi - lo)) if ink[y][x] else 0 for x in range(w)]
          for y in range(h)]
    for y in range(h):
        for x in range(w):
            if not ink[y][x] and any(0 <= y - j < h and 0 <= x - i < w and ink[y - j][x - i]
                                     for j, i in ((0, 1), (1, 0), (1, 1))):
                px[y][x] = dark
    return px


def deck_edit(rom):
    out = []
    for r in gfx.rows('deck_edit'):
        a, n, x0, x1 = int(r['offset'], 16), int(r['halves']), int(r['x0']), int(r['x1'])
        if r['kind'] == 'btn':
            px = redraw(halves_px(rom, a, n), x0, x1, r['en'], **BTN)
        elif r['kind'] == 'tab':
            px = redraw(halves_px(rom, a, n), x0, x1, r['en'], keep_stripes=True, **TAB)
        else:   # tab_todo: the game draws every tab's right half from one shared block (OBJ tile 598), not yet
            continue   # per tab; see docs/status.md
        data = px_halves(px, n)
        rom[a:a + len(data)] = data
        out.append((a, a + len(data)))
    return out


def preview(out, pal_bin=None, zoom=3):
    """original | English of every row, each with its OBJ palette (from a ppudump .pal.bin, else grey)"""
    import struct
    from PIL import Image
    orig = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
    new = bytearray(orig)
    deck_edit(new)
    pal = Path(pal_bin).read_bytes() if pal_bin else None

    def rgb(bank):
        if not pal:
            return [(i * 17,) * 3 for i in range(16)]
        c = struct.unpack_from('<16H', pal, 0x200 + bank * 32)
        return [((v & 31) * 8, (v >> 5 & 31) * 8, (v >> 10 & 31) * 8) for v in c]

    rws = gfx.rows('deck_edit')
    img = Image.new('RGB', (2 * 100, 18 * len(rws)), (0, 0, 0))
    for i, r in enumerate(rws):
        a, n = int(r['offset'], 16), int(r['halves'])
        cols = rgb(3 if r['kind'] == 'btn' else 13)
        for j, src in enumerate((orig, new)):
            px = halves_px(src, a, n)
            for y in range(16):
                for x in range(32 * n):
                    img.putpixel((j * 100 + x, i * 18 + y), cols[px[y][x]])
    img = img.resize((img.width * zoom, img.height * zoom), Image.NEAREST)
    img.save(out)
    print(out)


if __name__ == '__main__':
    import sys
    from pathlib import Path
    preview(sys.argv[1] if len(sys.argv) > 1 else 'work/gfx/deck_edit.png', sys.argv[2] if len(sys.argv) > 2 else None)
