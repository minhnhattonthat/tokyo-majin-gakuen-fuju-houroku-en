"""gfx_plaques.py: small BG plaques stored as a (tiles, palette, map) triple of the screen table whose map is not
30x20 but the plaque's own size (cols x rows), loaded into a fixed tile block with one reserved blank tile.

Pack select header (S18, ブースターパック選択): entry 0xD81E04 -> 46 tiles 0xC5F760 (bank 13), palette 0xC5F740,
19x4 map 0xC5FD20; the game puts the map at BG2 row 1 and fills the rest of the layer with tile 45 (blank, bank 0),
so tile 45 must stay blank and the set may use tiles 0-44 only. Reached after a battle victory
(docs/re/game.md §Chapter battles): state work/states/pack_select_pre.mss (victory banner) + `4 a;300 -`.

The interior is rebuilt from its own texture: each row's text-free pixels give an 8 px pattern, repeated across
the row, so columns without text share tiles; then the English line is lettered on it (white ramp, dark rim).
"""
import struct

import gfx

TEXTURE = {2, 4, 5, 7, 8}   # pack header palette 0xC5F740: browns of the plaque (1 = shadow, 9-F = rim and ink)


def retile(px, cols, rows, ntiles, bank, reserved):
    """pixel canvas -> (tiles bytes of ntiles, map bytes); identical tiles shared incl. h/v flips; the tile numbers
    in `reserved` ({index: tile bytes}) are kept as given and never used for new tiles"""
    tiles = dict(reserved)
    index = {}
    for i, t in reserved.items():
        index.setdefault(t, (i, 0))
    nxt = iter(i for i in range(ntiles) if i not in reserved)
    mp = bytearray()
    for ty in range(rows):
        for tx in range(cols):
            blk = [r[tx * 8:tx * 8 + 8] for r in px[ty * 8:ty * 8 + 8]]
            ent = None
            for flip, b in ((0, blk), (0x400, [r[::-1] for r in blk]), (0x800, blk[::-1]),
                            (0xC00, [r[::-1] for r in blk[::-1]])):
                e = gfx.encode(b, 1)
                if e in index:
                    i, f = index[e]
                    ent = i | (f ^ flip)
                    break
            if ent is None:
                i = next(nxt, None)
                assert i is not None, f'plaque needs more than {ntiles} tiles'
                e = gfx.encode(blk, 1)
                tiles[i] = e
                index[e] = (i, 0)
                ent = i
            mp += (bank | ent).to_bytes(2, 'little')
    return b''.join(tiles.get(i, bytes(32)) for i in range(ntiles)), bytes(mp)


def plaque(rom, entry, cols, rows, bank, box, text, white=(11, 13, 14, 15), rim=1, size=12, blank=None):
    """reletter the plaque of screen-table entry `entry`: box = (x, y, w, h) interior rect to rebuild"""
    t0, pal, m0 = (struct.unpack_from('<I', rom, entry + k)[0] & 0x1FFFFFF for k in (0, 4, 8))
    ntiles = (m0 - t0) // 32
    canvas = gfx.screen_canvas(rom[t0:m0], struct.unpack_from(f'<{cols * rows}H', rom, m0), w=cols)
    x, y, w, h = box
    for yy in range(y, y + h):
        pat = [v for v in canvas[yy][x:x + w] if v in TEXTURE][:8]
        assert len(pat) == 8, f'row {yy}: too little texture'
        canvas[yy][x:x + w] = [pat[(x + i) % 8] for i in range(w)]
    lab = gfx.letter_levels(text, w, h, size, list(white), rim, align='center')
    for yy in range(h):
        canvas[y + yy][x:x + w] = [p or s for p, s in zip(lab[yy], canvas[y + yy][x:x + w])]
    reserved = {} if blank is None else {blank: bytes(32)}
    tiles, mp = retile(canvas, cols, rows, ntiles, bank << 12, reserved)
    rom[t0:m0] = tiles
    rom[m0:m0 + len(mp)] = mp
    return [(t0, m0), (m0, m0 + len(mp))]


def pack_header(rom):
    r = {k['jp']: k['en'] for k in gfx.rows('plaques')}
    return plaque(rom, 0xD81E04, 19, 4, 13, (8, 8, 136, 14), r['ブースターパック選択'], blank=45)
