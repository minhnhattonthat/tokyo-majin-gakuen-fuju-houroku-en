"""strscan.py ROM [LO HI]: find NUL-terminated Shift-JIS strings and how many have a direct u32 ROM pointer.
Prints totals, per-64K cluster coverage, and samples of unpointed strings (recon helper)."""
import re
import struct
import sys
from collections import Counter

d = open(sys.argv[1], 'rb').read()
lo = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0
hi = int(sys.argv[3], 0) if len(sys.argv) > 3 else len(d)
ptrs = Counter()
for i in range(0, len(d) - 3, 4):
    w = struct.unpack_from('<I', d, i)[0]
    if 0x08000000 <= w < 0x09000000:
        ptrs[w & 0xffffff] += 1

hira = re.compile(rb'[\x82\x83][\x40-\xfc]')
# a string: run of sjis pairs / printable ascii, ending in NUL, containing >=2 kana
pat = re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]|[\x20-\x7e])+\x00')
strs = []
for m in pat.finditer(d, lo, hi):
    s = m.group()
    if len(hira.findall(s)) >= 2:
        strs.append((m.start(), m.end()))
pt = [s for s in strs if ptrs[s[0]]]
print('strings', len(strs), 'pointed', len(pt), 'bytes', sum(b - a for a, b in strs))
c, cp = Counter(a >> 16 for a, _ in strs), Counter(a >> 16 for a, _ in pt)
for k in sorted(c):
    print(hex(k << 16), c[k], cp[k])
un = [s for s in strs if not ptrs[s[0]]]
for a, b in un[:: max(1, len(un) // 20)][:20]:
    print(hex(a), d[max(lo, a - 8):a].hex(), d[a:b].decode('cp932', 'replace')[:30])
