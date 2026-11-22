"""codestr.py: the Shift-JIS strings in the code area (0x06485C-0x064A2A), which the pointer-range scan of
tools/strslots.py never saw, and the engine work that puts them in English (docs/re/text.md §Code-area strings).

    python -X utf8 tools/codestr.py --preview OUT.png    # the 47 rotated prefecture columns, JP order

Two tables of ROM pointers in 0xD7A614-0xD7A6FF point at 8-byte NUL-ended slots:

* D7A614: the 47 prefectures in gojuon order (愛知県 .. 和歌山県), only read by the Birthplace? picker 0x080041B8
  (args r0 = first index, r1 = BG0 tile base - 0x20, r2 = BG0 map). It draws 10 names per page as vertical columns:
  name i one cell (16 px) right of name i-1 (map + 0x24A + 4i), its characters one cell down each (map += 0x80),
  tiles from index 0x11 up, palette 12. English names are not drawable vertically letter by letter, so PREF_FN is
  replaced by a jump to an ARM routine (PREF_HOOK) that copies a pre-rendered 16x64 column per name (the name set
  sideways, top to bottom, as on a book spine, like the story captions) into 4 cells and writes their map entries.
  Kind `pref` in script/system/code.tsv; `en` = the name drawn.

* D7A6D0-D7A6FC: pieces the three text printers (BG glyph routine 0x08003Bxx, printer B 0x080047xx, printer C
  0x08051Cxx) substitute for the card-effect codes {&<v>NN} (v = x/y/z: which effect argument; NN = type):
    type 2, 6   D7A6D0[arg]: 自分 / 相手 / 両者, 2 units      type 5   D7A6DC[arg]: 右 / 左, 1 unit
    type 4      arg 5: 全ての (D7A6F8), 3 units; else icon   type 11  D7A6E4[arg]: - / 破壊 / 除去, 2 units
    numbers     {&S..} sign D7A6F0 (－, ＋) then digits from D7A6FC (０１２３４５６７８９, one unit per digit)
  The printers draw a FIXED number of units per piece (no NUL check), each unit one cell, through the same unit
  routine as the text around it, so English VWF units keep the strip (tools/vwf.py). Each piece is encoded into
  exactly its unit count (Encoder.encode_units: split chunks, then pad with the empty chunk, which draws nothing and
  advances nothing). Type 5 is redirected into the type 2/6 loop (2 units, its own table) and type 11's loop is
  raised to 4 units, in all three printers (LOOP_PATCHES). Kind `piece`, max = units.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import textcodec  # noqa: E402

PREF_TABLE, NPREF = 0xD7A614, 47
PREF_FN = 0x0041B8
PREF_ORIG = bytes.fromhex('f0b557464e464546')   # push {r4-r7,lr}; mov r7,sl; mov r6,sb; mov r5,r8
PREF_HOOK = 0xFE4000            # ARM routine, then the 47 columns (free 0xFF space, docs/re/text.md Free space)
PREF_NCELL = PREF_HOOK + 0x100  # cells each column uses (its tiles are packed: the JP pages used <= 32 cells)
PREF_GFX = PREF_HOOK + 0x140
CELLS = 4                       # cells per column (64 px): the JP names are 3-4 kanji

# piece table pointer -> units drawn (after LOOP_PATCHES)
PIECE_PTRS = {0xD7A6D0: 2, 0xD7A6D4: 2, 0xD7A6D8: 2,      # 自分 相手 両者
              0xD7A6DC: 2, 0xD7A6E0: 2,                    # 右 左 (type 5, redirected to 2 units)
              0xD7A6E8: 4, 0xD7A6EC: 4,                    # 破壊 除去 (type 11, raised to 4 units)
              0xD7A6F0: 1, 0xD7A6F4: 1,                    # － ＋
              0xD7A6F8: 3}                                 # 全ての
DIGITS_PTR = 0xD7A6FC                                      # ０..９: 10 units, unit d = digit d
MARGIN = 4      # px a piece leaves free in its last cell: a strip may enter it a few px past its first cell


def _thumb(asm, addr):
    import vwf
    return vwf.assemble(asm, 0x08000000 + addr, thumb=True)


def loop_patches():
    """(offset, original, new, what) for the three printers. Each type-5 block ends in a tail (bl unit routine;
    return cells + 0x1F) that the number formatter's ones digit jumps into (0x3F22, 0x4848, 0x51C8C), so the
    redirect overwrites only the block's first 12 bytes and the tail stays."""
    out = []
    # BG printer: type 5 at 0x3F04 (pool 0x3F30 = D7A6DC) -> loop body 0x3F46 (table slot in [sp+0x10])
    out.append((0x003F04, None, _thumb('movs r5, #0\nlsls r1, r6, #2\nldr r0, [pc, #0x24]\nadds r1, r1, r0\n'
                                       'str r1, [sp, #0x10]\nb #0x08003F46', 0x003F04),
                'BG printer type 5 -> 2-unit loop'))
    # printer B: type 5 at 0x4834 (pool 0x4854) -> loop 0x486A (table slot in sl)
    out.append((0x004834, None, _thumb('movs r5, #0\nlsls r1, r6, #2\nldr r0, [pc, #0x18]\nadds r1, r1, r0\n'
                                       'mov sl, r1\nb #0x0800486A', 0x004834),
                'printer B type 5 -> 2-unit loop'))
    # printer C: type 5 at 0x51C74 (pool 0x51C98) -> loop 0x51CAE (table slot in sl, unit counter r4)
    out.append((0x051C74, None, _thumb('movs r4, #0\nlsls r1, r5, #2\nldr r0, [pc, #0x1c]\nadds r1, r1, r0\n'
                                       'mov sl, r1\nb #0x08051CAE', 0x051C74),
                'printer C type 5 -> 2-unit loop'))
    for off, tail in ((0x003F04, 0x003F22), (0x004834, 0x004848), (0x051C74, 0x051C8C)):
        assert len(next(n for o, _, n, _ in out if o == off)) <= tail - off
    out += [(0x003FD0, bytes.fromhex('012d'), bytes.fromhex('032d'), 'BG printer type 11: 4 units'),
            (0x0048CC, bytes.fromhex('012d'), bytes.fromhex('032d'), 'printer B type 11: 4 units'),
            (0x051D18, bytes.fromhex('012c'), bytes.fromhex('032c'), 'printer C type 11: 4 units')]
    return out


def _ptr(d, p):
    return struct.unpack_from('<I', d, p)[0] - 0x08000000


def _cstr(d, a):
    return d[a:d.index(b'\0', a)]


def rows(d):
    """rows of script/system/code.tsv for the original ROM bytes d (ROM order)"""
    out = {}
    for i in range(NPREF):
        a = _ptr(d, PREF_TABLE + 4 * i)
        out[a] = ('pref', CELLS * 16, 'Birthplace? picker, gojuon index %d' % i)
    for p, n in PIECE_PTRS.items():
        out[_ptr(d, p)] = ('piece', n, 'card-effect piece, %d units (pointer %X)' % (n, p))
    out[_ptr(d, DIGITS_PTR)] = ('piece', 10, 'card-effect digits: one unit per digit (pointer %X)' % DIGITS_PTR)
    return [{'id': '%06X' % a, 'kind': k, 'max': str(m), 'jp': textcodec.decode(_cstr(d, a)), 'en': '',
             'notes': note} for a, (k, m, note) in sorted(out.items())]


def ranges(d):
    """every range apply() may write (tests/test_romdiff.py): piece slots, loop patches, the picker stub
    (PREF_HOOK lies in the free space after SPILL, allowed as a whole)"""
    rs = rows(d)
    starts = sorted(int(r['id'], 16) for r in rs)
    out = []
    for r in rs:
        if r['kind'] == 'piece':
            a = int(r['id'], 16)
            nxt = [s for s in starts if s > a]
            out.append((a, nxt[0] if nxt else a + 2 * int(r['max'])))
    out += [(off, off + len(new)) for off, _, new, _ in loop_patches()]
    out.append((PREF_FN, PREF_FN + 8))
    return out


def covered(d):
    """(start, end) byte ranges of the code-area strings (NUL included)"""
    return [(int(r['id'], 16), int(r['id'], 16) + len(textcodec.encode(r['jp'])) + 1) for r in rows(d)]


# ---------------------------------------------------------------- prefecture columns

def column(font_rows, text):
    """the name as a 16 x 64 nibble image: drawn flat with the VWF font, rotated 90 degrees clockwise (reading top to
    bottom), white (F) with the dark shadow (D) right and below, as the dialogue font"""
    import vwf
    L = CELLS * 16
    flat = [[0] * L for _ in range(16)]
    x, y0 = 1, 3                                   # flat rows 3..13 -> screen columns 12..2
    for ch in vwf.normalize(text):
        if ch == ' ':
            x += vwf.SPACE_ADV
            continue
        g = font_rows[ch]
        for yy, r in enumerate(g):
            for xx, c in enumerate(r):
                if c == '#':
                    if x + xx >= L - 1:
                        raise ValueError('prefecture %r is longer than %d px' % (text, L - 2))
                    flat[y0 + yy][x + xx] = 1
        x += len(g[0]) + 1
    ink = [[flat[15 - X][Y] for X in range(16)] for Y in range(L)]     # rotate clockwise: (x, y) -> (15 - y, x)
    img = [[0xF if ink[Y][X] else 0 for X in range(16)] for Y in range(L)]
    for Y in range(L):
        for X in range(16):
            if not ink[Y][X] and ((X and ink[Y][X - 1]) or (Y and ink[Y - 1][X]) or (X and Y and ink[Y - 1][X - 1])):
                img[Y][X] = 0xD
    return img


def cells_used(img):
    """cells down to the last inked row"""
    return max(y for y in range(len(img)) if any(img[y])) // 16 + 1


def column_tiles(img):
    """16 x 64 image -> 4 cells x (TL TR BL BR) 4bpp tiles = 0x200 bytes"""
    out = bytearray()
    for c in range(CELLS):
        for ty, tx in ((0, 0), (0, 8), (8, 0), (8, 8)):
            for y in range(8):
                row = img[16 * c + ty + y]
                v = 0
                for x in range(8):
                    v |= row[tx + x] << (4 * x)
                out += struct.pack('<I', v)
    return bytes(out)


PREF_ASM = '''
    stmfd sp!, {r4-r11, lr}
    and   r0, r0, #0xFF
    add   r6, r1, #0x200
    add   r5, r2, #0x240
    add   r5, r5, #0xA
    mov   r7, #0x11
    orr   r7, r7, #0xC000
    mov   r4, #0
    ldr   r8, gfx
col:
    add   r3, r0, r4
    cmp   r3, #%(npref)d
    movhs r3, #%(npref)d
    ldr   r10, ncell
    ldrb  r10, [r10, r3]
    add   r3, r8, r3, lsl #9
    mov   r9, r5
    cmp   r10, #0
    beq   blank
cell:
    mov   lr, #8
copy:
    ldmia r3!, {r1, r2, r11, r12}
    stmia r6!, {r1, r2, r11, r12}
    subs  lr, lr, #1
    bne   copy
    strh  r7, [r9]
    add   r7, r7, #1
    strh  r7, [r9, #2]
    add   r7, r7, #1
    strh  r7, [r9, #0x40]
    add   r7, r7, #1
    strh  r7, [r9, #0x42]
    add   r7, r7, #1
    add   r9, r9, #0x80
    subs  r10, r10, #1
    bne   cell
blank:
    add   r1, r5, #%(colbytes)d
    mov   r2, #0
bloop:
    cmp   r9, r1
    bhs   next
    strh  r2, [r9]
    strh  r2, [r9, #2]
    strh  r2, [r9, #0x40]
    strh  r2, [r9, #0x42]
    add   r9, r9, #0x80
    b     bloop
next:
    add   r5, r5, #4
    add   r4, r4, #1
    cmp   r4, #10
    blt   col
    ldmfd sp!, {r4-r11, lr}
    bx    lr
gfx: .word %(gfx)d
ncell: .word %(ncell)d
'''


def apply(rom, enc, script):
    """write the English code-area strings into bytearray rom (enc: vwf.Encoder; script: {id: row}); returns the
    written ranges. Rows without `en` keep the Japanese (and their engine path)."""
    import vwf
    out = []
    rs = [r for r in script.values() if r['kind'] in ('pref', 'piece')]
    pieces = [r for r in rs if r['kind'] == 'piece']
    prefs = sorted((r for r in rs if r['kind'] == 'pref'), key=lambda r: int(r['id'], 16))
    if any(r['en'] for r in pieces):
        if not all(r['en'] for r in pieces):
            raise ValueError('code.tsv: translate every piece or none (the loop patches assume English pieces)')
        starts = sorted(int(r['id'], 16) for r in rs)
        for r in pieces:
            a, n = int(r['id'], 16), int(r['max'])
            digits = r['notes'].startswith('card-effect digits')
            b = enc.encode_units(r['en'], n, 0 if n == 1 or digits else MARGIN)
            # slot = up to the next string; the digit row ends at its own NUL (code follows)
            cap = 2 * n if digits else next(s for s in starts if s > a) - a
            if len(b) > cap:
                raise ValueError('piece %s: %d bytes, slot holds %d' % (r['id'], len(b), cap))
            if len(b) + 2 <= cap:
                b += b'\0\0'
            rom[a:a + len(b)] = b
            out.append((a, a + len(b)))
        for off, old, new, _ in loop_patches():
            if old is not None and bytes(rom[off:off + len(old)]) != old:
                raise ValueError('code at %06X is not the original' % off)
            rom[off:off + len(new)] = new
            out.append((off, off + len(new)))
    if any(r['en'] for r in prefs):
        if len(prefs) != NPREF or not all(r['en'] for r in prefs):
            raise ValueError('code.tsv: translate all %d prefectures or none' % NPREF)
        order = [int(_ptr(rom, PREF_TABLE + 4 * i)) for i in range(NPREF)]
        by_addr = {int(r['id'], 16): r['en'] for r in prefs}
        font_rows = vwf._read_font_txt()
        imgs = [column(font_rows, by_addr[a]) for a in order]
        gfx = b''.join(column_tiles(img) for img in imgs) + bytes(0x200)   # + a blank column (index >= 47)
        ncell = bytes(cells_used(img) for img in imgs) + b'\0'
        code = vwf.assemble(PREF_ASM % {'npref': NPREF, 'colbytes': CELLS * 0x80, 'gfx': 0x08000000 + PREF_GFX,
                                        'ncell': 0x08000000 + PREF_NCELL}, 0x08000000 + PREF_HOOK)
        if len(code) > PREF_NCELL - PREF_HOOK:
            raise ValueError('prefecture hook is %d bytes' % len(code))
        end = PREF_GFX + len(gfx)
        if any(b != 0xFF for b in rom[PREF_HOOK:end]):
            raise ValueError('prefecture area %X-%X is not free' % (PREF_HOOK, end))
        rom[PREF_HOOK:PREF_HOOK + len(code)] = code
        rom[PREF_NCELL:PREF_NCELL + len(ncell)] = ncell
        rom[PREF_GFX:end] = gfx
        out.append((PREF_HOOK, end))
        if bytes(rom[PREF_FN:PREF_FN + 8]) != PREF_ORIG:
            raise ValueError('prefecture picker at %06X is not the original' % PREF_FN)
        rom[PREF_FN:PREF_FN + 8] = _thumb('ldr r3, [pc, #0]\nbx r3', PREF_FN) + struct.pack('<I', 0x08000000 + PREF_HOOK)
        out.append((PREF_FN, PREF_FN + 8))
    return out


def preview(out):
    from PIL import Image
    import extract
    rs = sorted((r for r in extract.load().values() if r['kind'] == 'pref'), key=lambda r: int(r['id'], 16))
    d = (ROOT / 'rom' / 'base.gba').read_bytes()
    order = {int(_ptr(d, PREF_TABLE + 4 * i)): i for i in range(NPREF)}
    rs.sort(key=lambda r: order[int(r['id'], 16)])
    font_rows = __import__('vwf')._read_font_txt()
    im = Image.new('RGB', (NPREF * 18, CELLS * 16), (60, 20, 30))
    pal = {0xF: (255, 255, 255), 0xD: (40, 40, 90)}
    for i, r in enumerate(rs):
        img = column(font_rows, r['en'] or 'x')
        for y, row in enumerate(img):
            for x, v in enumerate(row):
                if v:
                    im.putpixel((18 * i + x, y), pal[v])
    im.resize((im.width * 2, im.height * 2), Image.NEAREST).save(out)


if __name__ == '__main__':
    if sys.argv[1:2] == ['--preview']:
        preview(sys.argv[2])
    else:
        print(__doc__)
