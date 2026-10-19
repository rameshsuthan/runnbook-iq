import pytest
from test_ingestion import snapshot


def corpus(rows):
    snap=snapshot()
    template=snap.chunks[0]
    snap.chunks=[template.model_copy(update={'chunk_id':name,'title':'','section':'','text':text,'service':service}) for name,text,service in rows]
    return snap


def test_identifier_tokens_and_repeated_query_terms():
    from runbook_iq.keyword import tokenize,BM25Retriever
    assert tokenize('DB_POOL_TIMEOUT order-api db.pool') == ['db_pool_timeout','db','pool','timeout','order-api','order','api','db.pool','db','pool']
    assert tokenize('not pool_pool')==['not','pool_pool','pool']
    r=BM25Retriever(corpus([('a','pool pool wait','order-api'),('b','timeout','order-api')]))
    assert r.search('pool pool',{})==r.search('pool',{})
    assert r.search('pool',{})[0].chunk.chunk_id=='a'


def test_filter_before_top_five():
    from runbook_iq.keyword import BM25Retriever
    r=BM25Retriever(corpus([(str(i),'pool','other') for i in range(6)]+[('eligible','pool long document','order-api')]))
    assert [c.chunk.chunk_id for c in r.search('pool',{'service':'order-api'})]==['eligible']
    with pytest.raises(ValueError): r.search('pool',{'diagnosis':'leak'})


def test_no_overlap_is_empty():
    from runbook_iq.keyword import BM25Retriever
    assert BM25Retriever(corpus([('a','','order-api')])).search('pool',{})==[]
    assert BM25Retriever(corpus([])).search('pool',{})==[]
    assert BM25Retriever(corpus([('a','pool','order-api')])).search('xyz',{})==[]


def test_keyword_ties_have_stable_ids_and_limit():
    from runbook_iq.keyword import BM25Retriever
    r=BM25Retriever(corpus([(str(i),'pool','order-api') for i in reversed(range(7))]))
    assert [c.chunk.chunk_id for c in r.search('pool',{})]==['0','1','2','3','4']
