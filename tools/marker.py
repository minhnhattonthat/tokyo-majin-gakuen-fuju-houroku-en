"""marker.py: marker text for the phase 5 marker build (`build.py --marker`).

Every row's `en` becomes an id-tagged filler that keeps the Japanese layout: the same line breaks and control
codes, each Japanese text run replaced by English filler of the same pixel width as the Japanese (16 px a
character), so every box shows which row it is and how much English fits where the Japanese was. Story lines:
the speaker tag becomes 【id】 and the first text line starts with the id's line number. Choices: "id.N" per option.
System strings keep their slot size (`max`, relocation is phase 7): the filler shrinks, then the tag shortens
(full id, last 4 digits, '#') until the encoded string fits; a row that can't fit even '#' keeps its Japanese.

    python -X utf8 tools/marker.py ID..     # print the marker text of these rows
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import vwf  # noqa: E402

FILL = ('the quick brown fox jumps over the lazy dog while five boxing wizards jump quickly and '
        'pack my box with five dozen liquor jugs ') * 3
_TOK = re.compile(r'(\{[^{}]+\}|\[[0-9A-F]{2}\])')
_JP = re.compile(r'[^\x00-\x7f]')


def fit(font, text, px):
    """the longest prefix of text whose drawn width is <= px, trailing space dropped"""
    e = vwf.ext(font, text)
    n = max(i for i in range(len(text) + 1) if e[i] <= px)
    return text[:n].rstrip()


def _runs(line):
    return [p for p in _TOK.split(line) if p]


def _jp_px(s):
    """16 px per Japanese / fullwidth character, 8 per ASCII (the original cell layout)"""
    return sum(16 if _JP.match(ch) else 8 for ch in s)


def line_marker(font, line, tag, scale=1.0):
    """replace the literal runs of one line ({rt}-free) with tag + filler of the same width"""
    out, first = [], True
    for p in _runs(line):
        if _TOK.fullmatch(p):
            out.append(p)
            continue
        px = int(_jp_px(p) * scale)
        head = (tag + ' ') if first and tag else ''
        out.append(fit(font, head + FILL, max(px, vwf.ext(font, head.rstrip())[-1])) or 'x')
        first = False
    return ''.join(out)


def scene_marker(font, row):
    rid = row['id']
    if row['kind'] == 'choice':
        body = row['jp'][:-len('{wc}')] if row['jp'].endswith('{wc}') else row['jp']
        opts = body.split('{rt}')
        return '{rt}'.join(line_marker(font, o, '%s.%d' % (rid, i)) for i, o in enumerate(opts)) + '{wc}'
    lines = row['jp'].split('{rt}')
    out = []
    num = rid.split('.')[-1]
    for i, ln in enumerate(lines):
        if i == 0 and ln.startswith('【') and ln.endswith('】') and len(lines) > 1:
            out.append('【%s】' % rid)
            continue
        first_text = not any(o and not o.startswith('【' + rid) for o in out)
        out.append(line_marker(font, ln, num if first_text and out else (rid if first_text else '')))
    return '{rt}'.join(out)


def system_marker(font, row, encode):
    """encode(text) -> bytes; the marker must fit row['max'] bytes"""
    cap = int(row['max'])
    rid = row['id']
    for tag in (rid, rid[-4:], '#'):
        for scale in (1.0, 0.75, 0.5, 0.25, 0.0):
            lines = row['jp'].replace('{nl}', '{rt}{nl}').split('{rt}')
            # {nl} lines keep their code: split on {rt} only, {nl} stays at the start of its line
            out = [line_marker(font, ln, tag if i == 0 else '', scale) for i, ln in enumerate(lines)]
            text = '{rt}'.join(out).replace('{rt}{nl}', '{nl}')
            if len(encode(text)) <= cap:
                return text
    return ''


def apply(script, font):
    """{id: row} -> new {id: row} with marker `en` everywhere"""
    out = {}
    scene_texts = {}
    for rid, r in script.items():
        if r['kind'] in ('line', 'choice'):
            scene_texts[rid] = scene_marker(font, r)
    # system strings must fit their slots, so measure with the encoder that the scene text builds (plus the tags)
    sys_try = {rid: system_marker(font, r, lambda t: b'x' * _est_bytes(font, t))
               for rid, r in script.items() if r['kind'] == 'str'}
    for rid, r in script.items():
        en = scene_texts.get(rid, sys_try.get(rid, ''))
        out[rid] = dict(r, en=en)
    return out


def refit(script, enc):
    """after the encoder is built: re-fit every system marker that encodes longer than its slot"""
    for rid, r in script.items():
        if r['kind'] == 'str' and r['en'] and len(enc.encode(r['en'])) > int(r['max']):
            r['en'] = system_marker(enc.font, r, enc.encode)


def _est_bytes(font, t):
    """upper bound of the encoded size: one unit per chunk with only 1-2 char chunks guaranteed in the dict"""
    n = 0
    for k, v in vwf.split(t):
        if k == 'raw':
            n += len(v)
        else:
            # pairs are always worth a code in this marker text (FILL is repetitive), so ~2 chars a unit;
            # bounded by the cell rule: at least ceil(width / 16) units
            n += 2 * max((len(v) + 1) // 2, (vwf.ext(font, v)[-1] + 15) // 16)
    return n


if __name__ == '__main__':
    import extract
    rom = (ROOT / 'rom' / 'base.gba').read_bytes()
    font = vwf.load_font(rom)
    script = extract.load()
    m = apply({k: script[k] for k in sys.argv[1:]}, font)
    for k in sys.argv[1:]:
        print(k, script[k]['jp'], '->', m[k]['en'])
