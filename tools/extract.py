"""extract.py: dump every string of the original ROM to script/*.tsv, and read those files back for the build.

    python -X utf8 tools/extract.py            # write missing script files only (never touches an existing one)
    python -X utf8 tools/extract.py --check    # every file's id/kind/max/jp equals a fresh extract (exit 1 if not)
    python -X utf8 tools/extract.py --force    # rewrite id/kind/max/jp from the ROM, keeping en/notes per id

Files (UTF-8, tab-separated, header `id kind max jp en notes`, text in tools/textcodec.py notation):
    script/scenes/<scene>.tsv   one per story scene; <scene> is B00..B39 (table B, chapters) or A<g>.<i> (table A,
                                event scenes, 13 groups x 10), as in tools/debug/scenes.tsv. id <scene>.<nnnn> =
                                n-th text op of the scene; kind `line` (op 00: `【speaker】{rt}text`) or `choice`
                                (op 0F: options joined by {rt}, ending in {wc}); max empty (scenes are repacked).
    script/system/<range>.tsv   pointed system strings (tools/strslots.py), one file per range (cf, d1, d6); id =
                                ROM offset in hex; kind `str`; max = bytes the in-place slot holds (NUL excluded);
                                longer text is relocated in phase 7. notes list alias pointers.
                                kind `grid`: the name-entry screen's character grid rows (D6E56C-D6E710, drawn as text,
                                read with the u16 input grid at 0xD16740) and the deck-name entry's (D72F00-D730A4):
                                not dialogue, left out of the marker build
                                and translator batches; they change with the English name entry (engine work).
    script/system/code.tsv      the code-area strings 0x06485C-0x064A34 (tools/codestr.py): kind `pref` (the 47
                                Birthplace? prefectures, drawn as rotated graphics; max = px) and kind `piece`
                                (card-effect pieces the printers substitute for {&..} codes; max = units drawn).
An empty `en` means "keep the Japanese": build.py inserts `en` where present, else `jp`.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import codestr  # noqa: E402
import scenes  # noqa: E402
import strslots  # noqa: E402
import textcodec  # noqa: E402

SCRIPT = ROOT / 'script'
COLS = ['id', 'kind', 'max', 'jp', 'en', 'notes']
RANGE_NAMES = {0xCF12F0: 'cf', 0xD16800: 'd1', 0xD63000: 'd6'}
GRIDS = ((0xD6E56C, 0xD6E71C),   # name-entry grid rows, 12-byte slots
         (0xD72F00, 0xD730B0),   # deck-name entry grid rows (符咒編集 -> 新規 -> 符咒名は？), same layout
         (0xD1BDC8, 0xD1BDE0))   # sound-test digit glyph table ０..９ (counters index it by cell)


def scene_names(d):
    """{scene ROM offset: name}"""
    b, a = scenes.table(d)
    names = {s: 'B%02d' % i for i, s in enumerate(b)}
    names.update({s: 'A%d.%d' % (k // 10, k % 10) for k, s in enumerate(a)})
    return names


def extract(d):
    """{relative file path: [row dicts]} for the ROM bytes d, in ROM order"""
    out = {}
    names = scene_names(d)
    for sc in scenes.parse_all(d):
        nm = names[sc.addr]
        rows = []
        for t in sc.toks:
            if t.kind == 'op':
                continue
            rows.append({'id': '%s.%04d' % (nm, len(rows)), 'kind': 'line' if t.kind == 'text' else 'choice',
                         'max': '', 'jp': textcodec.decode(t.text), 'en': '', 'notes': ''})
        if rows:
            out['scenes/%s.tsv' % nm] = rows
    for s in strslots.scan(d):
        lo = next(a for a, b in strslots.RANGES if a <= s.addr < b)
        note = ' '.join('alias %X+%d' % (site, off) for site, off in s.aliases)
        out.setdefault('system/%s.tsv' % RANGE_NAMES[lo], []).append(
            {'id': '%06X' % s.addr, 'kind': 'grid' if any(a <= s.addr < b for a, b in GRIDS) else 'str',
             'max': str(s.cap - 1), 'jp': textcodec.decode(s.text),
             'en': '', 'notes': note})
    out['system/code.tsv'] = codestr.rows(d)
    return out


def covered(d):
    """bytearray, 1 where a byte belongs to an extracted unit (scene tables + region, slot text + NUL)"""
    cov = bytearray(len(d))
    cov[scenes.TABLE_B:scenes.REGION[1]] = b'\1' * (scenes.REGION[1] - scenes.TABLE_B)
    for s in strslots.scan(d):
        cov[s.addr:s.addr + len(s.text) + 1] = b'\1' * (len(s.text) + 1)
    for a, b in codestr.covered(d):
        cov[a:b] = b'\1' * (b - a)
    return cov


def uncovered_runs(d, lo=0, hi=None, minlen=4):
    """(start, end) of Shift-JIS runs in d[lo:hi] that look like text (>= minlen chars, at least half of them kana)
    and touch no extracted byte. Graphics produce kanji-heavy noise, real text is kana-heavy."""
    hi = len(d) if hi is None else hi
    cov = covered(d)
    out, i = [], lo
    while i < hi - 1:
        j = i
        k = kana = 0
        while j < hi - 1:
            w = d[j] << 8 | d[j + 1]
            is_kana = 0x829F <= w <= 0x82F1 or 0x8340 <= w <= 0x8396
            if not (is_kana or 0x889F <= w <= 0x9FFC or 0xE040 <= w <= 0xEAA4) or d[j + 1] == 0x7F:
                break
            kana += is_kana
            j += 2
            k += 1
        if k >= minlen and kana * 2 >= k:
            if not any(cov[i:j]):
                out.append((i, j))
            i = j
        else:
            i += 1
    return out


def read_tsv(path):
    lines = Path(path).read_text(encoding='utf-8').split('\n')
    if lines[-1] == '':
        lines.pop()
    head = lines[0].split('\t')
    if head != COLS:
        raise ValueError('%s: header %r, expected %r' % (path, head, COLS))
    rows = []
    for n, line in enumerate(lines[1:], 2):
        f = line.split('\t')
        if len(f) != len(COLS):
            raise ValueError('%s:%d: %d columns, expected %d' % (path, n, len(f), len(COLS)))
        rows.append(dict(zip(COLS, f)))
    return rows


def write_tsv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = ['\t'.join(COLS)]
    for r in rows:
        for c in COLS:
            if any(ch in r[c] for ch in '\t\r\n'):
                raise ValueError('%s %s: tab or newline in %s' % (path, r['id'], c))
        out.append('\t'.join(r[c] for c in COLS))
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')


def load(root=SCRIPT):
    """{id: row} for every script file under root"""
    out = {}
    for p in sorted(Path(root).rglob('*.tsv')):
        for r in read_tsv(p):
            if r['id'] in out:
                raise ValueError('%s: duplicate id %s' % (p, r['id']))
            out[r['id']] = r
    return out


def text_for(row):
    """bytes to insert for a row: en if translated, else jp"""
    return textcodec.encode(row['en'] if row['en'] else row['jp'])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--rom', type=Path, default=ROOT / 'rom' / 'base.gba')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    files = extract(a.rom.read_bytes())
    bad = written = 0
    for rel, rows in files.items():
        p = SCRIPT / rel
        if a.check or (p.exists() and a.force):
            have = read_tsv(p) if p.exists() else []
            key = lambda r: (r['id'], r['kind'], r['max'], r['jp'])  # noqa: E731
            if a.check:
                if [key(r) for r in have] != [key(r) for r in rows]:
                    print('differs from the ROM:', rel)
                    bad += 1
                continue
            old = {r['id']: r for r in have}
            for r in rows:
                o = old.get(r['id'])
                if o:
                    r['en'], r['notes'] = o['en'], o['notes'] or r['notes']
                    if o['jp'] != r['jp'] and o['en']:
                        print('%s: jp changed under a translation, re-check it' % r['id'])
            write_tsv(p, rows)
            written += 1
        elif not p.exists():
            write_tsv(p, rows)
            written += 1
    extra = sorted(set(str(p.relative_to(SCRIPT).as_posix()) for p in SCRIPT.rglob('*.tsv')) - set(files))
    for e in extra:
        print('no such unit in the ROM:', e)
    if a.check:
        n = sum(len(r) for r in files.values())
        print('%d files, %d strings: %s' % (len(files), n, 'match the ROM' if not bad and not extra else 'MISMATCH'))
        sys.exit(1 if bad or extra else 0)
    print('wrote %d of %d files' % (written, len(files)))


if __name__ == '__main__':
    main()
