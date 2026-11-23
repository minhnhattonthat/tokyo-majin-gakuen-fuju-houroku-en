# Tokyo Majin Gakuen: Fuju Houroku English translation

Unofficial English fan translation of **Tokyo Majin Gakuen: Fuju Houroku** (東京魔人學園符咒封録; Game Boy Advance,
Marvelous Interactive, developed by Shout Designworks): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story (main story and all side scenes) | Translated |
| Menus, cards, rules help, tutorials, system messages | Translated |
| Title screen, menus and banners drawn as graphics, card frames, sutra board labels | Translated |
| Boot logos (Shout Designworks / Marvelous, series anniversary emblem) | Left in Japanese (logos) |
| Name entry | Romaji syllables (each kana cell becomes ka, shi, tsu ...) |
| Haiku club passwords | Typed in kana, as the game checks them; all 32 are listed in the release README |
| Staff roll | Translated (name readings romanized from the kanji, a few unconfirmed) |

Known issues: the link-cable messages (two-GBA trade and battle) were fitted by measurement but not seen in game. See
[Issues](../../issues) for anything reported since.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/tokyo-majin-gakuen-fuju-houroku-en
cd tokyo-majin-gakuen-fuju-houroku-en
# copy your dump to: rom/base.gba
#   (16777216 bytes, SHA-1 8d9efb85a8f22ea72c17e4cfcac6877e16b9d5ac; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/tmgfh_en.gba
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Marvelous's and is included only so the
translation can be checked against it. Tokyo Majin Gakuen: Fuju Houroku is (c) Marvelous / Shout Designworks; this
project is not affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
