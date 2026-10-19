from types import SimpleNamespace


def test_model_metadata_uses_keyword_only_sdk_contract():
    from runbook_iq.pinecone_store import describe_embedding_model
    class Inference:
        def get_model(self, *, model_name):
            assert model_name=='llama-text-embed-v2'
            return SimpleNamespace(to_dict=lambda:{'model':model_name})
    assert describe_embedding_model(SimpleNamespace(inference=Inference()),'llama-text-embed-v2')=={'model':'llama-text-embed-v2'}


def test_search_returns_usage_without_second_request(tmp_path):
    from runbook_iq.pinecone_store import PineconeStore
    from runbook_iq.config import Settings
    class Index:
        calls=0
        def search(self,**kwargs):
            self.calls+=1
            return {'result':{'hits':[{'_id':'one','_score':.5,'fields':{'text':'evidence'}}]},'usage':{'read_units':6,'embed_total_tokens':4}}
    store=object.__new__(PineconeStore);store.settings=Settings(runtime_dir=tmp_path);store.index=Index()
    hits,operation=store.search_with_usage('q',{},5)
    assert len(hits)==1 and store.index.calls==1
    assert operation.units=={'read_units':6,'embed_total_tokens':4}
    assert operation.attempted and operation.stage=='dense_search'
