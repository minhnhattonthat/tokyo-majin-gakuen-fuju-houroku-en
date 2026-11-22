# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator (started 2026-11-22). Last build: `build/tmgfh_en.gba` 2026-11-22 (session 18),
  sha1 82aef7599a18..; check.py 37 passed.
- **Progress:** Phase 7 done 2026-11-22: build green, `tools/fit.py` 17 151 rows 0 problems, `tests/test_script.py`
  (batch rules incl. control-code multiset over the merged script), `tests/test_romdiff.py` (English build writes
  only scene tables/REGION, string slots + pointer sites, SPILL/hook area, the two hook stubs). `jp_left.py --sjis
  --gba-ptrs` on the build: only the kana name-entry grids D6E5xx/D72Fxx (kind `grid`, until English name entry)
  and a graphics false hit at 0x803B27. Phase 6 done pending independent review (2026-11-22): every row
  translated, batch check 0 errors, glossary current, story pass B00-B39 / A0-A12 / sys sheets with fixes
  (`qa_gate.py check work/qa/story/...` exits 0), `docs/polish.md` all ticked. The phase 6 review
  (`../.harness/reviews/...-phase6.md`) found no Critical; its Important 2/3 are fixed (D11: 焔羅様 = Enra-sama, 80
  rows; default surname Hiyuu; lint now checks kanji name + 様 and the glossary Avoid "Hiyu"), and its minors
  (glossary b003 note, style-reference voice rows, polish ids, B28.0015/16, A11.9.0051/52, B39 notes, 先生 rule).
  **Gap (Important 1):** the story-pass verdicts were written by the translating session, not an independent
  reviewer; codex is rate-limited until 2026-11-26 and Orca workers have no subagents. Before release, re-run the
  story pass with an independent reviewer (`qa_gate.py todo work/qa/story/manifest.tsv work/qa/story/verdicts
  --size 1`, a `translate-retro-game:reviewer` per chapter or `codex exec -s read-only`, reports in
  `work/qa/story/reports/`, new verdict files). `tools/set_en.py` sets or rewraps rows keeping every TSV column.
- **How:** fit lint `tools/fit.py` (budgets from `tools/windows.tsv`); after any `en` edit run `tools/check.py`,
  then `tools/story.py` + `qa_gate.py init` on the story manifest and add a verdict line for each changed sheet.
  No subagents in Orca workers; codex rate-limited until 2026-11-26.
- **Phase 8 so far (2026-11-22):** graphics pipeline built: `tools/gfx.py` (groups read `gfx/<group>.tsv`, letter
  with Liberation Sans Bold, `fonts/liberation`, OFL, onto the game's 16-step grey ramp with a dark rim; `build.py`
  calls `gfx.apply` on the English build only; `tests/test_romdiff.py` allows its ranges). Pilot group title_menu
  (G4) is English in game (`work/qa/gfx_title/menu_zoom.png`, selected item keeps its yellow palette). Full warp
  tour of the English build into `work/qa/tour_en/` (`--states` regenerated `work/states/`); visual-QA brief with
  this game's standing non-bugs in `docs/visual-qa-brief.md`.
  Tour result: 193/194 ok; `story_27` "blank final" is the game's own fade (JP final frame is black too,
  `work/qa/s27_cmp.png`): verdict ok. JP tour done: `work/qa/tour_jp` 194/194 (warp.py's default `--rom` is
  `rom/base.gba`: pass `--rom build/tmgfh_en.gba` for the English build).
  Session 2 (2026-11-22): PUSH START (0xD25B30) is already English in the original: no work. Menu labels English
  in game (`work/qa/gfx_menus/sheet.png`): group `menu_labels` (15 sprite labels: hub, shop, trade room, link room)
  and group `dungeon_menu` (BG2 screen, 126 tiles + 30x20 map rebuilt). New `tools/gfx_screens.py` renders the
  screen table's (tiles, palette, map) triples; `tools/debug/vramsrc.lua` finds a VRAM range's ROM source.
  Format notes in `docs/re/graphics.md` W1-W5 and §Screen table. check.py 37 passed, smoke ok.
  Visual-QA verdicts not started on purpose: redraws change most sheets, so tour + verdicts go last. Review
  sheets at full scale: `sheet.py DIR --div 1 --changed 0.02` (~86k image tokens for the whole tour; split it
  across sessions by chunk). Tour sheets are half-scale and too small to judge text.
  Session 3 (2026-11-22): English in game, each checked in a warp shot: room plaques (group room_banners,
  `tools/gfx_rooms.py`, 8bpp room screens: Fuin Cave + floor, Trading Hall, Link Battle Hall + "Deck in Use", Curio
  Shop; link-error screen C11C58 moved to free space for extra tiles: relocation proven on the dungeon screen, the
  error screen itself not reached), Fuin Cave floor number (group floor_numerals: hook 0xFD0000 for 0x080597D0,
  rotated Arabic digits 1-100, tested by poking 0x03003810), detour-map signs + 寄り道 banner (group signs,
  `tools/gfx_signs.py`), settings screen (banner, labels, every value: `tools/routes/settings_values.txt`), haiku
  banner, shop item list "Select Item" (`tools/routes/shop_buy.txt` from `work/states/shop.mss`). Deck-name entry
  screen (G6, group deck_name_screen) redrawn but **not yet seen in game** (no warp row: reach it via hub -> Deck Edit;
  add a scenes.tsv row). Tools: `tools/debug/bglayers.py` (each BG layer + OAM of a PPU dump),
  `tools/debug/gfx_preview_rooms.py`, `tools/debug/gfx_preview_bg4.py`; `gfx.bg4_edit` reletters any 4bpp 30x20
  screen (kinds bg / board / patch). Free space used: 0xFD0000 hook, 0xFD1000+ room screens, 0xFD8000+ 4bpp screens.
  Session 4 (2026-11-22): new warp row `deck_edit` (hub -> 符咒編集, `tools/routes/deck_edit.txt`; state
  `work/states/deck_edit.mss`). Deck-name entry redraw **seen in game** (deck_edit state + `6 down;30 -;6 down;30 -;6
  a`). Fixed: (1) default names were cut to 2 u16 codes at New Game ("Ma" for Magami, "Tatsu" for Tatsuma):
  `tools/patches.py` raises both copy loops (0x0805DF86, 0x0805DFCC) to 3 codes and the build fails if a default
  name needs more; (2) a third text printer **printer C** (0x080519A0, one unit per call, glyph into OBJ VRAM
  0x06010000 + sb; the deck submenu's deck name) drew VWF codes as kanji: new `hookc` entry in `tools/vwf.py`
  (stub at 0x08051DB8, same shape as printer B). Both checked in game (`work/qa/deck_x1`, `work/qa/warp/name_entry`).
  Tools: `tools/debug/callregs.lua` (registers at a function entry; CALL_AT=0x00000008 = every BIOS SWI, lr = caller),
  `tools/debug/sprblock.py` (render a ROM sprite block with a dumped OBJ palette).
  Session 5 (2026-11-22): deck editor buttons English in game (group `deck_edit`, `tools/gfx_deck.py`,
  `gfx/deck_edit.tsv`; `work/qa/deck_gfx/en_cmp2.png`): View All, Add Card, Remove, In Deck, submenu Edit / Copy /
  Erase / Name / Equip (32x16 halves at 0xC66C18, OBJ bank 3; interior cleared to colour 6, Liberation Bold with a
  right/down shadow like the JP glyphs). New `tools/debug/objsrc.py` (each OBJ's tiles -> ROM offsets from a ppu dump).
  Session 6 (2026-11-22): **deck editor all English** (`work/qa/tabs_en4/zoom.png`, `work/qa/sortpop7/z.png`,
  `work/qa/sortpop8/z.png`, `work/qa/hdr.png`): category tabs Owned .. Possession, 全 badge "All", sort keys Name / AP
  / AT / SP / HP / Value, order badges A-Z / Z-A / 9-1 / 1-9, kana-row badges A Ka Sa .. Wa (0xC6B118; the list
  still sorts by Japanese reading, so rows are the romanized gojuon rows), "Sorting your cards. / Please wait."
  popup (0xC6D078), header plaque "Deck Edit" (0xC6C078, marble rebuilt from its text-free columns). Engine: the
  tab loader 0x080448E8 shared one right half across tabs; `tools/patches.py` TABS_FN rewrites its two right-half
  loads in place (one call for a contiguous block at 0xFDF000 placed at OBJ tile 704; the popup is fixed at tiles
  640-703 (literals 0x0498CC/0x049A60/0x049F74, OBJs 0x08044A4C/64), and the loader ring 0x03004E40 holds 16
  entries with no overflow check, so the call count must not grow). Help template D7269C respaced (the tab name
  and sort key are overlaid at fixed x). Kana-row badges not yet seen in game (where do they show? scroll the
  name-sorted list). Route: deck_edit state + `6 a` (tabs), `6 a;90 -;6 a;90 -;6 r` (sort keys), `select` then `a`
  (sort popup). New probe `tools/debug/ppuat.lua` (PPU dump at frame AT into the run dir).
  Session 7 (2026-11-22): **player name entry English** (G6: "Your name?", Surname / Given name captions, Next /
  Back / Done, Hiragana / Katakana / Kanji; `work/qa/ne_en.png`): LZ77 screen, new `gfx.lz_screen_edit` (decode,
  edit, retile, recompress; the loader sizes everything from the LZ77 header, so the set may grow to 251 tiles
  below the BG2 screen base) and row kind `label` (text on the clear backdrop). Katakana rect widened on the
  deck-name screen too. **Pack select header** "Pick a Booster Pack" (`tools/gfx_plaques.py`: 19x4 plaque map,
  interior rebuilt from an 8 px period of its own texture, flip-sharing retile into 45 tiles + reserved blank).
  **Battle banners** S9 English (`tools/gfx_banners.py`, YOU/WIN! seen in game at the victory, YOU/LOSE at the
  defeat; LET'S/DUEL! and CASTER/SWAP rendered only (`work/qa/winb/blocks_en.png`), not yet seen in game).
  Battle states (English build): `work/states/pack_select_pre.mss` (victory banner; `4 a;300 -` -> pack select),
  `defeat_quote.mss` (`60 -;4 a;400 -` -> YOU LOSE; ~f3200 of that run = Rematch / Quit, font text, English).
  Note: `work/states/defeat.mss` is NOT the defeat; it is a battle with tutorial popups.
  Session 8 (2026-11-22): **battle HUD English** (group battle_ui, `tools/gfx_battle.py`, `gfx/battle_ui.tsv`;
  sprite table 0xD814C8): FIRST / SECOND plates, 32x32 numerals 1-5 (blue/red), the ten turn-order cards' corner
  badges 1-5 (8bpp), AP UP (4 variants), vertical phase banners DEPLOY / CLASH (32x96 each at 0xB4F808 /
  0xB4FE08; 0xB50000 lies inside, not a separate asset), VS, Attack / Wait panel. Seen in game from board_turn.mss
  + `work/qa/bd/rand.txt` (`work/qa/s6/`): numerals + badges f90, FIRST/SECOND f360, LET'S DUEL! f480, CASTER SWAP
  f1020, AP UP f1260, DEPLOY f1350. **Rendered only** (never loaded in 12 000 battle frames): VS, CLASH, Attack /
  Wait. New tools: `tools/debug/romblock.py` (block with its ROM palette, original | English; `--obj WxH`),
  `tools/debug/cardnums.py`, `tools/debug/srclog.lua` (BIOS copies whose source is in a ROM range = when a
  graphic loads). check.py 37 passed, smoke ok.
  Session 9 (2026-11-22): **story location captions** (23, group captions, rotated English; `work/qa/cap_en/both.png`),
  **13 chapter title cards** "Chapter One / Darkness" .. "Chapter Thirteen / Fated Stars" and the **end card 完 -> The
  End** (all 14 seen in game: `work/qa/cards/all.png`, warp rows card_01..card_13, card_end via new warp.lua
  `SEEK=<u16>`), **profile screens** Birthplace? / Birthday? (月 -> "/", fields read MM/DD) / Blood type? / Gender?
  Male Female (`work/qa/prof_en/z.png`; gender screen not seen in game). Details: `docs/re/graphics.md` §Phase 8
  findings. check.py 37 passed. Last build sha1 fb150f4b913c..
  Session 10 (2026-11-22): **code-area strings English** (`tools/codestr.py`, new extract unit
  `script/system/code.tsv`, notes in `docs/re/text.md` §Code-area strings). Birthplace? picker: 47 prefectures as
  rotated English columns (VWF font, read top to bottom; ARM hook 0xFE4000 replaces 0x080041B8, packed tiles), all
  windows seen in game (`work/qa/bp4/sheet.png`, `zoom.png`; state `work/states/birthplace.mss`, cold boot:
  `emu.py build/tmgfh_en.gba --route tools/routes/newgame.txt --frames 10260 --mash 20 --script
  tools/debug/onmode.lua --var "ON_ROUTES={[4]='300 -;6 right;40 -;6 right;40 -;6 a;200 -;6 a;200 -;6 down;60 -;6
  a;200 -;6 a;200 -;6 a;200 -;6 a;200 -'}"`). Card-effect pieces You/Foe/Both, right/left, destroy/remove, All, + -
  and digits 0-9 now VWF units with exact unit counts; type 5 redirected to 2 units and type 11 raised to 4 in all
  three printers; templates CF57E4-CF5914 reworded ("{&x06}: Life {&Sy0}"); fit.py counts piece cells. Seen in
  game: "You: Life +10", "Both: Life -20" (`work/qa/pc_board/pick.png`), "Mani levels turn / right", "Took 10 dmg",
  "+0 / +20 / +10" (`work/qa/pc2/z3.png`). **Not yet seen:** destroy/remove (type 11, 4 units) and All (type 4
  arg 5): no random battle drew them (`tools/debug/readframes.lua` WATCH_LO=0x08D7A6E4 logs when one does).
  Code area 0x0-0xC0000 swept (`tools/debug/codesweep.py`): nothing else. The 47 SJIS prefecture strings stay in
  ROM unread: list them as known in the release's `jp_left.py` run. Story gate 0 open (verdict file
  `zz_recheck10_20261122.tsv`). Second picker caller 0x080543xx (another screen) not seen.
  Session 11 (2026-11-22): **S7 large turn-order cards English** (10 cards, kind `bigcard` in `gfx/battle_ui.tsv`,
  `tools/gfx_battle.py`: old numeral + rim inpainted, Arabic digit in the same ink; "2" seen in game at the
  turn-order draw from board_turn.mss + `work/qa/bd/rand.txt`, `work/qa/bigcard/zoom.png`). **S27 rarity legend** English "Hi:Violet / ↕:Gold / Lo:Silver" (kind `legend`;
  64x64 OBJ, table 0xD63960 of (ptr, size) pairs): rendered only, the screen that shows it is not yet found (likely a
  card list/info screen; use srclog.lua with SRC_LO=0x08D3C1F8). check.py 37 passed.
  Session 12 (2026-11-22): **large card view name labels English** (S1 + S4 + S5, 468 labels, group card_classes,
  `tools/gfx_cards.py`): each card kind's name table (character records 0xD7ADE8 word 0; land / spell /
  possession / barrier u32 lists 0xD7D2D0 / 0xD7D5E0 / 0xD7D4FC / 0xD7D568) gives label i, text = the cf.tsv `en`
  of the same string (read from the original ROM: the build moves spilled strings). "Giant Bat" seen in game
  (L on a hand card: `work/states/hand_panel.mss` + `10 -;6 l;60 -`, `work/qa/cls5`); non-character kinds rendered
  only (`work/gfx/cc_c.png`, `cc_e.png`). **S27 rarity legend seen in game** (battle tutorial card page). Found:
  S3 = 40x8 mini name labels (thumbnail on the battle panel), S29 = battle-tutorial overlays + its 8bpp card panel
  (details in `docs/re/graphics.md`). New state `work/states/hand_panel.mss` (hand phase, card panel up). check.py
  37 passed, smoke ok, build sha1 adcea1280faf..
  Session 13 (2026-11-22): **card panel ability row fixed** (was "Aim 】 -- ▇ 】"; now "【Aim 】【 - - 】",
  `work/qa/ghostfix/panel.png`): the panel draws exactly two cells per label, so 1-unit labels drew a NUL glyph
  into stale tiles, and its open bracket uses the 【 glyph's right half. New `¦` unit break in script text (vwf.py
  UNIT_BREAK), D654D0 = `  【¦】`, 32 label rows reworded to one unit + icon / two units (fit.py `label_problems`;
  `docs/re/text.md` §Battle card panel ability labels; glossary updated). New probe `tools/debug/dstlog.lua`.
  **Phase plaques** 戦闘 -> BATTLE, 開始 -> START (S8, kind `phaseplate` in `gfx/battle_ui.tsv`, 0xB0AAAC /
  0xB0AEAC, red + pink copy each; the only two in that sprite area): BATTLE seen in game
  (`work/qa/plaque_en/z.png`), START rendered only (`work/qa/plaque/en.png`). Card 神速の剣士 -> "Lightning Blade"
  (matches the story tag; glossary). **Found:** the 陰/陽 badge on the panel is text icon 24/25 of the icon sheet
  0xACA06C (16x16, tiles TL TR BL BR, BG bank 15; `tools/debug/icons.py`), next to white 木火土金水 (6-10) and round
  element icons (11-15): these are the {Innn} icons used inline in text too.
  Session 14 (2026-11-22): **icons English** (D12): text icons 6-10 / 11-15 木火土金水 -> 5x7 pixel labels Wd Fi Ea Mt
  Wa, 24 陰 -> crescent moon, 25 陽 -> sun (`tools/gfx_icons.py`, `gfx/icons.tsv`; sheet `work/qa/icons_en.png`); the
  moon badge seen in game on the card panel (`work/qa/icons_g2/z.png`, board_turn.mss + bd/rand.txt, 1602 frames;
  hand_panel.mss keeps the old VRAM, use board_turn for panel checks); element text icons rendered only. **Card-frame
  emblems S20 English** (`tools/gfx_frames.py`, `gfx/frames.tsv`: 36 small 3x5 labels, 5 large 5x7; emblem found
  from its white kanji pixels; `work/qa/emb_en_small.png`, `emb_en_large.png`): "Fi" seen in game in the large card
  view (`work/qa/icons_g3/z.png`). check.py 37 passed, build sha1 49394591c614..
  Session 15 (2026-11-22): **S3 mini name labels English** (468 labels, group mini_labels,
  `tools/gfx_minilabels.py`, short forms `gfx/mini_labels.tsv`): a PPU dump (`work/qa/mini_ppu`) shows the label
  OBJ under the thumbnail's BG corner brackets, so only 26 px (tile x 5..30) is visible; 3x5 capital pixel font,
  centred; full name if it fits, else the TSV short form, else the last word (first word for High / Fudo / Park
  ..). "BAT" seen in game (`work/qa/mini_g1/z2.png`, board_turn.mss + bd/rand.txt). check.py 37 passed, build sha1
  348a9bc10f44..
  Session 16 (2026-11-22): **S28 attack-type badges English** 拳武飛術氣 -> FIST ARMS RNGD ART KI (group attack_types,
  `tools/gfx_attack.py`, `gfx/attack_types.tsv`, `work/qa/s28/a.png`): rendered only, the screen that loads it is
  not found (not in 8000 frames of battle_tutorial.mss). Checked, no work: sound test title is font text and
  English (S22 unused there); S19 leftover 0xC6A2D8 is frame line art. check.py 37 passed, build sha1 c9e04c1af2a0..
  Session 17 (2026-11-22): **link-error screen fully English, seen in game** (`warp.py MODE21`,
  `work/qa/p8s17/mode21_cmp3.png`): the overlay's "Link error." was cut to "Link err" (mode-21 setup copies a fixed
  0x4500 B = 276 tiles; the English overlay has 287) and the wallpaper 0xC0F358 still said 通信エラー x16. Fixes:
  `tools/patches.py` raises the copies (wallpaper 0x2000 -> 0x2900, overlay 0x4500 -> 0x4800), group link_error
  (`tools/gfx_linkerr.py`, `gfx/link_error.tsv`) reletters the 256x256 wallpaper LINK ERROR. Unhandled screen-table
  entries reviewed in one sheet (`work/qa/p8s17/unhandled_screens.png`): no other text left except the sutra board
  C165E8/C26298 (W13, art).
  Also session 17: **S17 card-pick plaques** Sell a Card / Trade a Card / Discard a Card (group shop_plaques,
  `tools/gfx_shopplaques.py`; "Sell a Card" seen in game; trade / discard plaques rendered only), sell-screen 早
  badge -> fast-forward mark, text icon 1 売 -> "Tr" (both seen). **Bug fixed:** the deck-editor tab patch forced its
  64-tile block to OBJ tile 704, which the sell screen's "Value=" glyphs also use ("Own---" on the selected tab):
  TABS_NEW now lets the game's allocator place it (tiles ~550-613; deck editor and sell screen rechecked,
  `work/qa/p8s17/tabs_fix.png`). Help rows D72434-D724BC got a fourth blank unit (the count digit covered "cards").
  Story gate 0 open (`zz_recheck17_20261122.tsv`, also covers sessions 13-14's label edits). Sort popup not re-seen
  after the allocator change (routes tried did not open it; it is fixed at 640-703, above the block).
  Session 18 (2026-11-22): **sutra board (mode 7, W13) English, seen in game**: the ten sin labels are selectable
  zones, so BG + red highlight sprites redrawn with the glossary names (group sutra_board, `tools/gfx_board.py`;
  tiles moved to 0xFC0000, setup copy-size literal 0x080567E4 raised; cursor walked over each label,
  `work/qa/p8s18/bm_z.png`; D13). Open graphics rows triaged (`docs/re/graphics.md`): S8 0xB1AC8C Siddham art, S14
  LZ77 creature art, S23 = title-screen talisman art, C37968/C37D88 shop icons: no work; S25/S26 = boot logos
  (mode 13), kept under D5 (D13). New probes `tools/debug/srcall.lua` (every ROM source a run loads) +
  `tools/debug/srchits.py` (filter logs by asset), `ppuat.lua` takes `AT={f1,f2}`. Warp MODE11 / MODE19 give blank
  screens (mode 11 needs setup). check.py 37 passed; build sha1 82aef7599a18..
- **Next (phase 8):** (0) graphics left: S16 0xC03F88 link-room badges (look like 待機中 / 通信中; loaded only in
  link-room sub-state 2, 0x0805BFE8: force the sub-state or poke it to see them, then redraw); 0xD280D0 (title
  set, table 0xD289A0) unidentified; trade / discard plaques (S17) in game (trade room -> Trade, needs cards). (1) see an element text icon ({I006}-{I015}) in game (card text popup of a Ward/Slay/Bane card)
  and a large frame (39-43). (2) a land / spell mini label in game (thumbnail of a non-character card on the
  panel). (3) S29 tutorial
  overlays + tutorial panel 0xD35868/0xD333B8 (match the English panel). Remaining graphics
  text: find where S28 attack badges show (card info screens?); find where VS / CLASH / Attack-Wait show (srclog.lua with SRC_LO=0x08ACCCCC over a longer or
  link battle); the name entry's kana grid (G7, English layout with the u16 grids below);
  邪気封印 card art,
  rematch menu graphics 0xD65298 if any (the menu seen was font text). Then a full English tour, verdicts per chunk
  (in an Orca worker: read the sheets yourself in a fresh pass, one verdict file per chunk; `codex exec -s
  read-only` after 2026-11-26); `inkbox.py` on choice/centred boxes; stress saves (needs save fields mapped);
  English name entry (u16 kana grids 0xD16740 / D6E56C / D72F00). Checks carried from phase 6: card-panel range
  CF24B0-CF2A00, battle-opponent name width (160 px), haiku list layout, sound test layout. The fit
  lint's unit budgets depend on the encoder built from all text, so an edit can push an old row over: run
  `tools/check.py` and reword the row it names. Rows of kind `grid` are not translated. Notes: system strings are often pieces joined
  at run time (turn banner 符咒士 / name + の / ターン; deck-editor prompts with 真神 and counts; deck help line 1;
  `　　枚` slots that receive numbers): check the joined line. The sound test body D1BD60 is written straight
  into d1.tsv as raw full-width bytes (ＢＧＭ / ＳＥ / ＤＬＧ / ＶＯＸ, 3 cells each: the counters draw from cell 5);
  the digit table D1BDC8 is kind `grid` (tools/extract.py GRIDS). Yes/no option lines are fixed:
  `[81][40]Yes[81][40]No`. 3 040 rows repeat an earlier `jp`: reuse translations by id. System strings that
  outgrow their slot now move to SPILL after the packed scenes (`strslots.write`, only when every pointer site is
  trusted and no alias points mid-string; the copy ends in a zero u16 because the printers stop on `ldrh` == 0).
  Sound test checked after it: `work/qa/warp/sound_test/final.png`. The haiku list (D16A40-D16F54) may be drawn
  vertically on the haiku screen's right strip: not yet seen in game; check in phase 8. tools/fit.py now gives
  CF24B0-CF2A00 (possession effects, 4-5 JP lines) the card_spell_text budget instead of the 3-line popup: inferred
  from the JP line counts, check in game.
- **Done:** Phase 5 engine spike and marker build (2026-11-22). VWF engine proven in game (`tools/vwf.py`,
  `fonts/vwf.txt`, D8; `docs/re/text.md` §Font) for both text routines (BG glyph routine 0x08003B84 and printer B
  0x0800455C, sprite text). Marker build `build.py --marker` boots and shows ids; probe tour 194/194
  (`work/qa/marker_gl`), no Japanese left outside extracted rows except B39.0020's staff-roll kanji (kept on
  purpose). Non-text: name-entry grid D6E56C-D6E710 and deck-name grid D72F00-D730A4 are kind `grid`; D6E3D4
  同期テスト中 is real link-debug text. Width gate: every reachable variant measured in game (dialogue, choice,
  tutorial pages, haiku, yes/no, enemy quote, card panel fields, printer-B popup, turn banner, rematch menu, board
  banner, card / deck prompts, deck help, sound test). Only the link-cable messages (D78E04-D79138) are a guess
  (needs a second GBA). Glyph torture line passed in a dialogue box (`work/qa/torture/`). Battle tooling:
  real-battle states `work/states/board_turn.mss`, `defeat.mss`, `hub_real.mss`; life variables verified
  (`docs/re/game.md` §Chapter battles: poke to force defeat or victory).
- **Done before:** Phase 4 extract: `tools/extract.py` -> `script/scenes/<B05|A3.2>.tsv` (170 files, 14 526 lines + 21
  choices) and `script/system/{cf,d1,d6}.tsv` (2 677 pointed strings), columns `id kind max jp en notes`, notation
  `tools/textcodec.py`; `build.py` inserts `en` (else `jp`); `tests/test_extract.py`. Phase 3 identity build
  (`tools/scenes.py`, `tools/strslots.py`, `tests/test_identity.py`). Phase 2 debug tool `tools/debug/warp.py`
  (194 rows, `--all --states`), save editor `tools/debug/save.py`, probes in `tools/debug/`. Phase 1 recon
  (`docs/re/text.md`, `docs/re/graphics.md`). Step 0 setup.
- **Carry-overs for phase 8:** scenes spill into SPILL (0xE62000+) in the full build; alias 0xCF4DC unverified in
  game. Boxes that are tight for English (choice 112 px fixed, card_skill 30 px, tutorial pages per entry) may want
  engine widening if the tour shows clipping.
- **Gaps in the debug tool (non-blocking, close before phase 8):** no normal path to the sound test (`sound_test`
  warps to mode 20). Save fields beyond names and chapter (cards, deck, money) unmapped; needed for stress saves.
- **Open bugs:** none.
- **Waiting on the user:** Non-blocking: staff-roll name readings (B39.0001-0064) are romanized from the kanji
  without a source; B39.0020's 﨤町 孝 ("Takashi Hazamachi") is a guess. Corrections welcome. Non-blocking: B04 shows a girl-player branch ({name2}-chan rows, B04.0174 老爺と少女), so
  the player's gender may be selectable; the glossary note "player is male" was softened to "neutral where the JP
  is"; confirm from the name-entry flow when QA reaches it. Keyboard input in the Mesen window not checked by hand (headless worker); scripted input
  verified. `codex exec` review hit its usage limit until 2026-11-26. Non-blocking: the five-element emblems
  木火土金水 on card frames (S20) and the rarity legend (S27) default to English redraws in phase 8 unless the user
  wants the kanji kept as icons; the sutra board (W13) is treated as art unless the user wants it translated. The
  link-cable message budgets are guesses (no second GBA in the emulator).
