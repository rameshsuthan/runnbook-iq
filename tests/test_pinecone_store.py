from types import SimpleNamespace


def test_model_metadata_uses_keyword_only_sdk_contract():
    from runbook_iq.pinecone_store import describe_embedding_model
    class Inference:
        def get_model(self, *, model_name):
            assert model_name=='llama-text-embed-v2'
            return SimpleNamespace(to_dict=lambda:{'model':model_name})
    assert describe_embedding_model(SimpleNamespace(inference=Inference()),'llama-text-embed-v2')=={'model':'llama-text-embed-v2'}
