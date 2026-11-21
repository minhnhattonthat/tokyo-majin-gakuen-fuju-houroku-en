#!/usr/bin/env bash
# sweep_review.sh SHEETDIR FIRST LAST: independent read-only review of gfx_sweep sheets with `codex exec`.
# Writes SHEETDIR/review_FIRST.tsv (sheet, asset label, text read, kind). Run from the repo root.
set -u
dir=$1; first=$2; last=$3
imgs=()
for i in $(seq -f %03g "$first" "$last"); do imgs+=(-i "$dir/sheet_$i.png"); done
prompt="You are a read-only visual QA reviewer for a Japanese GBA game translation (Tokyo Majin Gakuen: Fuju Houroku).
The attached images are sheets $first..$last (in order) of a static ROM graphics sweep: each asset is drawn as
grayscale 8x8 tiles and labelled above it with its hex ROM offset (a label like D25E50+1 is a continuation slice).
Many assets are noise, audio or art rendered at a guessed width.
List EVERY asset that shows lettering drawn as graphics: Japanese (kana/kanji, even fragmentary or split across tiles)
or English/romaji words (logos, buttons, menu labels, card names, numbers fonts, font sheets).
Ignore assets with no lettering. Output only TSV lines, no prose, no header:
sheet<TAB>label<TAB>text you can read (or '?' plus a short description)<TAB>kind (font|menu|logo|label|card|art-sign|other)
If a sheet has none, output: sheet<TAB>-<TAB>none<TAB>-"
codex exec --skip-git-repo-check --ephemeral -s read-only -o "$dir/review_$first.tsv" "${imgs[@]}" -- "$prompt" > "$dir/review_$first.log" 2>&1
echo "exit $? $dir/review_$first.tsv"
