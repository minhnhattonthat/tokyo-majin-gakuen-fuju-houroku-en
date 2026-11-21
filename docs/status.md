# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon (static graphics sweep 28 of 32 sheets reviewed). Last build: none yet (2026-11-22).
- **Done:** Step 0. Recon: text side in `docs/re/text.md`. Graphics: tour survey G1-G8 plus static sweep
  (`tools/gfx_sweep.py`, ROM map, rows S1-S19) in `docs/re/graphics.md`. Found the font (0xC6FB48, 4bpp, SJIS order)
  and the dialogue backgrounds (8bpp at 0xB5BC60.., so no unknown codec is needed).
- **Next:** finish phase 1: (a) `python -X utf8 tools/gfx_sweep.py rom/base.gba work/sweep/z1 --zoom 1`, review
  sheets 028-031 (UI region 0xD1B000-0xD60000, LZ77 blocks) and add rows to graphics.md; (b) check the structured
  records 0x7ED50C-0x8700xx (not tiles?); (c) optionally find real widths for the shredded strips (S2, S3, S11, S12,
  S16). Then phase 2: debug tool (scene warp by story-table index: tables at 0xD8211C/0xD82078, read at
  0x5E378/0x5E2F0).
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen window not checked by hand (headless worker); scripted input
  verified. `codex exec` review hit its usage limit until 2026-11-26 (sweep reviewed by hand instead).
