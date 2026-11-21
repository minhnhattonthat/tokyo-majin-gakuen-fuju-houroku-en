# choicetest.ps1 PX1 PX2: rebuild the width-test ROM with the first choice (B02.0052) set to two filler options of
# PX1 / PX2 pixels, replay from the state saved just before it (work/qa/w1_B2_7000.mss), shot every 10 frames.
param([int]$px1, [int]$px2, [string]$tag = "c")
$S = (python tools/skill.py).Trim()
$line = python -X utf8 -c "import sys; sys.path.insert(0,'tools'); import widthtest as w; f=w.font(); print('B02.0052\t'+w.fit(f,$px1)+'{rt}'+w.fit(f,$px2)+'{wc}')"
Get-Content work/qa/w1.tsv | Where-Object { $_ -notlike 'B02.0052*' } | Set-Content -Encoding utf8 work/qa/$tag.tsv
Add-Content -Encoding utf8 work/qa/$tag.tsv $line
python -X utf8 build.py --marker --qa "@work/qa/$tag.tsv" --out "build/$tag.gba"
# six presses take the script to the menu (it opens at ~frame 275); then idle so it stays up
$route = ((1..6 | ForEach-Object { "34 -;6 a" }) -join ";") + ";200 -"
python -X utf8 "$S/scripts/emu.py" "build/$tag.gba" --out "work/qa/$tag" --state-in work/qa/w1_B2_7000.mss --frames 440 --route-str $route --shots "320,400"
