"""Phase 7 ROM-level check: the English build changes no byte outside the places the build writes (scene tables and
REGION, string slots and their pointer sites, SPILL, the VWF hook area, the two 12-byte hook stubs). Catches a
write that wipes flag bytes, code or graphics while every text test still passes."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT))

import romdiff  # noqa: E402
import scenes  # noqa: E402
import strslots  # noqa: E402
import vwf  # noqa: E402

BASE = ROOT / 'rom' / 'base.gba'


def allowed_ranges(orig, size):
    import build
    rs = [range(scenes.TABLE_B, scenes.REGION[1]),          # tables A/B, then every scene back to back
          range(build.SPILL[0], size),                       # SPILL, then the hook code, width table and font
          range(vwf.GLYPH_FN, vwf.GLYPH_FN + 12),
          range(vwf.B_FN, vwf.B_FN + 12),
          range(vwf.C_FN, vwf.C_FN + 12)]
    import gfx
    rs += [range(a, b) for a, b in gfx.apply(bytearray(orig))]   # graphics-text redraws
    import patches
    rs += [range(a, b) for a, b in patches.apply(bytearray(orig), check=False)]   # code patches
    import codestr
    rs += [range(a, b) for a, b in codestr.ranges(orig)]   # code-area strings, piece loops, prefecture picker
    for s in strslots.scan(orig):
        rs.append(range(s.addr, s.addr + s.cap))
        rs += [range(r, r + 4) for r in s.refs]
    return rs


def test_english_build_writes_only_allowed_ranges():
    if not BASE.is_file():
        pytest.skip('no ROM dump (clone without rom/)')
    import build
    orig = BASE.read_bytes()
    new = build.build(orig)
    assert new != orig
    errs, ok = romdiff.check(orig, new, allowed_ranges(orig, len(new)), [])
    assert not errs, '\n'.join(errs)
    assert ok > 0
