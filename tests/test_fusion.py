import pytest
from runbook_iq.schemas import Candidate
from test_ingestion import snapshot


def candidate(id,rank,method='dense',score=.8):
    from runbook_iq.schemas import RetrievalOrigin
    return Candidate(chunk=snapshot().chunks[0].model_copy(update={'chunk_id':id}),rank=rank,method=method,scores={method:score},provenance=[RetrievalOrigin(query_id='q0',method=method,rank=rank,score=score)])


def test_rrf_deduplicates_each_list_and_preserves_origins():
    from runbook_iq.fusion import fuse
    a=candidate('a',1); b=candidate('b',2)
    result=fuse([[a,a,b],[candidate('b',1,'keyword',10),candidate('a',2,'keyword',7)]])
    assert [c.chunk.chunk_id for c in result]==['a','b']
    assert result[0].scores['fusion']==pytest.approx(1/61+1/62)
    assert len(result[0].provenance)==2
    assert [p.score for p in result[0].provenance]==[.8,7]
    assert a.method=='dense' and 'fusion' not in a.scores


def test_legacy_candidate_loads():
    assert Candidate(chunk=snapshot().chunks[0],rank=1).provenance==[]


def test_fusion_bounds_and_rejects_conflicting_records():
    from runbook_iq.fusion import fuse
    assert len(fuse([[candidate(str(i),i+1) for i in range(20)]]))==15
    a=candidate('a',1)
    changed=a.model_copy(update={'chunk':a.chunk.model_copy(update={'text':'different'})})
    with pytest.raises(ValueError):fuse([[a],[changed]])
    assert fuse([])==[]
