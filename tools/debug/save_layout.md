# Save layout (SRAM 32 KiB, `tools/debug/save.py`)

Mapped by diffing two game-written saves that differ only in the chapter (hub 記録 at chapter 5 and 6), and from
the checksum routine 0x08000E00.

| offset | size | field |
|---|---|---|
| 0x0000 | 12 | `MAJIN_HUJU1\0` |
| 0x000C | 8 | surname, Shift-JIS, 00-padded (RAM 0x03003830) |
| 0x0014 | 8 | given name (RAM 0x03005A70) |
| 0x06D5 | 1 | chapter 0..39 (RAM 0x03005AA8) |
| 0x06D7 | 1 | loaded into RAM 0x030035B0 (unknown) |
| 0x06D8 | 4 | checksum: u32 sum of the words at 0x0000..0x06D8 and 0x06DC..0x555C |
| 0x06DC | 0x4E80 | second buffer (copied from the EWRAM block that 0x03001EE0 points at: cards/deck, unmapped) |
| 0x555C | 0x6DC | copy of 0x0000..0x06DC (the rest of a second slot does not fit in 32 KiB) |

**Card collection (session 20, 2026-11-22):** the 0x06DC buffer (EWRAM 0x0203B100) starts with the owned-card
list: 4-byte records `u16 id, u8 a, u8 b`, unused records `FF FF FF FF` (room for 0x4E80/4 = 5024; the rest of the
buffer is FF in a chapter-3 game). Picking a booster pack after a battle appended 8 records at the end of the list
(`work/qa/pack1`, RAM diff f200 -> f2400; nothing else in the buffer changed). Kind = byte `a` (function 0x08052F28): 0x10 land (52, table
0xD7D2D0), 0x11 possession (27, 0xD7D4FC), 0x12 barrier (30, 0xD7D568), 0x13 spell (83, 0xD7D5E0), anything else
character (282, records 0xD7ADE8); `id` indexes that kind's table, `b` is 0 for the four non-character kinds.
Characters were seen with `a` 0..15 and `b` 8..31 (per-instance values, not decoded; `7, 16` works). Every-card save:
`save.py set work/saves/hub_ch05.sav work/saves/allcards.sav --add-cards 7:0-281:16 --add-cards 16:0-51
--add-cards 17:0-26 --add-cards 18:0-29 --add-cards 19:0-82`; the deck editor then
counts 282 / 52 / 83 / 30 / 27 (`work/qa/allcards/final.png`). Deck(s) and money not found here yet.

`save.py set` mirrors its edits into the copy. Test: `save.py test SAV` boots the save, picks 続きから and passes
when the hub (mode 6) loads with the save's chapter; a chapter-17 save renamed 山田 太郎 loads clean.
Unmapped: cards owned, deck, money/points, event flags. Map them by the same diff method (buy one card, finish one
event) when stress saves need them (phase 8).
