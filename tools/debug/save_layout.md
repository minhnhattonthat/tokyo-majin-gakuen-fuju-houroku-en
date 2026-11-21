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

`save.py set` mirrors its edits into the copy. Test: `save.py test SAV` boots the save, picks 続きから and passes
when the hub (mode 6) loads with the save's chapter; a chapter-17 save renamed 山田 太郎 loads clean.
Unmapped: cards owned, deck, money/points, event flags. Map them by the same diff method (buy one card, finish one
event) when stress saves need them (phase 8).
