"""screen_png.py: render 4bpp 30x20 BG screens (palette, tiles, map pointers as gfx.bg4_edit takes them) to PNGs.

    python -X utf8 tools/debug/screen_png.py PTRS[:pal_at] .. [--rom rom/base.gba] [--out work/gfx] [--zoom 2]

PTRS is the ROM offset of the tiles pointer (palette pointer at PTRS-8 unless :pal_at given, map pointer at PTRS+8),
e.g. 0xD16FE4 for the haiku club's kana grid. Writes <out>/screen_<PTRS>.png.
"""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import gfx  # noqa: E402
import gfx_signs  # noqa: E402


def render(rom, ptrs, pal_at=-8):
    pal, t0, m0 = (struct.unpack_from('<I', rom, ptrs + k)[0] & 0x1FFFFFF for k in (pal_at, 0, 8))
    size = struct.unpack_from('<I', rom, ptrs + 4)[0] if pal_at == -8 else m0 - t0   # the haiku table's byte count
    canvas = gfx.screen_canvas(rom[t0:t0 + size], struct.unpack_from('<600H', rom, m0))
    rgb = gfx_signs.pal_rgb(rom, pal)
    img = Image.new('RGB', (240, 160))
    img.putdata([rgb[p] if p else (255, 0, 255) for row in canvas for p in row])
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('ptrs', nargs='+')
    ap.add_argument('--rom', default=str(ROOT / 'rom' / 'base.gba'))
    ap.add_argument('--out', default=str(ROOT / 'work' / 'gfx'))
    ap.add_argument('--zoom', type=int, default=2)
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    for p in a.ptrs:
        s, _, pa = p.partition(':')
        img = render(rom, int(s, 16), int(pa) if pa else -8)
        img = img.resize((240 * a.zoom, 160 * a.zoom), Image.NEAREST)
        out = Path(a.out) / ('screen_%06X.png' % int(s, 16))
        img.save(out)
        print(out)


if __name__ == '__main__':
    main()
