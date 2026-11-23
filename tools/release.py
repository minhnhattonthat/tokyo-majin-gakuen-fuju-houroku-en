"""release.py: build, gate, patch and zip a release ($SKILL/references/pipeline.md §Release).

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-smoke]

Stops at the first failure, in this order:
  1. build.py (a plain build: no --marker, no --qa rows; the debug tool is emulator-side Lua in tools/debug/,
     so nothing of it is in the ROM)
  2. tools/check.py (tests + text lint)
  3. smoke boot of the build (emu.py --smoke, tools/routes/boot.txt)
  4. jp_left.py --sjis --gba-ptrs --known tools/jp_known.txt (exit 0 = no Japanese left but the listed runs)
  5. qa_gate.py check on every work/qa/**/manifest.tsv, each against the verdicts/ dir beside it
  6. tools/cover.py report (text coverage, waivers in docs/text_unshown.tsv)
  7. no unticked "- [ ]" line in docs/polish.md
  8. no template placeholder ("<Game title>" style) left in README.md or docs/release_readme.md
  9. BPS patch (bps.py make re-applies it), then a second, independent apply onto a fresh copy of the dump and a
     byte compare with the build
 10. zip = patch + README.txt (docs/release_readme.md with the hashes filled in), ZIP_DEFLATED

Output: release/v<VERSION>/ (gitignored). Refuses to overwrite an existing version's files without --force.
The playable image stays in build/tmgfh_en.gba. Publishing is the user's call: this never uploads anything.
"""
import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL  # noqa: E402

SCRIPTS = Path(SKILL) / 'scripts'
BASE = ROOT / 'rom' / 'base.gba'
BUILT = ROOT / 'build' / 'tmgfh_en.gba'
NAME = 'Tokyo_Majin_Gakuen_Fuju_Houroku_EN'
PLACEHOLDER = re.compile(r'<(?:Game title|platform|publisher|year|repo|file|size|sha1|game|ext|Dialogue|Menus|Title'
                         r'|Name entry|Songs|Translated|Left in|none known)[^>]*>|\{\{[^}]*\}\}')


def run(step, cmd):
    print(f'== {step}: {" ".join(str(c) for c in cmd)}', flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT)
    if r.returncode:
        sys.exit(f'release: FAILED at {step} (exit {r.returncode})')


def py(*args):
    return [sys.executable, '-X', 'utf8', *args]


def hashes(data):
    return {'size': len(data), 'crc32': '%08X' % zlib.crc32(data), 'md5': hashlib.md5(data).hexdigest(),
            'sha1': hashlib.sha1(data).hexdigest()}


def gate_manifests():
    for m in sorted((ROOT / 'work' / 'qa').rglob('manifest.tsv')):
        verdicts = m.parent / 'verdicts'
        if not verdicts.is_dir():
            sys.exit(f'release: {m} has no verdicts/ dir beside it (retire it as manifest.tsv.retired?)')
        run(f'qa_gate {m.relative_to(ROOT)}', py(SCRIPTS / 'qa_gate.py', 'check', m, verdicts))


def check_text_files():
    polish = (ROOT / 'docs' / 'polish.md').read_text(encoding='utf-8').splitlines()
    open_items = [ln for ln in polish if ln.lstrip().startswith('- [ ]')]
    if open_items:
        sys.exit('release: docs/polish.md has unticked lines:\n' + '\n'.join(open_items))
    print('== polish: all ticked')
    for f in (ROOT / 'README.md', ROOT / 'docs' / 'release_readme.md'):
        hits = PLACEHOLDER.findall(f.read_text(encoding='utf-8'))
        if hits:
            sys.exit(f'release: template placeholders left in {f.relative_to(ROOT)}: {sorted(set(hits))}')
    print('== READMEs: no placeholders')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--version', default='1.0')
    ap.add_argument('--force', action='store_true', help="overwrite this version's existing release files")
    ap.add_argument('--skip-smoke', action='store_true', help='skip the emulator smoke boot (not for a real release)')
    a = ap.parse_args(argv)

    out = ROOT / 'release' / f'v{a.version}'
    patch = out / f'{NAME}_v{a.version}.bps'
    zpath = out / f'{NAME}_v{a.version}.zip'
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f'release: {out.relative_to(ROOT)} already has v{a.version} files; pass --force to overwrite')

    run('build', py(ROOT / 'build.py'))
    run('check', py(ROOT / 'tools' / 'check.py'))
    if not a.skip_smoke:
        run('smoke', py(SCRIPTS / 'emu.py', BUILT, '--out', ROOT / 'work' / 'qa' / 'release_smoke',
                        '--route', ROOT / 'tools' / 'routes' / 'boot.txt', '--smoke'))
    run('jp_left', py(SCRIPTS / 'jp_left.py', BUILT, '--sjis', '--gba-ptrs', '--known', ROOT / 'tools' / 'jp_known.txt',
                      '--limit', '0'))
    gate_manifests()
    run('coverage', py(ROOT / 'tools' / 'cover.py', 'report'))
    check_text_files()

    out.mkdir(parents=True, exist_ok=True)
    run('patch', py(SCRIPTS / 'bps.py', 'make', BASE, BUILT, patch))
    built = BUILT.read_bytes()
    with tempfile.TemporaryDirectory() as td:
        clean = Path(td) / 'clean.gba'
        shutil.copyfile(BASE, clean)
        applied = Path(td) / 'applied.gba'
        run('re-apply', py(SCRIPTS / 'bps.py', 'apply', clean, patch, applied))
        if applied.read_bytes() != built:
            sys.exit('release: the patch applied to a clean dump does not equal build/tmgfh_en.gba')
    print('== re-apply: patched dump == build')

    base_h, out_h = hashes(BASE.read_bytes()), hashes(built)
    readme = (ROOT / 'docs' / 'release_readme.md').read_text(encoding='utf-8')
    fill = {'VERSION': a.version, 'PATCH': patch.name}
    fill.update({f'BASE_{k.upper()}': str(v) for k, v in base_h.items()})
    fill.update({f'OUT_{k.upper()}': str(v) for k, v in out_h.items()})
    unknown = sorted(set(re.findall(r'@([A-Z_0-9]+)@', readme)) - set(fill))
    if unknown:
        sys.exit(f'release: docs/release_readme.md has fields release.py does not fill: {unknown}')
    readme = re.sub(r'@([A-Z_0-9]+)@', lambda m: fill[m.group(1)], readme)
    readme += '\n' + (ROOT / 'docs' / 'haiku.md').read_text(encoding='utf-8').replace('# Haiku', '## Haiku', 1)
    (out / 'README.txt').write_text(readme.replace('\n', '\r\n'), encoding='utf-8')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(out / 'README.txt', 'README.txt')
    with zipfile.ZipFile(zpath) as z:
        names = sorted(z.namelist())
        if names != sorted([patch.name, 'README.txt']) or z.testzip() is not None:
            sys.exit(f'release: zip check failed: {names}')
    print(f'== done: {zpath.relative_to(ROOT)} ({zpath.stat().st_size} bytes) holds {names}')
    print(f'   base  {BASE.name}: {base_h}')
    print(f'   build {BUILT.name}: {out_h}')


if __name__ == '__main__':
    main()
