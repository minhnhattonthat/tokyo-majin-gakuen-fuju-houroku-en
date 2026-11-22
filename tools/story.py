"""Write story-pass chapter files for the read-only review (translate-retro-game: Story pass).

    python -X utf8 tools/story.py [--out work/qa/story/chapters] [--sys-size 250]

One file per story chapter: B00..B39 each, A-scenes grouped by their first number (A0 = A0.0, A0.1, ...), and
system text (cf, d1, d6) in chunks of --sys-size rows. Each row:

    >> id | speaker | JP          (layout breaks {rt} shown as " / ")
       EN

Rows of kind `grid` are skipped. Regenerate after every script edit, then re-run qa_gate.py init.
"""
import argparse
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = re.compile(r'^【([^】]*)】(?:\{rt\})?')


def rows(path):
    with open(path, encoding='utf-8', newline='') as f:
        r = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    head = r[0]
    for x in r[1:]:
        d = dict(zip(head, x))
        if d.get('kind') == 'grid' or not d.get('jp', '').strip():
            continue
        yield d


def flat(s):
    return s.replace('{rt}', ' / ')


def entry(d):
    jp, en = d['jp'], d.get('en', '')
    m = TAG.match(jp)
    speaker = m.group(1) if m else '-'
    if m:
        jp = jp[m.end():]
        n = TAG.match(en)
        if n:
            en = en[n.end():]
    return '>> %s | %s | %s\n   %s\n' % (d['id'], speaker, flat(jp), flat(en))


def scene_key(name):
    return [int(p) if p.isdigit() else p for p in re.split(r'(\d+)', name)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'work', 'qa', 'story', 'chapters'))
    ap.add_argument('--sys-size', type=int, default=250)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    chapters = {}
    scenes = os.path.join(ROOT, 'script', 'scenes')
    for name in sorted(os.listdir(scenes), key=scene_key):
        if not name.endswith('.tsv'):
            continue
        stem = name[:-4]
        ch = stem if stem.startswith('B') else stem.split('.')[0]
        chapters.setdefault(ch, []).append('## %s\n' % stem)
        chapters[ch].extend(entry(d) for d in rows(os.path.join(scenes, name)))
    for sys_name in ('cf', 'd1', 'd6'):
        lines = [entry(d) for d in rows(os.path.join(ROOT, 'script', 'system', sys_name + '.tsv'))]
        for i in range(0, len(lines), a.sys_size):
            chapters['sys_%s_%02d' % (sys_name, i // a.sys_size + 1)] = lines[i:i + a.sys_size]
    for ch, lines in chapters.items():
        with open(os.path.join(a.out, ch + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.writelines(lines)
    print('%d chapter files in %s' % (len(chapters), a.out), file=sys.stderr)


if __name__ == '__main__':
    main()
