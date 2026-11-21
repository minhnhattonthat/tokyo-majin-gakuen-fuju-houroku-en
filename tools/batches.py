"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500] [--only A0.,A1.]   work/tl/bNNN.tsv + build/terms_bNNN.txt
    python -X utf8 tools/batches.py check bNNN ...       check work/tl/bNNN.out.tsv
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/
    python -X utf8 tools/batches.py speakers             speaker tags with no glossary EN yet

Adapted from the skill's assets/batches.py for this game's TSVs (script/**/*.tsv: id kind max jp en notes).
Batch TSV: id, speaker (EN from the glossary, else JP), form, limit, JP. Dialogue rows (scene kind=line) carry the JP
body without the 【speaker】 tag and with line breaks removed; the translator writes the body only, and merge adds
【EN speaker】{rt} and wraps the body to the dialogue box (tools/fit.py). Every other row is translated whole, codes
included. A JP text that repeats (same jp) is batched once; merge writes the English to every row with that jp.
Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / 'work/tl'
SCRIPT = ROOT / 'script'
GLOSSARY = ROOT / 'glossary.md'
MAX_ENTRIES = 150
HDR = ['id', 'kind', 'max', 'jp', 'en', 'notes']

# ---- ADAPTER ----
TOKEN = re.compile(r'\{[^{}]+\}|\[[0-9A-F]{2}\]')
FREE = {'{rt}', '{nl}'}         # line breaks: the English places them (system rows) or merge does (dialogue)
VARIABLE = r'\{(?:name[12]|&[^}]*)\}'
# honorific after a name (kanji / katakana run, or a name code) -> EN form; kinship words are not honorifics
HONORIFICS = {'さん': '-san', 'くん': '-kun', 'ちゃん': '-chan', '先輩': '-senpai', '様': '-sama'}
NOT_HONORIFIC = re.compile(r'(?:お?[母父兄姉婆爺]|皆|奥|嬢|叔[父母]|伯[父母]|王|神|仏|奥|殿|お客|お嬢|お前|皆)$')
SPEAKER = re.compile(r'^【([^】]*)】\{rt\}')


def is_dialogue(row):
    return row['kind'] == 'line' and '{dc}' not in row['jp']


def needs_english(row):
    return bool(row['jp']) and not row['en'] and row['kind'] != 'grid' and '{dc}' not in row['jp']


def body(jp):
    """dialogue JP -> (speaker JP or '', body with breaks removed)"""
    m = SPEAKER.match(jp)
    spk = m.group(1) if m else ''
    rest = jp[m.end():] if m else jp
    return spk, rest.replace('{rt}', '')


def encodable(char):
    return char in fit.vwf.CHAR_BYTE or char in fit.vwf.NORMALIZE
# ---- end of ADAPTER ----


def kind(char):
    if '぀' <= char <= 'ゟ':
        return 'hiragana'
    if '゠' <= char <= 'ヿ':
        return 'katakana'
    if '一' <= char <= '鿿' or char == '々':
        return 'kanji'
    return 'other'


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary(section_filter=lambda s: s != 'Speaker tags'):
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables. The
    "Speaker tags" section is not enforced in text (女, 男 would match everywhere); speakers() reads it."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    section = ''
    for line in GLOSSARY.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            section = line[3:].strip()
        if not section_filter(section):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) >= 2 and cells[0] not in ('JP', '') and not set(cells[0]) <= set('-: '):
            avoid = [x.strip() for x in cells[4].split('/') if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split('/')], [x.strip() for x in cells[1].split('/')], avoid))
    return rows


def speakers(terms=None):
    """JP speaker tag -> EN: the Speaker tags section, then any glossary row whose first JP form is the tag"""
    out = {jps[0]: ens[0] for jps, ens, _ in glossary(lambda s: True)}
    out.update({jps[0]: ens[0] for jps, ens, _ in glossary(lambda s: s == 'Speaker tags')})
    return out


def honorifics(jp):
    """EN forms the JP's honorifics need"""
    need = []
    for jpf, enf in HONORIFICS.items():
        for m in re.finditer(re.escape(jpf), jp):
            before = jp[:m.start()]
            if not before:
                continue
            prev = before[-1]
            if not (kind(prev) in ('kanji', 'katakana') or before.endswith('}')):
                continue
            if jpf == '様' and kind(prev) != 'katakana' and not before.endswith('}'):
                continue
            if NOT_HONORIFIC.search(before):
                continue
            need.append(enf)
    return need


def problems(row, en, terms, enc=None):
    """Every rule, on one translated text (dialogue: the body only)."""
    jp = row['jp']
    if not en.strip():
        return ['empty English']
    out = []
    dlg = is_dialogue(row)
    src = body(jp)[1] if dlg else jp
    plain = TOKEN.sub('', en)
    if bad := sorted({c for c in plain if not encodable(c)}):
        out.append(f'unencodable characters {bad}')
    if re.search(r'\\u[0-9a-fA-F]{4}', en) or '\t' in en:
        out.append('escape sequence or tab in the English')
    if dlg and '{rt}' in en:
        out.append('dialogue body has {rt}: merge wraps it')
    want = Counter(t for t in TOKEN.findall(src) if t not in FREE)
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if want != have:
        out.append(f'control codes differ: JP {dict(want)} EN {dict(have)}')
    if re.search(VARIABLE + r'(st|nd|rd|th)\b', en):
        out.append('ordinal suffix after a variable')
    jp_plain = TOKEN.sub('', src)
    en_terms = ' '.join(TOKEN.sub(' ', en).split()).lower()
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(' '.join(e.split()).lower() in en_terms for e in ens):
            out.append(f'glossary: {jps[0]} -> {ens[0]}')
        out += [f'glossary Avoid: {a}' for a in avoid if re.search(rf'\b{re.escape(a)}\b', en)]
    for enf in honorifics(src):
        if enf.lower() not in en.lower():
            out.append(f'honorific needs {enf}')
    return out


def read_rows():
    return fit.read_script()


def write_file(path, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(HDR) + '\n')
        for r in rows:
            vals = [r[h] for h in HDR]
            assert all('\t' not in v and '\n' not in v for v in vals), r['id']
            f.write('\t'.join(vals) + '\n')


def read_tsv(path):
    return [line.split('\t') for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def existing():
    return sorted(TL.glob('b[0-9][0-9][0-9].tsv'))


def split(size, only=None):
    rows = read_rows()
    terms = glossary()
    spk = speakers(terms)
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / 'build').mkdir(exist_ok=True)
    taken_ids = {r[0] for p in existing() for r in read_tsv(p)}
    taken_jp = {rows[i]['jp'] for i in taken_ids if i in rows}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    seen, todo = set(taken_jp), []
    for rid, r in rows.items():
        if only and not any(rid.startswith(o) for o in only):
            continue
        if needs_english(r) and r['jp'] not in seen:
            seen.add(r['jp'])
            todo.append(r)
    batches, cur, chars, curfile = [], [], 0, None
    for r in todo:
        c = len(TOKEN.sub('', r['jp']))
        if cur and (chars + c > size or len(cur) >= MAX_ENTRIES):
            batches.append(cur)
            cur, chars = [], 0
        cur.append(r)
        chars += c
    if cur:
        batches.append(cur)
    for batch in batches:
        n += 1
        name = f'b{n:03d}'
        path = TL / f'{name}.tsv'
        if path.exists():
            sys.exit(f'{path} already exists')
        lines = []
        for r in batch:
            if is_dialogue(r):
                s, b = body(r['jp'])
                lines.append(f"{r['id']}\t{spk.get(s, s)}\tdlg\t2x232px\t{b}")
            else:
                v = fit.variant(r)
                form = 'choice' if r['kind'] == 'choice' else v[0]
                lim = f"{v[2]}px" if v[2] else 'as JP cells'
                lines.append(f"{r['id']}\t\t{form}\t{lim}\t{r['jp']}")
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
        jps = ' '.join(TOKEN.sub('', r['jp']) for r in batch)
        used = sorted({(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)})
        (ROOT / f'build/terms_{name}.txt').write_text(''.join(f'{j}\t{e}\n' for j, e in used)
                                                      or '(no glossary terms in this batch)\n', encoding='utf-8',
                                                      newline='\n')
    print(f'{len(batches)} new batches in {TL} ({sum(map(len, batches))} texts), {len(taken_ids)} ids already batched')


def finish(row, en, spk, enc):
    """translator text -> the row's final en (dialogue: speaker tag + wrapped body); None if it doesn't fit"""
    if not is_dialogue(row):
        return en
    s, _ = body(row['jp'])
    tag = f'【{spk[s]}】' if s else ''
    return fit.wrap_dialogue(tag, en, enc)


def check_batch(batch, rows, terms):
    want = [r[0] for r in read_tsv(TL / f'{batch}.tsv')]
    got = [(r[0], '\t'.join(r[1:])) for r in read_tsv(TL / f'{batch}.out.tsv')]
    bad = []
    if [r[0] for r in got] != want:
        ids = [r[0] for r in got]
        dup = sorted(i for i, c in Counter(ids).items() if c > 1)
        bad.append(f'ids differ: missing {sorted(set(want) - set(ids))[:8]} extra {sorted(set(ids) - set(want))[:8]} '
                   f'duplicate {dup[:8]} (order must match too)')
    spk = speakers(terms)
    for eid, en in got:
        if eid not in rows:
            continue
        r = rows[eid]
        ps = problems(r, en, terms)
        if is_dialogue(r):
            s, _ = body(r['jp'])
            if s and s not in spk:
                ps.append(f'speaker {s} has no glossary EN')
        bad += [f'{eid}: {p}: {en!r}' for p in ps]
    texts = {eid: en for eid, en in got}
    if bad:
        return bad, texts
    enc = fit.encoder(rows, [finish(rows[i], e, spk, None) if not is_dialogue(rows[i]) else e
                             for i, e in texts.items() if i in rows])
    final = {}
    for eid, en in texts.items():
        r = rows[eid]
        f = finish(r, en, spk, enc)
        if f is None:
            bad.append(f'{eid}: too long for the dialogue box (2 rows of 232/218 px): {en!r}')
            continue
        bad += [f'{eid}: {p}: {f!r}' for p in fit.problems(r, f, enc)]
        final[eid] = f
    return bad, final


def merge(final, rows, overwrite):
    by_jp = {}
    for eid, en in final.items():
        by_jp[rows[eid]['jp']] = en
    if not overwrite:
        for r in rows.values():
            if r['jp'] in by_jp and r['en'] and r['en'] != by_jp[r['jp']] and needs_english(dict(r, en='')):
                sys.exit(f"{r['id']} would lose {r['en']!r}: pass --overwrite if that is meant")
    files, changed = {}, 0
    for r in rows.values():
        files.setdefault(r['file'], []).append(r)
        if r['jp'] in by_jp and r['kind'] != 'grid' and '{dc}' not in r['jp'] and r['en'] != by_jp[r['jp']]:
            if r['en'] and not overwrite:
                continue
            r['en'] = by_jp[r['jp']]
            changed += 1
            r['_touched'] = True
    for path, rs in files.items():
        if any(r.get('_touched') for r in rs):
            write_file(path, rs)
    print(f'merged: {changed} rows changed')


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == 'split':
        only = args[args.index('--only') + 1].split(',') if '--only' in args else None
        return split(int(args[args.index('--size') + 1]) if '--size' in args else 3500, only)
    if cmd == 'speakers':
        rows, spk = read_rows(), speakers(glossary())
        c = Counter(body(r['jp'])[0] for r in rows.values() if is_dialogue(r))
        miss = [(s, n) for s, n in c.most_common() if s and s not in spk]
        print(f'{len(miss)} speaker tags without EN')
        print('\n'.join(f'{s}\t{n}' for s, n in miss))
        return 0
    overwrite = '--overwrite' in args
    names = [a for a in args if a != '--overwrite']
    if cmd not in ('check', 'merge') or not names:
        sys.exit(__doc__)
    rows, terms = read_rows(), glossary()
    failed = 0
    for batch in names:
        bad, final = check_batch(batch, rows, terms)
        failed += bool(bad)
        print(f'{batch}: ' + ('OK' if not bad else f'{len(bad)} problems'))
        for line in bad:
            print('  ' + line)
        if cmd == 'merge' and not bad:
            merge(final, rows, overwrite)
            rows = read_rows()
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
