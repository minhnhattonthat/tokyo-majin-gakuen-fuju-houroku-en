# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/vwf.txt | drawn for this project | MIT, same as repo | yes | dialogue / menu VWF (tools/vwf.py) | - |
| fonts/liberation/LiberationSans-Bold.ttf | https://github.com/liberationfonts/liberation-fonts release 2.1.5 | SIL OFL 1.1 (fonts/liberation/LICENSE) | yes, as rendered glyphs | graphics-text redraws (tools/gfx.py: title menu) | - |
| fonts/permanentmarker/PermanentMarker-Regular.ttf | https://github.com/google/fonts apache/permanentmarker (Font Diner, upstream commit b0786e3) | Apache 2.0 (fonts/permanentmarker/LICENSE.txt) | yes, as rendered glyphs | title logo + end-card logo (tools/gfx_logo.py, D17) | - |
