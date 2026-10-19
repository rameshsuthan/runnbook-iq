import json
import pytest
from runbook_iq.config import Settings
from runbook_iq.schemas import ProviderResponse,Usage

class Provider:
    def __init__(self,text='{"alternatives":["pool checks","pool evidence"]}',error=None):self.calls=0;self.text=text;self.error=error
    def invoke_structured(self,*args,**kwargs):
        self.calls+=1
        if self.error:raise self.error
        return ProviderResponse(text=self.text,usage=Usage(calls=1,input_tokens=10,output_tokens=5,estimated_usd=0))


def preparer(tmp_path,provider,require=False):
    from runbook_iq.queries import QueryPreparer
    from runbook_iq.cache import ExpansionCache
    return QueryPreparer(Settings(model='m',multi_query=True),provider,ExpansionCache(tmp_path/'cache'),'v1',{'order-api'},require_cache=require)


def test_original_is_first_and_queries_are_bounded():
    from runbook_iq.queries import validate_alternatives
    assert validate_alternatives('pool',[' pool  ','pool checks','pool evidence'],set())==['pool','pool checks']

@pytest.mark.parametrize('removed',['not','500','order-api','DB_POOL_TIMEOUT'])
def test_codes_names_numbers_quotes_and_negation_survive(removed):
    from runbook_iq.queries import validate_alternatives
    q='order-api DB_POOL_TIMEOUT is not a leak at 500 ms'
    assert validate_alternatives(q,[q.replace(removed,'')],{'order-api'})==[q]
    assert validate_alternatives('Why slow?',['Why is there a database outage?'],set())==['Why slow?']
    assert validate_alternatives('Explain "foo"',['Explain bar'],set())==['Explain "foo"']


def test_expansion_failure_uses_original_and_preserves_usage(tmp_path):
    p=Provider('not json');plan=preparer(tmp_path,p).prepare('pool',{})
    assert plan.queries==['pool'] and plan.warnings and plan.operations[0].attempted
    assert plan.operations[0].usage.input_tokens==10


def test_expansion_cache_identity_and_no_call_on_hit(tmp_path):
    p=Provider();q=preparer(tmp_path,p)
    assert len(q.prepare('pool',{}).queries)==3
    cached=q.prepare('pool',{})
    assert p.calls==1 and cached.operations[0].status=='cache_hit'
    q.prepare('pool',{'service':'order-api'});assert p.calls==2
    from runbook_iq.queries import ExpansionCacheMiss
    with pytest.raises(ExpansionCacheMiss):preparer(tmp_path,p,True).prepare('different',{})


def test_dense_multiquery_fuses_without_keyword(tmp_path):
    from test_retrieval_pipeline import pipeline
    from runbook_iq.graph import build_graph
    from runbook_iq.cache import AnswerCache
    from test_graph import Provider as Answer
    p,d,s=pipeline(False);s.multi_query=True
    expand=Provider();answer=Answer()
    g=build_graph(p,answer,AnswerCache(tmp_path/'answers'),s,'v1',expander=preparer(tmp_path,expand))
    result=g.invoke({'question':'pool','filters':{}})['result']
    assert len(d.calls)==3 and len(result.query_variants)==3
    assert result.usage.calls==2 and answer.calls==expand.calls==1
    assert result.retrieved_candidates[0].method=='fusion'

@pytest.mark.parametrize('text',['{"alternatives":["a","b","c"]}','{"alternatives":["a"],"extra":1}'])
def test_expansion_schema_rejects_extra_or_excess(tmp_path,text):
    assert preparer(tmp_path,Provider(text)).prepare('pool',{}).queries==['pool']


def test_added_negation_and_overlong_variants_are_rejected():
    from runbook_iq.queries import validate_alternatives
    assert validate_alternatives('pool waits',['no pool waits','x'*8001],set())==['pool waits']


def test_budget_failure_retains_original(tmp_path):
    from runbook_iq.budget import BudgetExceeded
    result=preparer(tmp_path,Provider(error=BudgetExceeded('cap'))).prepare('pool',{})
    assert result.queries==['pool'] and result.warnings==['expansion_budget_blocked']
    assert result.operations==[]


@pytest.mark.parametrize('original,changed',[
    ('Explain DB_POOL_TIMEOUT','Explain DB_POOL_TIMEOUT.extra'),
    ('Check order-api','Check order-api-prod'),
    ('Explain 500 ms','Explain 500.7 ms'),
])
def test_expansion_rejects_extended_identifiers_and_numbers(original,changed):
    from runbook_iq.queries import validate_alternatives
    assert validate_alternatives(original,[changed],{'order-api'})==[original]
    # Sentence punctuation must not be confused with an identifier extension.
    safe=original+'; show documented checks.'
    assert validate_alternatives(original,[safe],{'order-api'})==[original,safe]


@pytest.mark.parametrize('required',[False,True])
def test_cached_expansion_rechecks_current_embedding_limit(tmp_path,required):
    from runbook_iq.queries import QueryPreparer,ExpansionCacheMiss
    from runbook_iq.cache import ExpansionCache
    class Counter:
        def count(self,text):return len(text.split())
    provider=Provider(json.dumps({'alternatives':['pool '+'detail '*450]}))
    settings=Settings(model='m',embedding_max_tokens=2048)
    cache=ExpansionCache(tmp_path/'cache')
    first=QueryPreparer(settings,provider,cache,'v1',set(),counter=Counter()).prepare('pool',{})
    assert len(first.queries)==2
    smaller=settings.model_copy(update={'embedding_max_tokens':400})
    preparer=QueryPreparer(smaller,provider,cache,'v1',set(),require_cache=required,counter=Counter())
    if required:
        with pytest.raises(ExpansionCacheMiss,match='token'):preparer.prepare('pool',{})
    else:
        result=preparer.prepare('pool',{})
        assert result.queries==['pool'] and result.warnings
        assert len(result.operations)==1 and not result.operations[0].attempted
    assert provider.calls==1
