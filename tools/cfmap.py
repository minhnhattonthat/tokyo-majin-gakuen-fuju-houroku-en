"""cfmap.py: one line per string in an address range of a script/system TSV: id, kind, line count, longest JP line
in cells ({I0xx} icons count as one cell, other codes as none), start of the JP text. Used to group the card-text
ranges for the width gate (tools/windows.tsv).

    python -X utf8 tools/cfmap.py script/system/cf.tsv CF1300 CF8000
"""
import csv
import re
import sys


def cells(s):
    out = []
    for line in re.split(r'\{rt\}|\{nl\}', s):
        line = re.sub(r'\{I\d+\}', 'X', line)
        line = re.sub(r'\{[^}]*\}|\[..\]', '', line)
        out.append(len(line))
    return out


def main():
    path, lo, hi = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
    rows = list(csv.reader(open(path, encoding='utf8'), delimiter='\t'))[1:]
    for r in rows:
        if lo <= int(r[0], 16) < hi:
            c = cells(r[3])
            print(r[0], r[1], len(c), max(c), r[3][:40])


if __name__ == '__main__':
    main()
