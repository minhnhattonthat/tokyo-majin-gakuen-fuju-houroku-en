"""scene_peek.py ROM SCENE_OFF: print a story scene's header (u32 count, u16 offsets) and the bytes at each offset
relative to several bases, to pin the offset base (recon helper)."""
import struct
import sys

d = open(sys.argv[1], 'rb').read()
s = int(sys.argv[2], 0)
n = struct.unpack_from('<I', d, s)[0]
offs = struct.unpack_from('<%dH' % n, d, s + 4)
print('count', n, 'offs', [hex(o) for o in offs])
hdr_end = s + 4 + 2 * n


def show(a):
    out, i = [], a
    while i < a + 40:
        b = d[i]
        if 0x81 <= b <= 0x9f or 0xe0 <= b <= 0xef:
            try:
                out.append(d[i:i + 2].decode('cp932')); i += 2; continue
            except UnicodeDecodeError:
                pass
        out.append(chr(b) if 0x20 <= b < 0x7f else '{%02X}' % b)
        i += 1
    return ''.join(out)


for base_name, base in [('scene', s), ('hdr_end', hdr_end)]:
    print('--', base_name, hex(base))
    for o in offs:
        print(' ', hex(o), d[base + o - 4:base + o].hex(), '|', show(base + o))
