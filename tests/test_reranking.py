from types import SimpleNamespace
import pytest
from test_fusion import candidate
from runbook_iq.config import Settings

class Client:
    def __init__(self,data=None,error=False):self.calls=[];self.data=data;self.error=error
    def rerank(self,**kwargs):
        self.calls.append(kwargs)
        if self.error:raise RuntimeError('private-body')
        return {'data':self.data if self.data is not None else [{'index':1,'score':.9},{'index':0,'score':.1}], 'usage':{'rerank_units':1}}


def reranker(tmp_path,client):
    from runbook_iq.reranking import PineconeReranker
    from runbook_iq.quota import QuotaLedger
    return PineconeReranker(Settings(reranking=True),client,QuotaLedger(tmp_path/'q'))


def test_reranker_uses_original_query_and_canonical_text(tmp_path):
    c=Client();r=reranker(tmp_path,c);items=[candidate('a',1),candidate('b',2)]
    result=r.rerank('original',items)
    assert [v.chunk.chunk_id for v in result.evidence]==['b','a']
    assert c.calls[0]['query']=='original' and c.calls[0]['parameters']=={'truncate':'NONE'}
    assert c.calls[0]['rank_fields']==['text'] and c.calls[0]['top_n']==2
    assert c.calls[0]['documents'][0]=={'id':'a','text':items[0].chunk.text}
    assert result.operations[0].attempted

@pytest.mark.parametrize('data',[[{'index':0,'score':.2}]*2,[{'index':3,'score':.2},{'index':0,'score':.1}], [{'index':0,'score':float('nan')},{'index':1,'score':.1}],[]])
def test_reranker_rejects_duplicate_out_of_range_and_nonfinite(tmp_path,data):
    from runbook_iq.usage import CallFailure
    with pytest.raises(CallFailure):reranker(tmp_path,Client(data)).rerank('q',[candidate('a',1),candidate('b',2)])


def test_reranker_preserves_origins(tmp_path):
    items=[candidate('a',1),candidate('b',2)]
    result=reranker(tmp_path,Client()).rerank('q',items)
    assert result.evidence[0].provenance==items[1].provenance
    assert result.evidence[0].scores=={'dense':.8,'reranker':.9}
    assert 'reranker' not in items[1].scores


def test_empty_candidates_skip_call(tmp_path):
    c=Client();assert reranker(tmp_path,c).rerank('q',[]).evidence==[]
    assert c.calls==[]


def test_reranker_error_is_visible_without_fallback(tmp_path):
    from runbook_iq.usage import CallFailure
    c=Client(error=True)
    with pytest.raises(CallFailure) as e:reranker(tmp_path,c).rerank('q',[candidate('a',1)])
    assert len(c.calls)==1 and e.value.operation.attempted
    assert 'private-body' not in str(e.value)
