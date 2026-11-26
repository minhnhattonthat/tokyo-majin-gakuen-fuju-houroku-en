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
# 0's (符) for every tab and entry 7's (blank) for every sort key, so all tabs ended in the same 16 px. TAB_RIGHTS
# (written by tools/gfx_deck.py: tab k's right half at k * 0x100, k = 0-6, then the blank one) holds them all.
#
# OBJ VRAM on these screens (JP dumps, tools/debug/objtiles.py + dstlog.lua/dstranges.py, work/qa/p8s24): the game's
# bump allocator 0x03001368 fills ~150-639 (13 left halves at 494-597, then the two JP right halves 598-613, then a
# badge ..629); fixed users above it: sort popup 640-703, card view name/text 640-683, sell screen Value= glyphs
# 704-715, a RAM image 768-895, card view art 896-1023. Only 716-767 is never written. A 64-tile block through the
# allocator lands at 598-661 and was overwritten by the popup and the card view (garbled sell-screen tabs); fixed at
# 704 it hit Value=; at 944 the card view art. So the block is split: tabs 0-5 (48 tiles, 0x600 bytes) at the FIXED
# tiles 716-763 (allocator pointed there for that call and restored), tab 6 + blank (16 tiles) through the
# allocator at 598-613, exactly the JP footprint (two loader calls, as in the JP: the loader ring 0x03004E40 holds 16
# entries unchecked, 13 left halves + 2). The two calls at TABS_FN become a trampoline to TAB_HOOK (BL cannot reach
# 0x08FDxxxx), which leaves D = 716 - first left tile in [sp+0x1c] and the blank's tile in [sp+0x20]; the OBJ loop's
# right-tile read at 0x0449F0 calls TAB_RIGHT_TILE: D + left tile for tabs 0-5, the allocated tile for tab 6.
TAB_RIGHTS = 0xFDF000
TAB_HOOK = 0xFDF800            # free 0xFF after TAB_RIGHTS (0x800 bytes)
TAB_FIXED_CUR = 716 * 32 - 0x20    # allocator cur so that its next block starts at tile (cur + 0x20) >> 5 = 716
LOADER = 0x08054A18            # loader / allocator: r0 src, r3 bytes; [sp] offset, [sp+4] size, [sp+8] tile out,
                               # [sp+0xc] palette out, [sp+0x10] compressed flag
TABS_FN = 0x044978
TABS_ORIG = bytes.fromhex(
    '23480d9c4444a40024182068d0256d0149460091019105aa0292039751460491002100222b1c10f03bf82068f021090100914a46'
    '01920b9902910c9a039251460491002100222b1c10f02af8')


COND = {'beq': 0, 'bne': 1, 'bcs': 2, 'bcc': 3}


def thumb(base, items, labels=None):
    """tiny Thumb assembler: items are ints (halfwords), ('label', n), ('ldr', rd, n) (pc-relative literal),
    ('bl', n|addr), ('b', n), ('beq'|'bne'|'bcs'|'bcc', n), ('word', n, value) (4-aligned literal); base = GBA address
    of item 0.
    labels (a dict) receives each label's address."""
    def walk(labels):
        out, pc = [], base
        for it in items:
            if isinstance(it, int):
                out.append(struct.pack('<H', it)); pc += 2
                continue
            op = it[0]
            if op == 'label':
                labels[it[1]] = pc
            elif op == 'word':
                if pc % 4:
                    out.append(struct.pack('<H', 0x46C0)); pc += 2
                labels[it[1]] = pc
                out.append(struct.pack('<I', it[2])); pc += 4
            elif op == 'ldr':
                off = labels.get(it[2], pc + 4) - ((pc + 4) & ~3)
                assert 0 <= off < 1024 and off % 4 == 0 or it[2] not in labels, it
                out.append(struct.pack('<H', 0x4800 | it[1] << 8 | (off >> 2 & 0xFF))); pc += 2
            elif op == 'b' or op in COND:
                off = labels.get(it[1], pc + 4) - (pc + 4)
                assert op == 'b' or -256 <= off < 256 or it[1] not in labels, it
                out.append(struct.pack('<H', (0xE000 | (off >> 1 & 0x7FF)) if op == 'b'
                                       else (0xD000 | COND[op] << 8 | (off >> 1 & 0xFF))))
                pc += 2
            elif op == 'bl':
                to = it[1] if isinstance(it[1], int) else labels.get(it[1], pc + 4)
                off = to - (pc + 4)
                assert -0x400000 <= off < 0x400000, it
                out.append(struct.pack('<HH', 0xF000 | (off >> 12 & 0x7FF), 0xF800 | (off >> 1 & 0x7FF))); pc += 4
        return b''.join(out)
    labels = {} if labels is None else labels
    walk(labels)
    return walk(labels)


def _load(src, size_items):
    """loader call with r0 = src literal, r3 = size (built by size_items), tile out -> [sp+0x14]"""
    return [('ldr', 0, src), *size_items,
            0x2100,          # movs r1, #0
            0x9100, 0x9104,  # str r1, [sp]; str r1, [sp, #0x10]   offset 0, not compressed
            0x9301,          # str r3, [sp, #4]
            0xAA05, 0x9202,  # add r2, sp, #0x14; str r2, [sp, #8]  tile out
            0x3202, 0x9203,  # adds r2, #2; str r2, [sp, #0xc]       palette out (none: r1 = 0)
            0x2200,          # movs r2, #0
            ('ldr', 7, 'loader'),
            ('bl', 'bx_r7')]


_hook_labels, _tabs_labels = {}, {}
TAB_HOOK_CODE = thumb(0x08000000 + TAB_HOOK, [
    # TAB_HOOK: called from TABS_FN with the caller's sp + 0 (r4-r7 are dead there: 0x080449C4 sets them)
    0xB5F0,          # push {r4-r7, lr}
    0xB086,          # sub sp, #0x18           caller's [sp+n] = [sp+0x2C+n]
    ('ldr', 6, 'alloc'),
    0x6834,          # ldr r4, [r6]            saved cur
    ('ldr', 0, 'fixed'),
    0x6030,          # str r0, [r6]            next block at tile 716
    *_load('tabs05', [0x23C0, 0x00DB]),      # movs r3, #0xC0; lsls r3, r3, #3   0x600: tabs 0-5
    0xA805, 0x8805,  # add r0, sp, #0x14; ldrh r5, [r0]     tile of tab 0's right half (716)
    0x6034,          # str r4, [r6]            restore the allocator
    *_load('tab6', [0x2380, 0x009B]),        # movs r3, #0x80; lsls r3, r3, #2   0x200: tab 6 + blank
    0xA805, 0x8800,  # add r0, sp, #0x14; ldrh r0, [r0]     tab 6's tile (598)
    0x3008,          # adds r0, #8
    0x9013,          # str r0, [sp, #0x4C]     caller [sp+0x20] = blank's tile
    0x9914,          # ldr r1, [sp, #0x50]     caller [sp+0x24] = first left tile
    0x1A69,          # subs r1, r5, r1
    0x9112,          # str r1, [sp, #0x48]     caller [sp+0x1c] = D
    0xB006,          # add sp, #0x18
    0xBDF0,          # pop {r4-r7, pc}
    ('label', 'bx_r7'),
    0x4738,          # bx r7
    # TAB_RIGHT_TILE (from 0x0449F0, caller's sp, r5 = entry, r7 = its left tile): r3 = its right half's tile
    ('label', 'right_tile'),
    0x9B07,          # ldr r3, [sp, #0x1c]     D
    0x19DB,          # adds r3, r3, r7
    0x2D06,          # cmp r5, #6
    ('bne', 'rt_done'),
    0x9B08,          # ldr r3, [sp, #0x20]     blank's tile
    0x3B08,          # subs r3, #8             tab 6's tile
    ('label', 'rt_done'),
    0x4770,          # bx lr
    ('word', 'alloc', 0x03001368),
    ('word', 'fixed', TAB_FIXED_CUR),
    ('word', 'tabs05', 0x08000000 + TAB_RIGHTS),
    ('word', 'tab6', 0x08000000 + TAB_RIGHTS + 0x600),
    ('word', 'loader', LOADER | 1),
], _hook_labels)

# Tiles 716-763 are not always free (issue #1): a Land card's panel outside battle (deck editor / shop card view,
# 0x08021850 -> 0x0801CE60 with mode 0x03005538 != 1 / 0x16) copies the ten mani icons to the FIXED OBJ tiles
# 704-743 (16x16 sprites, both pentagrams), over the tab right halves; back on the list the Owned / Character / Land
# tabs showed mani drops. Nothing reloads the tabs there. These screens run in the per-frame callback that 0x08000664
# calls through [0x03001780] (0x08000672: bl 0x08063784 = bx r0; deck editor r0 = 0x08055A0D), not in the main
# loop's handler[0x03003828] (the 0x08D7A424 table holds mode set-up handlers). VB_HOOK replaces that call: in modes
# 6, 9 and 10 ([0x03005538], the deck editor / shop / trade room) it runs TAB_RESTORE first, then the callback. When a
# tab right half (32x16 OBJ, tile 716-763) is on screen and no 16x16 OBJ uses tiles 704-743 (the mani icons are not
# shown), TAB_RESTORE copies the six right halves back from ROM (CpuFastSet 0x600 bytes; the same bytes otherwise).
TAB_RESTORE = TAB_HOOK + 0x100
VB_CALL = 0x000672
VB_ORIG = bytes.fromhex('63f087f8')     # bl 0x08063784
CUR_MODE = 0x03005538                   # u16, read by 0x080003EC
RESTORE_MODES = (6, 9, 10)
_restore_labels = {}
TAB_RESTORE_CODE = thumb(0x08000000 + TAB_RESTORE, [
    ('label', 'check'),
    0xB5F0,          # push {r4-r7, lr}
    ('ldr', 4, 'oam'),
    0x2500,          # movs r5, #0             a tab right half is shown
    0x2680,          # movs r6, #128           OAM entries
    ('label', 'loop'),
    0x8820,          # ldrh r0, [r4]           attr0
    0x8861,          # ldrh r1, [r4, #2]       attr1
    0x88A2,          # ldrh r2, [r4, #4]       attr2
    0x3408,          # adds r4, #8
    0x0583, 0x0F9B,  # lsls r3, r0, #22; lsrs r3, r3, #30   attr0 bits 8-9
    0x2B02,          # cmp r3, #2              disabled
    ('beq', 'next'),
    0x0603, 0x0E1B,  # lsls r3, r0, #24; lsrs r3, r3, #24   y
    0x2BA0,          # cmp r3, #160
    ('bcc', 'vis'),
    0x2BE0,          # cmp r3, #224            160-223: off screen (224+ wraps to the top)
    ('bcc', 'next'),
    ('label', 'vis'),
    0x0592, 0x0D92,  # lsls r2, r2, #22; lsrs r2, r2, #22   tile
    0x0B83,          # lsrs r3, r0, #14        shape
    ('bne', 'notsq'),
    0x27B0, 0x00BF,  # movs r7, #0xB0; lsls r7, r7, #2      704
    0x1BD3,          # subs r3, r2, r7
    0x2B28,          # cmp r3, #40
    ('bcc', 'done'),                          # a mani icon is shown: leave the tiles alone
    ('b', 'next'),
    ('label', 'notsq'),
    0x2B01,          # cmp r3, #1              wide
    ('bne', 'next'),
    0x0B8B,          # lsrs r3, r1, #14        size
    0x2B02,          # cmp r3, #2              32x16
    ('bne', 'next'),
    0x27B3, 0x00BF,  # movs r7, #0xB3; lsls r7, r7, #2      716
    0x1BD3,          # subs r3, r2, r7
    0x2B30,          # cmp r3, #48
    ('bcs', 'next'),
    0x2501,          # movs r5, #1
    ('label', 'next'),
    0x3E01,          # subs r6, #1
    ('bne', 'loop'),
    0x2D00,          # cmp r5, #0
    ('beq', 'done'),
    ('ldr', 0, 'tabs05'),
    ('ldr', 1, 'dst'),
    0x22C0, 0x0052,  # movs r2, #0xC0; lsls r2, r2, #1      0x180 words
    0xDF0C,          # swi 0x0C                CpuFastSet
    ('label', 'done'),
    0xBCF0,          # pop {r4-r7}
    0xBC01,          # pop {r0}
    0x4700,          # bx r0
    # VB_HOOK (from VB_CALL, r0 = the frame callback)
    ('label', 'vb_hook'),
    0xB501,          # push {r0, lr}
    ('ldr', 1, 'cur_mode'),
    0x8809,          # ldrh r1, [r1]
] + [it for m in RESTORE_MODES for it in (0x2900 | m, ('beq', 'vb_check'))] + [   # cmp r1, #m; beq
    ('b', 'vb_go'),
    ('label', 'vb_check'),
    ('bl', 'check'),
    ('label', 'vb_go'),
    0xBC03,          # pop {r0, r1}
    0x468E,          # mov lr, r1
    0x4700,          # bx r0                   the callback returns to 0x08000676
    ('word', 'oam', 0x07000000),
    ('word', 'tabs05', 0x08000000 + TAB_RIGHTS),
    ('word', 'dst', 0x06010000 + 716 * 32),
    ('word', 'cur_mode', CUR_MODE),
], _restore_labels)

_TABS_ITEMS = [
    ('ldr', 3, 'hook'),          # 978
    ('bl', 'bx_r3'),             # 97A  lr = 97E
    ('b', 'after'),              # 97E  on to 0x080449C4 (the OBJ loop)
    ('label', 'bx_r3'),
    0x4718,                      # bx r3
    ('label', 'tramp_rt'),       # 0x0449F0 BLs here: r3 is free there (it receives the tile)
    ('ldr', 3, 'rt'),
    0x4718,                      # bx r3
    ('label', 'tramp_vb'),       # VB_CALL BLs here (BL cannot reach 0x08FDxxxx): r1 is free there
    ('ldr', 1, 'vb'),
    0x4708,                      # bx r1
    ('word', 'hook', 0x08000000 + TAB_HOOK | 1),
    ('word', 'rt', _hook_labels['right_tile'] | 1),
    ('word', 'vb', _restore_labels['vb_hook'] | 1),
]
_pad = (len(TABS_ORIG) - len(thumb(0x08000000 + TABS_FN, _TABS_ITEMS))) // 2
TABS_NEW = thumb(0x08000000 + TABS_FN, _TABS_ITEMS + [0x46C0] * _pad + [('label', 'after')], _tabs_labels)
assert len(TABS_NEW) == len(TABS_ORIG) == 0x4C and _tabs_labels['after'] == 0x080449C4, (len(TABS_NEW), _tabs_labels)
RIGHT_CALL = thumb(0x080449F0, [('bl', _tabs_labels['tramp_rt'])])   # replaces add r1, sp, #0x14; ldrh r3, [r1]
VB_NEW = thumb(0x08000000 + VB_CALL, [('bl', _tabs_labels['tramp_vb'])])

# (offset, original bytes, new bytes, what)
PATCHES = [
    (0x05DF86, bytes.fromhex('012e'), bytes.fromhex('022e'), 'deck-name default copy: cmp r6, #1 -> #2 (3 u16)'),
    (0x05DFCC, bytes.fromhex('012e'), bytes.fromhex('022e'), 'surname / given-name default copy: cmp r6, #1 -> #2'),
    (TABS_FN, TABS_ORIG, TABS_NEW, 'deck-editor tabs: own right halves (see TABS_FN)'),
    (0x0449F0, bytes.fromhex('05a90b88'), RIGHT_CALL, 'tabs 0-6: right tile from TAB_HOOK right_tile'),
    (TAB_HOOK, b'\xff' * len(TAB_HOOK_CODE), TAB_HOOK_CODE, 'tab hook: load the split right halves (see TABS_FN)'),
    (0x044A16, bytes.fromhex('0b990b88'), bytes.fromhex('089bc046'), 'sort keys 7-12: right tile = [sp+0x20]'),
    (TAB_RESTORE, b'\xff' * len(TAB_RESTORE_CODE), TAB_RESTORE_CODE, 'tab restore after a Land card view (issue #1)'),
    (VB_CALL, VB_ORIG, VB_NEW, 'frame callback call: VB_HOOK first (see TAB_RESTORE)'),
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
