# Visual-QA reviewer brief - Tokyo Majin Gakuen: Fuju Houroku (GBA)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/<id>/sheet.png`, same ids) and `glossary.md` (read it with
  offset/limit: whole-file reads come back as a stub).

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.
- Zoom into every Yes/No prompt, selection box, menu row and speech bubble: a few pixels of misalignment don't show
  at sheet scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box or cursor brackets, a label, a bubble;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- Japanese drawn as graphics that phase 8 has not redrawn yet (chapter cards, place-name strips, 邪気封印 card art,
  five-element emblems 木火土金水, rarity legend, game over, credits art, title logo): note it as `gfx-pending`
  in the verdict note, verdict `ok` only once `docs/re/graphics.md` lists it as a pending redraw.
- the kana name-entry grids (kind `grid`) until English name entry lands.
- the staff roll keeps 﨤 in B39.0020 on purpose.
- the VS name plate (surname + given name, no space) overflows both plate ends with 4+4-unit names: the original does
  the same with 4+4 kana (`work/qa/p8s35/vs_jplong.png`).
- the `stress_moveon` row stops on the battle START screen: the hub -> Move On path from a chapter-5 save hangs there in
  the original too.
- the deck / sell list header caught as two overlapping texts (e.g. "All Hel'd 47d"): the game's crossfade into the
  "Cards held" panel; the settled frame is clean (`stress_viewall`, checked at 10-frame steps in session 39).
