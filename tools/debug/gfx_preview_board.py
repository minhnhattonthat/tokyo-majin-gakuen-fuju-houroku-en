"""gfx_preview_board.py [--out PNG]: sutra board (group sutra_board) original | English at 3x, with every red
highlight sprite drawn over its label on a second English copy (bottom row).

    python -X utf8 tools/debug/gfx_preview_board.py --out work/gfx/sutra_board.png
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gfx  # noqa: E402
import gfx_board  # noqa: E402
import gfx_signs  # noqa: E402
from PIL import Image  # noqa: E402

out = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else Path('work/gfx/sutra_board.png')
orig = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
new = bytearray(orig)
gfx_board.apply(new)


def board(rom, sprites=False):
    t0, pal, m0 = (struct.unpack_from('<I', rom, gfx_board.ENTRY + k)[0] & 0x1FFFFFF for k in (0, 4, 8))
    size = struct.unpack_from('<I', rom, gfx_board.SIZE_LIT)[0]
    c = gfx.screen_canvas(rom[t0:t0 + size], struct.unpack_from('<600H', rom, m0))
    p = gfx_signs.pal_rgb(rom, pal)
    p[0] = (0, 0, 0)
    img = Image.new('RGB', (240, 160))
    img.putdata([p[v] for row in c for v in row])
    if sprites:
        sp = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8)
              for c in struct.unpack_from('<16H', rom, gfx_board.SPR - 0x20)]
        for r in gfx.rows('sutra_board'):
            k, x, y, w, h = (int(r[c]) for c in ('spr', 'x', 'y', 'w', 'h'))
            px = gfx.decode(rom[gfx_board.SPR + k * 0x100:][:0x100], w // 8, 8)
            for yy in range(h):
                for xx in range(w):
                    if px[yy][xx]:
                        img.putpixel((x + xx, y + yy), sp[px[yy][xx]])
    return img


sheet = Image.new('RGB', (480, 320))
sheet.paste(board(orig), (0, 0))
sheet.paste(board(new), (240, 0))
sheet.paste(board(orig, True), (0, 160))
sheet.paste(board(new, True), (240, 160))
out.parent.mkdir(parents=True, exist_ok=True)
sheet.resize((1440, 960), Image.NEAREST).save(out)
print(out)
