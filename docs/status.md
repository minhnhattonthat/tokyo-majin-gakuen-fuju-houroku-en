# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4. Extract (not started). Last build: `build/tmgfh_en.gba` 2026-11-22, sha1 8d9efb85a8f2..
  (identical to the dump), smoke ok.
- **Done:** Phase 3 identity build (2026-11-22): `build.py [--identity]` unpacks and repacks all 170 story scenes
  (`tools/scenes.py`: full opcode table, 14 526 lines + 21 choice menus, label offsets recomputed, tables A/B
  repointed, multi-region packing) and 2 665 pointed system string slots (`tools/strslots.py`, three ranges);
  output byte-identical, `tests/test_identity.py` (also: a lengthened / shortened line re-parses equal and spills
  the last scene into a second region). In game: a build with every scene shifted by 2 bytes played B05 and A3.2
  normally. Scene format and opcode lengths in `docs/re/text.md`.
- **Done before:** Step 0. Phase 1 recon (`docs/re/text.md`, `docs/re/graphics.md`). Phase 2 debug tool:
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
- **Next:** phase 4, extract to `script/` (one file per scene / string range) on top of `scenes.parse_all` and
  `strslots.scan`, with a `tbl.py` table for Shift-JIS plus the codes (`rt`, `wc`, `Innn`, `&..`, 01 00 / 02 00
  name variables), roundtrip and coverage tests. Open questions for phase 4: `strslots` takes a pointed string only
  if it decodes as text, so check the ranges for unpointed text (struct pointers inside 0xD63xxx, tables 0xE61108..)
  and for aliases (pointers into the middle of a string, e.g. 0xD1AA04/0xD1AA24); verify pointer sites before any
  relocation (some hits come from graphics). The scene region has no slack: longer English needs the spill region
  (free-space candidate 0xE61678+, trap-test in phase 7).
- **Gaps in the debug tool (non-blocking, close before phase 8):** the defeat / rematch screen (敗北 banner S9,
  再戦する 終了する) is not reached: battle life candidates and the poke test in `docs/re/game.md`. No normal path to
  the sound test found (`sound_test` warps straight to mode 20). Save fields beyond names and chapter (cards, deck,
  money) unmapped; needed for stress saves in phase 8.
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen window not checked by hand (headless worker); scripted input
  verified. `codex exec` review hit its usage limit until 2026-11-26. Non-blocking: the five-element emblems
  木火土金水 on card frames (S20) and the rarity legend (S27) default to English redraws in phase 8 unless the user
  wants the kanji kept as icons; the sutra board (W13) is treated as art unless the user wants it translated.
