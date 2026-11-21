# Text engine (recon, phase 1)

Dump: `rom.sha1` (BTFJ, 16 MiB, SRAM_V113 save at string 0xD7A308). Helpers: `tools/re_scan.py`, `strscan.py`,
`ctrl_inventory.py`, `scene_table.py`, `scene_peek.py`, `ptrfind.py`, `hexdump.py`.

## Encoding
- **Shift-JIS (cp932), NUL-terminated**: verified by decoding the menu prompts (0xCF1304 符を使用しました) and the
  opening dialogue (0xDD4B50 看護婦..., shown on screen in `work/qa/tour1`).
- Strings are padded with 00 to a 4-byte boundary inside script streams (verified on 0xDFFDE0..).
- English: the ROM has no proven half-width glyph path yet; the font decision (VWF hook) is phase 5.

## Control codes inside strings (counts across 0xCF0000-0xD20000 and 0xD60000-0xE30000)
| code | count | meaning (guess unless marked) |
|---|---|---|
| `rt` | 19379 | line break (verified by the on-screen line break in the opening) |
| `\n\r` (0A 0D) | ~330 | line break, second form (card/tutorial text at 0xD6xxxx) |
| `wc` `wk` `wd` | 132/15/3 | wait for key + clear (variants) |
| `dc` | 26 | end of a staff-roll page |
| `pp` | 3 | page/clear (tutorial) |
| `Innn` (3 digits) | ~600 | inline icon or card-name insert (e.g. `I000人物符`) |
| `&x99` `&y99` `&X99` `&Sx9` `&Sy9` `&Sz9` `&NX9` `&NY9` `&Ny9` | ~30 | position or number formatting (card stat screens at 0xCF56xx) |
| 01 00 / 02 00 raw bytes | ~130 | inline variable (player surname/name?) in story lines (0xDD696C) |

Argument counts are the digits shown; prove each with the marker build before the extractor depends on it.

## Regions and pointers
| range | content | pointers |
|---|---|---|
| 0xCF1300-0xCF8000 | system / menu / card-rule strings (528) | all have direct u32 `0x08xxxxxx` pointers (verified: 0xCF1318 <- 0xD7A740) |
| 0xD16800-0xD1C000 | misc strings (44) | direct u32 pointers (43 of 44) |
| 0xD63000-0xD7A000 | tutorial scripts, card text, names (緋勇 0xD79188, 龍麻 0xD79190), kana grid 0xD72FCC | tables at 0xE5F56C (408 entries, read from code at 0xD184/0xD1B0), 0xE61108, 0xE613BC, 0xE6147C, 0xE61538, 0xE615D8; struct pointers inside 0xD63xxx |
| **0xD82324-0xE2A3xx** | **story scenes: 170 scenes, ~12 000 lines** | scene table A 0xD8211C (130 u32, ascending, literal at 0x5E378), table B 0xD82078 (40 u32, literal at 0x5E2F0). Pointers are 2-byte aligned |

### Story scene format (verified on scene 0xD82324, partly guessed)
- `u32 count`, then `count` u16 values. The first count-1 are branch offsets **relative to scene+4+2*(count-1)**
  (they land on `06 00 <stat> <delta>` records: the emotion-choice outcomes); the last u16 is the first opcode.
- Body: u16 opcodes with args, e.g. `03 00 nn 00 00 00` (portrait/voice?), `00 00` + string (a line),
  `09 0B`, `FF FF` terminators, `10 00 05 00`, `14 00`.
- Lines are `【speaker】rt text\0`, padded to 4 bytes.
- Insert plan: re-serialize each scene with recomputed u16 offsets and repoint tables A/B. The opcode argument
  table must be complete first (phase 3/4: decode every scene until offsets and lengths reproduce byte-exactly).

## Free space
- **0xE61678-0xFE0000 (0x17E988 bytes of 0xFF)**: candidate. No code literal points into it (aligned scan hits are
  4bpp graphics noise). Trap-fill and tour before use (phase 7).
- 0xFE0000-0xFE4000 holds ARM code (branch table), 0xFE4000-0xFFF000 0xFF run (candidate), 0xFFF000+ data.
- Expanding to 32 MiB is possible (SRAM save, no EEPROM size issue) but would need xdelta; not needed with 1.5 MB free.

## Compression
- BIOS LZ77 (0x10): only 52 blocks (`tools/lz77.py scan`), 0x9D0C7 packed bytes. Most UI graphics are raw 4bpp
  (0xD1BF50+). The dialogue backgrounds are LZ77 8bpp blocks at 0xB5BC60.. (`docs/re/graphics.md`), so no
  unknown codec is needed.

## Font
- Dialogue glyphs are drawn into BG VRAM at runtime (VRAM 0x0000.., `work/qa/ppu_dlg`). Font in ROM: 4bpp glyphs
  in Shift-JIS order at 0xC6FB48-0xCE5748 (`docs/re/graphics.md`). The draw routine and glyph size are phase 5.

## Prior work
- An AI-assisted English patch is listed on RetroGameTalk (thread 74417) with graphics text left in Japanese.
  Unverified and not downloaded. If it is ever used, diff it only as a map.
