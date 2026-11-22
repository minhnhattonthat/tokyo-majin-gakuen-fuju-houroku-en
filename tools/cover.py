"""cover.py: text coverage runs (phase 8 gate; $SKILL/references/emulator-qa.md §Text coverage).

    python -X utf8 tools/cover.py scenes [B05 A3.2 ..] [--jobs 3]   # warp + mash through every story scene
    python -X utf8 tools/cover.py scenes --branches                  # again, once per branch option (forcebranch.lua)
    python -X utf8 tools/cover.py gaps [--rounds 8]                  # restart scenes at the label of each unread line
    python -X utf8 tools/cover.py rows [NAME ..]                   # the tools/debug/scenes.tsv rows (menus, battles)
    python -X utf8 tools/cover.py report [--by-scene]                # textcover.py over work/qa/cover
    python -X utf8 tools/cover.py remap work/qa/cover_b19 --base b359d4e  # carry an old build's coverage over

Each run is a cold boot of build/tmgfh_en.gba through tools/debug/warp.py with $SKILL lua/probes/textcover.lua on
every text range (system strings, scenes, SPILL), so its log.txt lists the addresses the game read. `scenes` uses
tools/routes/newgame_fast.txt (Text Speed Fast, Effects Off) and mashes A (period 4, hold 2: ~43 frames a line), with
frames sized from the scene's line count. The build writes build/strings.tsv (build.py write_strings); a copy is kept
in work/qa/cover/strings.tsv at each run, and `report` uses that copy, because addresses move on rebuilds.
Waivers: docs/text_unshown.tsv (id<TAB>reason).
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL  # noqa: E402

OUT = ROOT / 'work' / 'qa' / 'cover'
ROM = ROOT / 'build' / 'tmgfh_en.gba'
STRINGS = ROOT / 'build' / 'strings.tsv'
WAIVE = ROOT / 'docs' / 'text_unshown.tsv'
PROBE = os.path.join(SKILL, 'scripts', 'lua', 'probes', 'textcover.lua')
RANGES = "RANGES='08CF0000-08D7A000,08D82324-08E2B97C,08E62000-08F00000'"
WARP_AT = 3080      # newgame_fast.txt: story mode starts here
PER_LINE = 50       # frames per dialogue line with --mash 4 --mash-hold 2 (measured 43 on B05)


def scene_lines():
    out = {}
    for p in sorted((ROOT / 'script' / 'scenes').glob('*.tsv')):
        with open(p, encoding='utf-8') as f:
            out[p.stem] = sum(1 for ln in f if ln.strip() and not ln.startswith('id\t'))
    return out


def scene_ways():
    """{scene name: most ways of any branch op in it} (0A 9, 0F nn, 08/01 2; tools/debug/forcebranch.lua)"""
    import extract
    import scenes
    d = (ROOT / 'rom' / 'base.gba').read_bytes()
    names = extract.scene_names(d)
    out = {}
    for sc in scenes.parse_all(d):
        w = 1
        for i, t in enumerate(sc.toks):
            if t.kind == 'choice' or (t.kind == 'op' and t.raw[0] in (0x0A, 0x08, 0x01)):
                j = i + 1
                while j < len(sc.toks) and sc.toks[j].kind == 'op' and sc.toks[j].raw[0] == 9:
                    j += 1
                w = max(w, j - i - 1)
        out[names[sc.addr]] = w
    return out


def shown_ids():
    """ids read in any run under OUT (by the kept strings.tsv)"""
    ids = {}
    for ln in open(OUT / 'strings.tsv', encoding='utf-8'):
        k, v = ln.split()
        ids[int(v, 16)] = k
    seen = set()
    for log in OUT.rglob('log.txt'):
        for ln in open(log, encoding='utf-8', errors='replace'):
            if ln.startswith('TEXT '):
                k = ids.get(int(ln.split()[1], 16))
                if k:
                    seen.add(k)
    return seen


def label_starts():
    """{scene: [(label index, first line number at or after the label)]} from the original ROM"""
    import extract
    import scenes
    d = (ROOT / 'rom' / 'base.gba').read_bytes()
    names = extract.scene_names(d)
    out = {}
    for sc in scenes.parse_all(d):
        first, n = {}, 0
        for i, t in enumerate(sc.toks):
            if t.kind != 'op':
                first[i] = n
                n += 1
        ks = sorted(first)
        out[names[sc.addr]] = [(li, first[next((i for i in ks if i >= ti), ks[-1])]) for li, ti in enumerate(sc.labels)]
    return out


def gap_rounds(a):
    """rounds of label-start runs (tools/debug/startlabel.lua) until no scene line is left unread or a round adds
    nothing: each scene with unread lines starts at the last label at or before its first unread line"""
    from concurrent.futures import ThreadPoolExecutor
    lines, starts = scene_lines(), label_starts()
    # label runs kept from earlier invocations count as tried (label_r<round>/L<label>/<scene>)
    tried = {(d.name, int(d.parent.name[1:])) for d in OUT.glob('label_r*/L*/*') if d.is_dir()}
    first_rnd = 1 + max((int(d.name[7:]) for d in OUT.glob('label_r*')), default=0)
    for rnd in range(first_rnd, first_rnd + a.rounds):
        seen = shown_ids()
        todo = []
        for sc, n in sorted(lines.items()):
            miss = [i for i in range(n) if '%s.%04d' % (sc, i) not in seen]
            for i in miss:  # every untried label that holds an unread line (one run per label)
                lab = max((li for li, first in starts[sc] if first <= i), default=0)
                if (sc, lab) not in tried:
                    tried.add((sc, lab))
                    todo.append((sc, lab, n - i))
        print('round %d: %d scenes' % (rnd, len(todo)), flush=True)
        if not todo:
            return 0

        def one(job):
            sc, lab, left = job
            frames = WARP_AT + 600 + PER_LINE * left
            return warp([sc], min(80000, frames), [
                '--route', str(ROOT / 'tools' / 'routes' / 'newgame_fast.txt'), '--mash', '4', '--mash-hold', '2',
                '--script', str(ROOT / 'tools' / 'debug' / 'startlabel.lua'), '--var', 'LABEL=%d' % lab],
                argparse.Namespace(jobs=1, timeout=a.timeout), 'label_r%d/L%d' % (rnd, lab))
        with ThreadPoolExecutor(a.jobs) as ex:
            list(ex.map(one, todo))
    return 0


def warp(names, frames, extra, a, sub):
    cmd = [sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'debug' / 'warp.py'), *names, '--rom', str(ROM),
           '--out', str(OUT / sub), '--frames', str(frames), '--every', str(max(600, frames // 8)),
           '--jobs', str(a.jobs), '--timeout', str(a.timeout), '--script', PROBE, '--var', RANGES, *extra]
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    drop_runtimes(OUT / sub)
    return rc


def drop_runtimes(root):
    """delete each finished run's private emulator dir (emu.py mesen_run): its files are hard links to tools/mesen,
    but NTFS allows 1024 links per file, after which every run copies ~107 MB (that filled C: in session 35)"""
    for d in Path(root).rglob('_mesen'):
        if (d.parent / 'final.png').exists():
            shutil.rmtree(d, ignore_errors=True)


def script_rows(rev=None):
    """{id: (jp, en)} of every script/ TSV, from the working tree or from git revision rev"""
    out = {}
    for p in sorted((ROOT / 'script').rglob('*.tsv')):
        rel = p.relative_to(ROOT).as_posix()
        if rev:
            r = subprocess.run(['git', 'show', '%s:%s' % (rev, rel)], cwd=ROOT, capture_output=True)
            if r.returncode:
                continue
            text = r.stdout.decode('utf-8')
        else:
            text = p.read_text(encoding='utf-8')
        for ln in text.splitlines():
            c = ln.split('\t')
            if len(c) >= 5 and c[0] != 'id':
                out[c[0]] = (c[3], c[4])
    return out


def remap(a):
    """carry an older build's coverage over to this build: every id shown there whose jp/en are unchanged since
    --base (the commit that build was made from) is written as a TEXT line at its address in this build into
    work/qa/cover/remap_<old dir name>/log.txt. A string's reachability does not depend on its wording; the rows
    whose text changed are printed with the old runs that showed them, to re-run (or check) on this build."""
    old = Path(a.names[0]).resolve()
    if not (old / 'strings.tsv').exists():
        sys.exit('%s has no strings.tsv' % old)
    ids = {}
    for ln in open(old / 'strings.tsv', encoding='utf-8'):
        k, v = ln.split()
        ids[int(v, 16)] = k
    seen, runs = set(), {}
    for log in old.rglob('log.txt'):
        for ln in open(log, encoding='utf-8', errors='replace'):
            if ln.startswith('TEXT '):
                k = ids.get(int(ln.split()[1], 16))
                if k:
                    seen.add(k)
                    runs.setdefault(k, set()).add(log.parent.relative_to(old).as_posix())
    then, now = script_rows(a.base), script_rows()
    new = dict(ln.split() for ln in open(STRINGS, encoding='utf-8'))
    keep = sorted(k for k in seen if k in new and k in then and then[k] == now.get(k))
    changed = sorted(k for k in seen if k in new and then.get(k) != now.get(k))
    dst = OUT / ('remap_' + old.name)
    dst.mkdir(parents=True, exist_ok=True)
    with open(dst / 'log.txt', 'w', encoding='utf-8') as f:
        f.write('# remapped from %s (base %s) by tools/cover.py remap\n' % (old, a.base))
        for k in keep:
            f.write('TEXT %s\n' % new[k])
    print('%d shown in %s, %d carried over, %d changed since %s:' % (len(seen), old.name, len(keep), len(changed),
                                                                     a.base))
    for k in changed:
        print('  %-10s %s' % (k, ' '.join(sorted(runs[k])[:4])))
    return 0


def keep_strings():
    OUT.mkdir(parents=True, exist_ok=True)
    kept = OUT / 'strings.tsv'
    if kept.exists() and kept.read_bytes() != STRINGS.read_bytes():
        sys.exit('%s differs from %s: the build changed since the last coverage run; move work/qa/cover away and '
                 're-run every case' % (kept, STRINGS))
    shutil.copyfile(STRINGS, kept)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('what', choices=('scenes', 'gaps', 'rows', 'report', 'remap'))
    ap.add_argument('--base', help='remap: git commit the old coverage build was made from')
    ap.add_argument('--rounds', type=int, default=8, help='gaps: most rounds')
    ap.add_argument('names', nargs='*')
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--timeout', type=int, default=900)
    ap.add_argument('--by-scene', action='store_true', help='report: unshown counts per scene / system file')
    ap.add_argument('--branches', action='store_true', help='scenes: one run per branch option k of every '
                    'branching scene (tools/debug/forcebranch.lua BRANCH=k), into work/qa/cover/branch<k>')
    a = ap.parse_args()
    if a.what == 'report':
        cmd = [sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'textcover.py'), str(OUT),
               str(OUT / 'strings.tsv')] + (['--waive', str(WAIVE)] if WAIVE.exists() else [])
        if not a.by_scene:
            return subprocess.run(cmd).returncode
        p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        from collections import Counter
        miss = [ln.split()[2] for ln in p.stdout.splitlines() if ln.startswith('NEVER SHOWN')]
        total = Counter((ln.split('\t')[0].split('.')[0] if '.' in ln.split('\t')[0] else 'system')
                        for ln in open(OUT / 'strings.tsv', encoding='utf-8'))
        c = Counter(m.split('.')[0] if '.' in m else 'system' for m in miss)
        for k in sorted(total):
            if c[k]:
                print('%-8s %5d / %5d unshown' % (k, c[k], total[k]))
        print('total %d unshown of %d' % (len(miss), sum(total.values())))
        return p.returncode
    keep_strings()
    if a.what == 'remap':
        if len(a.names) != 1 or not a.base:
            sys.exit('remap OLD_COVER_DIR --base COMMIT')
        return remap(a)
    if a.what == 'gaps':
        return gap_rounds(a)
    if a.what == 'scenes':
        lines = scene_lines()
        names = a.names or sorted(lines)
        # group by length so each warp.py call gets one frame budget
        runs = [(None, names)]
        if a.branches:
            ways = scene_ways()
            runs = [(k, [n for n in names if ways[n] > 1 and (k < ways[n])]) for k in range(9)]
        rc = 0
        for k, todo in runs:
            # resume: a scene whose run dir already has final.png finished in an earlier (interrupted) pass
            sub = OUT / ('scenes' if k is None else 'branch%d' % k)
            todo = [n for n in todo if not (sub / n.replace('.', '_') / 'final.png').exists()]
            lo = 0
            need = {n: WARP_AT + 600 + PER_LINE * lines[n] for n in todo}
            extra = ['--route', str(ROOT / 'tools' / 'routes' / 'newgame_fast.txt'), '--mash', '4', '--mash-hold', '2']
            if k is not None:
                extra += ['--script', str(ROOT / 'tools' / 'debug' / 'forcebranch.lua'), '--var', 'BRANCH=%d' % k]
            for cap in (5000, 10000, 20000, 40000, 80000):
                grp = [n for n in todo if lo < need[n] <= cap]
                lo = cap
                if grp:
                    rc |= warp(grp, cap, extra, a, 'scenes' if k is None else 'branch%d' % k)
        return rc
    return warp(a.names or ['--all'], 3000, [], a, 'rows')


if __name__ == '__main__':
    sys.exit(main())
