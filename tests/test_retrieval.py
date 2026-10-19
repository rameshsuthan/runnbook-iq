import pytest
from runbook_iq.config import Settings
from test_ingestion import snapshot,Store


def test_canonical_evidence_filters_and_stale_rejection(tmp_path):
    from runbook_iq.ingestion import sync_corpus
    from runbook_iq.retrieval import PineconeRetriever
    class SearchStore(Store):
        def search(self,query,filters,top_k):
            self.filters=filters
            return [{'id':'foreign','score':.99,'text':'foreign'}, {'id':'c-v1','score':.8,'text':'evidence'}]
    store=SearchStore(); s=Settings(processed_dir=tmp_path,readiness_attempts=1)
    snap=snapshot(); sync_corpus(snap,s,store)
    class Counter:
        def count(self,text):return len(text)
    r=PineconeRetriever(s,snap,store,counter=Counter())
    found=r.search('q',{'service':'order-api'})
    assert len(found)==1 and found[0].chunk.chunk_id=='c-v1'
    assert store.filters=={'service':'order-api'} and found[0].scores=={'dense':.8}
    with pytest.raises(ValueError):r.search('q',{'diagnosis':'pool'})
    with pytest.raises(ValueError):r.search('x'*3000,{})
    sync_corpus(snapshot('v2'),s,store)
    with pytest.raises(ValueError,match='changed'):r.search('q',{})


def test_malformed_canonical_hit_preserves_completed_search_usage(tmp_path):
    from runbook_iq.ingestion import sync_corpus
    from runbook_iq.retrieval import PineconeRetriever,RetrievalPipeline
    from runbook_iq.schemas import OperationRecord
    from runbook_iq.usage import CallFailure
    class SearchStore(Store):
        def search_with_usage(self,query,filters,top_k):
            operation=OperationRecord(stage='dense_search',provider='pinecone',attempted=True,
                units={'read_units':1,'embed_total_tokens':7})
            return [{'id':'c-v1','text':'evidence','score':.8 if query=='first' else 'private-invalid-score'}],operation
    class Counter:
        def count(self,text):return 1
    settings=Settings(processed_dir=tmp_path,readiness_attempts=1)
    store=SearchStore();snap=snapshot();sync_corpus(snap,settings,store)
    dense=PineconeRetriever(settings,snap,store,counter=Counter())
    pipeline=RetrievalPipeline(settings,snap,dense)
    with pytest.raises(CallFailure) as caught:pipeline.retrieve(['first','second'],{})
    operations=caught.value.operations
    assert len(operations)==2
    assert all(o.attempted and o.units=={'read_units':1,'embed_total_tokens':7} for o in operations)
    assert operations[-1].status=='error'
    assert 'private-invalid-score' not in str(caught.value)
