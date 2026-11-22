"""inkbars.py: is each menu label centred in its highlight bar? ($SKILL inkbox.py on the bar found in the shot)

    python -X utf8 tools/debug/inkbars.py                      # every row of docs/qa/inkbox.tsv; exit 1 if any fails
    python -X utf8 tools/debug/inkbars.py SHOT.png --bar R,G,B [--ink R,G,B] [--tol 2]

The bar is the cursor highlight behind the selected item (this game's menus are art buttons, so the highlight is the
only box with a clean edge). Its x range = the pixels of exactly colour --bar (the bar's top band); its y range = from
that band's top down while the column just inside the bar's left edge differs from the column just outside it.
Ink = pixels within --diff of --ink (the label's fill), so art behind the text does not count.
--outline: the highlight is a frame drawn in --bar (title menu); the rect is that frame's inside.
docs/qa/inkbox.tsv: shot<TAB>bar<TAB>ink<TAB>outline (y or empty)<TAB>rect (x,y,w,h: given instead of found)<TAB>what
(shot paths relative to the repo root).
"""
import argparse
import csv
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL  # noqa: E402

TABLE = ROOT / 'docs' / 'qa' / 'inkbox.tsv'


def rgb(s):
    return tuple(int(v) for v in s.split(','))


def bar_rect(png, bar, outline=False):
    im = Image.open(png).convert('RGB')
    pts = [(x, y) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y)) == bar]
    if not pts:
        return None
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0 = min(p[1] for p in pts)
    if outline:     # a frame drawn in the bar colour: its inside
        y1 = max(p[1] for p in pts)
        return x0 + 1, y0 + 1, x1 - x0 - 1, y1 - y0 - 1
    y1 = y0
    if x0 > 0:
        while y1 + 1 < im.height and im.getpixel((x0 + 1, y1 + 1)) != im.getpixel((x0 - 1, y1 + 1)):
            y1 += 1
    else:
        y1 = max(p[1] for p in pts)
    return x0, y0, x1 - x0 + 1, y1 - y0 + 1


def check(png, bar, ink, tol, diff, outline=False, rect=''):
    r = tuple(int(v) for v in rect.split(',')) if rect else bar_rect(png, rgb(bar), outline)
    if r is None:
        return 2, 'no pixel of bar colour %s' % bar
    p = subprocess.run([sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts' / 'inkbox.py'), str(png),
                        '%d,%d,%d,%d' % r, '--ink', ink, '--diff', str(diff), '--tol', str(tol)],
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('shot', nargs='?')
    ap.add_argument('--bar')
    ap.add_argument('--ink', default='248,240,244')
    ap.add_argument('--tol', type=int, default=2)
    ap.add_argument('--diff', type=int, default=60)
    ap.add_argument('--outline', action='store_true', help='the highlight is a frame in the bar colour')
    a = ap.parse_args()
    if a.shot:
        rows = [{'shot': a.shot, 'bar': a.bar, 'ink': a.ink, 'what': '', 'outline': 'y' if a.outline else ''}]
    else:
        with open(TABLE, encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f, delimiter='\t'))
    bad = 0
    for row in rows:
        png = ROOT / row['shot'] if not Path(row['shot']).is_absolute() else Path(row['shot'])
        code, out = check(png, row['bar'], row['ink'] or a.ink, a.tol, a.diff, row.get('outline') == 'y',
                          row.get('rect') or '')
        bad += code != 0
        print('%-4s %-28s %s  %s' % ('ok' if code == 0 else 'FAIL', row.get('what', ''), out, row['shot']))
    print('%d/%d centred' % (len(rows) - bad, len(rows)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
