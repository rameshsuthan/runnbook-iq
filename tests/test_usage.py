import pytest
from decimal import Decimal
from runbook_iq.schemas import Usage


def op(usage,stage='generate',attempted=True):
    from runbook_iq.schemas import OperationRecord
    return OperationRecord(stage=stage,provider='gemini',model='m',status='ok',attempted=attempted,usage=usage)


def test_partial_usage_keeps_unknown_and_known_subtotal():
    from runbook_iq.usage import summarize_operations
    r=summarize_operations([op(Usage(calls=1,input_tokens=10,output_tokens=5,estimated_usd=Decimal('0'))),op(Usage(calls=1))])
    assert r['known_usage_subtotal'].input_tokens==10
    assert r['usage'].input_tokens is None and not r['usage_complete']
    assert r['usage'].calls==2


def test_reasoning_is_not_double_counted():
    from runbook_iq.usage import summarize_operations
    r=summarize_operations([op(Usage(input_tokens=10,output_tokens=20,reasoning_tokens=5,estimated_usd=0))])
    assert r['usage'].output_tokens==20 and r['usage'].reasoning_tokens==5


def test_setup_failure_counts_zero_attempts(tmp_path):
    from test_graph import run,Retriever,evidence
    class Provider:
        def generate(self,*args):raise ValueError('setup-private')
    _,s=run(tmp_path,Provider(),Retriever(evidence()))
    assert s['result'].usage.calls==0
    assert 'setup-private' not in s['result'].model_dump_json()


def test_answer_cache_does_not_erase_current_operations(tmp_path):
    from runbook_iq.graph import build_graph
    from runbook_iq.cache import AnswerCache
    from test_graph import Provider
    from test_retrieval_pipeline import pipeline
    p,d,s=pipeline()
    original=p.retrieve
    def retrieve(*args):
        b=original(*args)
        b.operations=[op(Usage(),stage='dense_search')]
        return b
    p.retrieve=retrieve
    g=build_graph(p,Provider(),AnswerCache(tmp_path/'c'),s,'v1')
    g.invoke({'question':'evidence','filters':{}})
    result=g.invoke({'question':'evidence','filters':{}})['result']
    assert result.cache_hit and result.usage.calls==0
    assert [r.stage for r in result.operations]==['dense_search','generate']
    assert result.operations[-1].status=='cache_hit'


def test_timeout_keeps_reservation(tmp_path):
    from runbook_iq.providers import GeminiProvider
    from runbook_iq.config import Settings
    from runbook_iq.budget import BudgetLedger
    from runbook_iq.usage import CallFailure
    class Client:
        def invoke(self,*args):raise TimeoutError('private-body')
    ledger=BudgetLedger(tmp_path/'usage',Decimal(3))
    p=GeminiProvider(Settings(model='m',billing='free',account_verified=True),ledger,Client())
    with pytest.raises(CallFailure) as e:p.generate('q',[])
    assert e.value.operation.attempted and e.value.operation.usage.calls==1
    assert 'private-body' not in str(e.value)
    with ledger.connect() as db:assert db.execute('select cost from requests').fetchone()[0] is None


def test_partial_retrieval_failure_preserves_earlier_operations(tmp_path):
    from test_retrieval_pipeline import pipeline
    from runbook_iq.usage import CallFailure
    p,d,s=pipeline()
    calls=[]
    def search(q,f):
        calls.append(q)
        record=op(Usage(),stage='dense_search')
        if len(calls)==2:raise CallFailure('network',record)
        return d.search(q,f),record
    d.search_with_usage=search
    with pytest.raises(CallFailure) as e:p.retrieve(['q1','q2'],{})
    assert len(e.value.operations)==2
