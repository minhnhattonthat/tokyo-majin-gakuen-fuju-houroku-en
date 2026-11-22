"""objtiles.py: which 4bpp OBJ tiles the visible sprites of a PPU dump use (find free OBJ VRAM for a relocation).

    python -X utf8 tools/debug/objtiles.py work/qa/run/ppu_2500 [more dumps ..]

Reads PREFIX.oam.bin (ppuat.lua / L.dump_ppu) and prints, per dump, the merged tile ranges in use (1D mapping,
4bpp tile units; an 8bpp OBJ counts twice its tiles), then the ranges free in every dump given.
"""
import sys

SIZES = {  # (shape, size) -> (w, h)
    (0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64),
    (1, 0): (16, 8), (1, 1): (32, 8), (1, 2): (32, 16), (1, 3): (64, 32),
    (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64),
}


def used(prefix):
    oam = open(prefix + '.oam.bin', 'rb').read()
    tiles = set()
    for i in range(128):
        a0, a1, a2 = (int.from_bytes(oam[i * 8 + k:i * 8 + k + 2], 'little') for k in (0, 2, 4))
        if (a0 >> 8) & 3 == 2:  # hidden (affine off, disable bit)
            continue
        w, h = SIZES.get(((a0 >> 14) & 3, (a1 >> 14) & 3), (8, 8))
        n = (w // 8) * (h // 8) * (2 if a0 & 0x2000 else 1)
        t = a2 & 0x3FF
        tiles.update(range(t, t + n))
    return tiles


def ranges(s):
    out, run = [], None
    for t in sorted(s):
        if run and t == run[1] + 1:
            run[1] = t
        else:
            run = [t, t]
            out.append(run)
    return ', '.join(f'{a}-{b}' if a != b else f'{a}' for a, b in out)


def main():
    allused = set()
    for p in sys.argv[1:]:
        u = used(p)
        allused |= u
        print(f'{p}: used {ranges(u)}')
    print('free in all:', ranges(set(range(1024)) - allused))


if __name__ == '__main__':
    main()
