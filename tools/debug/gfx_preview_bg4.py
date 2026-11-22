"""gfx_preview_bg4.py GROUP PTRS [PAL_AT] [--out PNG]: render a bg4_edit screen of rom/base.gba before | after.

    python -X utf8 tools/debug/gfx_preview_bg4.py deck_name_screen D81D68 4
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gfx  # noqa: E402
import gfx_screens  # noqa: E402
from PIL import Image  # noqa: E402

group, ptrs = sys.argv[1], int(sys.argv[2], 16)
pal_at = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else -8
out = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else Path(f'work/gfx/{group}.png')
orig = (gfx.ROOT / 'rom' / 'base.gba').read_bytes()
new = bytearray(orig)
gfx.GROUPS[group](new)
sheet = Image.new('RGB', (480, 160))
for i, rom in enumerate((orig, new)):
    p, t, m = (struct.unpack_from('<I', rom, ptrs + k)[0] & 0x1FFFFFF for k in (pal_at, 0, 8))
    sheet.paste(gfx_screens.render(rom, t, p, m, (m - t) // 32, 1), (240 * i, 0))
out.parent.mkdir(parents=True, exist_ok=True)
sheet.resize((960, 320), Image.NEAREST).save(out)
print(out)
