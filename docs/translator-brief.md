# Translator brief

Read in parts (offset/limit; whole-file reads above ~4 KB come back as a stub): `glossary.md` (Rulings, Style
rules, and the term rows in `build/terms_<batch>.txt`), `docs/style-reference.md`, `docs/synopsis.md`.

## Input
`work/tl/bNNN.tsv`: `id <TAB> speaker <TAB> form <TAB> limit <TAB> JP`.
- `dlg` rows: the JP body of one dialogue box, speaker tag and line breaks removed. Write the body only: no
  【speaker】, no `{rt}`. `tools/batches.py merge` adds the tag and wraps it into the box (2 rows: 232 px, then
  218 px; about 65 characters in all, fewer with capitals and W/M).
- Other forms (choice, card_name, popup, jp_layout, ...): translate the whole string, keep every code (`{wc}`,
  `{wk}`, `{I000}`, `{&NX0}`, `{name1}`, `[81][40]` ...) and place `{rt}` / `{nl}` breaks yourself: no more lines
  than the limit allows (`jp_layout` = as many lines as the JP page, each no wider than the JP line in cells x 16 px).
- `{name1}` = the player's surname, `{name2}` = given name (budgeted 64 px each). English order `{name2} {name1}`.

## Output
`work/tl/bNNN.out.tsv`, written with the file-write tool: `id <TAB> English`, every id once, input order.

## Validate
`python -X utf8 tools/batches.py check bNNN` until it prints OK; then `merge bNNN`.

## Quality bar (past mistakes)
- Each box stands alone on screen: a sentence split across boxes must still read in order, box by box.
- Keep the voice: ッ stress, drawn-out ェェ, rough speech, a spirit's archaic register. Don't flatten.
- Honorifics stay (`-san`, `-kun`, `-chan`, `-senpai`, `-sama`); the check flags a missing one.
- No suffix glued to a code ({name1}th); no abbreviations to fit: rephrase.
- Furigana in parentheses is a reading, not text.

## Report
`NEW TERM: jp -> en`, `UNSURE: id -- note`, `CUT: id -- what was dropped`.
