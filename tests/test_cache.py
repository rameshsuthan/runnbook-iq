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
