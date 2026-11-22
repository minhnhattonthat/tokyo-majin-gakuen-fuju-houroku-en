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
| 巫女 | shrine maiden / Miko | | Miko only where the 94 px card-name slot has no room | |
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
- b054-b056 (B16-B17): 《陰（かげ）》/《陰》 -> the Shade, 《陽（ひかり）》/《陽》 -> the Light, 《陰の者》 -> Shade folk,
  《陽の者》 -> Light folk, 《陰の氣》 -> Shade Ki. 《従わぬ者》 -> the Unyielding. 《何か》 -> Thing. 鬼狩り将軍 ->
  Oni-Hunter General. 転生 -> reincarnation. 《星》 -> Star. 《魂》 -> Soul. 《悪》 -> Evil. 《正義》 -> Justice.
  《仲間》 -> Comrade. シュテン / タマモ -> Shuten / Tamamo; 宇治の宝蔵 -> the treasure house of Uji. 近江 Omi,
  鈴鹿山 Mt. Suzuka, 蝦夷 Ezo. Takamaru's past is "1200 years ago".
- b057-b062 (B18): 《言霊》 -> Word Spirits (A12.1's plain 言霊 = "spirit of words"). 《運命》 -> Fate. 大嶽丸 ->
  Otakemaru. 藤原千方 -> Fujiwara no Chikata. 田村麻呂 / たむらまろ -> Tamuramaro; 鈴鹿姫 -> Princess Suzuka.
  古今著聞集 -> the Kokon Chomonju. 悪路王 -> Akuro-o (glossed once as "King of Evil Roads"). 蝦夷 (えみし) -> Emishi;
  (えぞ) -> Ezo. 天女 -> celestial maiden. 魔国 -> demon nation. 怨霊 -> vengeful ghost. 神鈴 -> Divine Bell. From B18
  Yamura calls the player plain {name1} (no -dono) in casual talk. Route choice B18.0113 -> With Yamura / With Isuzu.
- b063-b065 (B19-B21): 言霊の幸わう国 -> "the land where Word Spirits flourish". 人柱 -> human pillar. 極寒獄 ->
  frozen hell. 氷壁 -> ice wall. 《生》 -> Life. Uhatsura (優鉢羅) speaks cold and formal ("Very well", "fear not").
- b066-b067 (B22-B23): 《身》《口》《意》 -> Body, Speech and Mind. 森羅万象 -> all creation; 理 -> laws. 因果応報 ->
  "what they reap". 生け贄 -> sacrifice. The voice inside Isuzu (B23.0191-0209, later Suzuka) laughs "Hee hee".
- b068-b071 (B24): 《生け贄》 -> Sacrifice(s). 平将門の《首塚》 -> the Head Mound of Taira no Masakado. 咒 (しゅ)
  -> curse. 結界 -> barrier. 《傷》 -> Wound. 血華 -> flower of blood. Kumaso says おれ = I; mocking, sadistic.
  Shiroku (司録) and Shimei (司命) = the Shadows on the Right/Left; formal speech. B24.0509-0541 are voices of
  another Tokyo's defenders (Boy/Girl/Woman's Voice), heard through the player's Thought.
- b072-b074 (B25-B28): 日本武尊 -> Yamato Takeru; 熊襲魁帥 -> Kumaso Takeru. 無間空間 -> the Endless Space. 断罪人 ->
  executioners. 《処分》 -> Disposal. 《護るべきもの》 -> "what they must protect". The ten Great Sins (十悪, B28):
  《悪口》 Abuse, 《綺語》 Flattery, 《貪欲》 Greed, 《瞋恚》 Malice, 《妄語》 Lies, 《好色》 Lust, 《殺生》 Killing,
  《偸盗》 Theft, 《両舌》 Double Tongue, 《邪見》 False View (readings in brackets dropped). 《心》《口》《意》 at B28 ->
  Heart, Speech, Mind. Shimei's/Shiroku's incantation: 「司命、これよりこの者…命（いのち）を与える」 -> "I, Shimei,
  now grant this one... life once more!"; Shiroku's 命（めい） -> "orders".
- b075-b076 (B29-B31): 黄龍 -> the Golden Dragon; 黄龍の器 -> the Vessel of the Golden Dragon; 《器》 -> Vessel.
  《宿星》 -> fated Stars. 《大罪》人 -> Great Sinners. 天探女 -> Amanosagume. 冥土の土産 -> "a parting gift for the
  underworld". Enra's mantra オン・カカカ・ビサンマエイ・ソワカ -> "On kakaka bisanmaei... sowaka!!".
- b077-b088 (B32-B39): 探女 alone (Amewakahiko, Yamura, Isuzu, Takamaru) -> Sagume; 天探女 stays Amanosagume.
  俊 (Enra, Isuzu, Sagume) -> Shun; 矢村俊 -> Shun Yamura; 水兼伊涼 -> Isuzu Mizukane. 符 is always "talisman"
  (never "charm"). 蚩尤旗 -> Shiyuki, the Banner of Chiyou (first mention), then Shiyuki. 閻魔 -> Enma, judge of the
  dead. 《地の氣》 -> Earth Ki (《陰》の《地の氣》 Shade Earth Ki). 《罰》 -> Punishment. 《あいつら》 (heaven) -> "those
  up there" (no asterisks: the font has none). 千頭の矢 -> the thousand arrows; 観世音 -> Kannon. 院長先生 -> the
  director. Staff roll (B38.0139, B39.0000-0064): names in Western order, readings unverified; section heads as
  "-- X --" (the 對 ornament has no glyph); B39.0020's 﨤町 孝 is a guess, "Takashi Hazamachi".
- Card game (system text cf/d6, from b090). Not in the enforced tables: 符咒 (deck) is inside 符咒士 (Talismancer).
  Card types follow their icon: {I000}人物符 -> "{I000}Character", {I001}憑依式神符 -> "{I001}Possession Shikigami",
  {I002}結界式神符 -> "{I002}Barrier Shikigami", {I003}法術符 -> "{I003}Spell", {I004}土地符 -> "{I004}Land"; a bare
  {I000} as a noun -> "{I000}Character" or "{I000}" where the icon alone reads well. 符 alone -> talisman. 符咒 -> deck;
  符咒編集 -> Deck Edit; 山札 -> draw pile; 手札 -> hand; 墓地 -> graveyard; 場 -> field; 属性 -> element ({I009}属性の
  -> "{I009}-element" or "{I009}"); ＡＰ / ＨＰ / ＭＡＸＡＰ -> AP / HP / Max AP (the game's own abbreviations, kept);
  ライフ -> Life; ターン -> turn; 記録 -> save; 複写 -> copy; 捨てる -> discard; 引きなおし -> redraw; 打ち消す -> cancel.
  Ability tags 【X】 (the popup's tag line is 64 px / 4 units, so names are short; an element or attack-type icon
  goes after the bracket: 【Ward】{I009}): 召喚 Summon, 連続 Combo, 速攻 Haste, 狙い Aim, 吹飛 Blast, 見切 Dodge
  (見{Innn} 【Dodge】{Innn}), 麻痺 Stun, 魅了 Charm, 風水 Earth, 霊媒 Medium, 鎮守 Guardian, 透視 Scry, 送還 Banish,
  迷宮 Maze, 輪廻 Samsara, 跳躍 Leap, 賭け Gamble, 貫通 Pierce, 調査 Probe, 覚醒 Awaken, 血気 Vigor, 蘇生 Revive,
  葉隠 Stealth, 結界 Barrier, 範囲 Area, 祝福 Blessing, 知識 Lore, 睡眠 Sleep, 盗み Steal, 発火 Ignite, 生贄
  Sacrifice, 熱血 Fervor, 災厄 Calamity, 治療 Heal, 毒 Poison, 模写 Mimic, 悟り Insight, 恩恵 Boon, 復活 Return,
  式神 Dispel, 庇う Cover, 崩し Break, 居合 Iai, 外法 Heresy, 変生 Morph, 変化 Change, 呪詛 Curse, 吸血 Drain,
  友情 Bond, 博愛 Charity, 加速 Boost, 加護 Aegis, 創造 Create, 分身 Clone, 再生 Renew, 共鳴 Echo, 傀儡 Puppet,
  耐{Innn} Ward, 即{Innn} Slay, 必{Innn} Bane. Icons: {I012} AT, {I013} HP, {I014} SP, {I016} paralysis, {I017}
  poison, {I018} sleep, {I020}-{I024} attack types, {I005}-{I011} elements. 摩尼 -> Mani. 敵 -> foe. 術 (attack
  type) -> Art. Summoned characters: 病んだ狼 Sick Wolf, 警官 Police Officer, 悪代官 Evil Magistrate, 強欲な商人
  Greedy Merchant, 御用提灯 Official Lantern, 浪士 Ronin, 大百足 Giant Centipede, 夜の召使い Night Servant, 野良猫
  Stray Cat, 魍魎 Moryo, 威嚇する者 Intimidator, 異形のもの Misshapen One, 深きもの Deep One, 甦りし者 Risen One,
  人喰い鴉 Man-Eating Crow, 狂犬 Mad Dog, 大蝙蝠 Giant Bat, 群れをなす者 Swarming One, 盲目の邪神 Blind Evil God.
  Yes/no option line: `[81][40]Yes[81][40]No` (raw glyph pairs pass the batch check as text).
- A12.4.0038/0043 and A12.9.0057 start `【【` (a JP typo); merge tags them normally.
- The only row whose JP holds two boxes (`...{rt}{rt}【X】{rt}...`) is B11.0121:
  the batch check wants the repeated speaker name in the English, so put `【X】` in the body to pass, then after
  merging rewrite the en by hand as one ordinary box with no inner tag (fit counts {rt}{rt}【X】{rt} as 5 lines on
  one page; a later `merge --overwrite` of that batch undoes the fix).
- A term split across two boxes must stay in the box whose JP has it (the check enforces this per box).
