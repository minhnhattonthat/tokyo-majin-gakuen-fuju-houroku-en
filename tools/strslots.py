"""strslots.py: system strings reached by direct u32 pointers, written back into their own slots.

    python -X utf8 tools/strslots.py [ROM]   # list counts per range, rewrite every slot unchanged, check identity

The system string ranges (docs/re/text.md) mix NUL-terminated Shift-JIS strings with byte tables and graphics, so
a string is only taken where an aligned u32 0x08xxxxxx word points at it, it starts a string (the byte before is
00 or the range start) and it decodes as text. Its slot runs from the pointer target through the NUL and the zero
padding up to the next 4-byte boundary. Strings that don't fit their slot are relocated in phase 7 (pointer sites
must be verified first: graphics bytes can look like pointers), so `write` raises for now.
"""
import struct
import sys
from dataclasses import dataclass

RANGES = [(0xCF1300, 0xCF8000),    # system / menu / card-rule strings
          (0xD16800, 0xD1C000),    # haiku game, sound test, misc
          (0xD63000, 0xD7A000)]    # tutorial scripts, card text, names


@dataclass
class Slot:
    addr: int
    cap: int          # bytes the slot may hold, NUL included
    text: bytes       # without the NUL
    refs: list        # ROM offsets of the u32 words pointing here


def is_text(b):
    """bytes before a NUL look like game text: valid Shift-JIS / ASCII, at least one double-byte char"""
    if len(b) < 2:
        return False
    i, wide = 0, 0
    while i < len(b):
        c = b[i]
        if 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC:
            try:
                b[i:i + 2].decode('cp932')
            except UnicodeDecodeError:
                return False
            wide += 1
            i += 2
        elif 0x20 <= c < 0x7F or c in (0x0A, 0x0D):
            i += 1
        elif c in (1, 2) and i + 1 < len(b) and b[i + 1] == 0:
            i += 2
        else:
            return False
    return wide > 0


def pointer_sites(d):
    """{target offset: [sites]} for every aligned u32 pointing into RANGES"""
    out = {}
    lo = min(a for a, _ in RANGES) | 0x08000000
    hi = max(b for _, b in RANGES) | 0x08000000
    words = struct.unpack('<%dI' % (len(d) // 4), d)
    for k, w in enumerate(words):
        if lo <= w < hi:
            t = w - 0x08000000
            if any(a <= t < b for a, b in RANGES):
                out.setdefault(t, []).append(4 * k)
    return out


def scan(d):
    slots = []
    for t, sites in sorted(pointer_sites(d).items()):
        lo = next(a for a, b in RANGES if a <= t < b)
        if t > lo and d[t - 1] != 0:
            continue
        e = d.index(b'\0', t)
        if not is_text(d[t:e]):
            continue
        end = e + 1
        while end & 3 and d[end] == 0:
            end += 1
        slots.append(Slot(t, end - t, d[t:e], sites))
    # a slot never runs into the next pointer target
    for a, b in zip(slots, slots[1:]):
        if a.addr + a.cap > b.addr:
            a.cap = b.addr - a.addr
    return slots


def write(rom, slot, text):
    """write text (bytes, no NUL) into its slot, zero-filling the rest"""
    if len(text) + 1 > slot.cap:
        raise ValueError('string at %x: %d bytes, slot holds %d (relocation is phase 7)' % (
            slot.addr, len(text) + 1, slot.cap))
    rom[slot.addr:slot.addr + slot.cap] = text + b'\0' * (slot.cap - len(text))


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'rom/base.gba'
    d = open(path, 'rb').read()
    ss = scan(d)
    for a, b in RANGES:
        n = [s for s in ss if a <= s.addr < b]
        print('%06x-%06x: %d strings, %d pointer sites' % (a, b, len(n), sum(len(s.refs) for s in n)))
    r = bytearray(d)
    for s in ss:
        write(r, s, s.text)
    print('identical' if bytes(r) == d else 'DIFFERENT')
    sys.exit(0 if bytes(r) == d else 1)
