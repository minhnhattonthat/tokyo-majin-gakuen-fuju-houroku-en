"""re_scan.py ROM: header, save type, end of data, Shift-JIS run clusters (recon helper)."""
import re
import sys
from collections import Counter

d = open(sys.argv[1], 'rb').read()
print('size', hex(len(d)), 'title', d[0xA0:0xAC], 'code', d[0xAC:0xB0], 'maker', d[0xB0:0xB2], 'ver', d[0xBC])
for s in [b'EEPROM_V', b'SRAM_V', b'SRAM_F_V', b'FLASH_V', b'FLASH512_V', b'FLASH1M_V']:
    i = d.find(s)
    if i >= 0:
        print(s, hex(i), d[i:i + 12])
e = len(d)
while e > 0 and d[e - 1] in (0xff, 0):
    e -= 1
print('data end', hex(e))
pat = re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]){6,}')
runs = [(m.start(), m.end()) for m in pat.finditer(d)]
hira = re.compile(rb'\x82[\x9f-\xf1]')


def kana_share(a, b):
    s = d[a:b]
    pairs = [s[i:i + 2] for i in range(0, len(s) - 1, 2)]
    return sum(1 for p in pairs if hira.fullmatch(p)) / max(1, len(pairs))


runs = [r for r in runs if kana_share(*r) >= 0.3]
print('sjis runs >=6 chars', len(runs), 'bytes', sum(b - a for a, b in runs))
c = Counter(r[0] >> 16 for r in runs)
for k in sorted(c):
    print(hex(k << 16), c[k])
for a, b in runs[:int(sys.argv[2]) if len(sys.argv) > 2 else 10]:
    print(hex(a), d[a:b].decode('cp932', 'replace')[:40])
for lz in [b'\x10']:
    pass
