# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate in progress (started 2026-11-22). Last build: `build/tmgfh_en.gba` 2026-11-22 with B00-B03
  English, sha1 6e2fcc5dfb56.. (story_00 warp checked: `work/qa/pilot_zoom.png`). Marker build
  `build/tmgfh_marker.gba` sha1 91c3d9342694...
- **Progress:** batches b001-b004 merged (B00-B03, ~650 rows incl. repeats filled by merge). Batches b005-b006 (rest of
  B03-B04) are split in `work/tl/` (gitignored, this machine) and not translated yet. Remaining: B04-B39, every A
  detour scene, system cf/d1/d6 (~16 000 rows, ~360k JP chars). Staff roll ({dc} rows, B39) is left out of batches:
  translate by hand at the end.
- **How (each session):** read `docs/translator-brief.md`, `docs/style-reference.md`, `docs/synopsis.md` and the
  glossary (in parts). `python -X utf8 tools/batches.py split --only B05.,B06.` (chapter order: B then that
  chapter's A scenes; system last) -> translate `work/tl/bNNN.tsv` into `bNNN.out.tsv` (Write tool) -> `check` ->
  `merge` -> extend synopsis/glossary -> commit. No subagents in Orca workers and codex is rate-limited until
  2026-11-26: the worker translates itself, ~4-5 batches per context. Fit lint: `tools/fit.py` (all budgets from
  `tools/windows.tsv`, run by `tests/test_fit.py`); dialogue bodies are wrapped by merge (2 rows, 232/218 px,
  about 65 chars). Phase 6 done-when: batch check 0 errors everywhere, glossary current, a review pass with no
  Critical/Important (do it as a fresh read-only pass per chapter; codex once its limit resets).
- **Next:** b005. Rows of kind `grid` are not translated. Notes for translators: system strings are often pieces joined
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
