"""patches.py: small code patches for the English build (not text, not graphics).

    apply(rom) -> [(start, end), ...]   patch bytearray rom in place; returns the written ranges (tests/test_romdiff.py)

Default names (0x0805DF72-0x0805DFCE, New Game): the game clears the surname, given-name and six deck-name buffers
(4 u16 each) and copies the defaults 緋勇 / 龍麻 / 真神 from the pointer table 0xE6163C, two u16 per name (two
Shift-JIS kanji). English names are VWF codes (tools/vwf.py), two to three letters per u16: "Tatsuma" and "Magami"
are three codes, so the copy loops are raised to three u16 (the fourth stays the cleared zero). Every default name
must therefore encode to at most three codes; `check_names` enforces it.
"""
import struct

# (offset, original bytes, new bytes, what)
PATCHES = [
    (0x05DF86, bytes.fromhex('012e'), bytes.fromhex('022e'), 'deck-name default copy: cmp r6, #1 -> #2 (3 u16)'),
    (0x05DFCC, bytes.fromhex('012e'), bytes.fromhex('022e'), 'surname / given-name default copy: cmp r6, #1 -> #2'),
]
NAME_PTRS = (0xE6163C, 0xE61640, 0xE61644)   # surname, given name, deck name (u32 ROM pointers)
NAME_CODES = 3


def check_names(rom):
    """raise if a default name is longer than NAME_CODES u16 codes (it would be cut in the 4-u16 buffers)"""
    for p in NAME_PTRS:
        a = struct.unpack_from('<I', rom, p)[0] - 0x08000000
        units = struct.unpack_from('<4H', rom, a)
        n = units.index(0) if 0 in units else 4
        if n > NAME_CODES:
            raise ValueError('default name at %06X is %d codes; the buffer copy takes %d' % (a, n, NAME_CODES))


def apply(rom, check=True):
    """check=False for the marker build (marker text, not names) and for range listing on the original dump (its
    Shift-JIS names have no terminator inside the 8 bytes)"""
    out = []
    for off, old, new, _ in PATCHES:
        if bytes(rom[off:off + len(old)]) != old:
            raise ValueError('code at %06X is not the original' % off)
        rom[off:off + len(new)] = new
        out.append((off, off + len(new)))
    if check:
        check_names(rom)
    return out
