# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator (started 2026-11-22). Last build: `build/tmgfh_en.gba` 2026-11-22 (session 9),
  sha1 fb150f4b913c..; check.py 37 passed.
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
  **Found, not fixed (Important):** a code-area string table the extractor never saw, 0x06485C-0x064A2A, 8-byte
  slots, NUL-ended SJIS: the 47 prefectures (和歌山県 .. 愛知県, reverse gojuon order) shown **vertically** in the
  Birthplace? box (still Japanese in the English build, `work/qa/prof_en/z.png` left), then 両者 相手 自分 左 右 除去
  破壊 ＋ － 全ての and ０１２３４５６７８９ (card-effect pieces joined at run time? check card text that names targets).
  Needs: find the pointers to these slots (likely a pointer table near 0x0648xx/0x064Axx or literals), extract them
  as a system file, and for the prefectures either romanize short names in a horizontal list (printer change) or
  find the vertical draw routine; then sweep the code area 0x000000-0x0C0000 for other SJIS runs (`jp_left.py` with
  `--sjis` but no `--gba-ptrs` filter) since `--gba-ptrs` missed these.
- **Next (phase 8):** the code-area strings above first. Remaining graphics text: S19 leftovers 0xC6A2D8 (deck-editor window frame sheet:
  check for labels); find where VS / CLASH / Attack-Wait show (srclog.lua with SRC_LO=0x08ACCCCC over a longer or
  link battle); S7 large numeral cards 0xAE5FDC..; the name entry's kana grid (G7, English layout with the u16 grids below);
  card class labels (S1), card/skill name art (S5), 邪気封印 card art,
  emblems (S20), rarity legend (S27), card type icons (S28), info-screen labels (S29), sound test labels (S22),
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
