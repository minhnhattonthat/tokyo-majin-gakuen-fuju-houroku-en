# Game state (phase 2, for the debug tool)

All verified in Mesen runs (`tools/debug/varlog.lua`, `scenelog.lua`, `warp.py`) unless marked guess.

## Main loop and modes
Main loop 0x08000262 calls `handler[mode]` every frame; handler table 0x08D7A424 (22 entries), mode u16 at
**0x03003828** (setter 0x080003D4). Cold boot: 13 -> 14 -> (New Game) 2 -> 4 -> 2 -> 6.

| mode | handler | screen (from `warp.py MODE<m>` shots) |
|---|---|---|
| 0 | 0x080005E9 | init / soft reset (guess) |
| 1 | 0x0800E375 | garbled when entered directly (needs setup; guess: load or link) |
| 2, 3 | 0x0803F205 | story player (2 = chapter scene, 3 = event scene, set by 0x0803F384) |
| 4 | 0x0804053D | name entry 名前は？ (needs the opening's setup; garbled when entered directly) |
| 5 | 0x08042DD9 | blank when entered directly |
| 6 | 0x08055921 | detour hub 寄り道 / 符咒編集 / 記録 / 設定 / 先に進む (first item depends on the chapter) |
| 7 | 0x08056281 | sutra board (also the post-ending clear prompt) |
| 8 | 0x08059209 | 封陰窟 dungeon menu |
| 9 | 0x08056A59 | 骨董品店 antique shop |
| 10 | 0x08059A59 | 符咒交換之間 trade room (title 通信 -> 通信交換) |
| 11 | 0x0805AB95 | blank when entered directly |
| 12 | 0x0805D72D | 通信対戦之間 link battle room (title 通信 -> 通信対戦) |
| 13 | 0x080083DD | boot logos |
| 14 | 0x080087F1 | title |
| 15 | 0x0800AC29 | battle (rules tutorial on a fresh game) |
| 16 | 0x08009609 | 句会 haiku club |
| 17 | 0x0800A7B9 | 設定 settings |
| 18 | 0x080091ED | 寄り道 detour map |
| 19 | 0x0800CF3D | staff roll (credits); blank when entered directly, reached by ending chapters 38/39 |
| 20 | 0x0800DA5D | サウンドテスト sound test (S22); no normal path found yet |
| 21 | 0x0805A98D | 通信エラー link error |

## Story position
- **Chapter byte 0x03005AA8** (0..39) indexes scene table B 0x08D82078 (40 chapter scenes; B[0] = opening).
- Chapter end (0x0805E37C): next mode/param from the 41x2-byte table 0x08D7919D (`mode, param`; mode 6 for every
  chapter except 38 -> 19 = staff roll), param to **0x03005668**; chapter += 1; past 39 -> 0 and flag 0x8000.
- Event scenes: table A 0x08D8211C = 13 groups x 10 slots. Group from the chapter (0x0805E2F8): chapters
  2 5 8 11 14 18 21 24 27 32 35 37 -> groups 0-11, any other chapter -> 12. Slot byte **0x03003580**.
- **Flag word 0x0300382C** (set 0x080003F8, clear 0x08000408, test 0x08000418): bit 24 = play an event scene
  (table A) instead of the chapter scene; bits 0-9 = event slots seen this chapter (cleared at chapter end);
  bit 25 = chapter end goes to mode 7; bit 15 = game cleared.
- Story loader 0x0803F3B4: script pointer -> 0x030012CC.
- Names: surname 0x03003830, given name 0x03005A70 (Shift-JIS, set to 緋勇 / 龍麻 at New Game, before name entry).

## Title menu
No save: 始めから | 設定 (left/right). With a save: 2x2 始めから 続きから / 通信 設定, cursor on 続きから;
通信 opens 通信対戦 | 通信交換.

## Not reached yet
- Defeat / rematch: 再戦する / 終了する menu text at 0xD65298 and the 敗北 banner (S9) need a lost battle; no
  confirmed life variable yet. Candidates (guess): u16 200 at 0x020041B2 / 0x02004452 (own), 80 at 0x020040C0 /
  0x02004320 (enemy), from a RAM dump of `warp.py MODE15` at frame 2600. Holding own life at 1 with
  `tools/debug/poke.lua` and mashing A for 9000 frames ended on a black screen (work/qa/bt2): unresolved. Next: shoot
  every 30 frames after the poke, or watch.lua on the candidates to see the HUD reader.
- The normal path to the sound test (mode 20).
