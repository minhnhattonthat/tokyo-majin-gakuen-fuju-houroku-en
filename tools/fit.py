"""fit.py: the fit lint and the dialogue wrapper for English text (budgets: tools/windows.tsv).

    python -X utf8 tools/fit.py                 # lint every `en` in script/; exit 1 on any problem
    python -X utf8 tools/fit.py --ids A1.1.0003 # show the measured lines of some rows
    python -X utf8 tools/fit.py --sample "Text" # px width of one line as the VWF hook draws it

Widths are what the hook draws (tools/vwf.py): literal English runs are packed by the MTE encoder (ink extent from
the font's advances, one 16-px cell per unit); every other unit (a Japanese glyph, [81][40], an icon) is one cell;
{name1}/{name2} are budgeted at NAME_PX (4 cells: the JP name fields); {&S..}/{&N..} numbers at 3 cells. Lines
are split at {rt}/{nl}, pages at {pp}; a page ending in {wc}/{wk}/{wd} keeps room for the page icon on its last line
where the variant says so (last_px).

Variants (windows.tsv) are picked by row: scene `line` -> dialogue (3 rows incl. the 【speaker】 row, 232 px, last
row 218, 15 units); scene `choice` -> 112 px a option, 7 units; system rows by address range (RANGES); any other
system row keeps the JP layout: per page, no more lines than JP and each line <= 16 px x the longest JP line in cells.
"""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vwf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'script'
ROM = ROOT / 'rom' / 'base.gba'
NAME_PX = 64
NUM_PX = 48
TOKEN = re.compile(r'\{([^{}]+)\}|\[([0-9A-F]{2})\]')
BREAK = {'rt', 'nl'}
WAIT = {'wc', 'wk', 'wd'}

# (lo, hi inclusive-exclusive, variant, lines, px, last_px, units); lines None = as JP per page
RANGES = [
    (0xD16820, 0xD16A00, 'haiku', 2, 160, None, 10),
    (0xCF1318, 0xCF1568, 'yesno', 3, 128, None, 8),
    (0xD67B00, 0xD6DC00, 'enemy_quote', 3, 128, None, 8),
    (0xCF2A00, 0xCF5600, 'card_spell_text', 5, 124, None, 8),
    # possession effects 憑依された{I000}.. (4-5 JP lines: panel text, not the 3-line popup; inferred, check in game)
    (0xCF24B0, 0xCF2A00, 'card_spell_text', 5, 124, None, 8),
    (0xCF5930, 0xCF6540, 'card_name', 1, 94, None, 6),
    (0xCF6800, 0xCF6AFC, 'card_name', 1, 94, None, 6),
    (0xCF6D00, 0xCF71C8, 'card_name', 1, 94, None, 6),
    (0xCF6540, 0xCF6800, 'card_skill', 1, 30, None, 2),
    # ability triggers and effect lines (CF580C-CF5914 are two-line effects, not names); 128 px because the
    # untranslatable JP line {I013}{&Sy0}{I014}{&Sz0} is itself 128 px
    (0xCF5600, 0xCF5930, 'card_ability', 2, 128, None, 8),
    (0xCF71C8, 0xCF7320, 'card_label', 1, 40, None, 2),
    (0xCF6AFC, 0xCF6D00, 'place_effect', 2, 124, None, 8),
    (0xCF13C0, 0xCF2A00, 'popup', 3, 128, None, 8),
    (0xD652AC, 0xD6531C, 'battle_banner', 2, 208, None, 13),
    (0xD726FC, 0xD72CC4, 'card_prompt', 4, 124, None, 8),
    (0xD7874C, 0xD78CCC, 'card_prompt', 4, 124, None, 8),
    (0xD72434, 0xD724C0, 'deck_help', 3, 144, None, 9),
    (0xD1BDF4, 0xD1BEA8, 'sound_title', 1, 160, None, 10),
    (0xD1BDE0, 0xD1BDF4, 'sound_header', 1, 176, None, 11),
    (0xD78E04, 0xD7913C, 'link_message', None, 124, None, 8),
    (0xD65298, 0xD652AC, 'rematch_menu', 2, 112, None, 7),
]
SINGLE = {0xD726B0: ('deck_help', 3, 144, None, 9), 0xD678D4: ('popup', 3, 128, None, 8),
          0xD6790C: ('popup', 3, 128, None, 8)}
# card_tag (CF13C0-CF2A00): line 1 is the 【tag】 shown at 64 px; the popup shows all three lines at 128
TAG_FIRST_PX = 64


def read_script():
    rows = {}
    for path in sorted(SCRIPT.rglob('*.tsv')):
        with open(path, encoding='utf-8', newline='') as f:
            r = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
        hdr = r[0]
        for x in r[1:]:
            d = dict(zip(hdr, x))
            d['file'] = path
            rows[d['id']] = d
    return rows


def pages(text):
    """script text -> [[line tokens]] per page: each token ('lit', str) or ('code', name) or ('raw', hex)"""
    out, page, line, pos = [], [], [], 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            line.append(('lit', text[pos:m.start()]))
        pos = m.end()
        if m.group(1) is not None:
            c = m.group(1)
            if c in BREAK:
                page.append(line)
                line = []
            elif c == 'pp':
                page.append(line)
                out.append(page)
                page, line = [], []
            else:
                line.append(('code', c))
        else:
            line.append(('raw', m.group(2)))
    if pos < len(text):
        line.append(('lit', text[pos:]))
    page.append(line)
    out.append(page)
    return out


def measure(line, enc):
    """(px, units) of one line's tokens as drawn"""
    units = e = 0
    raw = []
    for k, v in line + [('end', None)]:
        if k == 'raw':
            raw.append(v)
            if len(raw) == 2:
                units += 1
                e = max(e, 16 * units)
                raw = []
            continue
        if k == 'lit':
            v = vwf.normalize(v)
            jp =[ch for ch in v if ch not in vwf.CHAR_BYTE]
            if jp:      # Japanese (non-VWF) glyphs: one cell each; split the run around them
                seg = ''
                for ch in v:
                    if ch in vwf.CHAR_BYTE:
                        seg += ch
                        continue
                    if seg:
                        e = max(e, 16 * units + enc.ext(seg)[-1])
                        units += len(enc.chunks(seg))
                        seg = ''
                    units += 1
                    e = max(e, 16 * units)
                if seg:
                    e = max(e, 16 * units + enc.ext(seg)[-1])
                    units += len(enc.chunks(seg))
            elif v:
                e = max(e, 16 * units + enc.ext(v)[-1])
                units += len(enc.chunks(v))
        elif k == 'code':
            if v in ('name1', 'name2'):
                units += NAME_PX // 16
                e = max(e, 16 * units)
            elif re.fullmatch(r'I\d\d\d', v):
                units += 1
                e = max(e, 16 * units)
            elif v.startswith(('&S', '&N')):
                units += NUM_PX // 16
                e = max(e, 16 * units)
    return e, units


def cells(line):
    """JP line width in cells (each glyph, icon or raw pair one cell; names 4; numbers 3)"""
    n = 0
    raw = 0
    for k, v in line:
        if k == 'lit':
            n += len(v)
        elif k == 'raw':
            raw += 1
            if raw % 2 == 0:
                n += 1
        elif v in ('name1', 'name2'):
            n += 4
        elif re.fullmatch(r'I\d\d\d', v):
            n += 1
        elif v.startswith(('&S', '&N')):
            n += 3
    return n


def variant(row):
    """(name, lines or None, px or None, last_px or None, units or None)"""
    if row['id'][0] in 'AB' and '.' in row['id']:
        if row['kind'] == 'choice':
            return ('choice', None, 112, None, 7)
        if '{dc}' in row['jp']:
            return ('staff_roll', None, None, None, None)
        return ('dialogue', 3, 232, 218, 15)
    try:
        a = int(row['id'], 16)
    except ValueError:
        return ('jp_layout', None, None, None, None)
    if a in SINGLE:
        return SINGLE[a]
    for lo, hi, name, lines, px, last, units in RANGES:
        if lo <= a < hi:
            return (name, lines, px, last, units)
    return ('jp_layout', None, None, None, None)


def problems(row, en, enc):
    out = []
    if row['kind'] == 'grid':
        return ['grid rows are not translated'] if en else []
    lit = ''.join(v for pg in pages(en) for ln in pg for k, v in ln if k == 'lit')
    bad = sorted(set(vwf.normalize(lit)) - set(vwf.CHAR_BYTE))
    if bad:
        return ['no glyph for %r' % ''.join(bad)]
    name, lines, px, last, units = variant(row)
    jp_pages, en_pages = pages(row['jp']), pages(en)
    if len(en_pages) != len(jp_pages) and name not in ('dialogue',):
        out.append('%d pages, JP has %d' % (len(en_pages), len(jp_pages)))
    waits = bool(re.search(r'\{w[ckd]\}\s*$', en))
    for pi, pg in enumerate(en_pages):
        jpg = jp_pages[min(pi, len(jp_pages) - 1)]
        jp_cells = max(cells(ln) for ln in jpg)
        lim_lines = lines or len(jpg)
        if len(pg) > lim_lines:
            out.append('page %d: %d lines > %d' % (pi + 1, len(pg), lim_lines))
        for li, ln in enumerate(pg):
            w, u = measure(ln, enc)
            p = px or 16 * jp_cells
            if name == 'popup' and row['jp'].startswith('【') and li == 0:
                p = TAG_FIRST_PX
            if li == len(pg) - 1 and pi == len(en_pages) - 1:
                if last:
                    p = min(p, last)
                elif name in ('jp_layout', 'link_message') and waits and len(jpg) > 1:
                    p = min(p, 16 * jp_cells)
            ulim = units or (p + 15) // 16
            if name == 'staff_roll':
                p, ulim = 240, 15
            if w > p:
                out.append('page %d line %d: %d px > %d (%s)' % (pi + 1, li + 1, w, p, name))
            if u > ulim:
                out.append('page %d line %d: %d units > %d (%s)' % (pi + 1, li + 1, u, ulim, name))
    return out


def body_rows(en):
    """split a dialogue en into (speaker tag or '', body without breaks)"""
    m = re.match(r'(【[^】]*】)\{rt\}(.*)$', en, re.S)
    return (m.group(1), m.group(2)) if m else ('', en)


def wrap(text, enc, widths, units=15):
    """greedy word wrap of text (no breaks) into len(widths) lines of <= widths[i] px; None if it doesn't fit"""
    words = text.replace('{rt}', ' ').split(' ')
    lines, cur = [], ''
    for w in words:
        if w == '':
            continue
        cand = (cur + ' ' + w) if cur else w
        li = len(lines)
        lim = widths[min(li, len(widths) - 1)]
        pw, pu = measure(pages(cand)[0][0], enc)
        if pw <= lim and pu <= units:
            cur = cand
            continue
        if not cur:
            return None
        lines.append(cur)
        cur = w
    if cur:
        lines.append(cur)
    if len(lines) > len(widths):
        return None
    for i, ln in enumerate(lines):
        pw, pu = measure(pages(ln)[0][0], enc)
        if pw > widths[i] or pu > units:
            return None
    return '{rt}'.join(lines)


def fits(line, lim, enc, units=15):
    w, u = measure(pages(line)[0][0], enc)
    return w <= lim and u <= units


def wrap_dialogue(speaker, body, enc):
    """'【Name】{rt}' + body wrapped to the dialogue box (2 text rows: 232 then 218 px, the last row keeps the page
    icon clear); one row when it fits, else the split with the longest first row; None if too long"""
    if speaker:
        body = ' '.join(body.split(' '))
        if fits(body, 218, enc):
            return speaker + '{rt}' + body
        words = body.split(' ')
        for i in range(len(words) - 1, 0, -1):
            a, b = ' '.join(words[:i]), ' '.join(words[i:])
            if fits(a, 232, enc) and fits(b, 218, enc):
                return speaker + '{rt}' + a + '{rt}' + b
        return None
    for widths in ([218], [232, 218], [232, 232, 218]):
        w = wrap(body, enc, widths)
        if w is not None:
            return w
    return None


def encoder(rows, extra=()):
    from vwf import Encoder, load_font
    font = load_font(ROM.read_bytes())
    return Encoder(font, [r['en'] for r in rows.values() if r.get('en')] + list(extra))


def lint(rows=None):
    rows = rows or read_script()
    enc = encoder(rows)
    bad = []
    for rid, r in rows.items():
        if r.get('en'):
            bad += ['%s: %s: %r' % (rid, p, r['en']) for p in problems(r, r['en'], enc)]
    return bad


def main(argv):
    if '--sample' in argv:
        rows = read_script()
        enc = encoder(rows, [argv[argv.index('--sample') + 1]])
        print(measure(pages(argv[argv.index('--sample') + 1])[0][0], enc))
        return 0
    if '--ids' in argv:
        rows = read_script()
        enc = encoder(rows)
        for rid in argv[argv.index('--ids') + 1:]:
            r = rows[rid]
            t = r['en'] or r['jp']
            print(rid, variant(r)[0], [[measure(ln, enc) for ln in pg] for pg in pages(t)], problems(r, t, enc))
        return 0
    rows = read_script()
    bad = lint(rows)
    print('%d translated rows, %d problems' % (sum(1 for r in rows.values() if r.get('en')), len(bad)))
    print('\n'.join(bad[:200]))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
