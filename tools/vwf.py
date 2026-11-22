"""vwf.py: the English text engine. A variable-width font hook in the game's per-cell glyph routine, and the MTE
encoder that feeds it.

    python -X utf8 tools/vwf.py --selftest            # font, encoder and hook checks (also run by tests/)
    python -X utf8 tools/vwf.py --sample "Text" OUT.png  # render a line as the hook draws it (zoomed)

The game draws every text unit (u16: a Shift-JIS character or a 2-letter control code) with 0x08003B84: one 16x16
cell = 4 tiles (TL TR BL BR, 0x80 bytes, 4bpp) at r1, 4 map entries at r2 (row stride 0x40), tile index [sp]. The
caller moves one cell right per unit (docs/re/text.md, Font). English goes in as units whose first byte is in LEADS
(Shift-JIS lead bytes and half-width-kana bytes the game never uses). Each such unit is a code for a chunk of 1-4
characters (table MTE, built per build from all English text). The hook draws the chunk at a pixel cursor that runs
across the cells of a strip (consecutive calls whose cell and map entry are each one step after the previous), so
the letters pack with variable width while every printer keeps its one-cell-per-unit loop. The encoder keeps the
ink of each strip inside the cells already handed out: after unit k the drawn extent is <= 16*k pixels. A strip
starts over after any non-VWF unit (Japanese glyph, icon, number code) and at every line break.

Printer B (unit routine 0x0800455C: yes/no prompts and other sprite text) draws each unit as its own 16x16 sprite
(cell at r1, x at [sp+4] +16 a unit, y at [sp+0x28]) and decodes Shift-JIS itself, so it gets a second entry,
hookb: its Shift-JIS branch (B_FN) jumps there; VWF units go through the same draw core with an odd fake map
pointer (x/4 | 1: one step of 4 per unit keeps the strip, the odd bit skips the map writes) and return to the
sprite placement; other codes return to the original path.

ROM layout (free 0xFF space, docs/re/text.md Free space): hook code at HOOK, then ADV (256 advances), FONT (256
glyphs x 16 rows x 2 words of 4bpp, pixel 0 in the low nibble) and MTE (NCODES u32, chunk chars, low byte first).
RAM: STATE, 16 bytes in EWRAM no mode touches (zero in 12 mode dumps, tools/debug/ramdump_at.lua).
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT_TXT = ROOT / 'fonts' / 'vwf.txt'

GLYPH_FN = 0x003B84            # per-cell glyph routine (Thumb), patched with a jump to HOOK
GLYPH_RESUME = 0x08003B91      # its 4th instruction (Thumb bit set), where the original path continues
B_FN = 0x00497C                # printer B (sprite text, unit routine 0x0800455C): its Shift-JIS branch, patched
B_ORIG = bytes.fromhex('0248844204d1032059e00000')   # ldr r0,=0x8140; cmp r4,r0; bne; movs r0,#3; b 0x8004A3A; pad
B_RET3 = 0x08004A3B            # (Thumb) return r0: full-width space
B_KANJI = 0x0800498D           # (Thumb) the original glyph lookup for other Shift-JIS codes
B_OBJ = 0x08004A2D             # (Thumb) after the glyph copy: place the 16x16 sprite at x [sp+4], y [sp+0x28]
C_FN = 0x051DB8                # printer C (sprite text, one unit per call: 0x080519A0, deck menu's deck name): its
C_ORIG = bytes.fromhex('0248834204d1032054e00000')   # Shift-JIS branch, same shape as B (unit in r3, string r4)
C_RET3 = 0x08051E6D            # (Thumb) return r0 (3 = full-width space)
C_KANJI = 0x08051DC9           # (Thumb) the original glyph lookup for other Shift-JIS codes
C_RET = 0x08051E6B             # (Thumb) after the glyph copy into OBJ VRAM 0x06010000 + sb: return r7 (0)
HOOK = 0xF00000                # ROM offset of the hook code and tables
STATE = 0x0203A000             # last cell, last map entry, strip base, pixel x
LEADS = list(range(0xA0, 0xE0)) + list(range(0xF0, 0xFA))
NCODES = len(LEADS) * 255      # trail byte 01-FF (never 00: the game ends strings at a zero u16)
PAL = 0xC000                   # palette 12, as the original sets for Shift-JIS glyphs
SPACE_ADV = 4
FROM_ROM = '【】「」『』'        # brackets cropped from the game's own font (speaker tags, quotes)
EXTRA = '…—“”‘’♪é' + FROM_ROM    # non-ASCII characters, char bytes 0x80 + index
CHAR_BYTE = {chr(c): c for c in range(0x20, 0x7F) if chr(c) not in '\\^`{|}'}   # {} [] are script notation
CHAR_BYTE.update({ch: 0x80 + i for i, ch in enumerate(EXTRA)})
NORMALIZE = {'　': ' ', '！': '!', '？': '?', '～': '~', '・': '·'}

_TOKEN = re.compile(r'\{([^{}]+)\}|\[([0-9A-F]{2})\]')


# ---------------------------------------------------------------- font

def rom_glyph(rom, code):
    """16x16 nibble rows of Shift-JIS code from the game font (lookup as 0x080040EE does; codes <= 0x9872)"""
    thr = [struct.unpack_from('<H', rom, 0xD7A5E6 + 2 * i)[0] for i in range(22)]
    banks = [struct.unpack_from('<I', rom, 0xD7DCC0 + 4 * i)[0] - 0x08000000 for i in range(22)]
    k = 1
    while k <= 0x15 and thr[k] <= code:
        k += 1
    idx = (code - (thr[k - 1] & 0xFF)) & 0xFF
    base = banks[k - 1] + (idx >> 3) * 0x400 + (idx & 7) * 0x40
    px = [[0] * 16 for _ in range(16)]
    for half in (0, 1):
        for tx in (0, 1):
            for ty in range(8):
                t = base + half * 0x200 + tx * 0x20 + ty * 4
                for i, b in enumerate(rom[t:t + 4]):
                    px[half * 8 + ty][tx * 8 + 2 * i] = b & 15
                    px[half * 8 + ty][tx * 8 + 2 * i + 1] = b >> 4
    return px


def _read_font_txt(path=FONT_TXT):
    glyphs, cur, rows = {}, None, []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.startswith('# ') or not line.strip():   # glyph rows are only '#' and '.', never '# '
            continue
        if line.startswith('= '):
            if cur is not None:
                glyphs[cur] = rows
            name = line[2:]
            cur = chr(int(name[2:], 16)) if name.startswith('U+') else name
            rows = []
        else:
            rows.append(line)
    if cur is not None:
        glyphs[cur] = rows
    for ch, rows in glyphs.items():
        if len(rows) != 11 or len({len(r) for r in rows}) != 1:
            raise ValueError('font glyph %r: need 11 rows of one width, got %s' % (ch, [len(r) for r in rows]))
    return glyphs


def load_font(rom):
    """{char: (px rows 16x16 nibbles, ink width incl. shadow, advance)}"""
    out = {' ': ([[0] * 16 for _ in range(16)], 0, SPACE_ADV)}
    for ch, rows in _read_font_txt().items():
        w = len(rows[0])
        ink = [[0] * 16 for _ in range(16)]
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c == '#':
                    ink[y + 4][x] = 1
        px = [[0xF if ink[y][x] else 0 for x in range(16)] for y in range(16)]
        for y in range(16):
            for x in range(16):
                if not ink[y][x] and ((x and ink[y][x - 1]) or (y and ink[y - 1][x]) or (x and y and ink[y - 1][x - 1])):
                    px[y][x] = 0xD
        out[ch] = (px, w + 1, w + 2)
    for ch in FROM_ROM:
        g = rom_glyph(rom, int.from_bytes(ch.encode('cp932'), 'big'))
        cols = [x for x in range(16) if any(g[y][x] for y in range(16))]
        x0, x1 = cols[0], cols[-1]
        px = [[g[y][x + x0] if x + x0 <= x1 else 0 for x in range(16)] for y in range(16)]
        out[ch] = (px, x1 - x0 + 1, x1 - x0 + 2)
    missing = set(CHAR_BYTE) - set(out)
    if missing:
        raise ValueError('font lacks %s' % ''.join(sorted(missing)))
    return out


def font_tables(font):
    """(ADV 256 bytes, FONT 256*128 bytes) indexed by char byte"""
    adv = bytearray(256)
    fnt = bytearray(256 * 128)
    for ch, (px, w, a) in font.items():
        c = CHAR_BYTE[ch]
        adv[c] = a
        for y in range(16):
            lo = sum(px[y][x] << (4 * x) for x in range(8))
            hi = sum(px[y][x + 8] << (4 * x) for x in range(8))
            struct.pack_into('<II', fnt, c * 128 + 8 * y, lo, hi)
    return bytes(adv), bytes(fnt)


# ---------------------------------------------------------------- text

def normalize(s):
    return ''.join(NORMALIZE.get(ch, ch) for ch in s)


def split(s):
    """script text -> list of ('lit', str) / ('raw', bytes): codes {..} and [XX] become raw bytes"""
    import textcodec
    out, pos = [], 0
    for m in _TOKEN.finditer(s):
        if m.start() > pos:
            out.append(('lit', normalize(s[pos:m.start()])))
        out.append(('raw', textcodec.encode(m.group(0))))
        pos = m.end()
    if pos < len(s):
        out.append(('lit', normalize(s[pos:])))
    return out


def has_vwf(s):
    """True if script text s needs the VWF encoder (any ASCII letter outside {codes} / [XX])"""
    return any(k == 'lit' and re.search(r'[A-Za-z0-9]', v) for k, v in split(s))


def ext(font, s):
    """[drawn right edge (ink + shadow) after each prefix of literal run s] (index 0 = empty prefix)"""
    out, x, e = [0], 0, 0
    for ch in s:
        _, w, a = font[ch]
        if w:
            e = max(e, x + w)
        x += a
        out.append(e)
    return out


class Encoder:
    """Build the chunk dictionary from every English text, then encode texts to unit bytes."""

    def __init__(self, font, texts):
        self.font = font
        runs = [v for t in texts for k, v in split(t) if k == 'lit']
        for r in runs:
            bad = set(r) - set(CHAR_BYTE)
            if bad:
                raise ValueError('no glyph for %r in %r' % (''.join(sorted(bad)), r))
        singles = sorted(CHAR_BYTE)          # every character keeps a code, so any later text still encodes
        count = {}
        for r in runs:
            for n in (2, 3, 4):
                for i in range(len(r) - n + 1):
                    g = r[i:i + n]
                    count[g] = count.get(g, 0) + 1
        ranked = sorted(count, key=lambda g: (-count[g] * (len(g) - 1), g))
        self.dict = set(singles) | set(ranked[:NCODES - len(singles)])
        self._cache = {}
        used = set(singles)
        for r in sorted(set(runs)):
            used.update(self.chunks(r))
        self.codes = {g: i for i, g in enumerate(sorted(used))}

    def ext(self, s):
        return ext(self.font, s)

    def width(self, s):
        """pixel width of a literal run as drawn (right edge of the last ink)"""
        return ext(self.font, normalize(s))[-1]

    def chunks(self, r):
        """split run r into the fewest chunks (1-4 chars, in the dictionary) with ext <= 16 * chunks so far"""
        if r in self._cache:
            return self._cache[r]
        e = self.ext(r)
        m = len(r)
        prev = [dict() for _ in range(m + 1)]      # prev[q][k] = p: chunk r[p:q] is unit k
        prev[0][0] = None
        for p in range(m):
            for k in sorted(prev[p]):
                for n in range(1, 5):
                    q = p + n
                    if q > m or r[p:q] not in self.dict or e[q] > 16 * (k + 1) or (k + 1) in prev[q]:
                        continue
                    prev[q][k + 1] = p
        k = min(prev[m])
        out, q = [], m
        while q:
            p = prev[q][k]
            out.append(r[p:q])
            q, k = p, k - 1
        self._cache[r] = out[::-1]
        return self._cache[r]

    def unit(self, chunk):
        i = self.codes.get(chunk)
        if i is None:                        # a text encoded after the dictionary was built (marker re-fit)
            i = self.codes[chunk] = len(self.codes)
            if i >= NCODES:
                raise ValueError('out of MTE codes (%d)' % NCODES)
        return bytes([LEADS[i // 255], i % 255 + 1])

    def encode(self, s):
        out = bytearray()
        for k, v in split(s):
            if k == 'raw':
                out += v
            else:
                for c in self.chunks(v):
                    out += self.unit(c)
        if len(out) & 1:
            raise ValueError('odd byte length for %r: every unit is 2 bytes' % s)
        return bytes(out)

    def encode_units(self, s, n, margin=0):
        """plain text s (no codes) as exactly n units, for printers that draw a fixed unit count (tools/codestr.py):
        the fewest chunks, longer chunks split while short of n, then the empty chunk (draws and advances nothing)
        as padding. margin: px the ink must leave free in the last unit."""
        s = normalize(s)
        ch = list(self.chunks(s))
        while len(ch) < n and any(len(c) > 1 for c in ch):
            i = max(range(len(ch)), key=lambda j: len(ch[j]))
            ch[i:i + 1] = [ch[i][0], ch[i][1:]]
        if len(ch) > n or self.ext(s)[-1] > 16 * n - margin:
            raise ValueError('%r needs %d units / %d px, the printer draws %d units' % (
                s, len(ch), self.ext(s)[-1], n))
        return b''.join(self.unit(c) for c in ch + [''] * (n - len(ch)))

    def mte_table(self):
        t = bytearray(4 * NCODES)
        for g, i in self.codes.items():
            t[4 * i:4 * i + len(g)] = bytes(CHAR_BYTE[ch] for ch in g)
        return bytes(t)


# ---------------------------------------------------------------- hook

HOOK_ASM = '''
hook:
    ldrb  r12, [r0]
    sub   r12, r12, #0xA0
    cmp   r12, #0x40
    blo   vwf
    sub   r12, r12, #0x50
    cmp   r12, #10
    addlo r12, r12, #0x40
    blo   vwf
    mov   r7, r10
    mov   r6, r9
    mov   r5, r8
    stmfd sp!, {r5-r7}
    sub   sp, sp, #0x18
    ldr   r4, lit_resume
    bx    r4
vwf:
    ldrb  r4, [r0, #1]
    rsb   r5, r12, r12, lsl #8
    add   r5, r5, r4
    sub   r5, r5, #1
    ldr   r6, lit_mte
    ldr   r6, [r6, r5, lsl #2]
    ldr   r7, [sp, #20]
    stmfd sp!, {r2, r7, r8-r11}
    ldr   r8, lit_state
    ldmia r8, {r9, r10}
    add   r9, r9, #0x80
    cmp   r9, r1
    addeq r10, r10, #4
    cmpeq r10, r2
    movne r9, #0
    strne r1, [r8, #8]
    strne r9, [r8, #12]
    str   r1, [r8]
    str   r2, [r8, #4]
    mov   r9, #0
    mov   r10, #0
    mov   r11, #0
    mov   r12, #0
    stmia r1!, {r9-r12}
    stmia r1!, {r9-r12}
    stmia r1!, {r9-r12}
    stmia r1!, {r9-r12}
    stmia r1!, {r9-r12}
    stmia r1!, {r9-r12}
    stmia r1!, {r9-r12}
    stmia r1!, {r9-r12}
    ldr   r10, [r8, #12]
charloop:
    ands  r11, r6, #0xFF
    beq   done
    ldr   r9, [r8, #8]
    ldr   r0, lit_font
    add   r0, r0, r11, lsl #7
    and   r3, r10, #7
    mov   r3, r3, lsl #2
    mov   r1, r10, lsr #3
    mov   r2, r1, lsr #1
    add   r4, r9, r2, lsl #7
    tst   r1, #1
    addne r4, r4, #0x20
    addeq r5, r4, #0x20
    addne r5, r4, #0x60
    add   lr, r4, #0x80
    rsb   r7, r3, #32
    mov   r12, #0
rowloop:
    ldmia r0!, {r1, r2}
    orrs  r9, r1, r2
    beq   nextrow
    movs  r11, r1, lsl r3
    ldrne r9, [r4, r12]
    orrne r9, r9, r11
    strne r9, [r4, r12]
    mov   r11, r1, lsr r7
    orrs  r11, r11, r2, lsl r3
    ldrne r9, [r5, r12]
    orrne r9, r9, r11
    strne r9, [r5, r12]
    movs  r11, r2, lsr r7
    ldrne r9, [lr, r12]
    orrne r9, r9, r11
    strne r9, [lr, r12]
nextrow:
    add   r12, r12, #4
    cmp   r12, #0x20
    moveq r12, #0x40
    cmp   r12, #0x60
    blo   rowloop
    and   r11, r6, #0xFF
    ldr   r9, lit_adv
    ldrb  r9, [r9, r11]
    add   r10, r10, r9
    mov   r6, r6, lsr #8
    b     charloop
done:
    str   r10, [r8, #12]
    ldmfd sp!, {r2, r7, r8-r11}
    tst   r2, #1
    bne   nomap
    mov   r7, r7, lsl #16
    mov   r7, r7, lsr #16
    orr   r7, r7, #0xC000
    strh  r7, [r2]
    add   r7, r7, #1
    strh  r7, [r2, #2]
    add   r7, r7, #1
    strh  r7, [r2, #0x40]
    add   r7, r7, #1
    strh  r7, [r2, #0x42]
nomap:
    ldmfd sp!, {r4-r7}
    ldmfd sp!, {r1}
    mov   r0, #0
    bx    r1
hookb:
    mov   r12, r4, lsr #8
    sub   r12, r12, #0xA0
    cmp   r12, #0x40
    blo   bvwf
    sub   r12, r12, #0x50
    cmp   r12, #10
    blo   bvwf
    ldr   r0, lit_sp
    cmp   r4, r0
    moveq r0, #3
    ldreq r12, lit_bret
    ldrne r12, lit_bjp
    bx    r12
bvwf:
    ldr   r2, [sp, #4]
    mov   r2, r2, lsr #2
    orr   r2, r2, #1
    ldr   r3, lit_bobj
    stmfd sp!, {r3}
    stmfd sp!, {r4-r7}
    mov   r0, r5
    mov   r1, r9
    b     hook
hookc:
    mov   r12, r3, lsr #8
    sub   r12, r12, #0xA0
    cmp   r12, #0x40
    blo   cvwf
    sub   r12, r12, #0x50
    cmp   r12, #10
    blo   cvwf
    ldr   r0, lit_sp
    cmp   r3, r0
    moveq r0, #3
    ldreq r12, lit_cret3
    ldrne r12, lit_cjp
    bx    r12
cvwf:
    ldr   r1, lit_cvram
    add   r1, r1, r9
    mov   r2, r1, lsr #5
    orr   r2, r2, #1
    ldr   r3, lit_cret
    stmfd sp!, {r3}
    stmfd sp!, {r4-r7}
    mov   r0, r4
    b     hook
lit_resume: .word @resume
lit_sp:     .word 0x8140
lit_bret:   .word @bret
lit_bjp:    .word @bjp
lit_bobj:   .word @bobj
lit_cret3:  .word @cret3
lit_cjp:    .word @cjp
lit_cret:   .word @cret
lit_cvram:  .word 0x06010000
lit_mte:    .word @mte
lit_state:  .word @state
lit_font:   .word @font
lit_adv:    .word @adv
'''


def assemble(asm, addr, thumb=False):
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_ARM, KS_MODE_THUMB
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB if thumb else KS_MODE_ARM).asm(asm, addr)
    return bytes(enc)


def layout(code_len):
    """ROM offsets of (ADV, FONT, MTE) after code_len bytes of hook code"""
    adv = HOOK + ((code_len + 0xFF) & ~0xFF)
    fnt = adv + 0x100
    mte = fnt + 256 * 128
    return adv, fnt, mte


def hook_code():
    # assemble twice: the first pass sizes the code, the second fills in the table addresses
    def asm(adv, fnt, mte):
        src = HOOK_ASM
        for k, v in (('resume', GLYPH_RESUME), ('mte', 0x08000000 + mte), ('state', STATE),
                     ('font', 0x08000000 + fnt), ('adv', 0x08000000 + adv), ('bret', B_RET3),
                     ('bjp', B_KANJI), ('bobj', B_OBJ), ('cret3', C_RET3), ('cjp', C_KANJI),
                     ('cret', C_RET)):
            src = src.replace('@' + k, '0x%08X' % v)
        return assemble(src, 0x08000000 + HOOK)
    code = asm(0, 0, 0)
    adv, fnt, mte = layout(len(code))
    return asm(adv, fnt, mte), (adv, fnt, mte)


def hookb_addr(label='hookb'):
    """address of the printer-B (or another label's) entry: ARM code is 4 bytes an instruction and the literal words
    come last, so the code before the label (its literal labels stubbed after it) has the label's offset as length"""
    pre = HOOK_ASM[:HOOK_ASM.index(label + ':')]
    lits = sorted(set(re.findall(r'\blit_\w+', pre)))
    code = assemble(pre + ''.join('%s: .word 0\n' % name for name in lits), 0x08000000 + HOOK)
    return 0x08000000 + HOOK + len(code) - 4 * len(lits)


STUB_ORIG = bytes.fromhex('f0b5 5746 4e46 4546 e0b4'.replace(' ', ''))   # push {r4-r7,lr}; mov r7,sl; .. push {r5-r7}


def install(rom, enc, font):
    """patch the glyph routine and write hook, font and MTE table into bytearray rom; returns the used end"""
    if bytes(rom[GLYPH_FN:GLYPH_FN + 10]) != STUB_ORIG:
        raise ValueError('glyph routine at %x is not the original' % GLYPH_FN)
    code, (adv_at, fnt_at, mte_at) = hook_code()
    adv, fnt = font_tables(font)
    mte = enc.mte_table()
    end = mte_at + len(mte)
    if any(b != 0xFF for b in rom[HOOK:end]):
        raise ValueError('VWF area %x-%x is not free (0xFF)' % (HOOK, end))
    rom[HOOK:HOOK + len(code)] = code
    rom[adv_at:adv_at + 256] = adv
    rom[fnt_at:fnt_at + len(fnt)] = fnt
    rom[mte_at:end] = mte
    stub = assemble('push {r4, r5, r6, r7, lr}\nldr r4, [pc, #4]\nbx r4\nnop', 0x08000000 + GLYPH_FN, thumb=True)
    rom[GLYPH_FN:GLYPH_FN + 8] = stub
    rom[GLYPH_FN + 8:GLYPH_FN + 12] = struct.pack('<I', 0x08000000 + HOOK)
    if bytes(rom[B_FN:B_FN + 12]) != B_ORIG:
        raise ValueError('printer B at %x is not the original' % B_FN)
    stub = assemble('ldr r0, [pc, #4]\nbx r0\nnop\nnop', 0x08000000 + B_FN, thumb=True)
    rom[B_FN:B_FN + 8] = stub
    rom[B_FN + 8:B_FN + 12] = struct.pack('<I', hookb_addr())
    if bytes(rom[C_FN:C_FN + 12]) != C_ORIG:
        raise ValueError('printer C at %x is not the original' % C_FN)
    stub = assemble('ldr r0, [pc, #4]\nbx r0\nnop\nnop', 0x08000000 + C_FN, thumb=True)
    rom[C_FN:C_FN + 8] = stub
    rom[C_FN + 8:C_FN + 12] = struct.pack('<I', hookb_addr('hookc'))
    return end


# ---------------------------------------------------------------- model of the hook (selftest, samples)

def draw(enc, units, cells=None):
    """draw unit bytes the way the hook does, one strip; returns a 16 x (16*cells) nibble image"""
    n = len(units) // 2
    cells = cells or n
    img = [[0] * (16 * cells) for _ in range(16)]
    x = 0
    inv = {i: g for g, i in enc.codes.items()}
    for k in range(n):
        lead, trail = units[2 * k], units[2 * k + 1]
        i = LEADS.index(lead) * 255 + trail - 1
        for ch in inv[i]:
            px, w, a = enc.font[ch]
            for y in range(16):
                for xx in range(16):
                    if px[y][xx]:
                        X = x + xx
                        if X >= 16 * (k + 1) and px[y][xx]:
                            raise AssertionError('unit %d draws at x=%d, past its cell' % (k, X))
                        img[y][X] |= px[y][xx]
            x += a
    return img


def sample_png(enc, text, out, zoom=3):
    from PIL import Image
    units = enc.encode(text)
    img = draw(enc, units)
    pal = {0: (0, 0, 32), 0xF: (255, 255, 255), 0xD: (90, 90, 120)}
    im = Image.new('RGB', (len(img[0]), 16))
    for y, row in enumerate(img):
        for x, v in enumerate(row):
            im.putpixel((x, y), pal.get(v, (255, 0, 0)))
    im.resize((im.width * zoom, im.height * zoom), Image.NEAREST).save(out)
    return len(units) // 2, enc.width(text)


def selftest():
    sys.path.insert(0, str(ROOT / 'tools'))
    rom = (ROOT / 'rom' / 'base.gba').read_bytes()
    font = load_font(rom)
    for ch, (px, w, a) in font.items():
        assert w <= 15 and a <= 16, ch
    text = ('The quick brown fox jumps over the lazy dog. PACK MY BOX WITH FIVE DOZEN LIQUOR JUGS! 0123456789 '
            '"Hi," she said… “OK”? (a-b) [x] 50% & #1: @me; ‘yes’ — ♪ café '
            '【Tatsuma】 「yo」 『we』')
    enc = Encoder(font, [text, 'Hello{rt}world{name1}!'])
    u = enc.encode(text)
    draw(enc, u)
    assert all(b != 0 for b in u)
    assert all(u[i] in LEADS for i in range(0, len(u), 2))
    v = enc.encode('Hello{rt}world{name1}!')
    assert v[4:6] == b'rt' or b'rt' in v
    code, lay = hook_code()
    assert len(code) < 0x400 and lay[0] > HOOK
    print('vwf selftest ok: %d glyphs, %d chars -> %d units (%.2f chars/unit), hook %d bytes' % (
        len(font), len(text), len(u) // 2, len(text) / (len(u) / 2), len(code)))


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT / 'tools'))
    if '--selftest' in sys.argv:
        selftest()
    elif '--sample' in sys.argv:
        i = sys.argv.index('--sample')
        text, out = sys.argv[i + 1], sys.argv[i + 2]
        font = load_font((ROOT / 'rom' / 'base.gba').read_bytes())
        enc = Encoder(font, [text])
        print('units %d, width %d px' % sample_png(enc, text, out))
    else:
        print(__doc__)
