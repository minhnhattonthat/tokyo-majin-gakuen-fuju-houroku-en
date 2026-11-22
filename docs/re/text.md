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
| 0xCF12F0-0xCF8000 | system / menu / card-rule strings (991 pointed slots, `tools/strslots.py`) mixed with byte tables | direct u32 `0x08xxxxxx` pointers (verified: 0xCF1318 <- 0xD7A740); most sites in 0xD7A000-0xD7DFFF, a few code literals; some hits from graphics are noise (land mid-string) |
| 0xD16800-0xD1C000 | misc strings (44) | direct u32 pointers (43 of 44) |
| 0xD63000-0xD7A000 | tutorial scripts, card text, names (緋勇 0xD79188, 龍麻 0xD79190), kana grid 0xD72FCC | tables at 0xE5F56C (408 entries, read from code at 0xD184/0xD1B0), 0xE61108, 0xE613BC, 0xE6147C, 0xE61538, 0xE615D8; struct pointers inside 0xD63xxx |
| **0xD82324-0xE2A3xx** | **story scenes: 170 scenes, ~12 000 lines** | scene table A 0xD8211C (130 u32, ascending, literal at 0x5E378), table B 0xD82078 (40 u32, literal at 0x5E2F0). Pointers are 2-byte aligned |

### Story scene format (verified: all 170 scenes re-encode byte-exactly, `tools/scenes.py`, phase 3)
- Loader 0x0803F3B4: `u16 n`, then `n` u16 label offsets relative to the body start `scene+2+2n`; label 0 is
  always 0 (the body start). The scene pointer only needs 2-byte alignment (a build that moved every scene by 2
  bytes played B05 and A3.2 normally).
- Interpreter 0x0803F424: op = one byte, 0xFF = stop. Handler table 0x08D6E44C, 24 entries x 12 bytes (init, exec,
  skip). Lengths in bytes, op byte included: 01:4 02:2 03:4 04:2 05:4 06:4 07:6 08:2 09:2 0A:2 0B:4 0C:4 0D:2
  0E:2 10:4 11:4 12:4 13:2 14:2 15:2 16:2 17:2, FF:2 (`FF FF`).
- Text ops: **00** `00 00` + `【speaker】rt line` + NUL, padded to even with 00 (14 526 lines; 01 00 / 02 00 inside a
  line are the player name variables, not terminators). **0F** `0F nn` + nn choice lines joined by `rt`, ending in
  `wc`, no NUL, padded to even (21 menus).
- Branches are by label index, never by byte offset: `09 nn` = goto label nn; `08 xx`, `01 a b 00` and `0A 00`
  (emotion choice, 179) are each followed by a list of `09 nn` and `FF FF`. `06 00 stat delta` = stat change. So a
  repack only recomputes the header offsets and the A/B pointers.
- **Branch ops (phase 8, verified by forcing them in game, `tools/debug/forcebranch.lua`):** each calls a helper
  whose r0 indexes the `09 nn` list after the op. 0A emotion choice (9 ways; 179 ops: 130 in A scenes, 49 in B):
  helper 0x0805F7D0 returns -1 while waiting, read at 0x0803FEB2. 0F text choice: 0x0805FAFC, at 0x08040166. 08 flag
  test (2 ways, 113): 0x0805E204, at 0x08040014. 01 stat test (2 ways, 25): 0x0805E160, at 0x080400AE. Script state
  struct pointer at 0x03007570: +0 current op pointer, +4 label index the loader seeks to.
- **Loader = label seek:** 0x0803F3B4 starts at label `[struct+4]` (op 09 nn stores nn - 1 there and the loader runs
  again). A chapter with a battle stops mid-scene (B18 after line 460: chapter end 0x0805E3BC -> hub) and resumes at a
  later label after the battle; `tools/debug/startlabel.lua LABEL=n` starts a warped scene at label n (B18 label 70 =
  line 461).
- Every scene ends with `FF FF`; no scene has an empty line. Scenes are back to back in 0xD82324-0xE2B97A (no slack:
  the region is full), then 00 00 and LZ77 data at 0xE2B97C. Longer text spills into a second region
  (`scenes.pack(..., regions)`); the spill region needs the phase 7 trap test first.
- Nothing but tables A/B points into the scenes (scan of every aligned u32: two hits, both mid-string noise).
- Largest scene body 0xDF62C2, 40 740 bytes; label offsets are u16, so one scene can grow to 64 KiB.

### Extraction (phase 4, verified by `tests/test_extract.py`)
- `tools/extract.py` writes `script/scenes/<B05|A3.2>.tsv` (170 files, 14 526 lines + 21 choices) and
  `script/system/{cf,d1,d6}.tsv` (2 677 pointed strings); notation in `tools/textcodec.py` (`{rt}`, `{nl}`,
  `{name1}`, `{I000}`, `{&Sx0}`, `[XX]`). Every string re-encodes byte-exactly; build from the files = the dump.
- Codes seen: `rt wc wk wd dc pp xn yn Innn`, `&xNN &yNN &XNN &zNN &Sx0 &Sy0 &Sz0 &NX0 &NY0 &Ny0`, `0A 0D`,
  `01 00`, `02 00`. Literal ASCII in Japanese text: only `!!` (0xD6B120). `xn`/`yn` (0xD64BB4.., name lists) are a
  guess. One non-canonical cp932 code: `FB B3` (﨤) in the staff roll, B39.0020, kept as `[FB][B3]`.
- `strslots` additions found by the coverage scan: range 1 starts at 0xCF12F0 (pointed from 0xD7A744); text
  embedded in structs after non-zero header bytes is taken when its pointer site is in code, the 0xD7A000 menu
  tables, the 0xE5F000-0xE62000 text tables or a text range (12 strings: 0xD16820, 0xD16A40, 0xD645E4, 0xD678D4,
  0xD6E3D4, 0xD6E56C, 0xD72434, 0xD725EC, 0xD7269C, 0xD78E04, 0xD78F44). A word pointing inside an accepted string
  becomes an alias of it, not a slot: only 0xCF4DC -> 0xD7080C+2 (`【睡眠】`+2; code area, unverified, check before
  relocating that string).
- Not text: name-entry kana grid 0xD16740-0xD16800 (u16 little-endian Shift-JIS codes, pointed from code 0x9DE8;
  English name entry needs it in phase 5/8); fullwidth digit table 0x64A20 (`０１２３４５６７８９`, number display).
- Coverage: no kana-heavy run in 0x0-0x100000 or 0xCF0000-0xE62000 lies outside the extracted units except the
  waived data above (`uncovered_runs`, run against the original ROM).

## Free space
- **0xE61678-0xFE0000 (0x17E988 bytes of 0xFF)**: candidate. No code literal points into it (aligned scan hits are
  4bpp graphics noise). Trap-fill and tour before use (phase 7).
- 0xFE0000-0xFE4000 holds ARM code (branch table), 0xFE4000-0xFFF000 0xFF run (candidate), 0xFFF000+ data.
- Expanding to 32 MiB is possible (SRAM save, no EEPROM size issue) but would need xdelta; not needed with 1.5 MB free.

## Compression
- BIOS LZ77 (0x10): only 52 blocks (`tools/lz77.py scan`), 0x9D0C7 packed bytes. Most UI graphics are raw 4bpp
  (0xD1BF50+). The dialogue backgrounds are LZ77 8bpp blocks at 0xB5BC60.. (`docs/re/graphics.md`), so no
  unknown codec is needed.

## Font (phase 5, verified in game with the marker build)
- Font: 16x16 4bpp glyphs (colours 0 transparent, F white, D shadow right/below), 8 per row in banks: bank table
  0x08D7DCC0 (22 u32), bank thresholds 0x08D7A5E6 (u16 Shift-JIS codes 8140, 8240, .. 9840); index = code - low
  byte of the bank's threshold, glyph = bank + (idx>>3)*0x400 + (idx&7)*0x40 (top 2 tiles), +0x200 (bottom 2).
  Codes above 0x9872 (JIS level 2) are looked up in a 132-entry list at 0x08D7A47C.
- **Per-cell routine 0x08003B84** (Thumb; 42 callers): r0 = string unit (u16, read big-endian), r1 = 0x80-byte cell
  (4 tiles TL TR BL BR) in a RAM buffer, r2 = map entry (row stride 0x40), r3 = colour, [sp] = tile index. Lead byte
  < 0x80: control units (`rt` returns 1, `I` icon 0x11, `w` 2, `d` 3, `x`/`y` 0x1F+n, `&` number); else the glyph is
  copied (0x08004184) and 4 map entries written with palette 0xC000. Callers move one cell (+0x80 tile bytes, +4 map
  bytes, +4 tile index) per unit and handle `rt` themselves; no caller checks units for anything but 0000, `rt`,
  `wc` (the choice skip scans u16s for `wc`, 0x080401A0) and the name codes.
- Generic printer 0x08003AA0 (12 callers; story dialogue through 0x08003B40): loops units until 0000, a new map row
  per `rt`, units per line counted at 0x030062A4[line]; no per-line limit. Story text is copied to IWRAM
  0x03003C48 first and drawn whole into EWRAM (tiles 0x02000020.., map 0x02003000..), then revealed left to right
  (a shot taken early shows a cut-off line: wait ~60 frames after a box opens).
- **Printer B, unit routine 0x0800455C** (12 callers: the loop 0x08004A54, 0x0801C7B2, 0x0801C878): sprite text,
  used by the yes/no prompts (CF1318-CF1564, `　はい　いいえ`). Never calls 0x08003B84: it decodes Shift-JIS itself
  (controls by lead byte; 0x8140 returns 3 = x advances 16 px, no cell; codes > 0x9872 go through the kanji list),
  copies the glyph into the cell at r1 (0x08004184) and places a 16x16 sprite with 0x08018CF4(0xE000, x [sp+4],
  y [sp+0x28]). The loop moves the cell +0x80 and x +16 per unit, y +16 per `rt`. The prompt's cursor cells are
  fixed (cells 0 and 3 of the option line, whatever the text). VWF entry `hookb` (tools/vwf.py) at its Shift-JIS
  branch 0x0800497C. Found by watching ROM reads of CF146C (its marker drew blank).
- **Printer C 0x080519A0** (args r0 string, r1 OBJ VRAM byte offset -> sb, r2, r3 colour): one unit per call, same
  Shift-JIS branch shape as printer B (unit in r3, string in r4; 0x8140 returns 3; > 0x9872 through the kanji list
  0xD7A47C), glyph copied to 0x06010000 + sb by 0x08004184; returns r7. Draws the deck submenu's deck name (buffers
  0x03005040, six decks x 4 u16). VWF entry `hookc` at 0x08051DB8 (r2 = cell >> 5 | 1, so consecutive cells
  continue one strip). Found by hooking the BIOS SWI vector (tools/debug/callregs.lua CALL_AT=0x00000008).
- Default names (New Game, 0x0805DF72..): surname 0x03003830, given name 0x03005A70, deck names 0x03005040, each
  4 u16, cleared then filled from the pointers at 0xE6163C/40/44; the copy loops are patched to 3 u16
  (`tools/patches.py`).
- Log printer 0x0803F5D6: copies lines into 16-unit slots (at most 15 units a line, longer lines continue in the
  next slot) and draws 10 lines.
- **English: VWF hook** (`tools/vwf.py`, decision in docs/decisions.md D8). The stub at 0x08003B84 jumps to ARM code
  at 0x08F00000 for units whose first byte is A0-DF or F0-F9 (never used by the game). Each such unit is an MTE code
  for 1-4 characters (table built per build from all English); the hook clears the cell and ORs the characters in at
  a pixel cursor that runs on across consecutive cells (a strip). State (16 bytes) at EWRAM 0x0203A000 (zero in 12
  mode RAM dumps). The encoder keeps the strip's ink inside the cells handed out so far (<= 16 px x units).
  Font: `fonts/vwf.txt` (cap 9 px, x-height 6, shadow added like the Japanese glyphs; advance = width + 2, space 4)
  plus 【】「」『』 cropped from the game font; ~5.8 px a character, 2.6 characters a unit in running text.
- **Glyph torture line (2026-11-22, passed):** B05.0000-0002 overridden with A-Z, a-z, digits, all ASCII
  punctuation, …—“”‘’♪é, 【】「」『』 and single / double / triple spaces (build via `build.py --qa`, warp
  story_05): every glyph draws, widths and spacing as encoded, no clipping (`work/qa/torture/boxes.png`,
  `brackets.png`).

## Code-area strings (phase 8, 2026-11-22; `tools/codestr.py`, `script/system/code.tsv`)
- 0x06485C-0x064A34: 8-byte NUL-ended Shift-JIS slots the pointer-range scan never saw (their pointer tables sit at
  0xD7A614-0xD7A6FF, outside the strslots ranges). `tools/debug/codesweep.py` over 0x0-0xC0000 finds nothing else
  (two 3-char hits at 0x02C02C / 0x046318 are code).
- **Prefectures** (D7A614, 47 pointers, gojuon order): only the Birthplace? picker 0x080041B8 reads them (callers
  0x08041Exx and 0x080543xx). It draws 10 names per window as vertical columns, one cell down per kanji (map
  +0x80), names one cell apart (map +0x24A + 4i), tiles packed from 0x11 (palette 12, BG0); the window scrolls one
  name at a time (first index 0..37). Tiles past ~0x95 belong to something else (4 cells for all 10 names showed
  garbage in column 10), so the English hook packs tiles too: per name only the cells its column needs (the JP
  windows use <= 32 cells, the English <= 33, window 37, seen clean). Map entries of unused cells are written 0
  (the blank entry around the picker). Hook: ARM at 0xFE4000, cell counts at +0x100, 47 + 1 blank columns of
  0x200 bytes at +0x140; the old routine's first 8 bytes jump there. The SJIS strings stay in ROM, unread.
- **Card-effect pieces** (D7A6D0-D7A6FC), substituted for `{&<v>NN}` by the code dispatchers of all three printers
  (BG 0x08003C64.., printer B 0x080046xx.., printer C 0x08051Axx..). NN = type: 0 / 3 / 14 icon; 2 and 6
  D7A6D0[arg] (自分 相手 両者) 2 units; 4 arg 5 全ての 3 units (else element icon); 5 D7A6DC[arg] (右 左) 1 unit;
  others D7A6E4[arg] (-, 破壊, 除去) 2 units. {&S..}/{&N..}: sign from D7A6F0 (－ ＋) if S, tens digit if not 0,
  ones digit, units from the digit row D7A6FC. Every piece is a FIXED unit count (no NUL check), each unit a cell
  through the same unit routine, so English VWF units continue the strip. Patches: type 5 redirected into the
  type 2/6 loop with its own table (2 units: "right"/"left"), type 11's loop raised to 4 units
  ("destroy"/"remove"). Gotcha: the number formatter's ones digit jumps into the type-5 block's tail (0x3F22,
  0x4848, 0x51C8C), so the redirect writes only the block's first 12 bytes. English pieces are padded to their
  count with the empty MTE chunk (`Encoder.encode_units`): it clears its cell and advances 0 px.
- Seen in game (`work/qa/pc2`, board_turn.mss + `work/qa/bd/rand.txt`): numbers "Took 10 dmg", "+0", "+20" in
  VWF digits (f1530), "Mani levels turn / right" (f9420).

## Battle card panel ability labels (phase 8, 2026-11-22)
- Row 10 of the panel: 【label】【label】. 0x08021438 loops twice per label (pointers 0xD7CCC0 + 4 * (id + 1), rows
  CF64E8-CF6778), calling the glyph routine 0x08003B84 at string + 0 and + 2 with no NUL check, one 16 px cell each
  at a fixed tile (0x102 + 4 * call). A 1-unit English label made the 2nd call draw the NUL through the original
  path (tiles 0x39-0x3C, palette 0, stale pixels: the "ghost"). Rule (fit.py `label_problems`): one unit, then one
  unit or one icon; JP 必{I010} = char then icon, so English is `B{I010}`, never `{I010}B`.
- Brackets: 0x080210D6 draws D654D0 【】 into tiles 1-8 and points the label's open bracket cell at the 【 glyph's
  RIGHT half (map C001 + 1) and the close bracket at 】's left half. VWF draws left-aligned, so D654D0 is
  `  【¦】`: two spaces put 【 in the right half of unit 1.
- `¦` (vwf.UNIT_BREAK) in script text ends a unit; a 2-4 character segment between breaks is forced into the MTE
  dictionary as one unit. Used for `  【¦】`, ` -¦ -` (－－), `Iai¦ ` (second cell blank).
- Repro / check: board_turn.mss + `work/qa/bd/rand.txt`, frame 1600 (`work/qa/ghostfix/panel.png`). Probe
  `tools/debug/dstlog.lua` (BIOS copies and CPU writes into a range) found the writer: the BG0 map is copied each
  frame from RAM 0x02002000.

## Battle message table and popups (phase 8, 2026-11-22)
- Table 0x08D7A700 (u32 string pointers, 27 code literals, e.g. 0x0800F21A, 0x0803E946 `ldr r0,[table,#0x44]`) with
  sub-table bases loaded by code: 0xD7A748 character ability descriptions (100, index = task [0x030035B8] +0x14,
  shown at 0x080232BE when A is pressed in state 4 of task 0x08022FE4, created by 0x08022F80 from five battle
  callers), 0xD7A8D8 possession / 0xD7A944 barrier / 0xD7A9BC spell effect texts (card kind 0x11/0x12/0x13 at
  0x08020FEA.., paired with name lists 0xD7D4FC / 0xD7D568 / 0xD7D5E0), 0xD7AB08, 0xD7AB74, 0xD7ABEC (land / spell
  effect lines), 0xD7AD38, 0xD7AD78, 0xD7ADE8 (character records).
- Popup printer 0x08018AB0 (r0 string, r1 x, r2 y, r3 flag; push at +0, r0 kept until 0x08018ABC), box drawn first by
  0x0801A8DC / 0x0801B044. The turn banner (0x080100B6) prints the popup string, then the name lines from RAM with
  0x08018B4C: the opponent name is a RAM copy at [0x0300756C]+0x694, made at battle setup, so a savestate made on an
  older build shows that build's name (board_turn.mss: 常世の使者; a rematch on the English build shows Tokoyo Envoy).
- Coverage: `tools/debug/popcycle.lua` loops any address list through the real popup (`tools/debug/popuplog.lua`
  logs the game's own calls).

## Prior work
- An AI-assisted English patch is listed on RetroGameTalk (thread 74417) with graphics text left in Japanese.
  Unverified and not downloaded. If it is ever used, diff it only as a map.
