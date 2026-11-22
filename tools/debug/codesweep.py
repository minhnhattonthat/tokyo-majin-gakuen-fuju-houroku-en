"""codesweep.py: NUL-ended Shift-JIS strings in a ROM range that look like text (>= MIN full-width characters, all
valid cp932 double-byte, starting after a NUL or on a 4-byte boundary), for blind spots of the pointer-range scan
(the code-area prefecture table 0x06485C was one).

    python -X utf8 tools/debug/codesweep.py [ROM] [--lo 0x0] [--hi 0xC0000] [--min 2]
"""
import argparse


def runs(d, lo, hi, mn):
    out, i = [], lo
    while i < hi - 1:
        if not (i % 4 == 0 or d[i - 1] == 0):
            i += 1
            continue
        j, n = i, 0
        while j < hi - 1 and (0x81 <= d[j] <= 0x9F or 0xE0 <= d[j] <= 0xEA):
            try:
                ch = d[j:j + 2].decode('cp932')
            except UnicodeDecodeError:
                break
            if ch.encode('cp932') != d[j:j + 2]:
                break
            j += 2
            n += 1
        if n >= mn and d[j] == 0:
            out.append((i, d[i:j].decode('cp932')))
            i = j + 1
        else:
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('rom', nargs='?', default='build/tmgfh_en.gba')
    ap.add_argument('--lo', type=lambda s: int(s, 0), default=0)
    ap.add_argument('--hi', type=lambda s: int(s, 0), default=0xC0000)
    ap.add_argument('--min', type=int, default=2)
    a = ap.parse_args()
    d = open(a.rom, 'rb').read()
    for off, s in runs(d, a.lo, a.hi, a.min):
        print('%06X %s' % (off, s))


if __name__ == '__main__':
    main()
