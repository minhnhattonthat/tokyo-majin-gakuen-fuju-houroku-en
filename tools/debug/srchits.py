"""srchits.py: which runs loaded which assets, from srcall.lua / srclog.lua logs.

    python -X utf8 tools/debug/srchits.py LOGDIR.. [--assets 0xD1EC50,0xD280D0..] [--span 0x400]

Walks each LOGDIR for log.txt, reads SRCALL/SRC lines and prints, per asset offset, the runs and frames whose
source r0 lies in [asset, asset + span). Without --assets, uses the open rows listed in ASSETS below.
"""
import argparse
import os
import re

# graphics rows with no group yet (docs/re/graphics.md); (offset, label)
ASSETS = [
    (0xB1AC8C, 'S8 small labels'), (0xBEF3A8, 'S14 emblem'), (0xBF07C8, 'S14 emblem'),
    (0xC03F88, 'S16 strip'), (0xC1ADF8, 'S16 strip'), (0xC37968, 'S16 icons'), (0xC37D88, 'S16 frame'),
    (0xD1EC50, 'S23 Tokyo map'), (0xD280D0, 'S25 brush'), (0xD2F0D8, 'S25 brush'), (0xD30448, 'S25 brush'),
    (0xD2A248, 'S26 1998 date'), (0xD35868, 'S26/S29 tutorial UI'), (0xD333B8, 'S29 tutorial panel'),
    (0xACCCCC, 'VS/CLASH/Attack-Wait'), (0xD65298, 'rematch menu'),
]
LINE = re.compile(r'SRC(?:ALL)? f(\d+) lr=([0-9A-F]+) r0=([0-9A-F]+) r1=([0-9A-F]+) r2=([0-9A-F]+)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dirs', nargs='+')
    ap.add_argument('--assets')
    ap.add_argument('--span', type=lambda s: int(s, 0), default=0x400)
    a = ap.parse_args()
    assets = [(int(x, 0), x) for x in a.assets.split(',')] if a.assets else ASSETS
    hits = {off: [] for off, _ in assets}
    for d in a.dirs:
        for root, _, files in os.walk(d):
            if 'log.txt' not in files:
                continue
            for ln in open(os.path.join(root, 'log.txt'), encoding='utf-8', errors='replace'):
                m = LINE.search(ln)
                if not m:
                    continue
                r0 = int(m.group(3), 16) - 0x08000000
                for off, _ in assets:
                    if off <= r0 < off + a.span:
                        hits[off].append('%s f%s r0=%06X lr=%s dst=%s' % (os.path.relpath(root, d), m.group(1), r0,
                                                                         m.group(2), m.group(4)))
    for off, label in assets:
        print('%06X %s: %s' % (off, label, '; '.join(hits[off][:6]) if hits[off] else '-'))


if __name__ == '__main__':
    main()
