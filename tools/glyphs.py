"""glyphs.py: decode tools/debug/glyphlog.lua logs: what text each run drew, and which of it is still Japanese.

    python -X utf8 tools/glyphs.py ROM LOGDIR..            # every GLYPH line, decoded, per run
    python -X utf8 tools/glyphs.py ROM LOGDIR.. --jp       # only strings that still draw Shift-JIS glyphs
    python -X utf8 tools/glyphs.py ROM LOGDIR.. --ids      # marker ids seen (marker build), one per line

LOGDIR is a run folder holding log.txt (emu.py / warp.py --script tools/debug/glyphlog.lua), or a folder of them.
VWF units are decoded through ROM's MTE table (tools/vwf.py layout), so pass the build the run used.
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import vwf  # noqa: E402

LINE = re.compile(r'GLYPH f(\d+) lr=([0-9A-F]{8}) ([0-9A-F]*)')
INV = {v: k for k, v in vwf.CHAR_BYTE.items()}


class Decoder:
    def __init__(self, rom):
        self.rom = rom
        code, (adv, fnt, mte) = vwf.hook_code()
        self.vwf = rom[vwf.HOOK:vwf.HOOK + 4] == code[:4]
        self.mte = mte

    def unit(self, b0, b1):
        """(text, is_japanese)"""
        if self.vwf and b0 in vwf.LEADS:
            i = vwf.LEADS.index(b0) * 255 + b1 - 1
            raw = self.rom[self.mte + 4 * i:self.mte + 4 * i + 4].rstrip(b'\0')
            return ''.join(INV.get(c, '?') for c in raw), False
        if b0 < 0x80:
            pair = bytes([b0, b1])
            if pair == b'rt':
                return '{rt}', False
            if pair in (b'\x01\x00', b'\x02\x00'):
                return '{name%d}' % b0, False
            return '{%s}' % pair.decode('latin-1').replace('\0', '0'), False
        try:
            return bytes([b0, b1]).decode('cp932'), True
        except UnicodeDecodeError:
            return '[%02X%02X]' % (b0, b1), True

    def string(self, hexs):
        out, jp = [], False
        for i in range(0, len(hexs), 4):
            t, j = self.unit(int(hexs[i:i + 2], 16), int(hexs[i + 2:i + 4], 16))
            out.append(t)
            jp |= j
        return ''.join(out), jp


def logs(paths):
    for p in paths:
        p = Path(p)
        for lg in ([p / 'log.txt'] if (p / 'log.txt').is_file() else sorted(p.glob('*/log.txt'))):
            yield lg.parent.name, lg


def runs(rom, paths):
    """{run name: [(frame, caller, text, has_japanese)]}"""
    d = Decoder(rom)
    out = {}
    for name, lg in logs(paths):
        rows = out.setdefault(name, [])
        for line in lg.read_text(encoding='utf-8', errors='replace').splitlines():
            m = LINE.search(line)
            if m:
                text, jp = d.string(m.group(3))
                rows.append((int(m.group(1)), m.group(2), text, jp))
    return out


ID = re.compile(r'([AB]\d+(?:\.\d+)?\.\d{4}(?:\.\d)?|\b[CDE][0-9A-F]{5}\b|\b[0-9A-F]{4}\b|#)')


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 2:
        print(__doc__)
        return 2
    rom = Path(a[0]).read_bytes()
    res = runs(rom, a[1:])
    if '--ids' in sys.argv:
        ids = sorted({i for rs in res.values() for _, _, t, _ in rs for i in ID.findall(t)})
        print('\n'.join(ids))
        return 0
    for name, rs in res.items():
        for f, lr, t, jp in rs:
            if '--jp' in sys.argv and not jp:
                continue
            print('%-18s f%-6d %s %s%s' % (name, f, lr, 'JP ' if jp else '', t))
    return 0


if __name__ == '__main__':
    sys.exit(main())
