"""set_en.py: set or rewrap the `en` of script rows, keeping every TSV column.

    python -X utf8 tools/set_en.py ID=TEXT [ID=TEXT ..]   # dialogue: TEXT is the body, wrapped with its speaker tag
    python -X utf8 tools/set_en.py --rewrap ID [ID ..]    # rewrap dialogue rows the fit lint names
    python -X utf8 tools/set_en.py --note ID=TEXT ..      # set the notes column

Dialogue rows (kind line, 【speaker】 tag) are wrapped by fit.wrap_dialogue; other rows are written as given.
Exit 1 if a body does not fit. Run tools/check.py afterwards.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r'(【[^】]*】)\{rt\}(.*)$')


def main(argv):
    mode = 'set'
    if argv and argv[0] in ('--rewrap', '--note'):
        mode, argv = argv[0][2:], argv[1:]
    want = {}
    for a in argv:
        if mode == 'rewrap':
            want[a] = None
        else:
            k, _, v = a.partition('=')
            want[k] = v
    rows = fit.read_script()
    enc = fit.encoder(rows)
    left = set(want)
    for f in sorted((ROOT / 'script').rglob('*.tsv')):
        lines = f.read_text(encoding='utf8').split('\n')
        changed = False
        for i, line in enumerate(lines):
            p = line.split('\t')
            if len(p) < 6 or p[0] not in want:
                continue
            ncols, rid = len(p), p[0]
            if mode == 'note':
                p[5] = want[rid]
            else:
                m = TAG.match(p[4]) if p[1] == 'line' else None
                if m:
                    body = want[rid] if want[rid] is not None else m.group(2).replace('{rt}', ' ')
                    w = fit.wrap_dialogue(m.group(1), body, enc)
                    if not w:
                        print(f'{rid}: does not fit: {body!r}')
                        return 1
                    p[4] = w
                elif want[rid] is not None:
                    p[4] = want[rid]
            assert len(p) == ncols
            lines[i] = '\t'.join(p)
            changed = True
            left.discard(rid)
            print(rid, p[5] if mode == 'note' else p[4])
        if changed:
            with open(f, 'w', encoding='utf8', newline='') as fh:
                fh.write('\n'.join(lines))
    if left:
        print('not found:', ' '.join(sorted(left)))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
