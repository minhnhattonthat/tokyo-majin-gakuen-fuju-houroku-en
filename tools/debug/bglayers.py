"""bglayers.py: render each text-mode BG layer and the sprites of a GBA PPU dump separately, to find which layer and
which tiles a graphic lives in.

    python -X utf8 tools/debug/bglayers.py DIR/ppu_002650 [--out DIR] [--zoom 2]
    (the dump comes from `warp.py ROW --script $SKILL/scripts/lua/probes/ppudump.lua --var DUMP_AT=N`)

Writes <prefix>.bg<n>.png (whole 256x256/512 map, scroll ignored) and <prefix>.obj.png, and prints for each layer:
BGxCNT fields (priority, char base, screen base, 8bpp, size), scroll and the used tile range per palette bank.
"""
import struct
import sys
from pathlib import Path

from PIL import Image


def pal_rgb(pal):
    return [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in struct.unpack_from('<256H', pal)]


def tile(vram, base, idx, bpp8):
    size = 64 if bpp8 else 32
    off = base + idx * size
    t = vram[off:off + size].ljust(size, b'\0')
    if bpp8:
        return [[t[y * 8 + x] for x in range(8)] for y in range(8)]
    return [[(t[y * 4 + x // 2] >> (4 * (x & 1))) & 15 for x in range(8)] for y in range(8)]


def bg(vram, pal, cnt, zoom):
    char, screen, bpp8, size = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800, cnt >> 7 & 1, cnt >> 14
    tw, th = (32, 64, 32, 64)[size], (32, 32, 64, 64)[size]
    img = Image.new('RGB', (tw * 8, th * 8), (255, 0, 255))
    px = img.load()
    used = {}
    for ty in range(th):
        for tx in range(tw):
            blk = (tx // 32) + (ty // 32) * (tw // 32)
            e = struct.unpack_from('<H', vram, screen + blk * 0x800 + (ty % 32 * 32 + tx % 32) * 2)[0]
            idx, hf, vf, bank = e & 0x3FF, e >> 10 & 1, e >> 11 & 1, e >> 12
            if idx:
                lo, hi = used.get(bank, (idx, idx))
                used[bank] = (min(lo, idx), max(hi, idx))
            t = tile(vram, char, idx, bpp8)
            for y in range(8):
                for x in range(8):
                    v = t[vf and 7 - y or y][hf and 7 - x or x]
                    if v:
                        px[tx * 8 + x, ty * 8 + y] = pal[v if bpp8 else bank * 16 + v]
    return img.resize((img.width * zoom, img.height * zoom), Image.NEAREST), char, screen, bpp8, size, used


def objs(vram, pal, oam, dispcnt, zoom):
    img = Image.new('RGB', (512, 256), (255, 0, 255))
    px = img.load()
    shapes = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
              (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}
    lines = []
    for i in range(128):
        a0, a1, a2 = struct.unpack_from('<3H', oam, i * 8)
        if a0 >> 8 & 3 == 2:   # disabled
            continue
        shape, sz = a0 >> 14, a1 >> 14
        if (shape, sz) not in shapes:
            continue
        w, h = shapes[shape, sz]
        x, y, bpp8, t0, bank = a1 & 511, a0 & 255, a0 >> 13 & 1, a2 & 1023, a2 >> 12
        lines.append(f'  obj{i}: x={x} y={y} {w}x{h} tile={t0} bank={bank} {"8bpp" if bpp8 else ""} prio={a2 >> 10 & 3}')
        one_d = dispcnt >> 6 & 1
        for ty in range(h // 8):
            for tx in range(w // 8):
                step = 2 if bpp8 else 1
                n = t0 + (ty * (w // 8) * step if one_d else ty * 32) + tx * step
                t = tile(vram, 0x10000, n, 0) if not bpp8 else \
                    [[vram[0x10000 + n * 32 + yy * 8 + xx] for xx in range(8)] for yy in range(8)]
                for yy in range(8):
                    for xx in range(8):
                        v = t[yy][xx]
                        if v:
                            X, Y = (x + tx * 8 + xx) % 512, (y + ty * 8 + yy) % 256
                            px[X, Y] = pal[256 + (v if bpp8 else bank * 16 + v)]
    return img.resize((img.width * zoom, img.height * zoom), Image.NEAREST), lines


def main(argv):
    prefix = Path(argv[0])
    out = Path(argv[argv.index('--out') + 1]) if '--out' in argv else prefix.parent
    zoom = int(argv[argv.index('--zoom') + 1]) if '--zoom' in argv else 1
    vram = Path(f'{prefix}.vram.bin').read_bytes()
    pal = pal_rgb(Path(f'{prefix}.pal.bin').read_bytes()[:0x200]) + \
        pal_rgb(Path(f'{prefix}.pal.bin').read_bytes()[0x200:0x400])
    io = Path(f'{prefix}.io.bin').read_bytes()
    oam = Path(f'{prefix}.oam.bin').read_bytes()
    dispcnt = struct.unpack_from('<H', io, 0)[0]
    print(f'DISPCNT={dispcnt:04X} mode={dispcnt & 7} bg_on={[n for n in range(4) if dispcnt >> (8 + n) & 1]} '
          f'obj={dispcnt >> 12 & 1}')
    out.mkdir(parents=True, exist_ok=True)
    for n in range(4):
        if not dispcnt >> (8 + n) & 1:
            continue
        cnt = struct.unpack_from('<H', io, 8 + 2 * n)[0]
        hofs, vofs = struct.unpack_from('<2H', io, 0x10 + 4 * n)
        img, char, screen, bpp8, size, used = bg(vram, pal, cnt, zoom)
        p = out / f'{prefix.name}.bg{n}.png'
        img.save(p)
        print(f'BG{n}: prio={cnt & 3} char=0x{char:04X} screen=0x{screen:04X} {"8bpp" if bpp8 else "4bpp"} '
              f'size={size} scroll=({hofs & 511},{vofs & 511}) tiles per bank: '
              + ' '.join(f'{b}:{lo}-{hi}' for b, (lo, hi) in sorted(used.items())) + f' -> {p}')
    if dispcnt >> 12 & 1:
        img, lines = objs(vram, pal, oam, dispcnt, zoom)
        p = out / f'{prefix.name}.obj.png'
        img.save(p)
        print(f'OBJ -> {p}')
        print('\n'.join(lines))


if __name__ == '__main__':
    main(sys.argv[1:])
