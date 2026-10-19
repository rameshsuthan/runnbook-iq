import pytest
from runbook_iq.config import Settings
from runbook_iq.schemas import ProviderResponse,Usage
from test_graph import Provider,Retriever,evidence

class Sequence(Provider):
    def __init__(self,valid=True,error=None):super().__init__();self.valid=valid;self.error=error;self.repairs=0
    def generate(self,q,items):
        self.original=(q,items);self.calls+=1
        return ProviderResponse(text='{}',usage=Usage(calls=1,input_tokens=3,output_tokens=2,estimated_usd=0))
    def repair(self,q,items,rejected,validation_error):
        self.repairs+=1
        assert (q,items)==self.original and rejected.text=='{}' and validation_error=='invalid_schema'
        if self.error:raise self.error
        if self.valid:return Provider.generate(self,q,items)
        self.calls+=1;return ProviderResponse(text='{}',usage=Usage(calls=1,input_tokens=3,output_tokens=2,estimated_usd=0))


def run(tmp_path,provider,expander=None):
    from runbook_iq.graph import build_graph
    from runbook_iq.cache import AnswerCache
    settings=Settings(model='test',repair=True,multi_query=expander is not None)
    graph=build_graph(Retriever(evidence()),provider,AnswerCache(tmp_path/'c'),settings,'v1',expander=expander)
    return graph,graph.invoke({'question':'q','filters':{}},config={'recursion_limit':16})


def test_invalid_then_valid_repairs_once(tmp_path):
    p=Sequence();g,s=run(tmp_path,p)
    assert s['result'].status=='answered' and s['result'].repair_attempts==1
    assert s['path'].count('validate')==2 and s['path'].count('retrieve')==1
    assert s['path'].count('prepare_queries')==1 and s['result'].usage.calls==2
    again=g.invoke({'question':'q','filters':{}})['result']
    assert again.cache_hit and again.usage.calls==0 and again.repair_attempts==0


def test_invalid_twice_terminates(tmp_path):
    p=Sequence(False);_,s=run(tmp_path,p)
    assert s['result'].status=='invalid_output' and p.calls==2 and p.repairs==1
    assert s['path'].count('validate')==2


def test_repair_budget_denied_preserves_first_error(tmp_path):
    from runbook_iq.budget import BudgetExceeded
    _,s=run(tmp_path,Sequence(error=BudgetExceeded('cap')))
    assert s['result'].status=='budget_exceeded' and s['result'].validation_error=='invalid_schema'
    assert s['result'].usage.calls==1


def test_provider_failure_does_not_repair(tmp_path):
    from runbook_iq.usage import CallFailure
    p=Provider(error=CallFailure('safe'));_,s=run(tmp_path,p)
    assert s['result'].status=='provider_error' and s['result'].repair_attempts==0


def test_invalid_cache_never_invokes_repair(tmp_path):
    from runbook_iq.cache import AnswerCache,answer_cache_key
    from runbook_iq.schemas import RunResult,GeneratedAnswer
    settings=Settings(model='test',repair=True)
    old=GeneratedAnswer(status='answered',documented_evidence='uncited',recommended_checks='uncited',citations=['c-v1'],missing_information=[])
    AnswerCache(tmp_path/'c').put(answer_cache_key(settings,'q',{},'v1',evidence()),RunResult(status='answered',answer=old))
    p=Sequence();_,s=run(tmp_path,p)
    assert s['result'].status=='invalid_output' and p.repairs==p.calls==0


def test_expansion_answer_repair_maximum_three_calls(tmp_path):
    from runbook_iq.schemas import QueryPlan,OperationRecord
    class Expander:
        def prepare(self,q,f):return QueryPlan(queries=[q],operations=[OperationRecord(stage='expand',attempted=True,usage=Usage(calls=1,input_tokens=5,output_tokens=3,estimated_usd=0))])
    p=Sequence();_,s=run(tmp_path,p,Expander())
    assert s['result'].usage.calls==3 and s['result'].repair_attempts==1
