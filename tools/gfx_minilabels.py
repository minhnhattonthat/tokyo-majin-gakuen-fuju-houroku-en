"""gfx_minilabels.py: the 40x8 mini card-name labels (S3), shown in the light strip at the top of the card thumbnail
on the battle card panel (大蝙蝠 above the art).

One block follows each large-label block of tools/gfx_cards.py (same kinds, same order, same entry -> label
mapping): 0xA0 B a card, 5 tiles in a row, palette as S1 (13 dark grey ink, 14 light grey, 12 black, 0 clear).
On screen (OBJ 120/121 at x 115, y 2, priority 3) tile rows 1-5 sit on the strip (rows 0 and 6 are the black frame);
the thumbnail's corner brackets are BG above the sprite and hide tile x 0-4 and 31-39, so only x 5..30 shows. The JP
ink spans x 1-36 and is clipped by the brackets in the original too (PPU dump `work/qa/mini_ppu`).

English: the card's large-label name in a hand-drawn 3x5 capital font (FONT), one blank column between letters,
ink 13, centred in x 5..30. Names wider than that use the short form in gfx/mini_labels.tsv (jp, en, short), keyed by
the large label's English, else their last word; the build fails if none fits. The panel header right below shows
the full name in the text font.

    python -X utf8 tools/gfx_minilabels.py OUT.png [FIRST COUNT]   # JP | EN preview
    python -X utf8 tools/gfx_minilabels.py --todo                  # names that still need a short form
"""
import csv
import struct
import sys

from PIL import Image

import gfx
import gfx_cards

SIZE, COLS, W, H = 0xA0, 5, 40, 8
INK = 13
X0, ROOM = 5, 26   # visible window x 5..30: the thumbnail's corner brackets (BG, above the OBJ) hide the rest
TOP = 1            # first ink row
# last words shared by many names (lands: 8 "... High", 6 "... Fudo"): the first word tells them apart
FIRST_WORD = {'Park', 'Fudo', 'High', 'Acad.', 'Hall', 'Shrine', 'One', "Breath", 'Time', 'Dark', 'Return', 'Light',
              'Mist', 'Throw'}

FONT = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'],
    'B': ['##.', '#.#', '##.', '#.#', '##.'],
    'C': ['.##', '#..', '#..', '#..', '.##'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '##.', '#..', '###'],
    'F': ['###', '#..', '##.', '#..', '#..'],
    'G': ['.##', '#..', '#.#', '#.#', '.##'],
    'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'I': ['#', '#', '#', '#', '#'],
    'J': ['..#', '..#', '..#', '#.#', '.#.'],
    'K': ['#.#', '#.#', '##.', '#.#', '#.#'],
    'L': ['#..', '#..', '#..', '#..', '###'],
    'M': ['#.#', '###', '###', '#.#', '#.#'],
    'N': ['##.', '#.#', '#.#', '#.#', '#.#'],
    'O': ['.#.', '#.#', '#.#', '#.#', '.#.'],
    'P': ['##.', '#.#', '##.', '#..', '#..'],
    'Q': ['.#.', '#.#', '#.#', '#.#', '.##'],
    'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['.##', '#..', '.#.', '..#', '##.'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'],
    'V': ['#.#', '#.#', '#.#', '#.#', '.#.'],
    'W': ['#.#', '#.#', '###', '###', '#.#'],
    'X': ['#.#', '#.#', '.#.', '#.#', '#.#'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'],
    'Z': ['###', '..#', '.#.', '#..', '###'],
    '-': ['..', '..', '##', '..', '..'],
    "'": ['#', '#', '.', '.', '.'],
    '.': ['.', '.', '.', '.', '#'],
    ' ': ['.', '.', '.', '.', '.'],
}


def width(text):
    return sum(len(FONT[c][0]) for c in text) + len(text) - 1


def shorts():
    """large-label English -> short form"""
    p = gfx.ROOT / 'gfx' / 'mini_labels.tsv'
    with open(p, encoding='utf8', newline='') as f:
        return {r['en']: r['short'] for r in csv.DictReader(f, delimiter='\t')}


def text_for(en, table=None):
    """the text a label shows (upper case): the name, else its short form, else its last word (its first word when
    the last is a generic place / filler word); None if none fits"""
    table = shorts() if table is None else table
    words = en.split()
    word = words[0] if words[-1] in FIRST_WORD else words[-1]
    for t in (en, table.get(en), word):
        if t and width(t.upper()) <= ROOM:
            return t.upper()
    return None


def bitmap(text):
    px = [[0] * W for _ in range(H)]
    x = X0 + (ROOM - width(text)) // 2
    for c in text:
        g = FONT[c]
        for y, row in enumerate(g):
            for dx, ch in enumerate(row):
                if ch == '#':
                    px[TOP + y][x + dx] = INK
        x += len(g[0]) + 1
    return px


def labels(rom=None):
    """[(mini label offset, jp, en)] in gfx_cards.labels order: the mini block of a kind starts where its large
    block ends"""
    rom = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
    out = []
    for kind, table, stride, n, tiles in gfx_cards.KINDS:
        mini = tiles + n * gfx_cards.SIZE
        for i in range(n):
            p = struct.unpack_from('<I', rom, table + stride * i)[0] & 0x1FFFFFF
            if not p:
                continue
            out.append(mini + i * SIZE)
    big = gfx_cards.labels()
    assert len(big) == len(out)
    return [(m, jp, en) for m, (_, jp, en) in zip(out, big)]


def mini_labels(rom):
    table = shorts()
    out, bad = [], []
    for a, jp, en in labels(rom):
        t = text_for(en, table)
        if t is None:
            bad.append(en)
            continue
        rom[a:a + SIZE] = gfx.encode(bitmap(t), COLS)
        out.append((a, a + SIZE))
    if bad:
        raise SystemExit('gfx_minilabels: no short form that fits %d px in gfx/mini_labels.tsv for: %s'
                         % (ROOM, ', '.join(sorted(set(bad)))))
    return out


def preview(out, first=0, count=None):
    orig = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
    new = bytearray(orig)
    mini_labels(new)
    offs = [a for a, _, _ in labels(orig)][first:]
    offs = offs[:count]
    pal = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8)
           for c in struct.unpack_from('<16H', orig, gfx_cards.PAL)]
    pal[0] = (120, 120, 120)   # the strip's grey
    per = 4
    rows = (len(offs) + per - 1) // per
    img = Image.new('RGB', (per * 2 * (W + 2) + per * 4, rows * (H + 2)), (40, 40, 90))
    for k, a in enumerate(offs):
        for col, src in enumerate((orig, new)):
            px = gfx.decode(src[a:a + SIZE], COLS, COLS)
            x0 = k % per * (2 * (W + 2) + 4) + col * (W + 2)
            for y in range(H):
                for x in range(W):
                    img.putpixel((x0 + x, k // per * (H + 2) + y), pal[px[y][x]])
    img.resize((img.width * 3, img.height * 3), Image.NEAREST).save(out)
    print(out)


if __name__ == '__main__':
    if sys.argv[1:] == ['--todo']:
        table = shorts()
        for en in sorted({en for _, _, en in labels()}):
            if text_for(en, table) is None:
                print('%s\t%d' % (en, width(en.upper())))
    elif len(sys.argv) in (2, 4):
        preview(sys.argv[1], *(int(v) for v in sys.argv[2:]))
    else:
        sys.exit(__doc__)
