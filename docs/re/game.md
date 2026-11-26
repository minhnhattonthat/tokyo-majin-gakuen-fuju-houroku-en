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
| 11 | 0x0805AB95 | link trade screen (blank when entered directly: task state 1 waits for the link at 0x0805AEBC; force with `tools/debug/setreg.lua --var AT=0x0805AEBC --var REG=0 --var VAL=1`) |
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

Per-frame work (issue #1, session 44): the table handlers set a mode up; each screen's frame logic is the callback
in **0x03001780**, called by 0x08000664 at 0x08000672 (`bl 0x08063784` = bx r0; deck editor 0x08055A0D). While a
screen runs, 0x03003828 can read 0 (handler 0 = `bx lr`); the current mode is the u16 at **0x03005538** (read by
0x080003EC; 1 in a chapter battle and the rules tutorial, 6 in the deck editor). Mani icons: 0x0801CE60 (r0 =
index 0-9) copies one 16x16 icon to OBJ tile 1 + 4i when the mode is 1 or 0x16, else to the fixed tile 704 + 4i;
outside battle the card panel 0x08020F40 calls it for card class 0x10 (Land cards), so a Land card view in the deck
editor / shop fills tiles 704-743 (`tools/patches.py` TAB_RESTORE).

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

## Chapter battles (mode 1, handler 0x0800E375)
- Hub 先に進む goes to mode 1 when the chapter has a battle (after B02 in a played game; after the opening the first
  one is the chapter-1 battle with the rules tutorial). It needs the deck the opening gives: after a chapter warp
  (`warp.py B01`, `MODE6.1`, or `work/saves/hub_ch05.sav` made from a warp) mode 1 hangs on a pink screen: the card
  panel loop 0x08021376-0x080213BC prints a name from a null pointer (r7 = 0x85549, open bus) forever.
- From a cold new game it works: `emu.py rom/base.gba --route tools/routes/newgame.txt --mash 20 --script
  tools/debug/onmode.lua --var "ON_ROUTES={[4]='300 -;6 right;40 -;6 right;40 -;6 a;150 -',[6]='400 -;6 up;40 -;6
  a;300 -'}" --var "ON_SAVE='<abs dir>'"` reaches mode 1 at f13595 (name entry keeps 緋勇 龍麻 via 終了; the hub
  cursor wraps up to 先に進む). Mode 1 starts with the rules tutorial pages, then the hand / card panel.
- Hand phase: left/right step through the hand (card panel on the right), Start opens the rules-help list
  (【基本ルール】..), L shows the card large; **left then A** (A alone does nothing) opens 引きなおしますか？ (cursor on
  いいえ); A -> 先手・後手を決めます (turn-order cards) -> 勝負 banner -> enemy portrait + quote (D67B54 我らを見捨てるな)
  -> 符咒士 緋勇龍麻 の ターン banner (printer B) -> the board. States: `work/states/nat/mode1_1.mss` (mode-1 entry),
  `work/states/battle1_select.mss` (hand phase, after 120 A presses from mode1_1).
- The "board" after left;a;a is the turn-order pick (two rows of face-down cards, 先手・後手を決めます, then
  同数札改め on a tie): it only needs time and a few presses. `work/states/board_turn.mss` (from battle1_select:
  `30 -;6 left;30 -;6 a;60 -;6 a;1400 -`) is there. A random route of A / directions / B (scratch `mkroute.py`, seed 1,
  in `work/qa/bd/rand.txt`) then plays real turns: discard prompts, spell popups, card panels, enemy quotes.
- **Life (verified):** u16 at 0x020121C8 and 0x03003EC0 (own, 200 at start) and 0x020120C8 and 0x03003EC4 (enemy,
  80); the HUD heart value. Player structs 0x100 apart. Poke both copies to 0 for 60 frames
  (`--script tools/debug/poke.lua --var "POKES={[0x020121C8]=0,[0x03003EC0]=0}" --var POKE_FROM=1200 --var
  POKE_TO=1260` from board_turn with rand.txt): defeat at ~f3000 (enemy quote, 敗北 banner, 再戦する / 終了する at
  f3342; `work/states/defeat.mss`); the enemy pair gives victory (勝利, ブースターパック選択 pick, card reveal with
  売買符として登録します prompt, then the story goes on to the hub; `work/qa/bd/win`). The old candidates
  0x020041B2 etc. were wrong.
- Deck editor: hub (mode 6) `400 -;6 down;40 -;6 a` = 符咒編集 (`work/qa/bd/deck`, mode6_1.mss there is a real-game
  hub after the chapter-1 battle, copied to `work/states/hub_real.mss`). 新規 opens the deck-name entry 符咒名は？
  (kana grid D72F00-D730A4, kind grid).

## Opponents and enemy quotes
- Opponent records at 0xD6E17C, 12 bytes each, 43 of them (0-42): u32 quote list (20 u32 string pointers), u16
  character id, u16 starting life (record 0: 80), u32 level. Getter 0x0803D7AC (r0 = index -> 0xD6E17C + 12 * index).
  The battle's index is the byte at [0x0300756C] + 0x7F1 (chapter 1 = 0); mode-1 setup 0x0800E7A4.. reads life etc.
  through the getter. Records 40-42 share one quote list. Quote 2 of opponent 26 is an empty string in the original.
- Quote box: a task with struct [0x030035B8]: u16 +0x34 quote index, u16 +0x38 state (jump table 0x0801C59C: 0 init,
  1 portrait, 2 slide in, 3 alloc at 0x0801C6C0, 4 print a char a frame, 5 print the rest, 6 wait A or 0x12B frames,
  7 slide out, 8 free, 9 end -> 0x0800E4BC next battle phase). Text by printer B (sprites), 3 lines.
  `tools/debug/forceopp.lua` forces an opponent; `tools/debug/quotecycle.lua` loops the box through every quote.
- Person-name table 0xE5F71C (300 u32 pointers: 0-5 misc, 6/7 the player's name, 8.. speaker names, ~290.. battle
  messages): the sound test's DLG row shows one name per entry (282 entries).

## Not reached yet
- The normal path to the sound test (mode 20).
