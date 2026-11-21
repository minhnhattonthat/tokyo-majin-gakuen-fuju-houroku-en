# Graphics-text survey (phase 1)

## Tour part
Tour: `tools/routes/tour1.txt` (cold boot -> opening) and `tools/routes/mash_a.txt` from `work/states/opening_9000.mss`.

| # | Screen | Element | Source | State |
|---|---|---|---|---|
| G1 | boot | シャウトデザインワークス logo | raw tiles, region 0xD23000.. | tour f000900 |
| G2 | boot | マーベラスインタラクティブ logo | raw tiles, 0xD23000.. | tour |
| G3 | title | 東京魔人學園 符咒封録 logo | raw 4bpp 0xD1BF50-0xD2DA47 (vramfind, `work/qa/ppu_title`) | keep JP unless an official EN logo exists (D5) |
| G4 | title | 始めから / 続きから / 通信 / 設定 / 通信対戦 / 通信交換; PUSH START | **verified in sweep**: 0xD25E50 (0xC00, 4bpp, 4 cols), PUSH START 0xD25B30 | |
| G5 | story | vertical scene captions (暗黒の渦――, etc.) | sweep candidates S9/S10 below | tour f008880 |
| G6 | name entry | 名前は？, 苗字, 名前, 進む 戻る 終了, かな カナ 漢字 | tiles (苗字/漢字 absent from text); sweep S19 likely | `docs/screenshots/name_entry_jp.png` |
| G7 | name entry | kana grid | text table 0xD72FCC (font) | needs an English layout |
| G8 | title | ©2000 Asmik Ace / ©2004 Marvelous / SHOUT! DESIGNWORKS | 0xD270B0 (already English) | no work |

## Static sweep (`tools/gfx_sweep.py rom/base.gba work/sweep/z1 --zoom 1`)
Assets = every 4-aligned pointer target from code/data tables + the 52 LZ77 blocks (decompressed) + the three
non-wave gaps in the sound area; each rendered as 4bpp (8bpp when all bytes < 0x80) at the width with the smoothest
tile seams. `index.tsv` maps sheet -> offset; `skipped.tsv` lists every region not rendered and why (code, m4a sound,
text, free space, 121 BG tilemaps, 509 records under 0x80 bytes). Reviewed by hand: sheets 000-027 (codex review hit
its usage limit). **Sheets 028-031 (0xC9xxxx.. onward incl. the 0xD1B000-0xD60000 UI region and most LZ77 blocks)
are still to review.** Widths are guesses: a strip that looks shredded (S9, S10, S13) needs its real width found.

### ROM map (verified by render)
| range | content |
|---|---|
| 0x000000-0x080000 | code |
| 0x080000-0x45B9CC | m4a sound (358 wave samples cover 0x320C73 B; the 3 gaps render as audio noise) |
| 0x45B9CC-0x7D0000 | 8bpp card portraits 96x104 (0x2700) and 32x40 thumbnails (0x500): art only |
| 0x7600CC-0x7DA8CC | 8bpp location cards (photos): signs in photos (黒崎商店, 中華料理, アーケード商店街) = art |
| 0x7ED50C-0x8700xx | structured non-tile records (0x20C0/0x230/0x140 groups): not graphics as rendered; **check** |
| 0x83E9AC-0x86F8CC | 8bpp blank card frames (0xC00) |
| 0x8704CC-0xA2CDCC | 8bpp event-card art (0x3300) + thumbnails (0x600); incidental kanji in art (A036CC calligraphy) |
| 0xB5BC60-0xBCB608 | dialogue backgrounds 240x? 8bpp photos (answers "background codec": not 4bpp, so not found raw) |
| 0xC6FB48-0xCAxxxx | **font**: 4bpp glyphs in Shift-JIS order (symbols, A-Z/a-z, kana, Greek, kanji); renders at 8 cols |

### Japanese elements found (rows to redraw; widths in parentheses are the sweep's guess)
| # | Offset | Element |
|---|---|---|
| S1 | 0xA4DACC | card class labels (魔の使い, 神速の剣士, 聖女, 弓使い, 忍者...) |
| S2 | 0xA50CA4 | large prerendered text block (card descriptions?) - wrong width, find real one |
| S3 | 0xA8B5CC, 0xAA1C0C, 0xAB5F0C, 0xABF16C, 0xAC6B4C | small prerendered text (wrong width) |
| S4 | 0xA9660C | location names (寛永寺, 江戸川大橋, 新宿中央公園, 如月骨董品店...) |
| S5 | 0xAA3C8C, 0xAB92EC, 0xAC024C | card/skill names (気脈の流れ, 一刀両断, 影武者...) |
| S6 | 0xACCCCC 対; 0xACD4EC 壱弐参四伍 (2 styles); 0xACE90C 先手/後手 | battle UI |
| S7 | 0xAE5FDC, 0xAEA8AC, 0xAEF17C, 0xAF3A4C, 0xAF831C; small 0xB021EC-0xB0646C | cards with 壱-伍 numerals |
| S8 | 0xB0AAAC, 0xB1AC8C, 0xB43A38 | small labels (zoom to read) |
| S9 | 0xB4B7E8 勝負/術者交代/勝利/敗北; 0xB4F808 配置之間 剣..; 0xB50000 | battle banners (vertical) |
| S10 | 0xB52048 AP上昇; 0xB54068 攻撃/待機 | battle UI |
| S11 | 0xBD515C-0xBD935C (strips of ~0x30 B steps) | place/scene names, wrong width (G5 candidates) |
| S12 | 0xBDCDA4-0xBE6738 | brush-style captions, wrong width (chapter/scene titles?) |
| S13 | 0xBEAC20, 0xBEBF00, 0xBECB2C, 0xBEDF7C, 0xBEEA4C, 0xC6D898 | menu windows with labels (終了, 戻る...) |
| S14 | 0xBEF3A8, 0xBF07C8 | emblem kanji (闇/悲/怒/喜/愛/哀?) |
| S15 | 0xBF2628 呪符交換之間; 0xC1B8E8 封陰窟 階; 0xC27A28 骨董品店 店内 | room/scene title art |
| S16 | 0xC11C58, 0xC165E8, 0xC1ADF8-0xC1B6F8, 0xC03F88-0xC05A28, 0xC24E08, 0xC26298, 0xC36408, 0xC37968, 0xC37D88 | menu/label strips (wrong width) |
| S17 | 0xC381A8 売り符選択 / 交換符選択 / 捨て符選択 | shop/trade menu |
| S18 | 0xC532C8, 0xC557E0, 0xC57CF8, 0xC5A210, 0xC5C728 東京魔人學園 符咒封録 booster packs; 0xC5F760 ブースターパック選択 | |
| S19 | 0xC66C18, 0xC67D38, 0xC6B118 (両隣 左行 右行...), 0xC6C078 符咒編集, 0xC6D078, 0xC6A2D8 | deck edit / help UI |

Not yet listed: chapter cards, game over, ending, credits as seen in game (need the debug tool, phase 2), and the
review of sheets 028-031.
