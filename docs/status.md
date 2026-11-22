# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator (started 2026-11-22). Last build: `build/tmgfh_en.gba` 2026-11-22 (session 19; sessions 20-29 did not
  rebuild it, because the coverage runs use it; unbuilt there: session 22's 4 text edits, session 23's haiku fix,
  session 24's tab-sprite fix + 2 text edits, sessions 26-29's graphics + D64260, session 30's D72710, session 31's
  D72824/D72830/D728A8/D728D8/D728EC/D72958/D72A84/D72A94, session 33's warn_box), sha1 82aef7599a18..; side
  build with everything: `build.py --out work/next/tmgfh_en.gba` (sha1 36135f37..); check.py 38 passed.
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
  Session 19 (2026-11-22): **text coverage tooling** (release gate, `emulator-qa.md` §Text coverage). `build.py`
  now writes `build/strings.tsv` (17 151 rows: every scene line / choice and pointed system string, kind `grid`
  left out, at its address in this build; code-area pieces/prefectures not listed). `tools/cover.py`: `scenes`
  (warp + mash every story scene with `$SKILL` textcover.lua, route `tools/routes/newgame_fast.txt` = Text Speed
  Fast + Effects Off, `--mash 4 --mash-hold 2` ~43 frames a line), `scenes --branches` (one run per branch option,
  `tools/debug/forcebranch.lua BRANCH=k`), `gaps` (rounds restarting each scene at the label before its first
  unread line, `tools/debug/startlabel.lua LABEL=n`), `rows` (the scenes.tsv rows), `report [--by-scene]`
  (textcover.py on `work/qa/cover`, using the strings.tsv copy kept there). `warp.py` gained `--route` and
  `--mash-hold`. Findings in `docs/re/text.md` §Story scene format (branch ops, loader = label seek).
  **Result so far:** plain pass over all 170 scenes ok; 9 543 of 17 151 unshown (system 2 532 / 2 604; A event
  scenes ~75% unshown = the 9-way emotion branches; B chapters stop where the chapter battle is, e.g. B18 after
  line 460). The `--branches` pass (10 jobs) was **stopped by Claude Code for low system memory** after branch0 and
  part of branch1: re-run with `--jobs 4` at most. B18 from label 70 was proven to read 461-853.
  Session 20 (2026-11-22): `cover.py scenes` now **resumes** (skips scenes whose run dir has final.png). The
  `--branches --jobs 4` pass was started in the background (log `work/qa/cover_branches.log`; branch0 done, branch1
  ~half when this session ended; it is slow: ~150 runs per branch). **Card collection mapped** (`tools/debug/
  save_layout.md`: 4-byte records at save 0x06DC, kind byte decoded from 0x08052F28); `save.py set --add-cards`
  (tested) builds `work/saves/allcards.sav` (every card owned, deck editor counts 282/52/83/30/27). **Card text
  coverage:** routes `tools/routes/allcards_browse.txt` (characters: Deck Edit -> View All -> card view, RIGHT steps
  a card, down does not) and `allcards_{land,spell,barrier,possession}.txt` (tab = down xk), run with emu.py `--sav
  work/saves/allcards.sav --script textcover.lua --var RANGES=...` into `work/qa/cover/cards_*`; **sound test**
  route `tools/routes/sound_test_cover.txt` (`warp.py MODE20 --route ...`, a raw spec so --frames applies) into
  `work/qa/cover/sound`: all track names shown. Battle runs (board_turn.mss + `work/qa/bd/rand.txt` 12000 f;
defeat_quote.mss) into `work/qa/cover/battle_*`: +45 only (each opponent has its own quotes: needs one battle per
chapter opponent, e.g. warp each chapter battle and poke life to end it, `docs/re/game.md` §Chapter battles).
System unshown 2532 -> 1843. What is left in system (by prefix):
  D645E4-D650xx person-name lists (xn/yn, 白岐, 九龍主人公 ..: where shown is unknown, maybe link/free-battle
  opponent lists), D6E8-D6EA long ability labels 【変生】.., CF72 short element-ish words, battle quotes D67C/D6D3/
  D6D6.. (enemy taunts: need battle runs), D725/D72A deck/discard prompts, D78F link-cable. **Choice boxes checked
  (B):** JP and EN both left-align options at x~66 (`work/qa/choice_cmp.png`, new probe `tools/debug/
  choiceshot.lua` screenshots while the 0F choice helper waits): not centred, inkbox not applicable (windows.tsv).
  Polish note: card view count line D72810 reads "1 cards, # 1" (slots are N then index); reword when rebuilding.
  Session 21 (2026-11-22): system unshown 1843 -> 532 (no rebuild). **Enemy quotes all shown** (820 = 41 quote
  lists x 20): opponent records 0xD6E17C (12 B: u32 quote list, u16 char, u16 life, u32 level; getter 0x0803D7AC;
  index = byte [0x0300756C]+0x7F1; 43 records, 40-42 share a list), quote task [0x030035B8] (`docs/re/game.md`
  §Opponents and enemy quotes). New probes
  `tools/debug/forceopp.lua` (any opponent in a battle/rematch) and `quotecycle.lua` (loops the quote box through
  every quote of OPPS, shot `q<opp>_<idx>.png` each): runs `work/qa/cover/quotes_{a..e}` (board_turn.mss +
  bd/rand.txt, ~155 frames a quote). Quote box checked: sheets `work/qa/quotes/sheet_00..17.png`, rightmost text
  pixel <= x 142 in the box (frame at 144), 3 lines max; q26_02 is an empty string in the original too. Verdict
  (self, fresh pass over sheets 00 + 10 + the 8 tightest): ok. **Sound test DLG/VOX** route
  `tools/routes/sound_test_dlg.txt` (steps all 282 DLG + 39 VOX entries: the DLG row shows each speaker's name, i.e.
  the person-name table 0xE5F71C) -> `work/qa/cover/sound_dlg`. **Rules help** (Start in the hand phase) route
  `tools/routes/rules_help.txt` from `work/states/hand_panel.mss` (A on Basic Rules replays the tutorial, so it starts
  one down; A/down pairs walk every topic) -> `work/qa/cover/rules_help`: D6E71C-D717D4 all shown.
  Session 22 (2026-11-22, no rebuild yet): system unshown 532 -> 262. **Battle message table** 0xD7A700 mapped
  (`docs/re/text.md` §Battle message table and popups): all 270 of its unshown strings (prompts, 100 character
  ability descriptions, possession / barrier / spell / land effect texts) shown in the real type-10 popup by new
  probe `tools/debug/popcycle.lua` (state at a popup call, then load + swap r0 per string; run
  `work/qa/cover/popups`), QA shots `work/qa/popups_qa/` (best of 4 hold timings; sheets + manifest + verdicts
  `self_20261122.tsv`: 4-line possession texts spill in this 3-line box but JP has 4 lines too, so their real window
  is another one, not found). **Text edits (not yet built):** CF2B68, CF44CC, CF4558, CF4608 were 4-5 lines vs JP 3:
  reworded to 3 lines (fit 0 problems, check 38 passed); after the rebuild re-run popcycle on those 4 and re-init
  the popups manifest. Element text icons now seen in game (Ea Fi Wd Mt moon in the Ward/Slay/Bane popups). **VS
  screen seen in game** (rematch from defeat_quote.mss, `work/qa/p8s22/vs_seen.png`, f3400 of `60 -`..mash 30).
  **Stale state:** board_turn.mss carries an old build's RAM copy of the opponent name (turn banner shows 常世の使者;
  a rematch on this build shows "Tokoyo Envoy"): not a bug, but make a fresh battle state before final battle QA.
  The VS plate shows the player name 緋勇龍麻 from the save: check a cold new game on the English build shows the
  English default. New probe `tools/debug/popuplog.lua` (logs popup calls). Rules help 【Abilities】 = last topic
  (down x17), its A pages are D6E8xx text, not the popup table.
  Session 23 (2026-11-22): **bug fixed: haiku rewards were unobtainable.** The haiku list D16A40-D16F54 is never
  shown: the haiku club (mode 16) strcmps the kana typed on its hiragana grid against it (table 0xD16940 = haiku ptr,
  reward card u16, 2 bytes; strcmp 0x08064098 called at 0x08009DA6, its only caller), so the English text matched
  nothing. The 32 rows are kind `grid` now (`tools/extract.py` GRIDS; meaning kept in notes), D14. Haiku input screen
  English: header 一句どうぞ -> "A haiku, please", buttons 改行 / 戻る / 終る -> NEXT LINE / DEL / END (group
  `haiku_input`, `gfx/haiku_input.tsv`, new `gfx.bg4_inplace`: keeps tile indices, because the grid's tiles double as
  the entered-kana sprites: a retiled set garbled them; grown sets go to 0xF80000 with the table's byte count
  raised). Proven in game on the side build: `tools/debug/haiku_route.py "ああねむい ねればねるとき ねちまおう"` from
  `work/states/haiku.mss` gives "Oh. A fine haiku..." + card "Drowsy Boy", same as the JP ROM
  (`work/qa/haiku_t_en/cmp.png`, `z.png`). New tools: `tools/debug/covrun.py` (one coverage run of a menu route into
  work/qa/cover/NAME, prints the system strings it newly showed), `tools/debug/screen_png.py` (render a 4bpp screen).
  `cover.py rows` (every scenes.tsv row with textcover) was run for the first time (`work/qa/cover/rows`). Deck
  submenu covered (`deck_sub2`, `deck_sub3` from new state `work/states/deck_edit_all.mss` = allcards.sav, English
  build, deck edit screen): help texts Edit/Copy/Delete/Name/Equip/Add, Are you sure?, Is this OK?, equipped deck
  can't be deleted. Shop booster buying needs value: "Not enough value" (money field not mapped: map it, then
  covrun the buy flow from shop.mss: D78A3C-D78C8C). **allcards.sav was made from the JP ROM** (deck named 真神,
  JP default names): after the rows run, remake it (`save.py make --rom build/tmgfh_en.gba`, then `set
  --add-cards`) so menu shots show the English defaults.
  Session 24 (2026-11-22): **bug fixed: sell-screen tab sprites garbled** (Trade badge and the Barrier/Possession
  tabs showed popup / card-name pixels after the sort popup or a card view; JP clean). The 64-tile English tab
  block went through the bump allocator to OBJ tiles 598-661, over the game's fixed 640+ users (sort popup 640-703,
  card view text 640-683). JP dumps (new `tools/debug/objtiles.py` = tiles the visible OBJs use; `dstlog.lua` +
  new `dstranges.py` = every OBJ VRAM write by writer) show only 716-767 is never written there, so
  `tools/patches.py` now splits the block: tabs 0-5 at fixed 716-763, tab 6 + blank through the allocator at
  598-613 (JP footprint, still 2 loader calls), via a hook at 0xFDF800 (own tiny Thumb assembler `patches.thumb`,
  trampolines in the old TABS_FN bytes). Checked on the side build: sell screen after popup + card view
  (`work/qa/p8s24/fix2500c.png`), deck editor walk (`deck_cmp.png`), dstlog shows no other writer of 716-767.
  New probe `tools/debug/modeswap.lua` (FROM/TO: swap a mode entry, e.g. the hub of a loaded save -> shop 9):
  `work/states/shop_all.mss` = shop with allcards.sav (current build), `shop_all_jp.mss` (JP). Sell flow:
  Sell -> A picks the tab -> A picks the sort key -> card grid (right steps) -> A card view -> A sell prompt.
  **Text:** D72B34 "Sell card for [n] P." (the value is drawn at unit 6 of line 1; the old slot sat on line 2),
  D72810 "[n] held, # [m]" (was "1 cards, # 1"); both seen in game (`work/qa/p8s24/sellfix.png`, `sellfix2.png`);
  story gate 0 open (`zz_recheck24_20261122.tsv`). Coverage runs `cover/sell1..3` (+6 system strings). Branch
  pass resumed in the background (branch3 ~125 of ~165 when the session ended).
  Session 25 (2026-11-22): haiku password table for the release README: `tools/haiku_list.py` -> `docs/haiku.md`
  (kana, typing romaji, meaning; D14 done). Branch pass resumed: branch3 finished, branch4 reached A8 when the
  run was killed for low system memory (incomplete dirs branch4/A8_0..A8_3 left: delete them, then resume; consider
  `--jobs 2`). gaps + report not run yet.
  Session 26 (2026-11-22): branch pass resumed with `--jobs 2` (branch4 finished; still running, cover.py PID
  37736, when the session ended: check `work/qa/cover_branches.log` and whether a Mesen/cover.py of this repo runs
  before starting `gaps`). **Battle-tutorial art English** (S29 + the 8bpp panel picture 0xD35868, group
  `tutorial`, `tools/gfx_tutorial.py`; art made once by `tools/debug/tut_compose.py` into indexed
  `gfx/tutorial/<ENTRY>.png`, details in `docs/re/graphics.md` S29): panel reads like the real English panel for
  the card (Fighter, 【Blst】【Cov】, 1Prce 2B(moon) 3Mrph, Took 40 dmg, BATTLE / Leaf, FIGHTER, Fi), highlights
  rebuilt from it, callouts Symbol / Origin / Element, captions "Hits for 50", "cuts damage by 30", "Characters get
  1Prce at [tree] Mani". D64260 "background" -> "origin" to match (story gate 0 open, `zz_recheck26_20261122.tsv`).
  Seen in game on the side build (`work/qa/p8s26/tut2`, `tut3`: battle_tutorial.mss + `--mash 20`, 6000 f; the
  warp row's own run stops mashing at f2700). check.py 38 passed. **Found, not fixed:** the tutorial's field
  cards are their own pre-drawn 64x64 **8bpp** OBJs with Japanese baked in: 0xD3CA78 (神速の剣士, grey emblem) and
  0xD3EB78 (格闘家, 木 emblem), palette = the 0x80 B before each, (ptr, size) entries 0xD63A38 / (0xD3EB78 not in
  the 0x1000-size scan: find its entry) and 0xD63A50 (0xD3DAF8) / 0xD63A80 (0xD40BF8), whose format is not 8bpp
  64x64 (render garbled): reletter the name strip (mini-label style: LIGHTNING / FIGHTER) and the emblem (Ea? / Wd)
  the way `gfx_frames.py` does. Seen at f1960 of tut3 (`work/qa/p8s26/fieldcard`, PPU dump there). Also check
  in a fresh real battle that card thumbnails on the panel show English emblems (S20) and mini labels: the
  hand_panel.mss / board_turn.mss shots show kanji emblems, probably stale VRAM in those states.
  Session 27 (2026-11-22): **tutorial field cards English** (group `fieldcards`, `tools/gfx_fieldcards.py`; details
  `docs/re/graphics.md` S29): LIGHTNING + Mt, FIGHTER + Wd seen in game on the side build (`work/qa/p8s27/fc`,
  `fc2`; the callout highlight of the 木 disc on D63558 relettered Wd too); upside-down opponent cards (BLADE, Fi /
  Mt) rendered only. Side build sha1 ad9d2c3e..; check.py 38 passed. Branch pass still running (cover.py PID 37736,
  `--jobs 2`): branch4 done, branch5 started (A scenes).
  Session 28 (2026-11-22): **link-trade screen (mode 11) English, seen in game** (`work/qa/p8s28/m11en_z.png`): the
  S16 "link-room badges" 0xC03F88.. are mode 11, the link trade (warp blank because state 1 waits for the link; new
  probe `tools/debug/setreg.lua` forces it: `warp.py MODE11 --script tools/debug/setreg.lua --var AT=0x0805AEBC
  --var REG=0 --var VAL=1`). BG plaques 交換符 -> Trade (room_banners rows; `gfx_rooms` takes a palette base and band
  colour per screen), badges 待機中 / 選択中 / 確認中 -> Waiting / Choosing / Checking and buttons 登録 / 終了 -> Add /
  Quit (group link_trade, `tools/gfx_linktrade.py`); Waiting / Checking rendered only. State `work/states/MODE11.mss`
  (side build): cursor moves to Add / Erase / Quit but A does nothing without a partner, so the S17 "Trade a Card"
  plaque stays rendered only (waive with the link-cable texts). Side build sha1 7b51c7e5..,
  check.py 38 passed, smoke ok. Branch pass still running (PID 37736, branch5).
  Session 29 (2026-11-22): **save value (money) mapped**: u16 at save 0x06CC (RAM 0x03002EE0, max 9999),
  `save.py set --money N`, `info` prints it; neighbouring fields listed in `tools/debug/save_layout.md`. New saves
  `work/saves/hub_ch05_en.sav` (English build), `allcards_en.sav` (every card + 9999), `rich_ch38.sav`, `rich_few.sav`
  (starting cards + 9999: pack screen shows NEW), `cards999.sav`; states `work/states/shop_rich.mss`,
  `shop_rich38.mss`, `shop_999.mss`, `trade_room_all.mss`, `shop_after_pack.mss` (pack screen, mid-registration).
  **Shop booster purchase covered** (D78990-D78C8C, all 13): Kenpucho / Oboro Kitan bought for real; the 3 packs not on
  sale (Kouryu, Keppuroku, Gehocho: not unlocked by chapter 38 either) + "can't buy any more cards" shown in the real
  shop box by `popcycle.lua` (new vars `CALL_AT=0x08003AA0 LR=0x08057E2F`: the shop dialogue printer and its one
  call site), shots `work/qa/p8s29/buy_pop.png`: all fit. **Trade registration is on the pack-opening screen** (A on
  a card: "Register it as a trade card?" / "Remove its trade entry?"); the Trading Hall's Deck Edit is the normal
  deck editor. **Graphics found and fixed** (side build): pack-opening 次へ button -> "Next" and 新 burst -> "NEW"
  (group pack_open, `tools/gfx_packopen.py`), card **thumbnail** emblems 木火土金水 -> Wd Fi Ea Mt Wa (frame table
  entries 44-87, group thumb_frames, `tools/gfx_thumbframes.py`; these were the "kanji emblems on panel thumbnails"
  noted in session 26, not stale VRAM). All three seen in game (`work/qa/p8s29/pack_en_z.png`, `thumb_cmp.png`);
  details `docs/re/graphics.md` §session 29. Side build sha1 cb3b225f..; check.py 38 passed. System unshown now 202
  (list: `python -X utf8 work/qa/p8s29/unshown.py` -> `work/qa/p8s29/unshown_sys.txt`; 32 of them are the haiku
  rows D168-D16F that leave strings.tsv at the rebuild). Branch pass still running (PID 37736, branch5 at A2).
  Session 30 (2026-11-22, no rebuild): **pack-opening screen exit found**: the Next button sits left of the first
  card; `left` from card 0 focuses it (bright, arrows), `left` again wraps to the last card; A on it leaves. From
  `shop_after_pack.mss`: `30 -;6 left;54 -;6 left;54 -;6 a` -> shop menu (`cover/p8s30_packexit12`). New probes
  `tools/debug/modeset.lua` (write a mode at frame AT), `pokeat.lua` (one-shot u16 pokes, also behind a pointer),
  `ptrlog.lua` (log a state struct's fields when they change). **Sell-all of trade cards shown, all fit**
  (D724EC, D72710, D72748, D7277C, D727A0: `cover/p8s30_tradesell4`, `tradesell5`; route: shop_after_pack +
  register via A on cards, `modeset.lua AT=800 TO=9`, then Sell, down to the Trade tab, A, A, left (Yes), A).
  D72710 reworded "unchecked" -> "not one by one" (story gate 0 open, `zz_recheck30_20261122.tsv`).
  **Discard (collection cap) mapped, not yet shown:** card count = s16 0x03003818; the post-battle flow
  (function around 0x08048B66, struct [0x030035B8], context +0x36 == 4) sets substate +0x38 = 7 (discard) when the
  count > 5000 (literal 0x1388) and asks for count-5000 discards (D72548 at 0x08048E24). The shop instead refuses
  to sell packs at the cap, so the discard follows only a battle reward. `full5020_en.sav` (5020 cards) made.
  Post-battle pack screen (`pack_select_pre.mss` + `4 a;300 -;6 a`) reveals cards one by one; `left;left;a`
  there did not reach Next (cursor index differs), nor did 8 x (A, right, A) then 8 x left: find the Next focus
  on that screen (shot every 20 frames while pressing left), with count poked >= 5000 at frame 10
  (`pokeat.lua --var "POKES={[0x03003818]=5000}"`). Poking +0x38 = 7 on either pack screen did nothing.
  Session 31 (2026-11-22, no rebuild; side build 6719c493..): **discard flow shown, all fit** (D724BC, D726FC,
  D72528 + D72548 "5010 / cards now held. / 10 cards to discard.", D72C1C, D72C40, D72C70, D72C98, D72CB4, D72914).
  The discard screen is the shop's Sell list with sub-mode 4: the switch at 0x08043272 on [0x030035B8]+0x34 (0 deck
  edit 0x080464C9, 1 sell 0x08047D35, 2 0x0804808D, 3 link trade 0x0804D41D (bounces without a partner), 4 discard
  0x08048375); the cap re-prompt runs when you press B with count > 5000 (state 6 handler 0x08048D70). Route
  (`cover/p8s31_disc6`): shop_all.mss + `poke.lua POKES={[0x03003818]=5010} POKE_FROM=10 POKE_TO=12` + new
  `tools/debug/setregs.lua SETS={[0x08043272]={0,4}}`, then the sell route; D72C40 (Dragon Heir) by also forcing
  `[0x0804D912]={0,0},[0x0804D958]={0,-1}`. **Deck editor strings shown, all fit:** D721A8 (exit with 61),
  D721E4, D722F4 (equip a copy), D7231C (7th copy), D72868 / D728BC (forced at 0x0804A788 r5=4 / 0x0804A77E r0=-1:
  allcards has one of each card), D72AE8, sort badges AP-..Val+ (D7256C-D725B4) and kana-row badges Ha..Wa
  (graphics too) in the Add Card sort list (`cover/p8s31_sort1`, `sort2`). **View All slot strip** (task
  0x0804AD61): A on a card in View All -> slot cursor (left/right, wraps; slot 6 = trade list): D72984, D729A8/C0
  (rare, forced 0x0804AFDA r4=-1), D729E8-D72A28 (in a deck), D72A84/A94 register, D72AA4/AB0 unregister, D72958,
  D72A4C (forced 0x0804B15E r4=0; the count sprite "60" overlaps line 2 in JP too: original). States
  `work/states/deck_add_view.mss` (per-deck Add Card, Two Swords view), `viewall_card.mss` (View All slot mode).
  **Bug fixed (side build, seen):** the add/remove prompt joins D72824 + deck name + D72830/D728A8; VWF units take
  16 px cells and the name starts after them, so "This card -> " pushed the name off the box. Now "Deck [name] /
  gets this card." / "loses this card."; results D728D8/D728EC "got / lost this card." (`work/qa/p8s31_deckfix/z.png`).
  Also reworded D72A84/94 "Register it as / a trade card.", D72958 "Will be unlisted." (story gate verdicts
  zz_recheck31*, gate 0 open). New `tools/debug/covframes.py RUN ID..` (first frame + shot of each id in a cover run).
  System unshown now 136, 32 of them haiku rows D168-D16F (list `work/qa/p8s29/unshown.py`): CF64E8-CF7340 land/spell names + short labels, D652xx
  (value points gained, link error), D678D4/D6790C (Truce destroyed), D16 haiku rows, and link-cable / link-trade
  texts (D6E3xx, D72490, D726E8, D72B20-D72BF8, D78E04-D79138: waive, need a partner).
  Session 32 (2026-11-23, no rebuild): **system unshown 136 -> 89, all shown fit** (shots under `work/qa/cover/p8s32_*`).
  Post-battle reward machine 0x08011BB8 (state u16 +0x38 of [0x030035B8], table 0x08011BDC, 18 states; strings via
  0x08E5FBA0 = E5F71C idx 289..): state 2 "Gained 30/15 value points!" when 0x08000418(0xA0000000) != 0 (value =
  15 + 15 * (1 - byte [0x0300756C]+0x7F3)); state 4/5/6 Fuin Cave card reward on floors 5, 10, .. ([card] " was" /
  "obtained!"). Forced on a real victory (board_turn.mss + rand.txt + enemy life poke f1200, `--mash 20` through
  the pack screen): `setregs.lua` `[0x08011D8E]={0,1}` (+ `[0x08011DA8]={0,1}` for 15) and `[0x08011EAC]={0,1},
  [0x08011EBE]={0,4}` (obtained, f5220). Truce destroyed D6790C / D678D4: task 0x080235F4 (created by 0x080235B4),
  forced with `[0x0802368A]={0,1},[0x0802369A]={0,1},[0x08023710]={5,0},[0x08023712]={3,0|1}` (f1260). " was
  canceled." (D67978 + D67964, task 0x08031610, creators 0x0803676A / 0x0803B590 / 0x0803EA54 not reached in random
  play) shown in the same box by swapping the obtained flow's pointers (`[0x08011FAA]={0,0x08E63B50},
  [0x08011FB2]={0,0x08D67964}`; same printer 0x08018B4C and x/y). Slay / Remove D65910 / D658F8: `popcycle.lua`
  (list `work/qa/p8s32/slay_list.txt`, HOLD 20 for Remove). **Card names:** the View All browse routes stepped too
  fast and skipped cards: slow routes `tools/routes/allcards_{land,spell,barrier,possession,chars}_slow.txt` (right every
  60 f) showed the 16 missing land / spell / barrier / possession names + 2 land effect lines. **Character symbol
  tags** (CF7240-CF7350, table 0x08D7D72C, index = byte `b` of the owned-card record; allcards.sav gives every card
  b=16 "Kami"): `work/saves/symbols_en.sav` (character id b with b = 0..35) showed all 36 (widest "Cloud" fits).
  **Found:** "character records" 282+ of 0xD7ADE8 are the ability-label table 0xD7CCC0 (101 labels), not cards: a
  save owning ids 282-296 shows junk in JP too (`work/qa/p8s32/enemy_cmp.png`; run deleted). Ability labels 97-100
  (W{I007} W{I008} W{I009} Awkn) not seen; which card has them is unknown (ability ids are not plain record bytes).
  Session 33 (2026-11-23, no rebuild; side build 36135f37..): **system strings done except link + haiku replies.**
  Theft D78850 shown (board.mss: `right;right;up;up;a`, `cover/p8s33_theft`, fits). D78E04 "Fuin Cave data will be
  reset" = detour menu (hub item 0 寄り道) item 4 最初から降りる (`cover/p8s33_cavereset`, hub_dungeon.mss + `30 -;6
  a;200 -;4 x (6 down;30 -);6 a`; fits). **Bug fixed (side build, seen):** that box's header ⚠警告⚠ was baked
  Japanese BG0 tiles (0xC26298): now "Warning" (group warn_box, `tools/gfx_warnbox.py`, `work/qa/p8s33/warn_en`;
  graphics.md §session 33; raw-tile sweep of the other suspect screen blocks found nothing new). Ability labels
  97-100 (CF64E8-CF6500): no card record carries ids 96-99 (byte 0xD7ADF2 + 28 * card + slot, read at 0x08021446);
  shown in the real card panel by forcing `setregs.lua SETS={[0x0802144C]={0,96..99}}` (`cover/p8s33_abil96..99`,
  board_turn.mss + bd/rand.txt, f1600; 【W Ea】 etc. fit). D65308 / D65318 are link-battle setup (compare the two
  players' records 0x03001F00 + 72 * player): **waiver file `docs/text_unshown.tsv`** written (45 link-only rows).
  System unshown now 83 = 45 waived + 38 D16 rows: 32 haiku (leave strings.tsv at the rebuild, kind grid) and **6
  haiku-judge replies D1685C-D16914** (only seen on the side build: after the rebuild cover them with
  `tools/debug/haiku_route.py` from haiku.mss: a right haiku, a wrong one, the same one twice).
  Session 34 (2026-11-23, no rebuild of build/; side build `work/next/tmgfh_en.gba` c4ab6971..): **English name
  entry (G7, D15)**: romaji syllable grids (`tools/name_grid.py` writes the d6.tsv grid rows; lowercase on the かな
  page, capitalised on カナ, small-kana rows = consonants k sh ch j r t p s g; buttons relabelled abc / Abc), tight
  letters `vwf.TIGHT` so tsu / Tsu / Shi / Chi fit one 16 px cell, `fit.py` checks one unit per cell. Seen in game:
  both pages, typing ("Tatstsu", deck "sakaa"), `work/qa/p8s34/`. **Bug fixed (side build, seen):** the deck-name
  screen's frame bottom was garbled since the session 3 redraw (retiled set 240 tiles ran into run-time tiles 223+):
  new `gfx.bg4_refit` keeps the 222-tile set (`work/qa/p8s34/dn_fix_cmp.png`). **CLASH and START plates seen in
  game** (forced; graphics.md §Session 34); S28 badges are an unused asset; Attack/Wait panel and the tutorial's
  opponent cards not reached (no reference found / not in a 9000-frame tutorial). **`cover.py remap OLD --base
  COMMIT`** carries an old build's coverage to a rebuild for rows whose jp/en are unchanged (dry run on build 19:
  15 650 of 15 666 carry over; the 16 changed rows are session 22-31 edits, each listed with the old runs that showed
  them). New probe `tools/debug/valwrite.lua`. State `work/states/name_entry_ne.mss` (side build, name entry).
- **Next (phase 8):** (1) wait for the branch pass (PID 37736, branch8 when session 34 ended; it runs on
  `build/tmgfh_en.gba`, so do not rebuild before it ends), then `cover.py gaps --jobs 2` + `report --by-scene` to
  find unreachable scene lines (scene unshown 1461 before branch7/8). (2) Rebuild (everything since session 19 incl.
  warn_box, name grids, deck-name fix), then `mv work/qa/cover work/qa/cover_b19`, `cover.py remap
  work/qa/cover_b19 --base b359d4e` (build 19 was made from b359d4e), re-run only what it lists as changed (popcycle
  for CF2B68/CF44CC/CF4558/CF4608; the menu routes for the D72xxx rows: sessions 24-31) and the name-grid rows are
  kind grid (not in strings.tsv). Then `cover.py report` must exit 0 with `docs/text_unshown.tsv`. (3) Full English
  tour + visual-QA verdicts per chunk, inkbox on choice / centred boxes, stress-save sheets: longest typed names
  are now 4 romaji units (e.g. Şhi x4, ~64 px): `save.py set` writes Shift-JIS only, so add a raw-units option
  (codes from that build's `vwf.Encoder`) or type them on name_entry_ne.mss, then check dialogue, VS plate, profile.
  Earlier: (A) text coverage: the branch pass was resumed again in session 22 (`--jobs 4`, log
  `work/qa/cover_branches.log`; resumed again in sessions 23 and 24: branch0-2 done, branch3+ (A scenes only) running
  when session 24 ended). A rebuild moves 12 207 string addresses (scenes re-pack), so after the rebuild the whole
  coverage must be re-run: finish this pass first only to find unreachable strings. If no Mesen process of this
  repo is running (other projects' Mesen may be), resume it with `python -X utf8 tools/cover.py scenes --branches
  --jobs 4` (it skips finished scenes; delete any run dir without final.png first), then `tools/cover.py gaps --jobs
  4`, then `report --by-scene`. Scenes should reach ~0 unshown. Then rebuild (session 22 text edits + session 23
  haiku fix: the haiku rows leave strings.tsv as kind grid), move `work/qa/cover` away and re-run the coverage (or
  waive with a note naming the changed rows). System strings left (228 after session 23, total 4 781 of 17 151; list them with
  `cover.shown_ids()` against `work/qa/cover/strings.tsv`): CF64E8-CF7340 short labels and land/spell names,
  D720A0-D72C98 sell / trade-registration / discard prompts (sell: from `work/states/shop_all.mss`, flow in session
  24; trade registration = pack-opening screen and View All slot 6; discard, registration rules, sort and kana-row
  badges all shown in session 31; left: link-trade only), sutra board sin descriptions: 8 of 9 shown (`cover/board_sins`: board.mss, cursor
  move + A on each label); Theft D78850 not yet (find its label's cursor path),
  (D78990-D78C8C shop booster purchase: done in session 29), D6526C link error / D6E3D4 sync test / D78E04-D79138 link cable
  (waive: needs a second GBA). For each menu: `tools/debug/covrun.py NAME --state-in S --route-str ".."`.
  Release README: list the 32 haiku (kana, romaji, meaning from the d1.tsv notes) so English players can enter them
  (D14). Waive only what
  is shown unreachable in `docs/text_unshown.tsv`. Do not rebuild between coverage runs (cover.py refuses when strings.tsv
  changed; move `work/qa/cover` away and re-run all after a rebuild). Stress saves: `allcards.sav` is the
  full-list one; long names via `save.py set --surname/--name`; max value via `--money 9999` (`allcards_en.sav`); deck not mapped yet. (0) graphics left: (S16 link-trade badges done in session 28); 0xD280D0 (title
  set, table 0xD289A0) unidentified; trade / discard plaques (S17) in game (trade room -> Trade, needs cards). (1) see an element text icon ({I006}-{I015}) in game (card text popup of a Ward/Slay/Bane card)
  and a large frame (39-43). (2) a land / spell mini label in game (thumbnail of a non-character card on the
  panel). (3) done in session 27. Remaining graphics
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
