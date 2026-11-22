"""covrun.py: one text-coverage run of a menu route (phase 8 system strings), counted by tools/cover.py report.

    python -X utf8 tools/debug/covrun.py NAME (--route R.txt | --route-str "..") [--sav work/saves/allcards.sav]
                                         [--state-in S.mss] [--frames N] [--every N] [--mash N] [--script x.lua]..

Runs $SKILL emu.py on build/tmgfh_en.gba with textcover.lua over the text ranges into work/qa/cover/NAME (a run there
counts in `cover.py report`), then prints the system strings this run showed that no other run under work/qa/cover
had shown, with their en text, and the run's shots as a sheet (work/qa/cover/NAME/sheet.png).
Refuses when build/strings.tsv differs from the coverage copy (the build changed since the coverage runs).
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL  # noqa: E402
import cover  # noqa: E402


def system_en():
    import csv
    out = {}
    for p in (ROOT / 'script' / 'system').glob('*.tsv'):
        with open(p, encoding='utf-8', newline='') as f:
            for r in csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
                if r and r[0] != 'id' and len(r) > 4:
                    out[r[0]] = r[4] or r[3]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('name')
    ap.add_argument('--route')
    ap.add_argument('--route-str')
    ap.add_argument('--sav')
    ap.add_argument('--state-in')
    ap.add_argument('--frames', type=int)
    ap.add_argument('--every', type=int, default=120)
    ap.add_argument('--mash', type=int)
    ap.add_argument('--script', action='append', default=[])
    ap.add_argument('--var', action='append', default=[])
    ap.add_argument('--timeout', type=int, default=900)
    a = ap.parse_args()
    cover.keep_strings()
    out = cover.OUT / a.name
    before = cover.shown_ids()
    cmd = [sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'emu.py'), str(cover.ROM), '--out', str(out),
           '--shot-every', str(a.every), '--sheet', '--timeout', str(a.timeout),
           '--script', cover.PROBE, '--var', cover.RANGES]
    for k in ('route', 'route_str', 'sav', 'state_in', 'frames', 'mash'):
        v = getattr(a, k)
        if v is not None:
            cmd += ['--' + k.replace('_', '-'), str(v)]
    for s in a.script:
        cmd += ['--script', s]
    for v in a.var:
        cmd += ['--var', v]
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    new = sorted(k for k in cover.shown_ids() - before if '.' not in k)
    en = system_en()
    for k in new:
        print('NEW', k, en.get(k, '?'))
    print('%d new system strings; run %s (exit %d)' % (len(new), out, rc))
    return rc


if __name__ == '__main__':
    sys.exit(main())
