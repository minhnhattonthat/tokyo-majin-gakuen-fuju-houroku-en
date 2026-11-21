# Graphics-text survey (phase 1, tour part)

Tour: `tools/routes/tour1.txt` (cold boot -> opening) and `tools/routes/mash_a.txt` from `work/states/opening_9000.mss`.

| # | Screen | Element | Source (first guess) | State |
|---|---|---|---|---|
| G1 | boot | シャウトデザインワークス logo | raw tiles, region 0xD23000.. | tour f000900 |
| G2 | boot | マーベラスインタラクティブ logo | raw tiles, 0xD23000.. (copyright and company art) | tour |
| G3 | title | 東京魔人學園 符咒封録 logo | raw 4bpp 0xD1BF50-0xD2DA47 (vramfind, title dump `work/qa/ppu_title`) | keep JP unless an official EN logo exists (D5) |
| G4 | title | 始めから / 続きから menu, PUSH START | not in SJIS text, so tiles; 0xD25xxx-0xD27xxx candidates | tour |
| G5 | story | vertical scene captions (暗黒の渦――, etc.) on the right edge | not in SJIS text, so tiles; one per scene (many) | tour f008880 |
| G6 | name entry | 名前は？, 苗字, 名前, 進む 戻る 終了, かな カナ 漢字 | tiles (苗字/漢字 absent from text) | `docs/screenshots/name_entry_jp.png` |
| G7 | name entry | kana grid | text table 0xD72FCC (font), needs an English alphabet layout | |
| G8 | title | copyright line ©2004 Marvelous / Shout Designworks | raw tiles 0xD23000.. (already English) | no work |

## Not yet surveyed (open)
- Static sweep of all raw/compressed graphics with correct tile widths (raw 4bpp blocks 0xD1B000-0xD60000 and others).
- Card-battle screens, card faces, status/menu screens, chapter cards, game over, ending, credits: need the debug tool
  (phase 2) to reach them.
