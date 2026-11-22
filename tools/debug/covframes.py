"""covframes.py: first frame each string id was drawn in one coverage run (to pick the shot to check).

    python -X utf8 tools/debug/covframes.py RUN_NAME ID [ID ..]     (RUN_NAME: a dir under work/qa/cover)

Maps ids to the build addresses through work/qa/cover/strings.tsv and reads the run's log.txt (TEXT <addr> f<frame>).
Prints `id frame nearest-shot` (the first shot at or after that frame).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COVER = ROOT / "work" / "qa" / "cover"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    run = COVER / argv[0]
    addr = {}
    for line in (COVER / "strings.tsv").read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            addr[parts[0]] = parts[1].upper()
    first = {}
    for line in (run / "log.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] == "TEXT":
            a, f = parts[1].upper(), int(parts[2][1:])
            first.setdefault(a, f)
    shots = sorted(int(p.stem[1:]) for p in run.glob("f*.png") if p.stem[1:].isdigit())
    for sid in argv[1:]:
        a = addr.get(sid)
        f = first.get(a) if a else None
        shot = next((s for s in shots if f is not None and s >= f), None)
        print(sid, f if f is not None else "-", f"f{shot:06d}.png" if shot is not None else "-")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
