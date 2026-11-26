"""ra_state.py: look inside a player's RetroArch mGBA savestate (.state / .stateN, RZIP-packed) without mGBA.

    python -X utf8 tools/debug/ra_state.py render STATE OUT.png      # the screen: text-mode BGs + regular OBJs
    python -X utf8 tools/debug/ra_state.py oam STATE [x0 y0 x1 y1]   # visible OBJs: index, x, y, shape/size, tile
    python -X utf8 tools/debug/ra_state.py dump STATE OUTDIR         # io/pal/oam/vram/iwram/ewram .bin files

Layout: RZIP ('#RZIPv\\x01#', u32 chunk size, u64 total, then u32 size + zlib chunks) -> 'RASTATE\\x01' 'MEM ' u32
size -> mGBA GBASerializedState: I/O 0x400, palette 0x800, OAM 0xC00, VRAM 0x1000, IWRAM 0x19000, EWRAM 0x21000.
Mesen can't load these states; for a scene to re-run, reach it with tools/debug/warp.py (issue #1: the renders told
which tutorial page and which OBJ tiles were hit). The renderer skips blending, windows and affine OBJs.
"""
import struct
import sys
import zlib
from pathlib import Path

REGIONS = {'io': (0x400, 0x400), 'pal': (0x800, 0x400), 'oam': (0xC00, 0x400), 'vram': (0x1000, 0x18000),
           'iwram': (0x19000, 0x8000), 'ewram': (0x21000, 0x40000)}
OBJ_SIZE = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
            (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def load(path):
    """the mGBA state bytes of a RetroArch state file (RZIP or plain)"""
    d = Path(path).read_bytes()
    if d[:8] == b'#RZIPv\x01#':
        total, = struct.unpack_from('<Q', d, 12)
        i, out = 20, bytearray()
        while i < len(d):
            n, = struct.unpack_from('<I', d, i)
            out += zlib.decompress(d[i + 4:i + 4 + n])
            i += 4 + n
        assert len(out) == total, (len(out), total)
        d = bytes(out)
    if d[:8] == b'RASTATE\x01':
        assert d[8:12] == b'MEM ', d[8:12]
        d = d[16:16 + struct.unpack_from('<I', d, 12)[0]]
    return d


def region(m, name):
    o, n = REGIONS[name]
    return m[o:o + n]


def objs(m):
    """visible regular OBJs: (index, x, y, w, h, shape, size, tile, palette, prio, 8bpp, hflip, vflip)"""
    oam = region(m, 'oam')
    for i in range(128):
        a0, a1, a2 = struct.unpack_from('<3H', oam, 8 * i)
        if a0 & 0x300 == 0x200 or a0 & 0x100 or a0 >> 14 == 3:
            continue
        w, h = OBJ_SIZE[(a0 >> 14, a1 >> 14)]
        y, x = a0 & 255, a1 & 511
        y, x = y - 256 if y >= 160 else y, x - 512 if x >= 240 else x
        yield (i, x, y, w, h, a0 >> 14, a1 >> 14, a2 & 1023, a2 >> 12, a2 >> 10 & 3, a0 >> 13 & 1,
               a1 >> 12 & 1, a1 >> 13 & 1)


def render(m):
    from PIL import Image
    io, pal, vram = region(m, 'io'), region(m, 'pal'), region(m, 'vram')
    h16 = lambda b, o: struct.unpack_from('<H', b, o)[0]

    def col(i):
        c = h16(pal, 2 * i)
        return (c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3

    disp, W, H, layers = h16(io, 0), 240, 160, []
    for n in range(4):
        if not disp & (0x100 << n) or (disp & 7) not in (0, 1) or ((disp & 7) == 1 and n > 2):
            continue
        cnt = h16(io, 8 + 2 * n)
        hofs, vofs = h16(io, 0x10 + 4 * n) & 511, h16(io, 0x12 + 4 * n) & 511
        cb, sb, c256, size = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800, cnt >> 7 & 1, cnt >> 14
        mw, mh = (256, 512, 256, 512)[size], (256, 256, 512, 512)[size]
        px = {}
        for y in range(H):
            for x in range(W):
                bx, by = (x + hofs) % mw, (y + vofs) % mh
                blk = bx // 256 + (by // 256) * (2 if mw == 512 else 1)
                e = h16(vram, sb + blk * 0x800 + ((by % 256) // 8 * 32 + (bx % 256) // 8) * 2)
                t, tx, ty = e & 1023, bx % 8, by % 8
                tx, ty = 7 - tx if e >> 10 & 1 else tx, 7 - ty if e >> 11 & 1 else ty
                if c256:
                    a = cb + t * 64 + ty * 8 + tx
                    ci = vram[a] if a < 0x10000 else 0
                else:
                    a = cb + t * 32 + ty * 4 + tx // 2
                    ci = (vram[a] >> 4 * (tx & 1)) & 15 if a < 0x10000 else 0
                    ci = ci + (e >> 12) * 16 if ci else 0
                if ci:
                    px[(x, y)] = col(ci)
        layers.append((cnt & 3, n, px))
    if disp & 0x1000:
        one_d = disp & 0x40
        for i, x0, y0, w, hh, _, _, t0, p, prio, c256, hf, vf in objs(m):
            px = {}
            for yy in range(hh):
                for xx in range(w):
                    sx, sy = x0 + xx, y0 + yy
                    if not (0 <= sx < W and 0 <= sy < H):
                        continue
                    tx, ty = (w - 1 - xx) if hf else xx, (hh - 1 - yy) if vf else yy
                    if c256:
                        t = t0 + ((ty // 8) * (w // 8) * 2 if one_d else (ty // 8) * 32) + (tx // 8) * 2
                        a = 0x10000 + (t & 1023) * 32 + (ty % 8) * 8 + tx % 8
                        ci = vram[a] if a < 0x18000 else 0
                        if ci:
                            px[(sx, sy)] = col(256 + ci)
                    else:
                        t = t0 + ((ty // 8) * (w // 8) if one_d else (ty // 8) * 32) + tx // 8
                        a = 0x10000 + (t & 1023) * 32 + (ty % 8) * 4 + (tx % 8) // 2
                        ci = (vram[a] >> 4 * (tx & 1)) & 15 if a < 0x18000 else 0
                        if ci:
                            px[(sx, sy)] = col(256 + p * 16 + ci)
            layers.append((prio, -1 - (127 - i) * 0.001, px))   # OBJ over a BG of the same priority; low index on top
    img = Image.new('RGB', (W, H), col(0))
    for _, _, px in sorted(layers, key=lambda l: (-l[0], -l[1])):
        for k, v in px.items():
            img.putpixel(k, v)
    return img


def main(argv):
    if len(argv) < 2 or argv[0] not in ('render', 'oam', 'dump'):
        print(__doc__)
        return 2
    m = load(argv[1])
    if argv[0] == 'render':
        render(m).save(argv[2])
    elif argv[0] == 'oam':
        box = [int(v) for v in argv[2:6]] if len(argv) >= 6 else [-64, -64, 240, 160]
        for i, x, y, w, h, sh, sz, t, p, prio, c256, _, _ in objs(m):
            if box[0] <= x < box[2] and box[1] <= y < box[3]:
                print('#%3d x=%4d y=%4d %2dx%-2d tile=%4d pal=%2d prio=%d%s' % (i, x, y, w, h, t, p, prio,
                                                                            ' 8bpp' if c256 else ''))
    else:
        out = Path(argv[2])
        out.mkdir(parents=True, exist_ok=True)
        for k in REGIONS:
            (out / (k + '.bin')).write_bytes(region(m, k))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
