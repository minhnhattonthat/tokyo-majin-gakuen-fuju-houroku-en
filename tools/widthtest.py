"""widthtest.py: width gate helpers (phase 5): ruler lines for `build.py --qa`, and pixel measurement in shots.

    python -X utf8 tools/widthtest.py ruler PX [START]   # digits ruler whose drawn width is >= PX (prints text, width)
    python -X utf8 tools/widthtest.py fit PX             # filler whose drawn width is exactly PX (or the next below)
    python -X utf8 tools/widthtest.py torture            # every glyph plus double spaces
    python -X utf8 tools/widthtest.py ink SHOT.png Y0 Y1 [X0 X1]   # leftmost / rightmost text-white column in rows Y0-Y1

A ruler runs past the box on purpose: the rightmost white pixel in the shot is the visible limit. Then build a line
exactly at that limit (`fit`) and confirm it shows whole. Text white is the font's colour F (palette 12 entry 15);
`ink` counts pixels with R, G and B all >= 200, so check the band holds no white art.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import vwf  # noqa: E402


def font():
    return vwf.load_font((ROOT / 'rom' / 'base.gba').read_bytes())


def ruler(f, px, start=0):
    s, i = '', start
    while vwf.ext(f, s)[-1] < px:
        s += str(i % 10)
        i += 1
    return s


def fit(f, px, text=None):
    import marker
    return marker.fit(f, text or marker.FILL.capitalize(), px)


TORTURE = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz  0123456789 .,!?\'":;-()/&%+=*#$<>[]_~@ '
           '…—“”‘’♪é 【】「」『』')


def ink(png, y0, y1, x0=0, x1=None):
    from PIL import Image
    im = Image.open(png).convert('RGB')
    x1 = im.width if x1 is None else x1
    xs = [x for x in range(x0, x1) for y in range(y0, y1 + 1) if min(im.getpixel((x, y))) >= 200]
    return (min(xs), max(xs)) if xs else None


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'ruler':
        f = font()
        s = ruler(f, int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)
        print(s, vwf.ext(f, s)[-1])
    elif cmd == 'fit':
        f = font()
        s = fit(f, int(sys.argv[2]))
        print(s, vwf.ext(f, s)[-1])
    elif cmd == 'torture':
        f = font()
        print(TORTURE, vwf.ext(f, TORTURE)[-1])
    elif cmd == 'ink':
        a = [int(v) for v in sys.argv[3:]]
        print(ink(sys.argv[2], *a))
    else:
        print(__doc__)
