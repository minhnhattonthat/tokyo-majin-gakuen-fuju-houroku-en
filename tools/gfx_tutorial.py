"""gfx_tutorial.py: English battle-tutorial screens (S29 / S26 0xD35868, group tutorial).

The rules tutorial (mode 1 on a fresh game) draws a picture of the card panel (8bpp screen, table entry 0xD635E8,
64 colours) and pink-framed callout overlays over it (4bpp screens, entries 0xD63288-0xD635C8). Each entry is
three (pointer, size) pairs: palette, tiles, map (30x20 u16; size 0x00A000F0 = 240x160). The English art is
composed once by tools/debug/tut_compose.py into gfx/tutorial/<ENTRY>.png, indexed in the screen's own palette;
this group retiles each PNG (identical and flipped tiles shared, tile 0 blank), writes the tiles back in place
when they fit the old block (else into free space, the pointer and byte count of every entry sharing the block
moved), and rewrites the map in place with the old palette-bank bits.
"""
import struct

from PIL import Image

import gfx

TABLE = (0xD63288, 0xD63600)
DIR = gfx.ROOT / 'gfx' / 'tutorial'
SPARE = 0xF90000   # inside the free 0xFF run 0xF20000-0xFBFFFF, after HAIKU_SPARE's two blocks (0xF80000-0xF83FFF)


def entries(rom, tiles):
    """table entries (offsets) whose tiles pointer is `tiles` (several entries reuse a screen)"""
    return [e for e in range(TABLE[0], TABLE[1], 0x18)
            if struct.unpack_from('<I', rom, e + 8)[0] & 0x1FFFFFF == tiles]


def retile(px, bpp):
    """indexed 240x160 rows -> (tile bytes, map entries without bank): tile 0 blank, flips shared"""
    def enc(rows):
        if bpp == 8:
            return bytes(v for r in rows for v in r)
        return bytes((r[x] & 15) | (r[x + 1] & 15) << 4 for r in rows for x in range(0, 8, 2))
    blank = enc([[0] * 8] * 8)
    tiles, index, ents = [blank], {blank: 0}, []
    for ty in range(20):
        for tx in range(30):
            t = [r[tx * 8:tx * 8 + 8] for r in px[ty * 8:ty * 8 + 8]]
            forms = ((t, 0), ([r[::-1] for r in t], 0x400), (t[::-1], 0x800), ([r[::-1] for r in t[::-1]], 0xC00))
            for rows, flip in forms:
                k = enc(rows)
                if k in index:
                    ents.append(index[k] | flip)
                    break
            else:
                index[enc(t)] = len(tiles)
                ents.append(len(tiles))
                tiles.append(enc(t))
    return b''.join(tiles), ents


def screen(rom, e, spare):
    p, ps, t, ts, m, _ = struct.unpack_from('<6I', rom, e)
    t, m = t & 0x1FFFFFF, m & 0x1FFFFFF
    bpp = 8 if (ps & 0xFFFF) > 0x20 else 4
    im = Image.open(DIR / f'{e:06X}.png')
    assert im.mode == 'P' and im.size == (240, 160), f'{e:06X}.png: need an indexed 240x160 image'
    flat = list(im.tobytes())   # mode P: one byte per pixel
    px = [flat[y * 240:y * 240 + 240] for y in range(160)]
    assert bpp == 8 or max(flat) < 16, f'{e:06X}.png: 4bpp screen with index >= 16'
    old = struct.unpack_from('<600H', rom, m)
    banks = [x & 0xF000 for x in old]
    bank = max(set(banks), key=banks.count)
    tiles, ents = retile(px, bpp)
    out = []
    for i, x in enumerate(ents):
        struct.pack_into('<H', rom, m + 2 * i, x | bank)
    out.append((m, m + 1200))
    if len(tiles) <= ts:
        rom[t:t + len(tiles)] = tiles
        return out + [(t, t + len(tiles))], spare
    a = spare
    assert all(b == 0xFF for b in rom[a:a + len(tiles)]), f'{a:06X} is not free space'
    rom[a:a + len(tiles)] = tiles
    for f in entries(rom, t):
        struct.pack_into('<II', rom, f + 8, 0x08000000 + a, len(tiles))
        out.append((f + 8, f + 16))
    return out + [(a, a + len(tiles))], (a + len(tiles) + 0xFF) & ~0xFF


def tutorial(rom):
    out, spare = [], SPARE
    for png in sorted(DIR.glob('D6*.png')):
        r, spare = screen(rom, int(png.stem, 16), spare)
        out += r
    return out
