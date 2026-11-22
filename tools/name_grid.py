"""name_grid.py: the English name-entry grids (G7). Each kana cell of the player-name grid (D6E56C-D6E710) and the
deck-name grid (D72F00-D730A4) becomes one VWF unit: a romaji syllable, lowercase on the hiragana page and
capitalised on the katakana page; the small-kana rows give consonants for glides and doubles (r + yu = ryu, t + ta =
tta). A name keeps the game's 4 units, the same budget as 4 kana. Blank cells stay full-width spaces, so the cursor
behaves as before. Tight letters (vwf.TIGHT: t s T S C set closer) keep tsu / Tsu / Shi / Chi inside one 16 px cell.

    python -X utf8 tools/name_grid.py          # print ID=TEXT for every grid row
    python -X utf8 tools/name_grid.py --set    # write them into script/system/d6.tsv (tools/set_en.py)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

ROMAJI = dict(zip(
    'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'
    'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ',
    'a i u e o ka ki ku ke ko sa shi su se so ta chi ţşu te to na ni nu ne no ha hi fu he ho ma mi mu me mo '
    'ya yu yo ra ri ru re ro wa wo n ga gi gu ge go za ji zu ze zo da ji zu de do ba bi bu be bo '
    'pa pi pu pe po'.split()))
ROMAJI.update({'ぁ': 'k', 'ぃ': 'sh', 'ぅ': 'ch', 'ぇ': 'j', 'ぉ': 'r',     # consonants: glides and doubles
               'ゃ': 't', 'ゅ': 'p', 'ょ': 's', 'っ': 'g', 'ー': '-'})
CAPS = {'ţşu': 'Ţşu', 'shi': 'Şhi', 'chi': 'Çhi', 'sh': 'Sh', 'ch': 'Ch'}
GRIDS = ((0xD6E56C, 0xD6E71C), (0xD72F00, 0xD730B0))
BLANK = '[81][40]'


def cell(ch):
    """one grid cell (kana) -> script text of its unit"""
    if ch == '　':
        return BLANK
    if ch == 'ヴ':
        return 'V'
    hira = chr(ord(ch) - 0x60) if 'ァ' <= ch <= 'ヶ' else ch
    r = ROMAJI[hira]
    if hira == ch:
        return r
    return CAPS.get(r, r[0].upper() + r[1:])


def rows():
    import extract
    out = {}
    for rid, row in extract.load().items():
        if row['kind'] == 'grid' and len(rid) == 6 and any(a <= int(rid, 16) < b for a, b in GRIDS):
            out[rid] = '¦'.join(cell(ch) for ch in row['jp'])
    return out


def main():
    r = rows()
    args = ['%s=%s' % kv for kv in sorted(r.items())]
    if '--set' in sys.argv:
        return subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'set_en.py'), *args]).returncode
    print('\n'.join(args))
    return 0


if __name__ == '__main__':
    sys.exit(main())
