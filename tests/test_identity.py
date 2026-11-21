"""Phase 3 identity build: unpack + repack with no edits gives the dump byte for byte, and the scene packer really
recomputes label offsets and table pointers when a line changes length."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT))

import scenes  # noqa: E402
import strslots  # noqa: E402

BASE = ROOT / 'rom' / 'base.gba'
SPILL = (0xE61678, 0xE70000)   # test-only: part of the 0xFF free-space candidate (not trap-verified yet)


@pytest.fixture(scope='module')
def orig():
    if not BASE.is_file():
        pytest.skip('no ROM dump (clone without rom/)')
    return BASE.read_bytes()


def test_build_is_identical(orig):
    import build
    import extract
    jp_only = {k: dict(r, en='') for k, r in extract.load().items()}
    assert build.build(orig, jp_only) == orig


def test_every_scene_reencodes_exactly(orig):
    scs = scenes.parse_all(orig)
    assert len(scs) == scenes.N_A + scenes.N_B
    ends = [s.addr for s in scs[1:]] + [scenes.REGION[1]]
    for sc, e in zip(scs, ends):
        assert sc.encode() == orig[sc.addr:e], hex(sc.addr)


@pytest.mark.parametrize('delta', [b'XXXX', b'XYZ', b''])
def test_repack_moves_labels_and_pointers(orig, delta):
    scs = scenes.parse_all(orig)
    first = scs[0]
    k = next(i for i, t in enumerate(first.toks) if t.kind == 'text')
    first.toks[k].text = (delta + first.toks[k].text) if delta else first.toks[k].text[:-2]
    regions = [scenes.REGION, SPILL]
    rom = bytearray(orig)
    scenes.pack(rom, scs, regions)
    built = bytes(rom)
    again = scenes.parse_all(built, regions)
    for a, b in zip(scs, again):
        assert a.labels == b.labels
        assert [(t.kind, t.raw, t.text) for t in a.toks] == [(t.kind, t.raw, t.text) for t in b.toks]
    # each table slot still reaches the same scene, now at its new address
    by_addr = {s.addr: s for s in scs}
    for new, old in zip(sum(scenes.table(built), []), sum(scenes.table(orig), [])):
        blob = by_addr[old].encode()
        assert built[new:new + len(blob)] == blob
    # a longer line pushes the last scene out to the spill region; a shorter one leaves zero fill
    olds = sum(scenes.table(orig), [])
    last = sum(scenes.table(built), [])[olds.index(max(olds))]
    assert (SPILL[0] <= last < SPILL[1]) == (len(delta) > 0)
    assert built[scenes.REGION[0]:scenes.REGION[1]] != orig[scenes.REGION[0]:scenes.REGION[1]]


def test_label_zero_is_body_start(orig):
    for sc in scenes.parse_all(orig):
        blob = sc.encode()
        n = struct.unpack_from('<H', blob)[0]
        assert struct.unpack_from('<H', blob, 2)[0] == 0 and n == len(sc.labels), hex(sc.addr)


def test_string_slots_roundtrip_and_refuse_overflow(orig):
    ss = strslots.scan(orig)
    assert len(ss) > 2000
    rom = bytearray(orig)
    for s in ss:
        strslots.write(rom, s, s.text)
    assert bytes(rom) == orig
    with pytest.raises(ValueError):
        strslots.write(rom, ss[0], b'A' * ss[0].cap)
