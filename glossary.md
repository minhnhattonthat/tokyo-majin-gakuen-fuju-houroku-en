# Glossary - Tokyo Majin Gakuen: Fuju Houroku

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces every table except "Speaker tags" (those become the 【tag】 of dialogue lines).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Yamura-kun, Isuzu-san). Name order: Western (given name first). (D1)
- Romanisation source: official English where it exists, else an earlier fan patch, else Hepburn without macrons. (D2)
- Credits: English. (D3)
- Register / flavour: keep light JP flavour (honorifics, shrine and onmyodo terms romanised where English has no
  word); modern Tokyo teens talk like modern teens; spirits and gods speak formally. Sound effects: *Slam!*. (D9)
- Abbreviations: none; full names and terms, engine work before cuts. (D4)
- The player: {name1} = surname, {name2} = given name (default 緋勇 / 龍麻 = Hiyuu / Tatsuma). Full name in English
  order: `{name2} {name1}`. Never add a suffix glued to a name code except honorifics (`{name1}-kun`).

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> "..." (or italics-free quotes), ・・・ / … / …… -> ..., ―――/―― -> --
  (or a sentence break), ！？ -> ?!, ッ at a line end (stress) -> ! or nothing, 《X》 -> X (capitalised when a term).
- Readings in parentheses (亡（ほろ）び, 朧（おぼろ）げ) are furigana: translate the word, drop the reading.
- No line breaks in dialogue: `tools/batches.py merge` wraps the body and adds the 【speaker】 tag.
- Plain ASCII plus the glyphs in tools/vwf.py EXTRA (… — “ ” ‘ ’ ♪ é 【 】 「 」 『 』); prefer plain ASCII.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 矢村 / 矢村俊 | Yamura | | Shun Yamura (矢村俊), a summoner (勧請師) of the Yamura family; called Yamura | |
| 伊涼 / 水兼伊涼 | Isuzu | | Isuzu Mizukane, the sealing shrine maiden (封印の巫女) | |
| 焔羅 | Enra | | | |
| 天探女 | Amanosagume | | | |
| 高丸 | Takamaru | | | |
| 優鉢羅 | Uhatsura | | | |
| クマソ | Kumaso | | | |
| アカガネ | Akagane | | | |
| 司命 | Shimei | | | |
| 司録 | Shiroku | | | |
| 天若日子 | Amewakahiko | | | |
| ヤマト | Yamato | | | |
| 梓 | Azusa | | | |
| キハタ | Kihata | | | |
| 鈴鹿御前 | Suzuka Gozen | | | |
| 藤原俊宗 | Fujiwara no Toshimune | | historical, kept in Japanese order | |
| 萩原朔太郎 / 萩原　朔太郎 | Sakutaro Hagiwara | | the poet | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 真神学園 | Magami Academy | | the player's school in Shinjuku (B07); nobody has heard of it | Majin Academy |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 符咒士 | Talismancer | | card duelist; the game's own word | |
| 氏神 | Ujigami | | the clan's guardian god; the player's role for the Yamura family (explained in B02) | guardian god |
| 勧請師 | Summoner | | 勧請 (calling down an Ujigami) = summon / summoning | |
| 邪氣 / 邪気 | Miasma | | the evil aura behind the incidents | |
| 大明神 | Great Deity | | 焔羅大明神 = Great Deity Enra | |
| 現世 | the mortal world | | うつしよ | |
| 神鈴 | Divine Bell | | Isuzu's bell; rings near Miasma | |
| 巫女 | shrine maiden | | | |
| 焔羅様 | Lord Enra | | Yamura and Isuzu's form of address | |
| 鬼道衆 | Kidoshu | | the oni clan the five Retainers belong to | |
| 龍脈 | Dragon Vein | | the earth's flow of power under Tokyo | ley line |

## Speaker tags
| JP | EN |
|---|---|
| 女の声 | Woman's Voice |
| 男の声 | Man's Voice |
| 男の声Ａ | Man's Voice A |
| 男の声Ｂ | Man's Voice B |
| 別の男の声 | Another Man's Voice |
| 別の声 | Another Voice |
| 声 | Voice |
| 少年 | Boy |
| 少年の声 | Boy's Voice |
| 少女 | Girl |
| 少女の声 | Girl's Voice |
| 女 | Woman |
| 男 | Man |
| 男たち | Men |
| 矢村の声 | Yamura's Voice |
| 伊涼の声 | Isuzu's Voice |
| 高丸の声 | Takamaru's Voice |
| 焔羅の声 | Enra's Voice |
| 司命の声 | Shimei's Voice |
| 司録の声 | Shiroku's Voice |
| クマソの声 | Kumaso's Voice |
| 紅の熱血漢 | Crimson Hothead |
| 癒しの霊媒師 | Healing Medium |
| 陰の武道家 | Martial Artist of Shadow |
| 陽の武道家 | Martial Artist of Light |
| 唄姫 | Songstress |
| 常世の唄姫 | Songstress of Tokoyo |
| 災厄の運び手 | Bringer of Calamity |
| 黒き疾風 | Black Gale |
| 愛の戦士 | Warrior of Love |
| 友情の戦士 | Warrior of Friendship |
| 勇気の戦士 | Warrior of Courage |
| 符術士 | Talisman Sorcerer |
| 魔女 | Witch |
| 槍使い | Spear Wielder |
| 桃園の乙女 | Maiden of the Peach Garden |
| 舞い手 | Dancer |
| 博徒の王 | King of Gamblers |
| 騎士 | Knight |
| 陰陽師 | Onmyoji |
| 朱の陰陽師 | Vermilion Onmyoji |
| 薔薇の妖女 | Rose Enchantress |
| 二重身 | Doppelganger |
| 暗殺者 | Assassin |
| 弓使い | Archer |
| 護人 | Guardian |
| 鮮血の妖婦 | Blood-Soaked Siren |
| 火走り | Firerunner |
| 静謐なる拳士 | Serene Fist |
| 勇猛たる拳士 | Valiant Fist |
| 小さき拳士 | Little Fist |
| 傀儡師 | Puppeteer |
| 封印する者 | The Sealer |
| 狂気の密教僧 | Mad Esoteric Monk |
| 忍者 | Ninja |
| くノ一 | Kunoichi |
| 憑依師 | Possessor |
| 慎ましき巫女 | Modest Shrine Maiden |
| 猛き巫女 | Fierce Shrine Maiden |
| 狐面の巫女 | Fox-Masked Shrine Maiden |
| 雷の従者 | Thunder Retainer |
| 風の従者 | Wind Retainer |
| 水の従者 | Water Retainer |
| 土の従者 | Earth Retainer |
| 炎の従者 | Flame Retainer |
| 邪剣士 | Wicked Swordsman |
| 怨恨の法師 | Vengeful Priest |
| 左の男 | Man on the Left |
| 右の男 | Man on the Right |
| 左の影 | Shadow on the Left |
| 右の影 | Shadow on the Right |
| 影 | Shadow |
| 死人使い | Necromancer |
| 風水師 | Geomancer |
| 霊銃使い | Spirit Gunner |
| 聖女 | Saint |
| 神速の剣士 | Lightning Swordsman |
| 巡り逢えし友 | Destined Friend |
| 先読み | Seer |
| 下劣な巨漢 | Vile Brute |
| 格闘家 | Fighter |
| 歪んだ格闘家 | Twisted Fighter |
| 狐火の遊女 | Foxfire Courtesan |
| 透視する者 | Clairvoyant |
| 老爺 | Elder |
| 老婆 | Old Woman |
| 老人 | Old Man |
| 老人の声 | Old Man's Voice |
| 老人たち | Old Folks |
| 霊的治療師 | Spirit Healer |
| 薫風の乙女 | Maiden of the Fragrant Breeze |
| からくり師 | Automaton Maker |
| 【からくり師 | Automaton Maker |
| 夢の支配者 | Lord of Dreams |
| 狂信者 | Zealot |
| 洗礼の処女 | Baptized Maiden |
| 最後の侠客 | Last of the Gallants |
| 風流人 | Aesthete |
| 龍を産みし者 | Bearer of the Dragon |
| 闇を狩る者 | Hunter of Darkness |
| 念動者 | Psychokinetic |
| 真実を記す者 | Recorder of Truth |
| 蛇の宿主 | Serpent's Host |
| 妖刀使い | Cursed Blade Wielder |
| 神槍の使い手 | Master of the Divine Spear |
| 流浪の剣士 | Wandering Swordsman |
| 朱の淫婦 | Vermilion Harlot |
| 刻を渡る者 | Walker of Time |
| 猫娘 | Cat Girl |
| 【猫娘 | Cat Girl |
| 邪手使い | Wicked Hand |
| 怪しい男 | Suspicious Man |
| 運命を描く者 | Painter of Fate |
| 筮法師 | Diviner |
| 退廃の詩人 | Decadent Poet |
| 鴉の王 | Crow King |
| 鴉 | Crow |
| 不死の剣士 | Undying Swordsman |
| 混沌の王 | King of Chaos |
| 狡猾な渡り手 | Cunning Drifter |
| 魂を導く少女 | Soul-Guiding Girl |
| 外法の剣士 | Heretic Swordsman |
| 外法の探求者 | Seeker of Heresy |
| 審判者 | Judge |
| 厳格な才女 | Strict Prodigy |
| 信じる者 | Believer |
| 隻眼の天狗 | One-Eyed Tengu |
| 不気味な女 | Eerie Woman |
| 不気味な男 | Eerie Man |
| 不気味な人形 | Eerie Doll |
| 不気味な声 | Eerie Voice |
| 勇敢なる魂 | Brave Soul |
| 女剣士 | Swordswoman |
| 飛脚 | Courier |
| 言霊 | Kotodama |
| 不良 | Delinquent |
| 不良Ａ | Delinquent A |
| 不良Ｂ | Delinquent B |
| 悪霊群 | Evil Spirits |
| 父親 | Father |
| 父親の声 | Father's Voice |
| 母親の声 | Mother's Voice |
| 警官 | Police Officer |
| 猟師風の男 | Huntsman |
| 婦長の声 | Head Nurse's Voice |
| 看護婦の声 | Nurse's Voice |
| 看護婦Ａの声 | Nurse A's Voice |
| 看護婦Ｂの声 | Nurse B's Voice |
| 女院長の声 | Director's Voice |
| ニュース | News |
| ＴＶ | TV |
| 無線 | Radio |
| 天気予報 | Weather Report |
| 大鷲 | Great Eagle |
| 犬 | Dog |
| 犬の声 | Dog's Voice |
| 野良犬 | Stray Dog |
| 狂犬 | Mad Dog |
| 若武者 | Young Warrior |
| 血まみれの男 | Bloodied Man |
| 妙な男たち | Strange Men |
| ドライバー | Driver |
| 野次馬 | Onlooker |
| 野次馬Ａ | Onlooker A |
| 野次馬Ｂ | Onlooker B |
| 野次馬Ｃ | Onlooker C |
| 呪わしい声 | Accursed Voice |
| 会社員 | Office Worker |
| 黒衣の男 | Man in Black |
| 学生 | Student |

## Decisions from earlier batches
- b001-b004 《X》 terms (not enforced: single kanji): 《力》 -> Power, 《氣》 -> Ki, 《念》 -> Thought, 《定め》 -> Destiny,
  《因果》 -> Causality, 《生》 -> Life, 《奴》 -> HE (the unseen enemy, capitals). Capitalised, no brackets.
- b003 address: Yamura calls the player {name1}-sama / {name1}-dono / Great Deity; Isuzu tries {name1}-kun,
  {name2}-chan. Enra calls the player "lad". The player is male (school uniform) by
  default, but B04 has a girl-player branch ({name2}-chan rows, 老爺と少女): keep player references neutral where
  the JP is, and follow the JP where a branch row names a gender.
- b005-b013 《X》 terms: 《罪》 -> Sin, 《欲望》 -> Desire, 《心》 -> Heart, 《覚悟》 -> Resolve, 《愛》 -> Love, 《友》 ->
  Friends, 《理性》 -> Reason, 《事実》 -> Fact, 《彼ら》 -> THEM, 《討ツ》 / 《壊した》 / 《死んだ》 -> capitals (SLAY,
  BROKEN, DEAD). 神隠し -> "spirited away". 氏神勧請 -> Ujigami Summoning. 地蔵様 -> Jizo-sama. マリィ -> Marie.
  {name1}殿 -> {name1}-dono (Yamura from B04 on). Isuzu calls Yamura "Shun".
- b015-b024 (A0-A3): 鬼道衆 -> Kidoshu, 鬼 -> oni, 龍脈 -> Dragon Vein. 《X》 terms: 《種》 Species, 《嫉妬》 Jealousy,
  《想い》 Feeling, 《デキソコナイ》 Defective(s), 《勢い》 Force, 《炎》 Flame, 《金》 Money, 《憤怒》 Wrath, 《滅び》 Ruin,
  《悩み》 Doubt, 《怒り》 Anger, 《拳》 Fist. Voices: Water Retainer (わらわ/そなた/かえ) = thou/thee; Earth Retainer
  (おで) = "me belly", "dat"; Talisman Sorcerer (Kansai) = "ya", "pal", dropped g's; Last of the Gallants calls the
  player 兄サン = "pal"; Psychokinetic's katakana speech = plain English, childish menace.
- b043-b047 (B11, A11): 《力場》 -> Power Field (the shrine's ground that powers Akagane). 符 (the weapon) ->
  talisman. Akagane calls Isuzu/Yamura "you two"; Isuzu calls him Akagane-san. The Eerie Man/Woman (Azusa's dead
  parents) speak coarse, mocking English ("brat", "Gyahaha").
- b048-b050 (A12, B12): 《大罪》 -> Great Sin (first in B12; pairs with 《罪》 Sin). 《喜び》 -> Joy. 現世 -> the mortal
  world. Choice B12.0049 符を渡す/渡さない -> Hand it over / Keep it. A12 voices: Cat Girl and One-Eyed Tengu speak
  Kansai ("ya", dropped g's, "ain't"; Cat Girl adds "nya"); the Automaton Maker's 儚い tic -> "how fleeting".
- b051-b053 (B13-B15): 鈴鹿の鬼姫 -> Oni Princess of Suzuka. 式神 -> shikigami; 式招来 -> "Shiki, I summon
  thee!". 妖 (あやかし) -> demon. 六十重の塔 -> the sixty-tiered tower (= Sunshine 60). 巣鴨監獄 -> Sugamo Prison.
  大江山 -> Mt. Oe. 魂魄 -> souls. 勧請ッ！ -> "Summoning!"; 氏神・{name1}大明神 -> "Ujigami, Great Deity {name1}!".
  Takamaru says 己 (おれ) = plain "I/me"; his Woman's Voice laughs くふふ = "Kuh-huhu". 《影》 -> Shadow.
- A12.4.0038/0043 and A12.9.0057 start `【【` (a JP typo); merge tags them normally.
- The only row whose JP holds two boxes (`...{rt}{rt}【X】{rt}...`) is B11.0121:
  the batch check wants the repeated speaker name in the English, so put `【X】` in the body to pass, then after
  merging rewrite the en by hand as one ordinary box with no inner tag (fit counts {rt}{rt}【X】{rt} as 5 lines on
  one page; a later `merge --overwrite` of that batch undoes the fix).
- A term split across two boxes must stay in the box whose JP has it (the check enforces this per box).
