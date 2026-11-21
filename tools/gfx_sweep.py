"""gfx_sweep.py ROM OUTDIR: phase-1 static graphics sweep.

Splits the ROM's data area into assets at every pointer target referenced from code (0x0-0x80000) or the data
tables (0xCF0000-0xE70000), plus the LZ77 blocks (decompressed), and renders each asset as 8x8 tiles at the width
(tiles per row) whose tile edges join most smoothly. Writes numbered sheets (sheet_NNN.png, each asset labelled with
its ROM offset) and index.tsv (sheet, offset, size, format, cols, score). Every region it does not render is printed
with the reason, and written to skipped.tsv.
"""
import os
import struct
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import lz77  # noqa: E402

SKIP = [  # (lo, hi, reason) - checked by hand, see docs/re/graphics.md
    (0x000000, 0x080000, 'ARM/Thumb code'),
    (0x080000, 0x45B9CC, 'm4a sound: wave samples (00 00 00 00 / freq / loop / size headers), song headers'),
    (0xCF0000, 0xD1B000, 'Shift-JIS text and tables (docs/re/text.md)'),
    (0xD60000, 0xE2A400, 'scripts and story text (docs/re/text.md)'),
    (0xE61678, 0x1000000, 'free 0xFF space / ARM code at 0xFE0000'),
]
EXTRA = [  # gaps inside the sound area not covered by wave samples: rendered in 0x4000 chunks to be sure
    (0x217D59 & ~3, 0x253B40), (0x305D0C, 0x348614), (0x4089B8, 0x434B2C),
]
MIN_SIZE = 0x80  # below this: palettes, records
SHEET_W, SHEET_H, ZOOM = 1024, 1024, 2


def targets(d):
    vals = struct.unpack_from('<%dI' % (len(d) // 4), d)
    t = set()
    for i, v in enumerate(vals):
        s = i * 4
        if 0x08000000 <= v < 0x09000000 and (s < 0x80000 or 0xCF0000 <= s < 0xE70000):
            t.add(v - 0x08000000)
    return sorted(t)


def tiles_of(c, bpp):
    tb = 8 * bpp
    out = []
    for k in range(len(c) // tb):
        b = c[k * tb:(k + 1) * tb]
        if bpp == 4:
            px = []
            for x in b:
                px += [x & 15, x >> 4]
        else:
            px = list(b)
        out.append(px)
    return out


def score(tl, cols):
    """Mean |difference| across horizontal and vertical tile seams (lower = more continuous)."""
    tot = n = 0
    for k, t in enumerate(tl):
        if (k + 1) % cols and k + 1 < len(tl):
            r = tl[k + 1]
            tot += sum(abs(t[y * 8 + 7] - r[y * 8]) for y in range(8)); n += 8
        if k + cols < len(tl):
            r = tl[k + cols]
            tot += sum(abs(t[56 + x] - r[x]) for x in range(8)); n += 8
    return tot / n if n else 0


def best_layout(c):
    bpp = 8 if len(c) >= 0x400 and max(c) < 0x80 and len(c) % 64 == 0 else 4
    tl = tiles_of(c, bpp)
    if not tl:
        return bpp, 1, 0, tl
    mx = 127 if bpp == 8 else 15
    cand = [w for w in (4, 5, 6, 8, 10, 12, 14, 15, 16, 20, 24, 30, 32) if w <= len(tl)] or [len(tl)]
    sample = tl[:2048]
    sc = {w: score(sample, w) for w in cand}
    lo = min(sc.values())
    best = max(w for w in cand if sc[w] <= lo * 1.15 + 1e-9)  # widest layout close to the best seam score
    return bpp, best, sc[best] / mx, tl


def is_tilemap(c):
    """GBA text-BG map: u16 entries, one palette nibble dominates, tile indices below 0x400 mostly."""
    if len(c) % 2 or len(c) < 0x200:
        return False
    v = struct.unpack_from('<%dH' % (len(c) // 2), c)
    nz = [x for x in v if x]
    if len(nz) < len(v) // 4:
        return False
    pal = max(range(16), key=lambda p: sum(1 for x in nz if x >> 12 == p))
    same = sum(1 for x in nz if x >> 12 == pal) / len(nz)
    idx = len(set(x & 0x3FF for x in nz))
    return same >= 0.9 and idx >= 8 and sum(1 for x in nz if (x >> 10) & 3) < len(nz) // 4


def render(tl, bpp, cols):
    rows = (len(tl) + cols - 1) // cols
    im = Image.new('L', (cols * 8, rows * 8))
    px = im.load()
    sc = 255 // (127 if bpp == 8 else 15)
    for k, t in enumerate(tl):
        tx, ty = (k % cols) * 8, (k // cols) * 8
        for i in range(64):
            px[tx + i % 8, ty + i // 8] = min(255, t[i] * sc)
    return im


def main(rom, out):
    os.makedirs(out, exist_ok=True)
    d = open(rom, 'rb').read()
    skipped = []
    lzs = lz77.scan(d)
    lz_ranges = [(o, e) for o, _, e in lzs]
    ts = [t for t in targets(d) if t >= 0x45B9CC and t % 4 == 0] + [len(d)]  # odd targets: struct fields
    assets = []
    for k in range(len(ts) - 1):
        lo, hi = ts[k], ts[k + 1]
        why = next((r for a, b, r in SKIP if a <= lo < b), None)
        if why:
            continue
        if any(a <= lo < b for a, b in lz_ranges):
            continue
        hi = min(hi, next((a for a, b, _ in SKIP if lo < a < hi), hi))
        if hi - lo < MIN_SIZE:
            skipped.append((lo, hi, 'under 0x80 bytes (palette/record)'))
            continue
        if is_tilemap(d[lo:hi]):
            skipped.append((lo, hi, 'BG tilemap (u16 entries, one palette)'))
            continue
        assets.append((lo, d[lo:hi], 'raw'))
    for o, s, e in lzs:
        assets.append((o, lz77.decompress(d, o)[0], 'lz77'))
    for a, b in EXTRA:
        for lo in range(a, b, 0x4000):
            assets.append((lo, d[lo:min(b, lo + 0x4000)], 'sound-gap'))
    for a, b, r in SKIP:
        skipped.append((a, b, r))
    # pack into sheets
    sheets, cur, x, y, rowh = [], None, 0, 0, 0
    idx = []

    def new_sheet():
        im = Image.new('L', (SHEET_W, SHEET_H), 64)
        sheets.append(im)
        return im
    cur = new_sheet()
    for lo, c, kind in sorted(assets):
        bpp, cols, sc, tl = best_layout(c)
        z = 1 if bpp == 8 else ZOOM  # 8bpp art is large; its lettering reads at 1x
        im = render(tl, bpp, cols).resize((cols * 8 * z, ((len(tl) + cols - 1) // cols) * 8 * z), Image.NEAREST)
        # split tall images into vertical slices that fit the sheet
        parts = []
        lab_h = 10
        maxh = SHEET_H - lab_h - 2
        for py in range(0, im.height, maxh):
            parts.append(im.crop((0, py, im.width, min(im.height, py + maxh))))
        for pn, p in enumerate(parts):
            w = max(p.width, 70)
            if x + w > SHEET_W:
                x, y, rowh = 0, y + rowh + 4, 0
            if y + p.height + lab_h > SHEET_H:
                cur = new_sheet(); x, y, rowh = 0, 0, 0
            dr = ImageDraw.Draw(cur)
            dr.text((x, y), '%X%s' % (lo, '' if not pn else '+%d' % pn), fill=255)
            cur.paste(p, (x, y + lab_h))
            rowh = max(rowh, p.height + lab_h)
            x += w + 6
        idx.append((len(sheets) - 1, lo, len(c), kind, bpp, cols, round(sc, 3)))
    for i, im in enumerate(sheets):
        im.save(os.path.join(out, 'sheet_%03d.png' % i))
    with open(os.path.join(out, 'index.tsv'), 'w', encoding='utf-8') as f:
        f.write('sheet\toffset\tsize\tsource\tbpp\tcols\tseam\n')
        for r in idx:
            f.write('%03d\t%07X\t%X\t%s\t%d\t%d\t%s\n' % r)
    with open(os.path.join(out, 'skipped.tsv'), 'w', encoding='utf-8') as f:
        for a, b, r in sorted(skipped):
            f.write('%07X\t%07X\t%s\n' % (a, b, r))
    small = [s for s in skipped if s[2].startswith('under')]
    print('assets', len(idx), 'sheets', len(sheets), 'small skipped', len(small),
          'bytes', hex(sum(b - a for a, b, _ in small)))
    for a, b, r in sorted(skipped):
        if not r.startswith('under'):
            print('skipped %07X-%07X %s' % (a, b, r))


if __name__ == '__main__':
    if '--zoom' in sys.argv:  # 4bpp zoom (default 2); 1 fits ~4x more per sheet for a first pass
        ZOOM = int(sys.argv[sys.argv.index('--zoom') + 1])
    main(sys.argv[1], sys.argv[2])
