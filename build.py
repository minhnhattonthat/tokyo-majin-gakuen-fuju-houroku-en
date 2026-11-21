"""build.py: build the patched ROM.

    python -X utf8 build.py                # -> build/tmgfh_en.gba
    python -X utf8 build.py --identity     # also fail unless the output is byte-identical to the dump

Steps: check the dump against rom.sha1, unpack every story scene (tools/scenes.py) and every pointed system string
(tools/strslots.py), put in each one's text from script/*.tsv (`en` where translated, else `jp`; tools/extract.py),
repack them, write the ROM. With no `en` yet the output must equal the dump: that proves the scene serializer
(label offsets, padding, table A/B repointing), the string slot writer and the script codec before English goes in.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))

import check_rom  # noqa: E402
import extract  # noqa: E402
import scenes  # noqa: E402
import strslots  # noqa: E402

BASE = ROOT / 'rom' / 'base.gba'
OUT = ROOT / 'build' / 'tmgfh_en.gba'


def build(orig, script=None):
    """return the rebuilt ROM bytes from the original dump bytes and the script rows ({id: row}, extract.load())"""
    script = extract.load() if script is None else script
    rom = bytearray(orig)
    names = extract.scene_names(orig)
    scs = scenes.parse_all(orig)
    for sc in scs:
        n = 0
        for t in sc.toks:
            if t.kind != 'op':
                t.text = extract.text_for(script['%s.%04d' % (names[sc.addr], n)])
                n += 1
    scenes.pack(rom, scs)
    for s in strslots.scan(orig):
        strslots.write(rom, s, extract.text_for(script['%06X' % s.addr]))
    return bytes(rom)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--identity', action='store_true', help='fail unless the output equals the dump')
    ap.add_argument('--out', type=Path, default=OUT)
    a = ap.parse_args()
    check_rom.check()
    orig = BASE.read_bytes()
    want = next(l for l in (ROOT / 'rom.sha1').read_text(encoding='utf-8').splitlines()
                if l.strip() and not l.startswith('#')).split()[0].lower()
    if hashlib.sha1(orig).hexdigest() != want:
        sys.exit('%s is not the dump in rom.sha1: copy the checked dump over it' % BASE)
    out = build(orig)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(out)
    same = out == orig
    print('%s  sha1 %s  %s' % (a.out.relative_to(ROOT) if a.out.is_relative_to(ROOT) else a.out,
                               hashlib.sha1(out).hexdigest(), 'identical to the dump' if same else 'differs from the dump'))
    if a.identity and not same:
        diff = [i for i in range(len(orig)) if out[i] != orig[i]]
        print('%d bytes differ, first at %x' % (len(diff), diff[0]))
        sys.exit(1)


if __name__ == '__main__':
    main()
