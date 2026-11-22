# Graphics-text survey (phase 1)

## Tour part
Tour: `tools/routes/tour1.txt` (cold boot -> opening) and `tools/routes/mash_a.txt` from `work/states/opening_9000.mss`.

| # | Screen | Element | Source | State |
|---|---|---|---|---|
| G1 | boot | シャウトデザインワークス logo | raw tiles, region 0xD23000.. | tour f000900 |
| G2 | boot | マーベラスインタラクティブ logo | raw tiles, 0xD23000.. | tour |
| G3 | title | 東京魔人學園 符咒封録 logo | raw 4bpp 0xD1BF50-0xD2DA47 (vramfind, `work/qa/ppu_title`) | keep JP unless an official EN logo exists (D5) |
| G4 | title | 始めから / 続きから / 通信 / 設定 / 通信対戦 / 通信交換; PUSH START | **verified in sweep**: 0xD25E50 (0xC00, 4bpp, 4 cols), PUSH START 0xD25B30 | **English (phase 8 pilot)**: `tools/gfx.py` group title_menu, `gfx/title_menu.tsv`; shot `work/qa/gfx_title/menu_zoom.png` |
| G5 | story | vertical scene captions (暗黒の渦――, etc.) | sweep candidates S9/S10 below | tour f008880 |
| G6 | name entry | 名前は？, 苗字, 名前, 進む 戻る 終了, かな カナ 漢字 | BG2 screen, screen-table entry 0xD7DF1C: LZ77 tiles 0xBEAC20 (234 tiles, bank 10, VRAM 0x0600C000), palette 0xE51FDA, raw 30x20 map 0xE577AA; loader 0x08003268 sizes the buffer and the VRAM copy from the LZ77 header | **English** (group name_entry_screen, `gfx.lz_screen_edit`; `work/qa/ne_en.png`) |
| G7 | name entry | kana grid | text table 0xD72FCC (font) | needs an English layout |
| G8 | title | ©2000 Asmik Ace / ©2004 Marvelous / SHOUT! DESIGNWORKS | 0xD270B0 (already English) | no work |

## Static sweep (`tools/gfx_sweep.py rom/base.gba work/sweep/z1 --zoom 1`)
Assets = every 4-aligned pointer target from code/data tables + the 52 LZ77 blocks (decompressed) + the three
non-wave gaps in the sound area; each rendered as 4bpp (8bpp when all bytes < 0x80) at the width with the smoothest
tile seams. `index.tsv` maps sheet -> offset; `skipped.tsv` lists every region not rendered and why (code, m4a sound,
text, free space, 121 BG tilemaps, 509 records under 0x80 bytes). Reviewed by hand: all sheets 000-031 (codex review hit
its usage limit); `tools/gfx_zoom.py` re-renders any asset at chosen widths. Widths are guesses: a strip that looks shredded (S9, S10, S13) needs its real width found.

### ROM map (verified by render)
| range | content |
|---|---|
| 0x000000-0x080000 | code |
| 0x080000-0x45B9CC | m4a sound (358 wave samples cover 0x320C73 B; the 3 gaps render as audio noise) |
| 0x45B9CC-0x7D0000 | 8bpp card portraits 96x104 (0x2700) and 32x40 thumbnails (0x500): art only |
| 0x7600CC-0x7DA8CC | 8bpp location cards (photos): signs in photos (黒崎商店, 中華料理, アーケード商店街) = art |
| 0x7ED50C-0x86F8CC | 8bpp card frames: table 0xD80BD4 = 44 (tiles, palette, map) triples (tiles 0x20C0, palette 0x140 indexed directly by pixel values 0x81-0x9F, map 0x230 = 14x20 u16), rendered by `tools/card_art.py`; then (tiles, palette) pairs from 0xD80DE4 = the 0xC00 blank frames at 0x83E9AC.. The sweep skipped them because pixel values >= 0x80 failed its 8bpp test. Only lettering: element emblems (S20) |
| 0x8704CC-0xA2CDCC | 8bpp event-card art (0x3300) + thumbnails (0x600); incidental kanji in art (A036CC calligraphy) |
| 0xB5BC60-0xBCB608 | dialogue backgrounds 240x? 8bpp photos (answers "background codec": not 4bpp, so not found raw) |
| 0xC6FB48-0xCAxxxx | **font**: 4bpp glyphs in Shift-JIS order (symbols, A-Z/a-z, kana, Greek, kanji); renders at 8 cols |

### Japanese elements found (rows to redraw; widths in parentheses are the sweep's guess)
| # | Offset | Element |
|---|---|---|
| S1 | 0xA4DACC | card name labels of the **large card view** (L on a hand card): 112x16 4bpp, 14x2 tiles row-major, 0x380 B, palette 0xB08C6C (12 black, 13/14 greys, no rim). Character card i (records 0xD7ADE8, 0x1C B, word 0 = class string in cf.tsv) has label i, 282 labels; S2 0xA50CA4 lies inside this block. **English** (group card_classes, `tools/gfx_cards.py`, text = the cf.tsv `en` of the same string; "Giant Bat" seen in game, `work/qa/cls5`) |
| S2 | 0xA50CA4 | part of S1 (not a separate block) |
| S3 | 0xA8B5CC, 0xAA1C0C, 0xAB5F0C, 0xABF16C, 0xAC6B4C | **40x8 mini name labels**, 0xA0 B (5 tiles) a card, one block right after each S1/S4/S5 block in the same order; shown on the card thumbnail at the top of the battle panel (大蝙蝠 above the art): OBJ 120/121 (32x8 + 8x8) at x 115 y 2, prio 3, bank 12; the thumbnail's corner brackets are BG above it, so only tile x 5..30 is visible (the JP is clipped there too). **English** (group mini_labels, `tools/gfx_minilabels.py`): 3x5 capital pixel font centred in x 5..30; the full name if it fits, else a short form from `gfx/mini_labels.tsv`, else the last word (first word for place suffixes High / Fudo / Park ..). "BAT" seen in game (`work/qa/mini_g1/z2.png`). Several characters share a shown word (10x BLADE, 7x GIRL): the panel header below gives the full name |
| S4 | 0xA9660C | land card labels (52, list 0xD7D2D0), S1 format: **English** (card_classes) |
| S5 | 0xAA3C8C spells (83, list 0xD7D5E0), 0xAB92EC possessions (27, 0xD7D4FC), 0xAC024C barriers (30, 0xD7D568) | S1 format, zero list entries have blank labels: **English** (card_classes; 再生 / 外法 entries point at the 4-letter ability abbreviations, the label gets Renew / Heresy). Rendered only: no non-character card was opened large in game |
| S6 | 0xACCCCC 対 (64x64); 0xACD4EC 壱弐参四伍 (ten 32x32 OBJs, blue then red); 0xACE90C 先手/後手 (64x32 plates) | battle UI, sprite table 0xD814C8 (12 B entries: tiles, palette, map/anim): **English** (group battle_ui, `tools/gfx_battle.py`): FIRST / SECOND and the numerals 1-5 seen in game (turn-order pick from `board_turn.mss`); VS rendered only (not loaded in a 12 000-frame battle: link battle?) |
| S7 | 0xAE5FDC, 0xAEA8AC, 0xAEF17C, 0xAF3A4C, 0xAF831C; small 0xB021EC-0xB0646C | cards with 壱-伍 numerals. The ten 8bpp 64x64 turn-order cards (blue 0xB021EC.., red 0xAFCC4C..; palette = 0xA0 B before the tiles) have the badge redrawn as 1-5 (`cardnum`, seen in game; `tools/debug/cardnums.py`). The ten large cards (8bpp 112x160 = 14x20 tiles in row order, screen-table entries 0xD815A0..; blue 0xAE5FDC 0xAEA8AC 0xAEF17C 0xAF3A4C 0xAF831C with 80-colour palettes, red 0xACF24C 0xAD3BBC 0xAD852C 0xADCE9C 0xAE180C with 160; palette right before the tiles, indexed directly) have the numeral painted on the art: **English** (`bigcard`, glyph area inpainted, digit in the same ink with a white rim; seen in game at the turn-order draw, `work/qa/bigcard/zoom.png`) |
| S8 | 0xB0AAAC, 0xB1AC8C, 0xB43A38 | small labels (zoom to read). 0xB1AC8C (sprite entry 0x524, battle code) = coloured Siddham seed syllables (16x32 OBJs, `work/qa/p8s18/rb_B1b.png`): Sanskrit script used as art, **no work** |
| S9 | 0xB4B7E8 勝負/術者交代/勝利/敗北; 0xB4F808 配置之間 剣..; 0xB50000 | battle banners: eight 64x64 OBJ blocks (0x800 each, two stacked per banner, OBJ bank 10) **English** (group banners, `tools/gfx_banners.py`: LET'S/DUEL!, CASTER/SWAP, YOU/WIN!, YOU/LOSE; shots `work/qa/winb2`, `work/qa/def_en2`); 配置之間 and 0xB50000 not yet checked. Vertical phase banners 32x96 (0x600 each, copied to OBJ 0x06017000): 0xB4F808 配置之間 -> DEPLOY (seen in game, f1350 of board_turn + `work/qa/bd/rand.txt`), 0xB4FE08 剣戟之間 -> CLASH (rendered only); flying-card sprites follow at 0xB50408/0xB50428 |
| S10 | 0xB52048 AP上昇 (four 64x64: arrow up / up lit / down / down lit); 0xB54068 攻撃/待機 (48x48 panel, map 0xB544E8) | **English**: AP UP seen in game (f1260); Attack / Wait panel rendered only (never loaded in the random battle) |
| S11 | 0xBD515C-0xBD935C (strips of ~0x30 B steps) | place/scene names, wrong width (G5 candidates) |
| S12 | 0xBDCDA4-0xBE6738 | brush-style captions, wrong width (chapter/scene titles?) |
| S13 | 0xBEAC20, 0xBEBF00, 0xBECB2C, 0xBEDF7C, 0xBEEA4C, 0xC6D898 | menu windows with labels (終了, 戻る...) |
| S14 | 0xBEF3A8, 0xBF07C8 | LZ77 (8 KB each, sprite entries 0x4D7/0x4D8, loaded at 0x0805EFAA near the link-room code): creature sprites with kanji plates on their bodies (偸盗 ..., `work/qa/p8s18/s14_*.png`): character art, **no work** |
| S15 | 0xBF2628 呪符交換之間; 0xC1B8E8 封陰窟 階; 0xC27A28 骨董品店 店内 | room/scene title art |
| S16 | 0xC11C58, 0xC165E8, 0xC1ADF8-0xC1B6F8, 0xC03F88-0xC05A28, 0xC24E08, 0xC26298, 0xC36408, 0xC37968, 0xC37D88 | menu/label strips (wrong width). 0xC165E8 = sutra board BG, 0xC1ADF8-0xC1B6F8 = its ten red highlight sprites: **English** (W13, group sutra_board). 0xC03F88 (entry 0x52D) is loaded only in link-room sub-state 2 (0x0805BFE8, `r7 == 2`, with entries 0x532/0x54E/0x552): small status badges (look like 待機中 / 通信中 with a cross icon, `work/qa/p8s18/s16c.png`); **open**: needs a linked partner or a forced sub-state to see them. 0xC37968 / 0xC37D88 (entries 0x566/0x567, shop code 0x08057B74..0x08058250): shop item icons and frame pieces, no text |
| S17 | 0xC381A8 売り符選択 / 交換符選択 / 捨て符選択 | card-pick plaques (sprite entry 0xD81DF8; each two 64x32 OBJs, 0x800 B): **English** Sell a Card / Trade a Card / Discard a Card (group shop_plaques, `tools/gfx_shopplaques.py`); "Sell a Card" seen in game (shop.mss + `30 -;6 a;240 -`). Same module: the sell screen's pink 早 badge 0xC6FAC8 (Trade tab = sell all at once) -> fast-forward mark; text icon 1 売 (trade-card counter) -> "Tr" (group icons). All seen in game (`work/qa/p8s17/sell4z.png`, `help2.png`) |
| S18 | 0xC532C8, 0xC557E0, 0xC57CF8, 0xC5A210, 0xC5C728 東京魔人學園 符咒封録 booster packs; 0xC5F760 ブースターパック選択 | pack art = title logo (G3, kept); header: entry 0xD81E04, 46 tiles + a 19x4 map 0xC5FD20 at BG2 row 1, tile 45 = the layer's blank: **English** "Pick a Booster Pack" (group plaques, `tools/gfx_plaques.py`; `work/qa/pack3/hdr.png`) |
| S19 | 0xC66C18, 0xC67D38, 0xC6B118 (正順 逆順 降順 昇順 あ行..わ行), 0xC6C078 符咒編集, 0xC6D078 (sorting popup), 0xC6A2D8 | deck edit: **English** (group deck_edit, `tools/gfx_deck.py`; tab loader patch TABS_FN in `tools/patches.py`) ; 0xC6A2D8 checked 2026-11-22: frame line art only, no text (its tail runs into the English 0xC6B118 badges) |

| S20 | card frames 0x7ED50C.. (table 0xD80BD4) | five-element emblems 木 火 土 金 水 (small circle, bottom left; large in frames 39-43). **English** Wd Fi Ea Mt Wa (`tools/gfx_frames.py`, D12; "Fi" seen in game) |
| S21 | 0xD1B1A8 (2 tiles wide, 16x16) | settings values: 遅い? 普通 速い 有り 無し ... (message speed / on-off) |
| S22 | 0xD1B944 (4 tiles wide) | サウンドテスト: the sound test screen draws its title in font text (English, `work/qa/warp/sound_test/final.png`), this graphic is not shown there ; 0xD1B0A8 2-wide unclear kana |
| S23 | 0xD1EC50 (0x4020, BG tileset) | not a map: the gold talisman art behind the title logo (神 真 太極 宿星, the sutra board's design; (ptr, size) table 0xD289B0, map 0xD22C70; `work/qa/p8s18/s23_screen.png`): art, **no work** |
| S24 | 0xD23140 | title logo plus furigana とうきょうまじんがくえん ふじゅほうろく (with G3) |
| S25 | 0xD280D0 (8 wide); 0xD2F0D8, 0xD30448 (shredded) | 0xD2F0D8 / 0xD30448 = boot-logo screens (mode 13, (ptr, size) table 0xD31DB8: palette, tiles, 30x20 map triples): brush katakana シャウトデザインワークス and マーベラスインタラクティブ company logos, **kept** under D5 (D13; `work/qa/p8s18/m13z.png`). 0xD280D0 (table 0xD289A0, title-screen set) not identified |
| S26 | 0xD2A248 (8bpp, 1998 6.18 date + kanji); 0xD35868 (8bpp UI with kana/kanji) | 0xD2A248 = boot-logo emblem 1998 6.18 東京魔人學園伝奇 生誕伍周年記念 2003 (series 5th-anniversary mark on a dragon, table 0xD31DB8): **kept** under D5 (D13). 0xD35868: battle-tutorial panel (S29) |
| S27 | 0xD3C1F8 | rarity legend 高:紫色 ↕:金色 低:銀色: 64x64 4bpp OBJ (8x8 tiles in row order, palette 0xD3C1D8, size 0x800 in the (ptr, size) table at 0xD63960 next to 0xD48F78 and 0xD451F8 S28). **English** "Hi:Violet / ↕:Gold / Lo:Silver" (kind `legend` in battle_ui; **seen in game** in the battle tutorial's card page, `work/qa/tut1` f2000) |
| S28 | 0xD451F8 (five 32x16 OBJs: icon + kanji, palette 0xD451D8, entry 0xD63978 of the (ptr, size) table) | attack types 拳 武 飛 術 氣: **English** FIST ARMS RNGD ART KI (group attack_types, `tools/gfx_attack.py`, `work/qa/s28/a.png`); rendered only: not loaded in 8000 frames of battle_tutorial.mss (srclog), no direct pointer to the table entry |
| S29 | 0xD53CD8, 0xD57D48, 0xD59218, 0xD5A748, 0xD5E538, 0xD5F1A8 | **battle tutorial overlays**: screen table of (palette, size)(tiles, size)(map, 0xA000F0 = 240x160) pair triples 0xD63288-0xD635F8 (`work/gfx/d63/sheet.png`); callouts シンボル / 背景 / 五行属性, highlight copies of panel pieces 青葉, 格闘家, 【吹飛】【庇う】, 1貫通2必殺3変生, 40D受けた時 + stat line, and small captions (50で攻撃, でダメージを30軽減, 人物符は 魑尼で1貫通 能力を得る). The tutorial's card panel under them is the 8bpp screen 0xD35868 (S26, 806 tiles, entry 0xD635E8) plus 0xD333B8 (0xD635D0): all Japanese, seen in `work/qa/tut1` f2000-f2450. **English** (group tutorial, `tools/gfx_tutorial.py`; art composed once by `tools/debug/tut_compose.py` into indexed `gfx/tutorial/<ENTRY>.png`): 0xD35868 is 8bpp (403 tiles, 64 colours; the "806" above counted 4bpp tiles), lettered with the game's VWF font to read like the real panel for this card (FIGHTER mini label, Fi emblem, BATTLE / Leaf plates, Fighter, 【Blst】【Cov】 + sun, 1Prce 2B(moon) 3Mrph, Took 40 dmg, +20, +10 / +0; pieces from two English panel shots `gfx/tutorial/ref_*.png`); the pink-framed highlights are rebuilt from it (flood fill from the screen edge: frame = pink within 2 px of outside); callouts Symbol / Origin (D64260 now says "origin") / Element on the plate texture; captions "Hits for 50" (a text window covers x >= 94 on that page), "cuts damage by 30", "Characters get 1Prce at [tree] Mani" with the English Wd icon. 0xD333B8 (field only) has no text. D63420 (+2 tiles) and D635A0 grow and move to 0xF90000+ (no VRAM damage seen over the whole tutorial). Seen in game: `work/qa/p8s26/tut2`, `tut3` (battle_tutorial.mss + mash 20, 6000 f). **Field cards** (session 27, group fieldcards, `tools/gfx_fieldcards.py`): pre-drawn 64x64 8bpp OBJs, entries 0xD63A38.. (ptr, size): 0xD3CA78 神速の剣士 (金), 0xD3EB78 + 0xD3FB78 (one 0x2000 block, two frames) 格闘家 (木), opponent cards drawn upside down 0xD3DAF8 (火) / 0xD40BF8 (金), names ○○の剣士 only 4 px tall (unreadable: lettered BLADE); palette = 0x80 B before each block. Name strip -> LIGHTNING / FIGHTER / BLADE (3x5 caps), emblem -> Mt / Wd / Fi. The pink-ringed emblem highlight on D63558 is BG art of the same 木 disc: relettered Wd in `gfx/tutorial/D63558.png`. Seen in game: `work/qa/p8s27/fc` f240 (LIGHTNING, Mt), `fc2` f1920 (FIGHTER, Wd); opponent cards rendered only |

### Screens reached with the debug tool (phase 2; `python -X utf8 tools/debug/warp.py <row>`)
Seen in warp shots; whether each label is tiles or font text is settled in phase 8 by a VRAM dump of the row.
| # | warp row | Japanese on screen |
|---|---|---|
| W1 | `hub`, `hub_dungeon`, `hub_save` | 寄り道/封陰窟, 符咒編集, 記録, 設定, 先に進む: **English** (group menu_labels, sprites 0xB43A38-0xB44637); 記録しますか？ はい いいえ (font) |
| W2 | `detour_map` | 寄り道 banner; signs 光明院, 句会, 骨董品店, 封陰窟: **English** (group signs: OBJ sprites 0xD09A98 + 0xD0A8B8 (two palettes, same tiles), banner 0xD0B6D8) |
| W3 | `dungeon` | menu: **English** (group dungeon_menu, BG2 screen 0xC24E08); 封陰窟 階 plaque: **English** (room_banners, 8bpp BG3 screen 0xC1B8F8); floor numeral sprites 0xC273A8 drawn by 0x080597D0 (floor = [0x03003810] + 1): **Arabic digits** via hook (floor_numerals) |
| W4 | `shop`, `trade_room` | menus **English** (menu_labels); 骨董品店 店内 (8bpp 0xC27A28) / 呪符交換之間 (0xBF2628) plaques **English** (room_banners); item list 商品選択 (0xC36408) **English** (shop_list_screen) |
| W5 | `link_battle`, `title_link_battle` | menus **English**; 通信対戦之間 + 使用符咒 (8bpp 0xC05B28) **English** (room_banners); link-error screen 0xC11C58 (通信エラーです…) **English**, block moved to free space; its wallpaper 0xC0F358 (通信エラー x16, 4bpp 32x32 map) **English** LINK ERROR (group link_error, `tools/gfx_linkerr.py`). The mode-21 setup copies both with fixed sizes, raised in `tools/patches.py` (0x0805AAA0, 0x0805AAC4). Seen in game: `warp.py MODE21` (`work/qa/p8s17/mode21_cmp3.png`) |

Shots: `work/qa/gfx_menus/sheet.png`, `link_zoom.png`. Menu labels are 64x16 sprites, 8x2 tiles row-major (0x200 B),
indices 0 transparent, 1 rim, 2-5 grey to white (OBJ bank 1); 符咒編集 has three copies (B43E38, BFC1B8, C0EF38).

### Screen table 0xD7DCC0-0xD81ED8 (`tools/gfx_screens.py` renders each into `work/gfx/screens/`)
8bpp room backgrounds have a 0x100-byte (128-colour) palette (`gfx_screens.py` renders them; the game takes the
block size from the map pointer, so a block moved to free space with its two pointers updated loads fine: tested).
u32 pointer runs; a BG screen is a (tiles, palette, map) triple: palette right before the tiles, a 30x20 u16 map
right after them (tile count = (map - tiles) / 32; entries = bank << 12 | tile from the block's first tile; the
game adds its own VRAM base). Dungeon menu: entry 0xD81C3C (0xC24E08 tiles, 0xC24DE8 palette, 0xC25DC8 map; VRAM
base 0x90, bank 11, written by BIOS CpuSet at the scene load). Sources found with `tools/debug/vramsrc.lua`
(non-zero writes into a VRAM range, with registers: r0 of a BIOS copy is the ROM source).
Other triples that render as menus: 0xC36408 商品選択 (shop list), 0xC6D898 deck-name entry (符咒名は？ 進む 戻る 終了
かな カナ 漢字, G6).
| W6 | `title_save`, `title_link_*` | 続きから, 通信, 通信対戦, 通信交換 (G4) |
| W7 | `settings`, `title_settings` | **English** (settings_screen): BG2 screen 0xD19834/map 0xD1A554 (pointers 0xD1BB5C..) banner + white labels; yellow selected-label and value sprites 0xD1AA24 (k * 0x100) |
| W8 | `sound_test` | サウンドテスト, BGM, SE, セリフ, ボイス + song/line names (S22) |
| W9 | `haiku` | 句会 banner **English** (haiku_screen, BG2 0xD0E320, pointers 0xD16F94..), 蛍火の句会 (font) |
| W10 | `ending_38`, `ending_39` | staff roll: role captions ◎グラフィック◎, ◎企画・開発◎, ◎プロデューサー◎, ◎監督◎, names (D3: English) |
| W11 | `ending_39` | 東京魔人學園 符咒封録 完 end card (tiles) |
| W12 | `story_00`, `story_NN` | vertical scene captions (暗黒の渦――: G5) at the top right of story scenes |
| W13 | `board` | sutra board (mode 7): the ten sin labels 悪口 貪欲 妄語 好色 綺語 両舌 邪見 殺生 偸盗 瞋恚 are the zones the player picks (Add / Cancel menu, font text explains each): **English** Abuse, Greed, Lies, Lust, Flattery, Double Tongue, False View, Killing, Theft, Malice (glossary b072-b074; group sutra_board, `tools/gfx_board.py`): BG3 entry 0xD81B7C retiled into 0xFC0000 (the setup's fixed copy size literal 0x080567E4 raised), side labels rotated; red highlight sprites 0xC1ADF8 + k * 0x100 redrawn to match. Seen in game, cursor moved over each (`work/qa/p8s18/bm_z.png`). The other board text (神, 真, 太極, 宿星, talismans) is art |
| W14 | `battle_tutorial` | battle HUD; これから戦闘の基本的なルールを説明します (font) |
| W15 | `name_entry` | G6/G7 |
Not reached: the defeat / rematch screen (敗北 S9, 再戦する 終了する at 0xD65298); see `docs/re/game.md`.

Sheets 028-031 reviewed (2026-11-22): 0xCAF748-0xCE5748 is the rest of the font; 0xCE7768 is the 符咒封録 logo art
(G3); 0xE407F8.. (sheet 031) is non-graphic data. No LZ77 block was left unreviewed (they sit in sheets 021-025).
The shredded strips (S2, S3, S11, S12, S16, S25) get their real layout from in-game VRAM dumps in phase 8.

## Phase 8 findings (2026-11-22, session 9)
- **S11 = location captions** (G5/W12): sprite table entries 74-96 (0xD81840, 12 B: tiles, palette 0xBD513C, 0),
  23 captions x 0x300 B = a 16x96 4bpp column, three 16x32 OBJs at x 216. **English** (group captions,
  `tools/gfx_captions.py`, `gfx/captions.tsv`: rotated text reading top to bottom, then the JP line).
- **S12 = LZ77 screens** of the BG loader 0x08003224 (r1 = index into the 12 B table 0xD7DD18: tiles, palette, map;
  BG2 char 0x0600C000, screen 0xE800, bank 14 or 10). Indices 28-40 (entries 0xD7DE68 + 12k) = the **13 chapter
  title cards** 第壱話 闇 .. 第拾参話 宿星, index 41 (0xD7DF04) = the 完 end card, 43-47 = name entry and the
  profile questions (出身地は？ 0xD7DF28, 誕生日は？ 0xD7DF34, 血液型は？ 0xD7DF4C, 性別は？ 0xD7DF58; the gender one
  is never loaded in a normal new game: the L+R easter egg of B39.0119?). All **English** (groups chapter_cards,
  end_card, profile_screens; edit kind `shadow` for the brush cards). Indices 0-27: 8bpp backgrounds, no text.
- Scene command `02 NN` (u16 0xNN02) shows BG NN (0x08003070, called from 0x0803FCEC); cards sit mid-scene in B0 2 5
  8 11 14 18 21 24 27 32 35 37, 完 in B39. The script interpreter's live read pointer is word 0 of the struct at
  [0x03007570] (0x030012CC = scene base, 0x030012D0 a per-step copy): warp.lua `SEEK=0x1C02` jumps there; scenes.tsv
  rows card_01..card_13, card_end.
- Credits role captions are font text (already English).
