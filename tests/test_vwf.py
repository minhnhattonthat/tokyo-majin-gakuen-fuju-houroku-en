"""Phase 5 engine: the VWF font, the MTE encoder's invariants (units the game can't misread, ink inside the cells
already handed out), the hook patch, and the marker build."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT))

import vwf  # noqa: E402

BASE = ROOT / 'rom' / 'base.gba'
SAMPLE = ['The quick brown fox jumps over the lazy dog.', 'PACK MY BOX WITH FIVE DOZEN LIQUOR JUGS!',
          '【Tatsuma】{rt}"Hello," {name1} said…{rt}It\'s 50% off — ♪ café',
          'start{rt}written wc dc pp rt xn yn I000 &x01',          # letters that spell the game's inline codes
          'Mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm', 'i i i i i i i i i i i i i i i i i i', '   spaced   out   ']


@pytest.fixture(scope='module')
def orig():
    if not BASE.is_file():
        pytest.skip('no ROM dump (clone without rom/)')
    return BASE.read_bytes()


@pytest.fixture(scope='module')
def font(orig):
    return vwf.load_font(orig)


@pytest.fixture(scope='module')
def enc(font):
    return vwf.Encoder(font, SAMPLE)


def test_font_glyphs_fit_a_cell(font):
    assert set(vwf.CHAR_BYTE) <= set(font)
    for ch, (px, w, a) in font.items():
        assert 0 <= w <= 15 and a <= 16, ch
        assert all(px[y][x] == 0 for y in range(16) for x in range(w, 16)), ch   # nothing right of the width


@pytest.mark.parametrize('text', SAMPLE)
def test_units_are_safe_and_ink_stays_in_handed_out_cells(enc, text):
    u = enc.encode(text)
    assert len(u) % 2 == 0
    for k, v in vwf.split(text):
        if k == 'lit':
            b = b''.join(enc.unit(c) for c in enc.chunks(v))
            for i in range(0, len(b), 2):
                assert b[i] in vwf.LEADS and b[i + 1] != 0      # never ASCII (no rt/wc..), never a 0000 end
            vwf.draw(enc, b)                                     # raises if a unit draws past its own cell
            assert ''.join(enc.chunks(v)) == vwf.normalize(v)


def test_inline_codes_pass_through(enc):
    u = enc.encode('a{rt}b{name1}c{I000}')
    assert b'rt' in u and b'\x01\x00' in u and b'I000' in u


def test_unknown_character_is_an_error(font):
    with pytest.raises(ValueError):
        vwf.Encoder(font, ['ü'])


def test_mte_table_round_trips(enc):
    t = enc.mte_table()
    inv = {v: k for k, v in vwf.CHAR_BYTE.items()}
    for g, i in enc.codes.items():
        raw = t[4 * i:4 * i + 4].rstrip(b'\0')
        assert ''.join(inv[b] for b in raw) == g


def test_install_patches_only_the_stub_and_the_vwf_area(orig, font, enc):
    rom = bytearray(orig)
    end = vwf.install(rom, enc, font)
    diff = [i for i in range(len(orig)) if rom[i] != orig[i]]
    assert all(vwf.GLYPH_FN <= i < vwf.GLYPH_FN + 12 or vwf.B_FN <= i < vwf.B_FN + 12 or vwf.HOOK <= i < end
               for i in diff)
    assert struct.unpack_from('<I', rom, vwf.GLYPH_FN + 8)[0] == 0x08000000 + vwf.HOOK
    # printer B's stub jumps to hookb, whose first instruction is mov r12, r4, lsr #8
    hb = struct.unpack_from('<I', rom, vwf.B_FN + 8)[0]
    assert vwf.HOOK < hb - 0x08000000 < end and hb & 3 == 0
    assert struct.unpack_from('<I', rom, hb - 0x08000000)[0] == 0xE1A0C424
    assert vwf.layout(0x1C0)[0] > vwf.HOOK


def test_marker_build_fits_and_tags_every_row(orig):
    import build
    import extract
    import marker
    script = extract.load()
    font = vwf.load_font(orig)
    m = marker.apply(script, font)
    assert all(r['en'] for r in m.values() if r['kind'] in ('line', 'choice'))
    assert all(r['en'].startswith('【' + r['id']) or r['id'] in r['en'] or r['kind'] != 'line'
               for r in m.values() if r['jp'].startswith('【') and '{rt}' in r['jp'])
    out = build.build(orig, mark=True)                              # raises if a slot or a scene doesn't fit
    assert out[vwf.HOOK:vwf.HOOK + 4] != b'\xff\xff\xff\xff'
