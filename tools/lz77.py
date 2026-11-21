"""lz77.py: GBA BIOS LZ77 (type 0x10) decompress/compress, plus `scan ROM` that lists every offset that decodes
cleanly (4-byte aligned, size 32 B..256 KiB, back-references inside the output)."""
import struct
import sys


def decompress(d, off, limit=1 << 18):
    """Return (data, end_offset) or None if the block is not valid LZ77."""
    if d[off] != 0x10:
        return None
    size = struct.unpack_from('<I', d, off)[0] >> 8
    if size < 32 or size > limit:
        return None
    out = bytearray()
    i = off + 4
    n = len(d)
    while len(out) < size:
        if i >= n:
            return None
        flags = d[i]
        i += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                if i + 1 >= n:
                    return None
                b1, b2 = d[i], d[i + 1]
                i += 2
                ln = (b1 >> 4) + 3
                disp = ((b1 & 0xF) << 8 | b2) + 1
                if disp > len(out):
                    return None
                for _ in range(ln):
                    out.append(out[-disp])
            else:
                if i >= n:
                    return None
                out.append(d[i])
                i += 1
    return bytes(out[:size]), i


def compress(data):
    """Greedy LZ77 (type 0x10), VRAM-safe (disp >= 2)."""
    out = bytearray(struct.pack('<I', 0x10 | (len(data) << 8)))
    i = 0
    while i < len(data):
        flag_pos = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if i >= len(data):
                break
            best_len, best_disp = 0, 0
            start = max(0, i - 4096)
            for j in range(i - 2, start - 1, -1):
                ln = 0
                while ln < 18 and i + ln < len(data) and data[j + ln] == data[i + ln]:
                    ln += 1
                if ln > best_len:
                    best_len, best_disp = ln, i - j
                    if ln == 18:
                        break
            if best_len >= 3:
                flags |= 0x80 >> bit
                v = ((best_len - 3) << 12) | (best_disp - 1)
                out += bytes([v >> 8, v & 0xFF])
                i += best_len
            else:
                out.append(data[i])
                i += 1
        out[flag_pos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def scan(d, lo=0, hi=None):
    hi = hi or len(d)
    found = []
    off = lo
    while off < hi:
        if d[off] == 0x10:
            r = decompress(d, off)
            if r:
                found.append((off, len(r[0]), r[1]))
                off = (r[1] + 3) & ~3
                continue
        off += 4
    return found


if __name__ == '__main__':
    if sys.argv[1] == 'scan':
        d = open(sys.argv[2], 'rb').read()
        f = scan(d)
        print('blocks', len(f), 'packed', hex(sum(e - o for o, _, e in f)), 'unpacked', hex(sum(s for _, s, _ in f)))
        for o, s, e in f[:int(sys.argv[3]) if len(sys.argv) > 3 else 0]:
            print(hex(o), hex(s), hex(e))
