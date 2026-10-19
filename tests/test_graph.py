import json
import pytest
from runbook_iq.config import Settings
from runbook_iq.schemas import Candidate,ProviderResponse,Usage
from test_ingestion import snapshot

class Retriever:
    def __init__(self,candidates=None,error=None):self.candidates=candidates or [];self.error=error
    def search(self,q,filters):
        if self.error:raise self.error
        return self.candidates
class Provider:
    def __init__(self,status='answered',citation='c-v1',error=None):self.calls=0;self.status=status;self.citation=citation;self.error=error
    def generate(self,q,evidence):
        self.calls+=1
        if self.error:raise self.error
        return ProviderResponse(text=json.dumps({'status':self.status,'documented_evidence':f'Documented fact [{self.citation}]' if self.status=='answered' else '', 'recommended_checks':f'Check metric [{self.citation}]' if self.status=='answered' else '', 'missing_information':['Live metrics'], 'citations':[self.citation] if self.status=='answered' else []}),usage=Usage(calls=1,input_tokens=10,output_tokens=20))

def run(tmp_path,provider,retriever,question='q'):
    from runbook_iq.graph import build_graph
    from runbook_iq.cache import AnswerCache
    graph=build_graph(retriever,provider,AnswerCache(tmp_path/'cache.db'),Settings(model='test'),'v1')
    return graph,graph.invoke({'question':question,'filters':{}})

def evidence():return [Candidate(chunk=snapshot().chunks[0],rank=1)]

def test_empty_evidence_skips_generation_and_terminates(tmp_path):
    p=Provider();_,state=run(tmp_path,p,Retriever())
    assert state['result'].status=='insufficient_evidence' and p.calls==0
    assert state['path']==['prepare_request','prepare_queries','retrieve','select_evidence','fallback']


def test_cited_answer_cache_and_fresh_state(tmp_path):
    p=Provider();g,state=run(tmp_path,p,Retriever(evidence()+evidence()))
    assert state['result'].status=='answered' and len(state['result'].sources)==1
    second=g.invoke({'question':'q','filters':{}})
    assert second['result'].cache_hit and second['result'].usage.calls==0 and p.calls==1
    assert len(second['candidates'])==2 and second['repair_retries']==0

@pytest.mark.parametrize('status',['answered','insufficient_evidence'])
def test_generator_can_abstain_with_nonempty_evidence(tmp_path,status):
    p=Provider(status=status);_,s=run(tmp_path,p,Retriever(evidence()))
    assert s['result'].status==status and p.calls==1


def test_invalid_citation_has_no_repair(tmp_path):
    p=Provider(citation='c-unknown');_,state=run(tmp_path,p,Retriever(evidence()))
    assert state['result'].status=='invalid_output' and p.calls==1

@pytest.mark.parametrize('failure,expected',[('retrieval','retrieval_error'),('provider','provider_error'),('budget','budget_exceeded')])
def test_failure_paths(tmp_path,failure,expected):
    from runbook_iq.budget import BudgetExceeded
    err=BudgetExceeded('limit') if failure=='budget' else RuntimeError('secret-sentinel')
    p=Provider(error=err if failure!='retrieval' else None)
    _,state=run(tmp_path,p,Retriever(evidence(),error=err if failure=='retrieval' else None))
    assert state['result'].status==expected
    assert 'secret-sentinel' not in state['result'].model_dump_json()
    assert p.calls<=1


def test_empty_question_no_calls(tmp_path):
    p=Provider();_,state=run(tmp_path,p,Retriever(evidence()),question='  ')
    assert state['result'].status=='invalid_request' and p.calls==0


def test_missing_inline_citations_are_reported_without_response_body(tmp_path):
    class MissingInline(Provider):
        def generate(self,q,evidence):
            self.calls+=1
            return ProviderResponse(text=json.dumps({'status':'answered',
                'documented_evidence':'private-sentinel','recommended_checks':'Check metrics',
                'missing_information':[], 'citations':['c-v1']}),usage=Usage(calls=1))
    provider=MissingInline();_,state=run(tmp_path,provider,Retriever(evidence()))
    result=state['result']
    assert result.status=='invalid_output' and provider.calls==1
    assert getattr(result,'validation_error',None)=='missing_inline_citations'
    assert 'private-sentinel' not in result.model_dump_json()
    assert state['path'][-1]=='validate'
