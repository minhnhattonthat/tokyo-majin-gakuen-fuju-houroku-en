Tokyo Majin Gakuen: Fuju Houroku - English translation patch v@VERSION@
==========================================================================

Unofficial English fan translation of Tokyo Majin Gakuen: Fuju Houroku (東京魔人學園符咒封録), Game Boy Advance,
Marvelous Interactive / Shout Designworks. This zip holds only a patch: no game data, and no patched ROM will be
shared. You need your own dump of the Japanese cartridge.

## Base ROM (apply the patch to exactly this file)

    No-Intro name: Tokyo Majin Gakuen - Fuju Houroku (Japan).gba
    Size:   @BASE_SIZE@ bytes
    CRC32:  @BASE_CRC32@
    MD5:    @BASE_MD5@
    SHA-1:  @BASE_SHA1@

Patched result:

    Size:   @OUT_SIZE@ bytes
    CRC32:  @OUT_CRC32@
    SHA-1:  @OUT_SHA1@

## How to patch

Apply @PATCH@ (BPS format) with Floating IPS (flips), beat, or RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/).
The patcher checks the base ROM: if it refuses, your dump is a different one (compare the hashes above).

## Playing

Tested in Mesen (MesenCE) with the official GBA BIOS. Any accurate GBA emulator or a flash cart should work.
From a cold boot the title screen appears after about 22 seconds of logos (Shout Designworks, Marvelous).

## What is translated

- All story and side-scene dialogue, menus, cards, rules help, tutorials and system messages.
- Title screen, menus and banners drawn as graphics, card frames, the sutra board labels.
- Name entry uses romaji syllables: each kana cell is one unit (ka, shi, tsu ...; the small-kana row gives single
  consonants: r + yu = ryu). Names keep the game's 4 units (deck names 3).
- Left in Japanese: the boot logos (Shout Designworks, Marvelous, series anniversary emblem).
- Haiku club: the game compares the kana you type against its 32 haiku, so they stay in kana. The list below gives
  every haiku in kana and romaji with a rough meaning.

## Known issues

- The link-cable messages (two-GBA trade and battle) were fitted by measurement but not seen in game.
- Staff-roll name readings are romanized from the kanji; a few are unconfirmed.
Report bugs at https://github.com/minhnhattonthat/tokyo-majin-gakuen-fuju-houroku-en/issues (a savestate helps most).

## Credits

Translation, hacking and tools: minhnhattonthat. Made with extensive AI assistance (Claude by Anthropic);
corrections are very welcome. Fonts: Liberation Sans (SIL OFL) for redrawn graphics.
Tokyo Majin Gakuen: Fuju Houroku is (c) Marvelous / Shout Designworks. This is an unofficial fan work, not affiliated
with them. Do not distribute pre-patched ROMs.
