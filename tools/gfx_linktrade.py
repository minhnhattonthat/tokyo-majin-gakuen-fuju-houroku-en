"""gfx_linktrade.py: link-trade screen (mode 11) sprite badges, rows of gfx/link_trade.tsv (group link_trade).

Mode 11's loader 0x0805BEAC (steps 0-2 of its task state 2) loads sprite entries 0x52E-0x532 of the table 0xD7DD18
(tiles, palette, 0): status badges 待機中 0xC047A8, 選択中 0xC04BC8, 確認中 0xC05208 (each 0x400 B: a bright 64x16
badge, then its dim copy at +0x200; a 64x16 badge is two 32x16 OBJs = 4x2 tiles, 0x100 B each, 46 px used), and the
buttons 登録 / 終了 0xC04FE8 (two 32x16 OBJs). The badge palettes are 16-colour ramps (dark 1 .. light 15).

Each row: the rect x0..x1, y0..y1 is refilled with `fill` (hex index; empty = per pixel row, the most common
colour below `ink`, the lowest index counted as JP lettering, for the gradient buttons), then `en` is lettered centred with gfx.letter (Liberation Sans
Bold) on the ramp lo..hi with rim `rim`. Seen in game with `warp.py MODE11 --script tools/debug/setreg.lua --var
AT=0x0805AEBC --var REG=0 --var VAL=1` (forces the link check of task state 1; docs/re/graphics.md S16).
"""
from collections import Counter

import gfx


def halves_px(rom, a, n):
    hs = [gfx.decode(rom[a + k * 0x100:a + (k + 1) * 0x100], 4, 8) for k in range(n)]
    return [sum((h[y] for h in hs), []) for y in range(16)]


def px_halves(px, n):
    return b''.join(gfx.encode([row[k * 32:k * 32 + 32] for row in px], 4) for k in range(n))


def redraw(px, x0, x1, y0, y1, fill, ink, text, size, ramp):
    for y in range(y0, y1 + 1):
        if fill is None:   # gradient buttons: per row, the most common non-ink colour
            row = px[y][x0:x1 + 1]
            bg = [v for v in row if v < ink] or row
            fill_y = Counter(bg).most_common(1)[0][0]
        else:
            fill_y = fill
        for x in range(x0, x1 + 1):
            px[y][x] = fill_y
    w, h = x1 - x0 + 1, y1 - y0 + 1
    lab = gfx.letter(text, w, h, size, ramp=ramp)
    for y in range(h):
        for x in range(w):
            if lab[y][x]:
                px[y0 + y][x0 + x] = lab[y][x]


def apply(rom):
    out = []
    for r in gfx.rows('link_trade'):
        a, n = int(r['offset'], 16), int(r['halves'])
        px = halves_px(rom, a, n)
        fill = int(r['fill'], 16) if r['fill'] else None
        redraw(px, int(r['x0']), int(r['x1']), int(r['y0']), int(r['y1']), fill, int(r['ink'] or '0', 16), r['en'],
               int(r['size']), (int(r['lo'], 16), int(r['hi'], 16), int(r['rim'], 16)))
        data = px_halves(px, n)
        rom[a:a + len(data)] = data
        out.append((a, a + len(data)))
    return out
