from pathlib import Path
import pytest
from runbook_iq.config import Settings

class Counter:
    def count(self, text): return len(text.split()) + 4


def source(root, body, doc='test'):
    root.mkdir(exist_ok=True)
    (root / f'{doc}.md').write_text(f'---\ndocument_id: {doc}\ntitle: Test\nservice: order-api\ndocument_type: runbook\nrevision: "2026-10-18"\n---\n# Synthetic\n\n{body}')


def test_stable_ids_and_partial_changes(tmp_path):
    from runbook_iq.corpus import build_corpus
    source(tmp_path, '## First\nCafé 東京\n\n## Second\nStable paragraph')
    a = build_corpus(tmp_path, Settings(), Counter())
    b = build_corpus(tmp_path, Settings(), Counter())
    assert a == b
    source(tmp_path, '## First\nChanged café 東京\n\n## Second\nStable paragraph')
    c = build_corpus(tmp_path, Settings(), Counter())
    assert a.version != c.version
    assert a.chunks[-1].chunk_id == c.chunks[-1].chunk_id
    assert a.chunks[0].chunk_id != c.chunks[0].chunk_id


def test_fences_and_roundtrip(tmp_path):
    from runbook_iq.corpus import build_corpus, write_snapshot, read_snapshot
    fence = '```sql\nSELECT 1;\n# not a heading\n```'
    source(tmp_path, '## Checks\n' + fence)
    snap = build_corpus(tmp_path, Settings(), Counter())
    assert fence in snap.chunks[0].text
    write_snapshot(snap, tmp_path / 'out')
    assert read_snapshot(tmp_path / 'out' / 'candidate.json') == snap


def test_oversized_fence_and_duplicate_ids(tmp_path):
    from runbook_iq.corpus import build_corpus
    source(tmp_path, '## Checks\n```\n' + 'big ' * 3000 + '\n```')
    with pytest.raises(ValueError, match='oversized'):
        build_corpus(tmp_path, Settings(), Counter())
    source(tmp_path, '## Checks\nsmall')
    (tmp_path / 'duplicate.md').write_text((tmp_path / 'test.md').read_text())
    with pytest.raises(ValueError, match='Duplicate'):
        build_corpus(tmp_path, Settings(), Counter())


def test_long_prose_preserved_and_bounded(tmp_path):
    from runbook_iq.corpus import build_corpus
    prose = ' '.join(f'unique{i}' for i in range(1000))
    source(tmp_path, '## Checks\n' + prose)
    snap = build_corpus(tmp_path, Settings(), Counter())
    assert len(snap.chunks) >= 3
    assert all(Counter().count(c.text) <= 400 for c in snap.chunks)
    for word in prose.split(): assert word in '\n'.join(c.text for c in snap.chunks)

@pytest.mark.parametrize('fence',[
    '   ```sql\n'+'word '*450+'\n   ```',
    '````markdown\n```\n'+'word '*450+'\n```\n````',
    '```sql\n'+'word '*450+'\n```',
],ids=['indented','longer-with-embedded','adjacent-to-prose'])
def test_all_valid_fences_preserved_and_oversized_rejected(tmp_path,fence):
    from runbook_iq.corpus import build_corpus
    source(tmp_path,'## Checks\nprose immediately before\n'+fence)
    with pytest.raises(ValueError,match='oversized'):
        build_corpus(tmp_path,Settings(embedding_max_tokens=400),Counter())
    small=fence.replace('word '*450,'SELECT 1;')
    source(tmp_path,'## Checks\nprose immediately before\n'+small)
    snap=build_corpus(tmp_path,Settings(),Counter())
    assert small.strip() in '\n'.join(c.text for c in snap.chunks)
