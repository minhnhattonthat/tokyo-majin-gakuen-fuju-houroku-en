"""haiku_list.py: the haiku club passwords as a Markdown table for the release README (D14).

    python -X utf8 tools/haiku_list.py > docs/haiku.md

Reads the `grid` rows D16A40-D16F54 of script/system/d1.tsv (the kana the game compares against), romanizes them
(Hepburn, long vowels as typed) and takes the English meaning from the notes column.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_BASE = dict(zip(
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
    "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽぁぃぅぇぉ",
    "a i u e o ka ki ku ke ko sa shi su se so ta chi tsu te to na ni nu ne no ha hi fu he ho ma mi mu me mo "
    "ya yu yo ra ri ru re ro wa o n ga gi gu ge go za ji zu ze zo da ji zu de do ba bi bu be bo pa pi pu pe po "
    "a i u e o".split()))
_SMALL_Y = {"ゃ": "ya", "ゅ": "yu", "ょ": "yo"}


def romaji(kana: str) -> str:
    out: list[str] = []
    sokuon = False
    for ch in kana:
        if ch == "　":
            out.append(" / ")
        elif ch == "っ":
            sokuon = True
            continue
        elif ch == "ー":
            out.append(out[-1][-1] if out else "")
        elif ch in _SMALL_Y and out:
            prev = out.pop()
            if prev.endswith(("shi", "chi", "ji")):
                out.append(prev[:-1] + _SMALL_Y[ch][1:])
            else:
                out.append(prev[:-1] + _SMALL_Y[ch])
        else:
            syl = _BASE.get(ch, ch)
            if sokuon:
                syl = ("t" if syl.startswith("ch") else syl[0]) + syl
            out.append(syl)
        sokuon = False
    return "".join(out)


def rows():
    for line in (ROOT / "script/system/d1.tsv").read_text(encoding="utf8").splitlines():
        f = line.split("\t")
        if len(f) >= 6 and f[1] == "grid" and "D16A40" <= f[0] <= "D16F54":
            meaning = f[5].split("meaning:", 1)[-1].strip().replace("　", " / ")
            yield f[3], romaji(f[3]), meaning


def main():
    print("| # | Type this (kana) | Romaji | Meaning |")
    print("|---|---|---|---|")
    for i, (kana, rom, meaning) in enumerate(rows(), 1):
        print(f"| {i} | {kana.replace('　', ' ')} | {rom} | {meaning} |")


if __name__ == "__main__":
    main()
