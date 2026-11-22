"""build.py: build the patched ROM.

    python -X utf8 build.py                # -> build/tmgfh_en.gba
    python -X utf8 build.py --identity     # also fail unless the output is byte-identical to the dump
    python -X utf8 build.py --marker       # -> build/tmgfh_marker.gba: every row replaced by its id marker

Steps: check the dump against rom.sha1, unpack every story scene (tools/scenes.py) and every pointed system string
(tools/strslots.py), put in each one's text from script/*.tsv (`en` through the VWF encoder where translated, else
`jp`; tools/extract.py, tools/vwf.py), repack them (scenes spill into SPILL when REGION is full), install the VWF
hook when any `en` exists, write the ROM. With no `en` yet the output must equal the dump: that proves the scene
serializer (label offsets, padding, table A/B repointing), the string slot writer and the script codec.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))

import check_rom  # noqa: E402
import codestr  # noqa: E402
import extract  # noqa: E402
import scenes  # noqa: E402
import marker  # noqa: E402
import gfx  # noqa: E402
import patches  # noqa: E402
import strslots  # noqa: E402
import vwf  # noqa: E402

BASE = ROOT / 'rom' / 'base.gba'
OUT = ROOT / 'build' / 'tmgfh_en.gba'


SPILL = (0xE62000, vwf.HOOK)   # free 0xFF space (docs/re/text.md) for scenes that no longer fit REGION


def build(orig, script=None, mark=False, qa=None):
    """return the rebuilt ROM bytes from the original dump bytes and the script rows ({id: row}, extract.load()).
    Rows with `en` go through the VWF encoder (tools/vwf.py), the rest keep `jp`; with no `en` anywhere the output
    is the dump. mark: replace every row's `en` with its marker (tools/marker.py). qa: {id: en} overrides applied
    last (width tests, stress lines)."""
    script = extract.load() if script is None else script
    font = vwf.load_font(orig)
    if mark:
        script = marker.apply(script, font)
    if qa:
        script = dict(script)
        for rid, en in qa.items():
            script[rid] = dict(script[rid], en=en)
    enc = vwf.Encoder(font, [r['en'] for r in script.values() if r['en'] and r['kind'] != 'pref']) if any(
        r['en'] for r in script.values()) else None
    if mark:
        marker.refit(script, enc)

    def text_for(row):
        return enc.encode(row['en']) if row['en'] else extract.text_for(row)

    rom = bytearray(orig)
    names = extract.scene_names(orig)
    scs = scenes.parse_all(orig)
    for sc in scs:
        n = 0
        for t in sc.toks:
            if t.kind != 'op':
                t.text = text_for(script['%s.%04d' % (names[sc.addr], n)])
                n += 1
    end = scenes.pack(rom, scs, regions=(scenes.REGION, SPILL))
    spill = [(end + 3) & ~3 if SPILL[0] <= end <= SPILL[1] else SPILL[0], SPILL[1]]
    for s in strslots.scan(orig):
        strslots.write(rom, s, text_for(script['%06X' % s.addr]), spill)
    if enc:
        codestr.apply(rom, enc, script)  # code-area strings: effect pieces + loop patches, prefecture picker
        vwf.install(rom, enc, font)
        patches.apply(rom, check=not mark)  # code patches (tools/patches.py): default-name copy length
        if not mark:
            gfx.apply(rom)  # graphics-text redraws (tools/gfx.py, gfx/*.tsv)
    return bytes(rom)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--identity', action='store_true', help='fail unless the output equals the dump')
    ap.add_argument('--marker', action='store_true', help='marker build (phase 5): every row shows its id')
    ap.add_argument('--qa', action='append', default=[], metavar='ID=TEXT',
                    help='override one row\'s en (script notation); repeatable; @FILE reads ID<TAB>TEXT lines')
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    a.out = a.out or (OUT.with_name('tmgfh_marker.gba') if a.marker else OUT)
    qa = {}
    for q in a.qa:
        lines = Path(q[1:]).read_text(encoding='utf-8').splitlines() if q.startswith('@') else [q.replace('=', '\t', 1)]
        for ln in lines:
            if ln.strip() and not ln.startswith('#'):
                k, v = ln.split('\t', 1)
                qa[k] = v
    check_rom.check()
    orig = BASE.read_bytes()
    want = next(l for l in (ROOT / 'rom.sha1').read_text(encoding='utf-8').splitlines()
                if l.strip() and not l.startswith('#')).split()[0].lower()
    if hashlib.sha1(orig).hexdigest() != want:
        sys.exit('%s is not the dump in rom.sha1: copy the checked dump over it' % BASE)
    out = build(orig, mark=a.marker, qa=qa)
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
