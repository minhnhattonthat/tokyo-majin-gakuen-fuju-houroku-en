"""ctrl_inventory.py ROM: count ASCII runs and non-SJIS bytes inside Shift-JIS strings of the text regions,
to list control codes and their shapes (recon helper)."""
import re
import sys
from collections import Counter

d = open(sys.argv[1], 'rb').read()
REGIONS = [(0xcf0000, 0xd20000), (0xd60000, 0xe30000)]
pat = re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]|[\x01-\x7e])+\x00')
kana = re.compile(rb'[\x82\x83][\x40-\xfc]')
asc, low = Counter(), Counter()
ex = {}
for lo, hi in REGIONS:
    for m in pat.finditer(d, lo, hi):
        s = m.group()
        if len(kana.findall(s)) < 2:
            continue
        i = 0
        while i < len(s) - 1:
            b = s[i]
            if 0x81 <= b <= 0x9f or 0xe0 <= b <= 0xef:
                i += 2
                continue
            j = i
            while j < len(s) - 1 and not (0x81 <= s[j] <= 0x9f or 0xe0 <= s[j] <= 0xef):
                j += 1
            run = s[i:j]
            k = re.sub(rb'[0-9]', b'9', run) if run.isascii() else run
            asc[k] += 1
            ex.setdefault(k, (m.start() + i, run))
            i = j
for k, n in asc.most_common(60):
    print(n, k, hex(ex[k][0]), ex[k][1])
