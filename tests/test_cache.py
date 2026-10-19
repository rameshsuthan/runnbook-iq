import pytest
from runbook_iq.config import Settings
from runbook_iq.schemas import RunResult, GeneratedAnswer


def test_cache_scope_and_invalid_results(tmp_path):
    from runbook_iq.cache import AnswerCache, answer_cache_key
    s=Settings(model='test')
    base=answer_cache_key(s,'q',{},'v1',[])
    assert base != answer_cache_key(s,'other',{},'v1',[])
    assert base != answer_cache_key(s,'q',{'service':'x'},'v1',[])
    assert base != answer_cache_key(s,'q',{},'v2',[])
    assert base != answer_cache_key(s.model_copy(update={'model':'other'}),'q',{},'v1',[])
    cache=AnswerCache(tmp_path/'c.db')
    with pytest.raises(ValueError): cache.put(base,RunResult(status='invalid_output'))
    result=RunResult(status='insufficient_evidence',answer=GeneratedAnswer(status='insufficient_evidence',documented_evidence='',recommended_checks='',missing_information=['Need evidence'],citations=[]))
    cache.put(base,result)
    assert cache.get(base)==result and cache.get('absent') is None


def test_effective_retrieval_queries_change_key():
    from runbook_iq.cache import answer_cache_key
    from runbook_iq.config import Settings
    from test_graph import evidence
    args=(Settings(model='m'),'q',{},'v1',evidence())
    first=answer_cache_key(*args,query_variants=['q'],retrieval_configuration={'hybrid':False})
    assert first!=answer_cache_key(*args,query_variants=['q'],retrieval_configuration={'hybrid':True})
    assert first!=answer_cache_key(*args,query_variants=['q','other'],retrieval_configuration={'hybrid':False})


def test_unset_context_bound_preserves_frozen_expansion_cache(tmp_path):
    from runbook_iq.config import resolve_route
    from runbook_iq.corpus import digest
    from runbook_iq.cache import ExpansionCache,expansion_cache_key
    settings=Settings(model='test')
    legacy_route=resolve_route(settings,'expand').model_dump(mode='json')
    legacy_route.pop('context_window_tokens')
    old_key=digest({'prompt':'query-expand-v1','schema':'alternatives-v1','question':'q','filters':{},'corpus_version':'v1','route':legacy_route})
    cache=ExpansionCache(tmp_path/'c');cache.put(old_key,['q','other'])
    assert cache.get(expansion_cache_key(settings,'q',{},'v1'))==['q','other']
