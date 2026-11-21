# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon (text side done; graphics static sweep left). Last build: none yet (2026-11-22).
- **Done:** Step 0 (dump pinned, MesenCE qa-1 + GBA BIOS in tools/mesen, smoke boots the original, scripted input works, pre-commit rejects failing tests, guard hook in .claude/settings.json blocks sed -i/heredocs). Recon: Shift-JIS encoding, control codes, all text regions, pointer tables, 170-scene story table and its scene format, 1.5 MB free-space candidate, LZ77 scan: `docs/re/text.md`. Tour-based graphics survey (G1-G8): `docs/re/graphics.md`.
- **Next:** finish phase 1. (a) Static graphics sweep: render the raw 4bpp blocks 0xD1B000-0xD60000 at their real widths (use the VRAM-dump matches in graphics.md as anchors) and the 52 LZ77 blocks; list every Japanese cell. (b) Find the background codec (1150 tiles not found raw). (c) Optional: locate the font by hooking the glyph draw. Then phase 2: debug tool (scene warp by story-table index: tables at 0xD8211C/0xD82078, read at 0x5E378/0x5E2F0).
- **Open bugs:** none.
- **Waiting on the user:** keyboard input in the Mesen window not checked by hand (headless worker); scripted input verified.
