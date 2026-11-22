"""gfx_signs.py: reletter a 4bpp sign board (a sprite or tile block with its own 16-colour palette in the ROM).

The board is every non-zero pixel; its inside (pixels whose 8 neighbours are all board) is repainted: the board's
shading is fitted as a plane per colour channel over the pixels that are not ink (the light ones on a dark-ink sign,
the dark ones on a light-ink banner), the English is lettered over it in the palette's darkest (or brightest) colour,
rotated 90 degrees clockwise on a vertical board, and each pixel takes the nearest colour of the palette (1-15).
"""
import struct

import numpy as np

from gfx_rooms import text_alpha


def pal_rgb(rom, off):
    return [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in struct.unpack_from('<16H', rom, off)]


def reletter(px, pal, text, vertical, size, font_path, light_ink=False, inset=0):
    """px: pixel rows (indices, edited in place); pal: 16 RGB; returns px"""
    h, w = len(px), len(px[0])
    a = np.array(px)
    board = a != 0
    inner = board.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            inner &= np.roll(np.roll(board, dy, 0), dx, 1)
    inner[0, :] = inner[-1, :] = inner[:, 0] = inner[:, -1] = False
    ys, xs = np.nonzero(inner)
    y0, y1, x0, x1 = ys.min() + inset, ys.max() - inset, xs.min() + inset, xs.max() - inset
    lum = np.array([sum(c) / 3 for c in pal])
    la = lum[a]
    win = np.full_like(la, -1e9 if not light_ink else 1e9)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            sh = np.roll(np.roll(np.where(inner, la, -1e9 if not light_ink else 1e9), dy, 0), dx, 1)
            win = np.maximum(win, sh) if not light_ink else np.minimum(win, sh)
    bgmask = inner & ((la >= win - 24) if not light_ink else (la <= win + 24))
    by, bx = np.nonzero(bgmask)
    A = np.stack([np.ones_like(bx), bx, by], 1).astype(float)
    rgb = np.array(pal, float)
    coef = [np.linalg.lstsq(A, rgb[a[by, bx], k], rcond=None)[0] for k in range(3)]
    ink = rgb[int(np.argmax(lum[1:])) + 1] if light_ink else rgb[int(np.argmin(lum[1:])) + 1]
    tw, th = x1 - x0 + 1, y1 - y0 + 1
    al, rim = text_alpha(text, th if vertical else tw, tw if vertical else th, size, font_path)
    if vertical:
        al, rim = al.rotate(-90, expand=True), rim.rotate(-90, expand=True)
    al, rim = np.array(al, float) / 255, np.array(rim, float) / 255
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not inner[y, x]:
                continue
            c = np.array([coef[k] @ (1, x, y) for k in range(3)])
            if light_ink:   # a soft dark rim keeps light letters readable on the banner
                c = c * (1 - 0.5 * rim[y - y0, x - x0])
            t = al[y - y0, x - x0]
            c = c * (1 - t) + ink * t
            px[y][x] = 1 + int(np.argmin(((rgb[1:] - c) ** 2).sum(1)))
    return px
