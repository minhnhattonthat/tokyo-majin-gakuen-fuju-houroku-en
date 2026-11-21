"""Offline checks for the debug tool: scene list shape, save editor checksum and edits."""
import csv
import re
import struct
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
sys.path.insert(0, str(ROOT / "tools"))

import save  # noqa: E402

SPEC = re.compile(r"^(B([0-9]|[1-3][0-9])|A([0-9]|1[0-2])\.[0-9]|MODE([0-9]|1[0-9]|2[01])(\.\d+)?|WAIT\d+)$")


def test_scenes_tsv_rows():
    rows = list(csv.DictReader((ROOT / "tools" / "debug" / "scenes.tsv").open(encoding="utf-8"), delimiter="\t"))
    names = [r["name"] for r in rows]
    assert len(names) == len(set(names))
    for r in rows:
        assert None not in r and all(v is not None for v in r.values()), r["name"]
        assert SPEC.match(r["spec"]), r
        if r["route"]:
            assert (ROOT / r["route"]).is_file(), r["route"]
    specs = {r["spec"] for r in rows}
    assert all("B%d" % n in specs for n in range(40))
    assert all("A%d.%d" % (g, s) in specs for g in range(13) for s in range(10))


def _fake_save():
    d = bytearray(b"\xff" * 0x8000)
    d[0:0x555C] = bytes(0x555C)
    d[0:12] = save.MAGIC
    d[0x0C:0x10] = "緋勇".encode("cp932")
    d[0x14:0x18] = "龍麻".encode("cp932")
    d[0x6D5] = 5
    d[0x1000:0x1004] = b"\x12\x34\x56\x78"  # something in the second buffer
    struct.pack_into("<I", d, save.CKS, save.checksum(d))
    d[save.COPY:save.COPY + 0x6DC] = d[0:0x6DC]
    return d


def test_checksum_covers_both_parts():
    d = _fake_save()
    c = save.checksum(d)
    d[0x1000] ^= 1
    assert save.checksum(d) != c
    d[0x1000] ^= 1
    d[save.CKS] ^= 1  # the stored checksum itself is not summed
    assert save.checksum(d) == c


def test_edit_chapter_and_names():
    d = _fake_save()
    save.edit(d, SimpleNamespace(chapter=17, surname="山田", name="太郎"))
    assert d[0x6D5] == 17
    assert save.sjis_field(d, 0x0C) == "山田" and save.sjis_field(d, 0x14) == "太郎"
    assert struct.unpack_from("<I", d, save.CKS)[0] == save.checksum(d)
    assert d[save.COPY:save.COPY + 0x6DC] == d[0:0x6DC]
