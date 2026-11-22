"""icons.py: render 16x16 icons (4 tiles each, order TL TR BL BR) from a ROM range with a BG palette bank of a ppu
dump, 16 a row, zoom 3.

    python -X utf8 tools/debug/icons.py ROM OFFSET COUNT BANK PAL_BIN OUT.png [ORDER]

The text icon sheet is at 0xACA06C (bank 15; 陰 = icon 24, 陽 = 25, white 木火土金水 = 6-10, round ones 11-15).
"""
import struct, sys
from PIL import Image
rom = open(sys.argv[1], 'rb').read()
off, n, bank = int(sys.argv[2], 16), int(sys.argv[3]), int(sys.argv[4])
pal = open(sys.argv[5], 'rb').read()
cols = [struct.unpack_from('<H', pal, 32 * bank + 2 * i)[0] for i in range(16)]
cols = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in cols]
order = sys.argv[7] if len(sys.argv) > 7 else 'TL,TR,BL,BR'
img = Image.new('RGB', (18 * 16, 18 * ((n + 15) // 16)), (255, 0, 255))
pos = {'TL': (0, 0), 'TR': (8, 0), 'BL': (0, 8), 'BR': (8, 8)}
for k in range(n):
    for j, name in enumerate(order.split(',')):
        t = off + (4 * k + j) * 32
        for y in range(8):
            for x in range(8):
                b = rom[t + y * 4 + x // 2]
                v = (b >> 4) if x & 1 else (b & 15)
                if v:
                    img.putpixel(((k % 16) * 18 + pos[name][0] + x, (k // 16) * 18 + pos[name][1] + y), cols[v])
img = img.resize((img.width * 3, img.height * 3), Image.NEAREST)
img.save(sys.argv[6])
