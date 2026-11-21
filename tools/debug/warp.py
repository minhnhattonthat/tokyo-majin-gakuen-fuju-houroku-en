"""warp.py: reach any scene from a cold boot, by name from tools/debug/scenes.tsv or by raw spec (B05, A3.2, MODE6.1).

    python -X utf8 tools/debug/warp.py NAME|SPEC [...] [--rom build/tmgfh_en.gba] [--out work/qa/warp] [--mash 60]
    python -X utf8 tools/debug/warp.py --all [--jobs 3] [--states]     # every scenes.tsv row; exit 1 if any fails
    python -X utf8 tools/debug/warp.py --list

Each run: emu.py with the row's route (default tools/routes/newgame.txt) + tools/debug/warp.lua, a shot every
--every frames after the warp, a contact sheet, and a pass/fail from the log: the run passes when warp.lua logged
"WARP ok" (the loader read the expected table entry, or the mode was set) and the final frame is not blank.
--states also saves work/states/<name>.mss at the end of the run (cold-boot made, so regenerate after code/font edits).
"""
import argparse
import csv
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from skill import SKILL  # noqa: E402

SCENES = os.path.join(ROOT, 'tools', 'debug', 'scenes.tsv')
WARP_LUA = os.path.join(ROOT, 'tools', 'debug', 'warp.lua')
DEFAULT_ROUTE = os.path.join(ROOT, 'tools', 'routes', 'newgame.txt')
WARP_FRAME = 1670  # newgame route: story mode is entered here


def load_scenes():
    rows = []
    with open(SCENES, encoding='utf-8', newline='') as f:
        for r in csv.DictReader((ln for ln in f if not ln.startswith('#')), delimiter='\t'):
            rows.append(r)
    return rows


def row_for(name, rows):
    for r in rows:
        if r['name'] == name:
            return r
    # raw spec: a one-off row
    return {'name': name.replace('.', '_'), 'spec': name, 'frames': '', 'mash': '', 'route': '', 'sav': '', 'vars': '',
            'what': ''}


def run(row, a):
    name = row['name']
    out = os.path.join(a.out, name)
    os.makedirs(out, exist_ok=True)
    frames = int(row.get('frames') or a.frames)
    route = row.get('route') or DEFAULT_ROUTE
    if not os.path.isabs(route):
        route = os.path.join(ROOT, route)
    first = 600 if row['spec'].startswith('WAIT') else WARP_FRAME + a.every
    shots = ','.join(str(f) for f in range(first, frames + 1, a.every))
    cmd = [sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'emu.py'), a.rom, '--out', out,
           '--route', route, '--frames', str(frames), '--shots', shots, '--timeout', str(a.timeout),
           '--script', WARP_LUA, '--var', "SCENE='%s'" % row['spec'], '--sheet']
    mash = row.get('mash') or (str(a.mash) if a.mash else '')
    if mash and mash != '0':
        cmd += ['--mash', mash]
    for v in (row.get('vars') or '').split():
        cmd += ['--var', v]
    if row.get('sav'):
        cmd += ['--sav', os.path.join(ROOT, row['sav'])]
    if a.states:
        os.makedirs(os.path.join(ROOT, 'work', 'states'), exist_ok=True)
        cmd += ['--state-out', os.path.join(ROOT, 'work', 'states', name + '.mss')]
    with open(os.path.join(out, 'run.txt'), 'w', encoding='utf-8') as lf:
        p = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT)
    log = ''
    lp = os.path.join(out, 'log.txt')
    if os.path.exists(lp):
        log = open(lp, encoding='utf-8', errors='replace').read()
    ok = p.returncode == 0 and 'WARP ok' in log and 'WARP WRONG' not in log
    blank = False
    fin = os.path.join(out, 'final.png')
    if ok and os.path.exists(fin):
        sys.path.insert(0, os.path.join(SKILL, 'scripts'))
        import sheet
        # a fade can land on the final frame; a hang leaves every late shot blank
        import glob
        late = sorted(glob.glob(os.path.join(out, 'f*.png')))[-3:] + [fin]
        blank = all(sheet.is_blank(sheet.read_png(p)) for p in late)
        ok = not blank
    why = '' if ok else ('exit %d' % p.returncode if p.returncode else 'blank final' if blank else 'no WARP ok')
    return name, ok, why, out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('names', nargs='*')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--rom', default=os.path.join(ROOT, 'rom', 'base.gba'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'work', 'qa', 'warp'))
    ap.add_argument('--frames', type=int, default=3000)
    ap.add_argument('--every', type=int, default=150)
    ap.add_argument('--mash', type=int, default=0, help='default mash period for rows without one')
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--timeout', type=int, default=300)
    ap.add_argument('--states', action='store_true')
    a = ap.parse_args()
    rows = load_scenes()
    if a.list:
        for r in rows:
            print('%-16s %-10s %s' % (r['name'], r['spec'], r['what']))
        return 0
    todo = rows if a.all else [row_for(n, rows) for n in a.names]
    if not todo:
        ap.error('give scene names, or --all')
    for sav in sorted({r['sav'] for r in todo if r.get('sav')}):
        if not os.path.exists(os.path.join(ROOT, sav)):
            # the base save is game-written by our own route (save.py make), so a clean clone can regenerate it
            print('making', sav)
            subprocess.run([sys.executable, '-X', 'utf8', os.path.join(ROOT, 'tools', 'debug', 'save.py'), 'make',
                            '--rom', a.rom], check=True, cwd=ROOT)
    bad = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for name, ok, why, out in ex.map(lambda r: run(r, a), todo):
            print('%-16s %s %s' % (name, 'ok  ' if ok else 'FAIL', why or out))
            bad += not ok
    print('%d/%d ok' % (len(todo) - bad, len(todo)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
