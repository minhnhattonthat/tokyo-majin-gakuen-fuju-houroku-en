"""Phase 7 text lint over the merged script (not just batches): control-code multiset JP == EN, encodable
characters, no ordinal after a variable, honorifics kept. `batches.py check` runs the same rules per batch, but hand
edits after merge (review passes) never go through it: one dropped a {I000} from CF3C40."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import batches  # noqa: E402


def test_merged_rows_pass_batch_rules():
    bad = []
    for rid, r in batches.read_rows().items():
        en = r.get('en') or ''
        if not en or r.get('kind') == 'grid':
            continue
        # dialogue: merge added the speaker prefix and {rt} wraps; check the body as a batch would hold it
        text = batches.body(en)[1].replace('{rt}', ' ') if batches.is_dialogue(r) else en
        bad += ['%s: %s' % (rid, p) for p in batches.problems(r, text, [])]
    assert not bad, '\n'.join(bad[:40])
