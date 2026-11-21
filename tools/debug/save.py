"""save.py: read and edit Fuju Houroku battery saves (SRAM, 32 KiB, header MAJIN_HUJU1).

    python -X utf8 tools/debug/save.py info SAV
    python -X utf8 tools/debug/save.py set SAV OUT [--chapter N] [--surname 緋勇] [--name 龍麻]
    python -X utf8 tools/debug/save.py make [--rom rom/base.gba]       # game-written base save -> work/saves/hub_ch05.sav
    python -X utf8 tools/debug/save.py test SAV [--rom ...]            # boot SAV, 続きから, assert the loaded chapter

Layout (tools/debug/save_layout.md): slot at 0x0000, length 0x555C:
  +0x000 'MAJIN_HUJU1\\0'; +0x00C surname (Shift-JIS, 8 bytes, 00-padded); +0x014 given name (8 bytes);
  +0x6D5 chapter byte (0x03005AA8 in RAM, 0..39); +0x6D8 u32 checksum; +0x6DC..0x555C second buffer (0x4E80).
  checksum = sum of the u32 words of +0x000..0x6D8 and +0x6DC..0x555C (routine 0x08000E00).
A partial copy of the first part (+0x000..0x6DC) sits at 0x555C (the 32 KiB SRAM cuts the rest off); edits are
mirrored there so both agree. Always edit a game-written file (`make`), never one built from zeros.
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))

SLOT, COPY = 0x0000, 0x555C
PART1, CKS, PART2_END = 0x6D8, 0x6D8, 0x555C
MAGIC = b'MAJIN_HUJU1\x00'
SURNAME, NAME, NAME_LEN = 0x00C, 0x014, 8
CHAPTER = 0x6D5
BASE_SAVE = os.path.join(ROOT, 'work', 'saves', 'hub_ch05.sav')


def checksum(d, base=SLOT):
    w1 = struct.unpack_from('<%dI' % (PART1 // 4), d, base)
    w2 = struct.unpack_from('<%dI' % ((PART2_END - 0x6DC) // 4), d, base + 0x6DC)
    return (sum(w1) + sum(w2)) & 0xFFFFFFFF


def load(path):
    d = bytearray(open(path, 'rb').read())
    if d[SLOT:SLOT + 12] != MAGIC:
        sys.exit('%s: no MAJIN_HUJU1 header at slot 0' % path)
    return d


def sjis_field(d, off):
    return bytes(d[off:off + NAME_LEN]).split(b'\x00')[0].decode('cp932', 'replace')


def info(d):
    stored = struct.unpack_from('<I', d, SLOT + CKS)[0]
    calc = checksum(d)
    print('surname   %s' % sjis_field(d, SLOT + SURNAME))
    print('name      %s' % sjis_field(d, SLOT + NAME))
    print('chapter   %d' % d[SLOT + CHAPTER])
    print('checksum  stored %08X calc %08X %s' % (stored, calc, 'ok' if stored == calc else 'BAD'))
    same = d[COPY:COPY + 0x6DC] == d[SLOT:SLOT + 0x6DC]
    print('copy@%X  %s' % (COPY, 'matches slot' if same else 'differs from slot'))
    return stored == calc


def put_name(d, off, s):
    b = s.encode('cp932')
    if len(b) > NAME_LEN:
        sys.exit('name %r is %d bytes; the field holds %d' % (s, len(b), NAME_LEN))
    d[off:off + NAME_LEN] = b.ljust(NAME_LEN, b'\x00')


def edit(d, a):
    if a.chapter is not None:
        if not 0 <= a.chapter <= 39:
            sys.exit('chapter 0..39')
        d[SLOT + CHAPTER] = a.chapter
    if a.surname is not None:
        put_name(d, SLOT + SURNAME, a.surname)
    if a.name is not None:
        put_name(d, SLOT + NAME, a.name)
    struct.pack_into('<I', d, SLOT + CKS, checksum(d))
    d[COPY:COPY + 0x6DC] = d[SLOT:SLOT + 0x6DC]


def emu(rom, out, route, extra):
    from skill import SKILL
    cmd = [sys.executable, '-X', 'utf8', os.path.join(SKILL, 'scripts', 'emu.py'), rom, '--out', out,
           '--route', os.path.join(ROOT, 'tools', 'routes', route)] + extra
    with open(os.path.join(out + '.txt'), 'w', encoding='utf-8') as lf:
        return subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT).returncode


def make(a):
    out = os.path.join(ROOT, 'work', 'qa', 'save_make')
    os.makedirs(out, exist_ok=True)
    rc = emu(a.rom, out, 'hub_save.txt', ['--script', os.path.join(ROOT, 'tools', 'debug', 'warp.lua'),
                                          '--var', "SCENE='MODE6.1'", '--var', 'CH=5'])
    src = os.path.join(out, os.path.splitext(os.path.basename(a.rom))[0] + '.sav')
    if rc or not os.path.exists(src):
        sys.exit('make: emu exit %d, no %s' % (rc, src))
    os.makedirs(os.path.dirname(BASE_SAVE), exist_ok=True)
    shutil.copyfile(src, BASE_SAVE)
    ok = info(load(BASE_SAVE))
    print('wrote', BASE_SAVE)
    return 0 if ok else 1


def test(a):
    """Boot SAV, title -> 続きから (cursor starts there when a save exists), wait for the hub; pass when the chapter
    byte read back from RAM equals the save's and no corruption path (mode 0/title again) is taken."""
    d = load(a.sav)
    want = d[SLOT + CHAPTER]
    out = os.path.join(ROOT, 'work', 'qa', 'save_test', os.path.splitext(os.path.basename(a.sav))[0])
    os.makedirs(out, exist_ok=True)
    rc = emu(a.rom, out, 'title_continue.txt', ['--sav', a.sav, '--frames', '2400', '--script',
                                                os.path.join(ROOT, 'tools', 'debug', 'loadcheck.lua')])
    log = open(os.path.join(out, 'log.txt'), encoding='utf-8').read()
    got = [ln for ln in log.splitlines() if ln.startswith('LOAD')]
    print('\n'.join(got) or 'no LOAD line')
    ok = rc == 0 and any(('mode=6' in g and 'ch=%d ' % want in g + ' ') for g in got)
    print('%s: %s (want chapter %d) -> %s' % (a.sav, 'ok' if ok else 'FAIL', want, out))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('info'); p.add_argument('sav')
    p = sub.add_parser('set'); p.add_argument('sav'); p.add_argument('out')
    p.add_argument('--chapter', type=int); p.add_argument('--surname'); p.add_argument('--name')
    p = sub.add_parser('make'); p.add_argument('--rom', default=os.path.join(ROOT, 'rom', 'base.gba'))
    p = sub.add_parser('test'); p.add_argument('sav'); p.add_argument('--rom', default=os.path.join(ROOT, 'rom', 'base.gba'))
    a = ap.parse_args()
    if a.cmd == 'info':
        return 0 if info(load(a.sav)) else 1
    if a.cmd == 'set':
        d = load(a.sav)
        edit(d, a)
        open(a.out, 'wb').write(d)
        return 0 if info(d) else 1
    if a.cmd == 'make':
        return make(a)
    return test(a)


if __name__ == '__main__':
    sys.exit(main())
