import pytest
from runbook_iq.config import Settings
from runbook_iq.schemas import Candidate
from test_ingestion import snapshot

class Search:
    def __init__(self):self.calls=[]
    def search(self,q,filters):
        self.calls.append((q,filters))
        return [Candidate(chunk=snapshot().chunks[0],rank=1,scores={'dense':.8})]


def pipeline(hybrid=True,verify=lambda:None):
    from runbook_iq.retrieval import RetrievalPipeline
    from runbook_iq.keyword import BM25Retriever
    s=Settings(hybrid=hybrid,model='test')
    dense=Search();snap=snapshot()
    return RetrievalPipeline(s,snap,dense,BM25Retriever(snap),verify_snapshot=verify),dense,s


def test_hybrid_graph_uses_both_methods_once(tmp_path):
    from runbook_iq.graph import build_graph
    from runbook_iq.cache import AnswerCache
    from test_graph import Provider
    p,d,s=pipeline();provider=Provider()
    result=build_graph(p,provider,AnswerCache(tmp_path/'cache'),s,'v1').invoke({'question':'evidence','filters':{}})['result']
    assert result.status=='answered' and len(d.calls)==1 and provider.calls==1
    assert {o.method for o in result.retrieved_candidates[0].provenance}=={'dense','keyword'}
    assert result.query_variants==['evidence']


def test_corpus_change_discards_entire_batch():
    calls=[]
    def verify():
        calls.append(1)
        if len(calls)>1:raise ValueError('Corpus changed')
    p,d,s=pipeline(verify=verify)
    from runbook_iq.usage import CallFailure
    with pytest.raises(CallFailure,match='snapshot'):p.retrieve(['evidence'],{})
    assert len(d.calls)==1


def test_dense_off_matches_baseline():
    p,d,s=pipeline(False)
    batch=p.retrieve(['q'],{})
    assert [(c.chunk.chunk_id,c.scores,c.rank) for c in batch.candidates]==[('c-v1',{'dense':.8},1)]
    assert p.select('q',batch).evidence==batch.candidates


def test_retrieval_mode_never_constructs_chat_provider(tmp_path):
    from runbook_iq.graph import build_graph
    p,d,s=pipeline()
    result=build_graph(p,None,None,s,'v1',mode='retrieval').invoke({'question':'evidence','filters':{}})['result']
    assert result.status=='retrieved' and result.answer is None and result.usage.calls==0
    assert result.selected_evidence and len(d.calls)==1


def test_pipeline_filters_bounds_and_error():
    p,d,s=pipeline()
    result=p.retrieve(['a','b','c'],{'service':'order-api'})
    assert len(result.candidates)<=15 and len(d.calls)==3
    assert all(f=={'service':'order-api'} for _,f in d.calls)
    with pytest.raises(ValueError):p.retrieve(['a']*4,{})
    with pytest.raises(ValueError):p.retrieve(['a'],{'diagnosis':'x'})
    def broken(*args):raise RuntimeError('failure')
    p.keyword.search=broken
    with pytest.raises(RuntimeError):p.retrieve(['q'],{})
