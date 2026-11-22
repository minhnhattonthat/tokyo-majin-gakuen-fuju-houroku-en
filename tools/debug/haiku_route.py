"""haiku_route.py: emu.py route that types a haiku on the haiku club's kana grid (from work/states/haiku.mss, the
welcome line), then waits for the verdict. Used to check the haiku passwords (D16A40.., kind grid) still match.

    python -X utf8 tools/debug/haiku_route.py "ああねむい ねればねるとき ねちまおう" > work/qa/haiku_type.txt

Grid on screen: 10 columns あかさたなはまやらわ by あいうえお, row 5 small kana ぁぃぅぇぉっ . ょ ゛ ゜ (dakuten
are typed as the base kana, then ゛ / ゜), row 6 the buttons at columns 7/8/9: 改行 (NEXT LINE), 戻る (DEL), 終る
(END); 16 px cursor cells; up from row 0 wraps to the column's lowest cell. Moves go along row 0, so blank cells
never get in the way. Checked 2026-11-22: the JP ROM and the English build give the same verdict and card.
"""
import sys

COLS = ['あいうえおぁ', 'かきくけこぃ', 'さしすせそぅ', 'たちつてとぇ', 'なにぬねのぉ', 'はひふへほっ', 'まみむめも',
        'やゆよ', 'らりるれろ', 'わをんー']
DAKU = dict(zip('がぎぐげござじずぜぞだぢづでどばびぶべぼ', 'かきくけこさしすせそたちつてとはひふへほ'))
HANDAKU = dict(zip('ぱぴぷぺぽ', 'はひふへほ'))


def cells(ch):
    """grid cells to press for one kana: dakuten / handakuten are the base kana, then ゛ (8, 5) / ゜ (9, 5)"""
    if ch in DAKU:
        return cells(DAKU[ch]) + [(8, 5)]
    if ch in HANDAKU:
        return cells(HANDAKU[ch]) + [(9, 5)]
    for c, col in enumerate(COLS):
        if ch in col:
            return [(c, col.index(ch))]
    raise SystemExit('not on the grid: ' + ch)


def main():
    text = sys.argv[1]
    out = ['30 -', '4 a', '60 -', '4 a', '150 -']
    c, r = 0, 0

    def press(k, n=1):
        for _ in range(n):
            out.extend(['4 ' + k, '16 -'])

    def goto(tc, tr):
        nonlocal c, r
        press('up', r) if r < 6 else press('down', 1)   # to row 0 (from the button row, down wraps to row 0)
        r = 0
        press('right' if tc > c else 'left', abs(tc - c))
        c = tc
        if tr == 6:
            press('up')
        else:
            press('down', tr)
        r = tr

    for ch in text:
        for tc, tr in ([(7, 6)] if ch in ' 　' else cells(ch)):
            goto(tc, tr)
            press('a')
    goto(9, 6)
    press('a')
    out += ['120 -', '4 a', '120 -', '4 a', '120 -', '4 a', '120 -', '4 a', '120 -', '4 a', '300 -']
    print('\n'.join(out))


if __name__ == '__main__':
    main()
