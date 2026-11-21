# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate (next; phase 5 done 2026-11-22). Last build: `build/tmgfh_en.gba` 2026-11-22, sha1
  8d9efb85a8f2.. (built from `script/`, identical to the dump), smoke ok. Marker build `build/tmgfh_marker.gba`
  sha1 91c3d9342694.. (after the deck-name grid change).
- **Next:** phase 6, translate in batches (`references/translation.md`). Budgets per box variant are in
  `tools/windows.tsv` (columns variant / applies_to / lines / px / last_px / units / status / evidence); no lint reads
  it yet: the fit lint (VWF widths via `tools/vwf.py ext`, per-variant px and line counts, the dialogue last-line
  218 px, per-entry tutorial limits, `{&..}` numbers and `{I0xx}` 16-px icons counted) is the first job before the
  first batch. Rows of kind `grid` are not translated. Notes for translators: system strings are often pieces joined
  at run time (turn banner 符咒士 / name + の / ターン; deck-editor prompts with 真神 and counts; deck help line 1;
  `　　枚` slots that receive numbers): check the joined line. The sound test body D1BD60 keeps its full-width cell
  layout (label <= 64 px in cells 1-4, then the JP spaces and ／). Yes/no option lines are fixed:
  `[81][40]Yes[81][40]No`. 3 040 rows repeat an earlier `jp`: reuse translations by id. Slots that grow past `max`
  need relocation (phase 7; build raises today), so a batch check against `max` is informational until then.
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
- **Carry-overs for phase 7:** the scene region has no slack, so longer English needs the spill region (free-space
  candidate 0xE61678+, trap-test it); verify every slot's pointer sites before relocating (alias 0xCF4DC
  unverified); English name entry needs the u16 kana grid at 0xD16740 (and the deck-name grid). Boxes that are too
  narrow for English (choice 112 px fixed, card_skill 30 px, tutorial pages per entry) may want engine widening.
- **Gaps in the debug tool (non-blocking, close before phase 8):** no normal path to the sound test (`sound_test`
  warps to mode 20). Save fields beyond names and chapter (cards, deck, money) unmapped; needed for stress saves.
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen window not checked by hand (headless worker); scripted input
  verified. `codex exec` review hit its usage limit until 2026-11-26. Non-blocking: the five-element emblems
  木火土金水 on card frames (S20) and the rarity legend (S27) default to English redraws in phase 8 unless the user
  wants the kanji kept as icons; the sutra board (W13) is treated as art unless the user wants it translated. The
  link-cable message budgets are guesses (no second GBA in the emulator).
