"""gfx_preview_rooms.py: render the room_banners screens of rom/base.gba with the English lettering applied.

    python -X utf8 tools/debug/gfx_preview_rooms.py [--out work/gfx/rooms_en.png]   # 2x zoom, two screens a row
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gfx  # noqa: E402
import gfx_rooms  # noqa: E402
import gfx_screens  # noqa: E402
from PIL import Image  # noqa: E402

out = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else Path('work/gfx/rooms_en.png')
import struct  # noqa: E402

orig = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
rom = bytearray(orig)
gfx.room_banners(rom)
screens = list(dict.fromkeys(int(r['screen'], 16) for r in gfx.rows('room_banners')))
entry = {t: e for e, t, *_ in gfx_screens.screens(orig)}
ims = []
for t in screens:
    t2, p, m = (v & 0x1FFFFFF for v in struct.unpack_from('<3I', rom, entry[t]))   # moved blocks too
    ims.append(gfx_screens.render(rom, t2, p, m, (m - t2) // 32, 8))
sheet = Image.new('RGB', (480, 160 * ((len(ims) + 1) // 2)))
for i, im in enumerate(ims):
    sheet.paste(im, (i % 2 * 240, i // 2 * 160))
out.parent.mkdir(parents=True, exist_ok=True)
sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save(out)
print(out)
