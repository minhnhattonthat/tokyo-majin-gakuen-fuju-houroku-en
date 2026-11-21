"""Phase 4 extraction: the codec roundtrips every string, script/ matches the ROM, the text banks are fully covered,
and build.py really inserts `en`."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT))

import extract  # noqa: E402
import scenes  # noqa: E402
import strslots  # noqa: E402
import textcodec  # noqa: E402

BASE = ROOT / 'rom' / 'base.gba'

# Where real text lives: code + literal pools, and the text banks from the system strings to the tutorial tables.
# 0x100000-0xCF0000 is graphics and the font (docs/re/graphics.md); its kana-looking runs are pixel noise.
TEXT_BANKS = [(0x000000, 0x100000), (0xCF0000, 0xE62000)]
# uncovered kana-looking runs that are not text, with the reason
WAIVE = [((0x0914C0, 0x091500), 'byte table in code (values 0x83-0x8F)'),
         ((0x0FEB20, 0x0FEB80), 'byte table'),
         ((0xD16740, 0xD16800), 'name-entry kana grid: u16 little-endian Shift-JIS codes, data (phase 5/8)'),
         ((0xD3C1F8, 0xD3C800), 'rarity legend graphics (docs/re/graphics.md S27)')]


@pytest.fixture(scope='module')
def orig():
    if not BASE.is_file():
        pytest.skip('no ROM dump (clone without rom/)')
    return BASE.read_bytes()


def test_codec_roundtrips_every_string(orig):
    n = 0
    for sc in scenes.parse_all(orig):
        for t in sc.toks:
            if t.kind != 'op':
                assert textcodec.encode(textcodec.decode(t.text)) == t.text, hex(sc.addr)
                n += 1
    for s in strslots.scan(orig):
        assert textcodec.encode(textcodec.decode(s.text)) == s.text, hex(s.addr)
        n += 1
    assert n > 17000


def test_codec_tokens():
    assert textcodec.decode(b'\x01\x00\x82\xa0rtI012&Sx0\n\r!!\xfb\xb3wc') == '{name1}あ{rt}{I012}{&Sx0}{nl}!![FB][B3]{wc}'
    assert textcodec.encode('{name2}{wk}[00]') == b'\x02\x00wk\x00'
    for bad in ('{foo}', 'a\tb', 'x[y', '{rt'):
        with pytest.raises(ValueError):
            textcodec.encode(bad)


def test_script_matches_rom(orig):
    """the committed script/ files carry exactly what a fresh extract gives (id, kind, max, jp), in order"""
    fresh = extract.extract(orig)
    files = sorted(p.relative_to(extract.SCRIPT).as_posix() for p in extract.SCRIPT.rglob('*.tsv'))
    assert files == sorted(fresh)
    key = lambda r: (r['id'], r['kind'], r['max'], r['jp'])  # noqa: E731
    for rel, rows in fresh.items():
        assert [key(r) for r in extract.read_tsv(extract.SCRIPT / rel)] == [key(r) for r in rows], rel


def test_every_unit_has_a_row(orig):
    script = extract.load()
    n_scene = sum(t.kind != 'op' for sc in scenes.parse_all(orig) for t in sc.toks)
    slots = strslots.scan(orig)
    assert len(script) == n_scene + len(slots)
    assert all('%06X' % s.addr in script for s in slots)


def test_text_banks_fully_covered(orig):
    left = []
    for lo, hi in TEXT_BANKS:
        for a, b in extract.uncovered_runs(orig, lo, hi):
            if not any(wlo <= a < whi for (wlo, whi), _ in WAIVE):
                left.append('%x %s' % (a, orig[a:b].decode('cp932', 'replace')))
    assert not left, left


def test_build_inserts_en(orig):
    import build
    script = extract.load()
    import glyphs
    row = dict(script['B05.0000'], en='【Man】{rt}TEST start {name1}')
    script['B05.0000'] = row
    out = build.build(orig, script)
    assert out != orig
    b, _ = scenes.table(out)
    sc = next(s for s in scenes.parse_all(out) if s.addr == b[5])
    first = next(t for t in sc.toks if t.kind == 'text')
    text, jp = glyphs.Decoder(out).string(first.text.hex().upper())
    assert text == row['en'] and not jp


def test_slot_overflow_raises(orig):
    import build
    script = extract.load()
    k = '%06X' % strslots.scan(orig)[0].addr
    script[k] = dict(script[k], en='M' * (int(script[k]['max']) + 1))   # one 'M' a unit: 2 bytes each
    with pytest.raises(ValueError):
        build.build(orig, script)
