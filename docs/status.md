# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build (in progress). Last build: `build/tmgfh_en.gba` 2026-11-22, sha1
  8d9efb85a8f2.. (built from `script/`, identical to the dump), smoke ok.
- **In progress (phase 5):** VWF engine done and proven in game (`tools/vwf.py`, `fonts/vwf.txt`, D8; details in
  `docs/re/text.md` §Font). Marker build `build.py --marker` -> `build/tmgfh_marker.gba` boots, story boxes show
  【B05.0002】 etc. (marker build sha1 b70905c0c25d.., 2026-11-22).
  Session 2026-11-22 (2): **printer B** found: the yes/no prompts (CF1318-CF1564) are sprite text from a second
  unit routine 0x0800455C that decodes Shift-JIS itself; its marker drew blank. VWF now covers it (`hookb` in
  `tools/vwf.py`, stub at 0x0800497C; `docs/re/text.md` §Font), proven in game ("Save? / Yes No" in
  `work/qa/w3/hub_save`). `glyphlog.lua` logs both routines; `warp.py --var` passes probe variables.
  Probe tour finished (`work/qa/marker_gl`, 194/194 ok; the first 52 rows ran before printer B was probed):
  `glyphs.py --jp` shows no Japanese outside extracted rows (only B39.0020's staff-roll kanji `[FB][B3]`, kept raw
  on purpose); 2 181 ids seen. Non-text: the name-entry grid rows D6E56C-D6E710 now have kind `grid` (extract.py;
  out of the marker and translation, they change with the English name entry). D6E3D4 同期テスト中 is real (link
  debug) text, kept. Width gate in `tools/windows.tsv`: dialogue, choice, tutorial_page (per-entry boxes: limit =
  longest JP line in cells, 5 pages measured), battle_strip (box measured, ids unknown), haiku 160, yesno 128 with a
  fixed option line `[81][40]Yes[81][40]No`.
- **Left for phase 5:** measure the battle boxes not seen yet: enemy battle quotes (D68xxx-D6DBxx, 2 lines `{rt}`),
  card names (D64ADC..) and card effect text (D67xxx, D6790C), the battle_strip's string ids, sound test labels
  (D1BD60.., `{xn}` positioned). A mashed MODE15 run (`warp.py MODE15 --frames 6000 --mash 20`) only reaches the
  tutorial pages and goes black at ~f4070 on the original too; a real battle needs a save or route into a chapter
  battle (also the defeat screen gap below). Shop and hub menus are tiles, no text routine.
- **Done:** Phase 4 extract (2026-11-22): `tools/extract.py` -> `script/scenes/<B05|A3.2>.tsv` (170 files, 14 526
  lines + 21 choices) and `script/system/{cf,d1,d6}.tsv` (2 677 pointed strings), columns `id kind max jp en notes`,
  notation `tools/textcodec.py` (Shift-JIS plus `{rt}` `{nl}` `{name1}` `{I000}` `{&Sx0}` .., other bytes `[XX]`).
  `build.py` inserts `en` (else `jp`) from the files; the build from untranslated files equals the dump.
  `tests/test_extract.py`: codec roundtrip on every string, files equal a fresh extract, one row per unit, no
  uncovered kana-heavy run in code or the text banks (waivers: name-entry grid, three noise tables), `en` really
  lands in the ROM, slot overflow raises. The coverage scan found 13 strings `strslots` had skipped (range 1 starts
  at 0xCF12F0; struct-embedded text pointed from code / text tables) and one alias (0xCF4DC -> 0xD7080C+2). Details
  in `docs/re/text.md` §Extraction. 3 040 rows repeat an earlier `jp` (14 184 distinct): reuse translations by id
  in phase 6.
- **Done before:** Phase 3 identity build (2026-11-22): `build.py [--identity]` unpacks and repacks all 170 story scenes
  (`tools/scenes.py`: full opcode table, 14 526 lines + 21 choice menus, label offsets recomputed, tables A/B
  repointed, multi-region packing) and 2 665 pointed system string slots (`tools/strslots.py`, three ranges);
  output byte-identical, `tests/test_identity.py` (also: a lengthened / shortened line re-parses equal and spills
  the last scene into a second region). In game: a build with every scene shifted by 2 bytes played B05 and A3.2
  normally. Scene format and opcode lengths in `docs/re/text.md`.
  Before that: Step 0. Phase 1 recon (`docs/re/text.md`, `docs/re/graphics.md`). Phase 2 debug tool:
  `tools/debug/warp.py` + `warp.lua` + `scenes.tsv` (194 rows: all 40 chapter scenes, all 130 event scenes, every
  game mode screen, title submenus with and without a save, name entry, hub save prompt, both endings with the staff
  roll and the 完 card). `warp.py --all --states` passes every row from a cold boot (194/194 on 2026-11-22; each
  row's sheet in `work/qa/warp/<row>/`) and regenerates `work/states/<row>.mss`. A row passes on "WARP ok" (the
  loader read the expected table entry, or the game entered the expected mode) and not all of its last shots blank
  (chapters 3/16/24/27/29 have black voice-only stretches). Save editor `tools/debug/save.py` (layout `tools/debug/save_layout.md`):
  `make` writes the base save through the game's own 記録, `set` edits chapter and names with the checksum fixed,
  `test` loads it through 続きから (chapter-17 save renamed 山田 太郎 loads clean). Game state notes in
  `docs/re/game.md`; warp-reached screens added to `docs/re/graphics.md` as rows W1-W15. Probes: `varlog.lua`,
  `scenelog.lua`, `ramat.lua`, `poke.lua`, `loadcheck.lua`.
- **Next:** phase 5, engine spike and marker build (`references/pipeline.md` §Marker, `platform-gba.md`): find the
  dialogue / menu draw routine and glyph size (font 0xC6FB48-0xCE5748, glyphs drawn into BG VRAM at runtime), decide
  the English font path (VWF hook vs half-width glyphs). The encoder must not let English letters form the inline
  codes (`rt`, `wc`, `dc`, `pp`, `xn`, `I` + 3 digits, `&`..): the game reads them anywhere in a string, so plain
  ASCII "start" would break a line; the font decision settles the byte form. Then a marker build (`[id]` in every
  line, from `script/` via a marker `en`), flag non-text slots (candidates: layout strings like 0xD6E56C `ー　　　　`,
  debug text 0xD6E3D4 `同期テスト中`), measure every box variant's width in game (the width gate). Carry-overs: the
  scene region has no slack, so longer English needs the spill region (free-space candidate 0xE61678+, trap-test in
  phase 7); verify every slot's pointer sites before relocating (alias 0xCF4DC unverified); English name entry needs
  the u16 kana grid at 0xD16740.
- **Gaps in the debug tool (non-blocking, close before phase 8):** the defeat / rematch screen (敗北 banner S9,
  再戦する 終了する) is not reached: battle life candidates and the poke test in `docs/re/game.md`. No normal path to
  the sound test found (`sound_test` warps straight to mode 20). Save fields beyond names and chapter (cards, deck,
  money) unmapped; needed for stress saves in phase 8.
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen window not checked by hand (headless worker); scripted input
  verified. `codex exec` review hit its usage limit until 2026-11-26. Non-blocking: the five-element emblems
  木火土金水 on card frames (S20) and the rarity legend (S27) default to English redraws in phase 8 unless the user
  wants the kanji kept as icons; the sutra board (W13) is treated as art unless the user wants it translated.
