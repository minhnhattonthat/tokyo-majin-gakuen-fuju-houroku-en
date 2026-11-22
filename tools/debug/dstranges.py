"""dstranges.py: summarise a dstlog.lua log of OBJ VRAM (0x06010000+) writes as 4bpp tile ranges per writer.

    python -X utf8 tools/debug/dstranges.py work/qa/run/log.txt [more logs ..]

Each SWI line (CpuSet 0x0B / CpuFastSet 0x0C, r2 = count | flags) becomes the tile range it fills; CPU lines count
one tile each. Prints writer (lr / pc) -> merged tile ranges, then the OBJ tiles no logged write touched.
"""
import re
import sys
from collections import defaultdict


def tiles_of(line):
    m = re.match(r'SWI(..) f(\d+) lr=(\w+) r0=\w+ r1=(\w+) r2=(\w+)', line)
    if m:
        swi, _, lr, r1, r2 = m.group(1), m.group(2), m.group(3), int(m.group(4), 16), int(m.group(5), 16)
        cnt = r2 & 0x1FFFFF
        unit = 4 if (swi == '0C' or r2 & (1 << 26)) else 2
        if r2 & (1 << 24):  # fill: same length
            pass
        nbytes = cnt * unit
        if swi not in ('0B', '0C'):
            nbytes = 32  # decompress: length unknown here
        a, b = r1 - 0x06010000, r1 - 0x06010000 + max(nbytes, 1) - 1
        return 'lr=' + lr, range(max(a, 0) // 32, min(b, 0x7FFF) // 32 + 1)
    m = re.match(r'CPU f\d+ pc=(\w+) lr=\w+ addr=(\w+)', line)
    if m:
        a = int(m.group(2), 16) - 0x06010000
        return 'pc=' + m.group(1), range(a // 32, a // 32 + 1)
    return None, range(0)


def ranges(s):
    out, run = [], None
    for t in sorted(s):
        if run and t == run[1] + 1:
            run[1] = t
        else:
            run = [t, t]
            out.append(run)
    return ', '.join(f'{a}-{b}' if a != b else f'{a}' for a, b in out)


def main():
    by = defaultdict(set)
    for f in sys.argv[1:]:
        for line in open(f, encoding='utf-8', errors='replace'):
            who, r = tiles_of(line.strip())
            if who:
                by[who].update(t for t in r if 0 <= t < 1024)
    alls = set()
    for who, s in sorted(by.items(), key=lambda kv: min(kv[1]) if kv[1] else 0):
        alls |= s
        print(f'{who}: {ranges(s)}')
    print('never written:', ranges(set(range(1024)) - alls))


if __name__ == '__main__':
    main()
