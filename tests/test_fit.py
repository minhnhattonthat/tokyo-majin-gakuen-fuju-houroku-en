"""Every shipped English row fits its box (tools/fit.py) and passes the batch rules (tools/batches.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import fit  # noqa: E402


def test_fit_lint_clean():
    bad = fit.lint()
    assert not bad, '\n'.join(bad[:30])


def test_wrap_keeps_last_row_clear():
    rows = fit.read_script()
    text = 'All you can see is pitch-black darkness.'
    enc = fit.encoder(rows, [text])
    out = fit.wrap_dialogue('【Woman】', text, enc)
    assert out and out.count('{rt}') == 2
    assert not fit.problems({'id': 'B00.9999', 'kind': 'line', 'jp': '【女】{rt}あ'}, out, enc)
