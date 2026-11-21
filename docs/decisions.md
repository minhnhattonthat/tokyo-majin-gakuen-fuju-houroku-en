# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-22 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer. |
| D2 | 2026-11-22 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-22 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-22 | Abbreviations | engine work first (default), abbreviate | Engine work first (default). |
| D5 | 2026-11-22 | Graphics text left in Japanese | none (default), list | Translate all (titles, menus, banners, cards); keep the original Japanese logo only if no official English logo exists. |
| D6 | 2026-11-22 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints. |
| D7 | 2026-11-22 | Existing saves | user saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-22 | English font path (engineering default under D4/D6, not asked) | half-width 8 px pairs (28 chars a line), the game's fullwidth Latin cropped to VWF (~27), new compact VWF font (~38) | New VWF font `fonts/vwf.txt` through a hook in the per-cell glyph routine plus MTE units (`tools/vwf.py`): the most text per line with no change to any printer loop; style matches the game (white, dark shadow, 16 px rows). |
