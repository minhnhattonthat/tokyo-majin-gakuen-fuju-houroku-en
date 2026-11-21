"""ptrfind.py ROM OFFSET..: list aligned u32 words equal to 0x08000000|OFFSET (recon helper; never patch from this)."""
import struct
import sys

d = open(sys.argv[1], 'rb').read()
words = struct.unpack('<%dI' % (len(d) // 4), d)
idx = {}
for i, w in enumerate(words):
    if 0x08000000 <= w < 0x09000000:
        idx.setdefault(w, []).append(i * 4)
for a in sys.argv[2:]:
    o = int(a, 0)
    hits = idx.get(0x08000000 | o, [])
    print(hex(o), [hex(h) for h in hits[:12]], len(hits))
