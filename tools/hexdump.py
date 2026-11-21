"""hexdump.py ROM OFFSET [LEN] [--sjis]: hex + Shift-JIS view of a ROM range (recon helper)."""
import sys

d = open(sys.argv[1], 'rb').read()
off = int(sys.argv[2], 0)
n = int(sys.argv[3], 0) if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else 256
if '--sjis' in sys.argv:
    out, i = [], off
    while i < off + n:
        b = d[i]
        if (0x81 <= b <= 0x9f or 0xe0 <= b <= 0xef) and i + 1 < len(d):
            try:
                out.append(d[i:i + 2].decode('cp932')); i += 2; continue
            except UnicodeDecodeError:
                pass
        if 0x20 <= b < 0x7f:
            out.append(chr(b))
        else:
            out.append('{%02X}' % b)
        i += 1
    print(''.join(out))
else:
    for i in range(off, off + n, 16):
        print('%07X  %s' % (i, d[i:i + 16].hex(' ')))
