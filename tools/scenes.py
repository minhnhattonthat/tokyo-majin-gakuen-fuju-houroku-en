"""scenes.py: story scene codec (tables A/B, format in docs/re/text.md).

    python -X utf8 tools/scenes.py [ROM]     # parse every scene, re-serialize, report byte-identical or not

A scene is `u16 n`, `n` u16 label offsets (relative to the body start, label 0 = 0), then the body: a stream of
opcodes (byte op + byte arg, fixed lengths in OP_LEN), text ops 0x00 (`00 xx` + Shift-JIS, NUL, pad to even) and
0x0F (`0F nn` + nn choice lines joined by `rt`, ending in `wc`, pad to even), and 0xFF (`FF FF`, stop). Labels are
referenced from opcodes by index (`09 nn` goto), never by byte offset, so re-serializing only recomputes the header.
Opcode table: 0x08D6E44C (24 entries x 12 bytes: init, exec, skip handler), interpreter 0x0803F424.
"""
import struct
import sys
from dataclasses import dataclass, field

TABLE_B = 0xD82078          # 40 chapter scenes (u32 0x08xxxxxx), literal at 0x5E2F0
TABLE_A = 0xD8211C          # 130 event scenes (13 groups x 10), literal at 0x5E378
N_B, N_A = 40, 130
REGION = (0xD82324, 0xE2B97A)   # every scene, back to back; 0xE2B97A-0xE2B97C is 00 00 padding before LZ77 data

# total length in bytes of each fixed-size opcode (op byte included); 0x00 / 0x0F / 0xFF are handled apart
OP_LEN = {0x01: 4, 0x02: 2, 0x03: 4, 0x04: 2, 0x05: 4, 0x06: 4, 0x07: 6, 0x08: 2, 0x09: 2, 0x0A: 2, 0x0B: 4,
          0x0C: 4, 0x0D: 2, 0x0E: 2, 0x10: 4, 0x11: 4, 0x12: 4, 0x13: 2, 0x14: 2, 0x15: 2, 0x16: 2, 0x17: 2}
OP_TEXT, OP_CHOICE, OP_END = 0x00, 0x0F, 0xFF


@dataclass
class Tok:
    """One opcode. kind 'op' (raw = all bytes), 'text' (raw = 2-byte head, text = bytes before the NUL) or
    'choice' (raw = 2-byte head, text = bytes up to and including the closing 'wc')."""
    kind: str
    raw: bytes
    text: bytes = b''

    def encode(self):
        if self.kind == 'op':
            return self.raw
        b = self.raw + self.text + (b'\0' if self.kind == 'text' else b'')
        return b + b'\0' * (len(b) & 1)


@dataclass
class Scene:
    addr: int                     # original ROM offset (for ids and reports)
    labels: list                  # token index of each label
    toks: list = field(default_factory=list)

    def encode(self):
        body, offs, pos = [], [], []
        o = 0
        for t in self.toks:
            pos.append(o)
            b = t.encode()
            body.append(b)
            o += len(b)
        offs = [pos[i] for i in self.labels]
        if o > 0xFFFF:
            raise ValueError('scene %x body is %d bytes; label offsets are u16' % (self.addr, o))
        return struct.pack('<H%dH' % len(offs), len(offs), *offs) + b''.join(body)


def text_end(d, j):
    """index just past the NUL of a scene string starting at j. 01 00 / 02 00 are inline name variables."""
    while True:
        b = d[j]
        if b == 0:
            return j + 1
        if b in (1, 2) and d[j + 1] == 0:
            j += 2
        elif 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC:
            j += 2
        else:
            j += 1


def parse(d, addr, end):
    """parse the scene at addr, ending at end (the next scene or the region end) or earlier at zero fill: every
    scene ends with FF FF and no scene has an empty line (00 00 00 00), so FF FF + 00 00 00 00 is a packer's tail"""
    n = struct.unpack_from('<H', d, addr)[0]
    offs = struct.unpack_from('<%dH' % n, d, addr + 2)
    base = addr + 2 + 2 * n
    toks, starts = [], {}
    i = base
    while i < end:
        starts[i - base] = len(toks)
        op = d[i]
        if op == OP_TEXT:
            j = text_end(d, i + 2)
            t = Tok('text', d[i:i + 2], d[i + 2:j - 1])
        elif op == OP_CHOICE:
            j = d.index(b'wc', i + 2) + 2
            t = Tok('choice', d[i:i + 2], d[i + 2:j])
        elif op == OP_END:
            j = i + 2
            t = Tok('op', d[i:j])
        elif op in OP_LEN:
            j = i + OP_LEN[op]
            t = Tok('op', d[i:j])
        else:
            raise ValueError('scene %x: unknown op %02x at %x' % (addr, op, i))
        j += j & 1 if t.kind != 'op' else 0
        toks.append(t)
        i = j
        if op == OP_END and d[i:i + 4] == b'\0\0\0\0':
            break
    if i > end:
        raise ValueError('scene %x: ran to %x, expected end %x' % (addr, i, end))
    try:
        labels = [starts[o] for o in offs]
    except KeyError as e:
        raise ValueError('scene %x: label offset %s is not on an opcode' % (addr, e))
    return Scene(addr, labels, toks)


def table(d):
    """(B pointers, A pointers) as ROM offsets"""
    b = [struct.unpack_from('<I', d, TABLE_B + 4 * i)[0] - 0x08000000 for i in range(N_B)]
    a = [struct.unpack_from('<I', d, TABLE_A + 4 * i)[0] - 0x08000000 for i in range(N_A)]
    return b, a


def parse_all(d, regions=(REGION,)):
    """every scene, in table order of their addresses; a scene ends at the next scene or its region's end"""
    b, a = table(d)
    addrs = sorted(set(a + b))
    assert addrs[0] == REGION[0], hex(addrs[0])
    out = []
    for k, s in enumerate(addrs):
        reg_end = min((hi for lo, hi in regions if lo <= s < hi), default=len(d))
        nxt = addrs[k + 1] if k + 1 < len(addrs) else len(d)
        out.append(parse(d, s, min(nxt, reg_end)))
    return out


def pack(rom, scenes, regions=(REGION,)):
    """write scenes in order into regions (each filled before the next; bytearray rom, in place), zero-fill each
    region's tail, and repoint tables A/B. Scenes keep 2-byte alignment (the loader reads u16s). Raises if they
    don't fit. Returns the end of the used part of the last region written."""
    old_b, old_a = table(rom)
    where = {}
    regs = list(regions)
    r = 0
    o = regs[0][0]
    for sc in scenes:
        blob = sc.encode()
        o += o & 1
        while o + len(blob) > regs[r][1]:
            rom[o:regs[r][1]] = b'\0' * (regs[r][1] - o)
            r += 1
            if r == len(regs):
                raise ValueError('scenes overflow the regions at scene %x' % sc.addr)
            o = regs[r][0] + (regs[r][0] & 1)
        rom[o:o + len(blob)] = blob
        where[sc.addr] = o
        o += len(blob)
    rom[o:regs[r][1]] = b'\0' * (regs[r][1] - o)
    for base, olds in ((TABLE_B, old_b), (TABLE_A, old_a)):
        for i, s in enumerate(olds):
            struct.pack_into('<I', rom, base + 4 * i, 0x08000000 + where[s])
    return o


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'rom/base.gba'
    d = open(path, 'rb').read()
    scs = parse_all(d)
    r = bytearray(d)
    end = pack(r, scs)
    big = max(scs, key=lambda s: len(s.encode()))
    print('scenes %d, texts %d, choices %d, region end %x, largest %x (%d bytes)' % (
        len(scs), sum(t.kind == 'text' for s in scs for t in s.toks),
        sum(t.kind == 'choice' for s in scs for t in s.toks), end, big.addr, len(big.encode())))
    print('identical' if bytes(r) == d else 'DIFFERENT')
    sys.exit(0 if bytes(r) == d else 1)
