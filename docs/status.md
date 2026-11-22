# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator (started 2026-11-22). Last build: `build/tmgfh_en.gba` 2026-11-22, full English,
  sha1 f29d33d734e0..; smoke ok (`work/qa/smoke`), check.py 37 passed.
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
  **Deck editor graphics found, not redrawn yet (S19):** header 符咒編集 = OBJ 128x32 (two 64x32, 0x800 B) at 0xC6C078
  (OBJ bank 10); button sheet 0xC66C18 = 32x16 OBJ halves (0x100 B each, OBJ bank 3): row 1 全体|確認 呪符|登録
  呪符|削除, row 2 a second 全体確認 + 登録|枚数, row 3 装備 編集 複写 削除 名前 (deck submenu, each one 32x16 button)
  then category tabs with icons 持ち符 売買符 人物符 土地符 法術符 結界符 憑依符 + 全 (shown by 全体確認,
  route `6 a` from deck_edit). Render: `sprblock.py rom/base.gba C66C18 32 16 36 <ppu .pal.bin> 3 out.png`. The
  labels have a textured box: re-letter on a cleared copy of the box (like bg4_edit's `patch`). Also 登録枚数 label.
  Name entry (`name_entry` row) is all Japanese graphics (名前は？ 苗字 名前 進む 戻る 終了 かな カナ 漢字 + kana grid).
- **Next (phase 8):** remaining graphics text: deck editor (S19, see above); name entry screen (G6/G7); booster-pack
  select header (screen 0xC5F760, map looks non-standard); help UI (S19 0xC6B118 両隣 左行 右行); battle UI (S6/S9/S10, sprites/screens 0xB4xxxx);
  vertical scene captions (W12/G5, S11/S12); card class labels (S1), card/skill name art (S5), 邪気封印 card art,
  emblems (S20), rarity legend (S27), card type icons (S28), info-screen labels (S29), sound test labels (S22),
  defeat/rematch (S9, 0xD65298), credits role captions + end card (W10/W11). Then a full English tour, verdicts per chunk
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
