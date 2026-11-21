"""scene_table.py ROM: find runs of u32 pointers into the story region (0xD70000-0xE30000), report each table,
whether its targets are contiguous, and the story bytes no table covers (recon helper)."""
import struct
import sys

d = open(sys.argv[1], 'rb').read()
LO, HI = 0x08D70000, 0x08E30000


def isp(i):
    w = struct.unpack_from('<I', d, i)[0]
    return LO <= w < HI


tables = []
i = 0
while i < len(d) - 4:
    if isp(i):
        j = i
        while j < len(d) - 4 and isp(j):
            j += 4
        if (j - i) // 4 >= 8:
            tables.append((i, (j - i) // 4))
        i = j
    else:
        i += 4
for t, n in tables:
    ps = [struct.unpack_from('<I', d, t + 4 * k)[0] & 0xffffff for k in range(n)]
    asc = all(a < b for a, b in zip(ps, ps[1:]))
    print('table %x n=%d first %x last %x ascending=%s' % (t, n, ps[0], ps[-1], asc))
