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
