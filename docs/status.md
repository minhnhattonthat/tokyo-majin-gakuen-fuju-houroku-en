# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool (not started). Last build: none yet (2026-11-22).
- **Done:** Step 0. Phase 1 recon: text side in `docs/re/text.md` (Shift-JIS, control codes, pointer tables, story
  scene format, free space 0xE61678-0xFE0000). Graphics in `docs/re/graphics.md`: tour rows G1-G8, static sweep of
  every sheet (`tools/gfx_sweep.py`, rows S1-S29, ROM map), font at 0xC6FB48-0xCE5748, dialogue backgrounds LZ77 8bpp,
  card-frame table 0xD80BD4 (`tools/card_art.py`). `tools/gfx_zoom.py` re-renders any asset at chosen widths.
- **Next:** phase 2, the debug tool: scene warp by story-table index (tables at 0xD8211C/0xD82078, read at
  0x5E378/0x5E2F0) as `tools/debug/warp.lua` + `tools/debug/scenes.tsv`; include the screens the static sweep can't
  read (chapter cards, game over, ending, credits, the Tokyo map S23, the card info screens S26/S29, the sound test
  S22: find where サウンドテスト is reached), then add their rows to graphics.md. Save editor `save.py` (SRAM_V113).
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen window not checked by hand (headless worker); scripted input
  verified. `codex exec` review hit its usage limit until 2026-11-26 (sweep reviewed by hand instead). Non-blocking:
  the five-element emblems 木火土金水 on card frames (S20) and the rarity legend (S27) default to English redraws in
  phase 8 unless the user wants the kanji kept as icons.
