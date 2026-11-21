import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def test_rom_sha1_listing_parses():
    lines = [l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    assert len(lines) == 1
    sha, name = lines[0].split(None, 1)
    assert len(sha) == 40 and name.endswith(".gba")


def test_rom_matches_if_present():
    import check_rom
    name = [l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")][0].split(None, 1)[1]
    if not (ROOT / name).is_file():
        pytest.skip("no ROM dump (clone without rom/)")
    check_rom.check()
