"""patches.py: small code patches for the English build (not text, not graphics).

    apply(rom) -> [(start, end), ...]   patch bytearray rom in place; returns the written ranges (tests/test_romdiff.py)

Default names (0x0805DF72-0x0805DFCE, New Game): the game clears the surname, given-name and six deck-name buffers
(4 u16 each) and copies the defaults 緋勇 / 龍麻 / 真神 from the pointer table 0xE6163C, two u16 per name (two
Shift-JIS kanji). English names are VWF codes (tools/vwf.py), two to three letters per u16: "Tatsuma" and "Magami"
are three codes, so the copy loops are raised to three u16 (the fourth stays the cleared zero). Every default name
must therefore encode to at most three codes; `check_names` enforces it.
"""
import struct

# Deck-editor tab sheet 0xC67D38 (13 entries x 0x200 = left 32x16 + right 32x16: tabs 0-6, sort keys 7-12), set up
# by 0x080448E8. The game loads each entry's left half (8 OBJ tiles, from tile 494 up) and only two right halves, entry
# 0's (符) for every tab and entry 7's (blank) for every sort key, so all tabs ended in the same 16 px. The two calls
# at TABS_FN are rewritten in place: save the bump allocator (0x03001368), point it at OBJ tile 704 (0x5800 - 0x20;
# tiles 704-767 are free here: the "sorting" popup is fixed at 640-703, another user at 768), load TAB_RIGHTS (written
# by tools/gfx_deck.py: tab k's right half at k * 0x100, k = 0-6, then the blank one) in ONE loader call (the loader
# ring 0x03004E40 holds 16 entries unchecked, so the count must not grow), restore the allocator, and leave
# D = right tile - first left tile in [sp+0x1c] and the blank's tile in [sp+0x20] for the OBJ loop below.
TAB_RIGHTS = 0xFDF000
TABS_FN = 0x044978
TABS_ORIG = bytes.fromhex(
    '23480d9c4444a40024182068d0256d0149460091019105aa0292039751460491002100222b1c10f03bf82068f021090100914a46'
    '01920b9902910c9a039251460491002100222b1c10f02af8')
TABS_NEW = b''.join(struct.pack('<H', h) for h in (
    0x4E0F,          # 978 ldr r6, =0x03001368 (allocator: cur, pal)
    0x6830,          # 97A ldr r0, [r6]
    0x9007,          # 97C str r0, [sp, #0x1c]   save cur
    0x20B0, 0x01C0,  # 97E movs r0, #0xB0; lsls r0, r0, #7
    0x3820,          # 982 subs r0, #0x20         0x57E0 -> first tile (cur + 0x20) >> 5 = 704
    0x6030,          # 984 str r0, [r6]
    0x4650,          # 986 mov r0, sl            (0)
    0x9000, 0x9004,  # 988 str r0, [sp]; str r0, [sp, #0x10]   offset 0, not compressed
    0x2380, 0x011B,  # 98C movs r3, #0x80; lsls r3, r3, #4      0x800 bytes (block size and copy size)
    0x9301,          # 990 str r3, [sp, #4]
    0xA805, 0x9002,  # 992 add r0, sp, #0x14; str r0, [sp, #8]   tile out -> [sp+0x14]
    0x9703,          # 996 str r7, [sp, #0xc]    palette out (none: r1 = 0)
    0x4808,          # 998 ldr r0, =TAB_RIGHTS
    0x2100, 0x2200,  # 99A movs r1, #0; movs r2, #0
    0xF010, 0xF83B,  # 99E bl 0x08054A18          the loader / allocator
    0x9807, 0x6030,  # 9A2 ldr r0, [sp, #0x1c]; str r0, [r6]   restore cur
    0xA805, 0x8800,  # 9A6 add r0, sp, #0x14; ldrh r0, [r0]     R = first right tile
    0x9909,          # 9AA ldr r1, [sp, #0x24]   L = first left tile
    0x1A41,          # 9AC subs r1, r0, r1
    0x9107,          # 9AE str r1, [sp, #0x1c]   D
    0x3038,          # 9B0 adds r0, #0x38         R + 56: the blank right half
    0x9008,          # 9B2 str r0, [sp, #0x20]
    0xE006,          # 9B4 b 0x080449C4
    0x46C0,          # 9B6 (pad)
    0x1368, 0x0300,  # 9B8 .word 0x03001368
)) + struct.pack('<I', 0x08000000 + TAB_RIGHTS) + bytes.fromhex('c046c046')   # 9BC .word TAB_RIGHTS; 9C0 pad
assert len(TABS_NEW) == len(TABS_ORIG) == 0x4C

# (offset, original bytes, new bytes, what)
PATCHES = [
    (0x05DF86, bytes.fromhex('012e'), bytes.fromhex('022e'), 'deck-name default copy: cmp r6, #1 -> #2 (3 u16)'),
    (0x05DFCC, bytes.fromhex('012e'), bytes.fromhex('022e'), 'surname / given-name default copy: cmp r6, #1 -> #2'),
    (TABS_FN, TABS_ORIG, TABS_NEW, 'deck-editor tabs: own right halves (see TABS_FN)'),
    (0x0449F0, bytes.fromhex('05a90b88'), bytes.fromhex('079bdb19'), 'tabs 0-6: right tile = [sp+0x1c] + r7'),
    (0x044A16, bytes.fromhex('0b990b88'), bytes.fromhex('089bc046'), 'sort keys 7-12: right tile = [sp+0x20]'),
    # link-error screen (mode 21, setup 0x0805AA20) copies its screens with fixed sizes (0x08000884 r0 src, r1 dst,
    # r2 bytes): the English needs more tiles (tools/gfx_linkerr.py, room_banners C11C58). VRAM: BG3 chars 0x0000,
    # BG0 chars 0x4000, screens 0xF000 / 0xF800, so both still fit.
    (0x05AAA0, bytes.fromhex('8022'), bytes.fromhex('a422'), 'link-error wallpaper copy 0x2000 -> 0x2900 (328 tiles)'),
    (0x05AAC4, bytes.fromhex('8a22'), bytes.fromhex('9022'), 'link-error overlay copy 0x4500 -> 0x4800 (288 tiles)'),
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
