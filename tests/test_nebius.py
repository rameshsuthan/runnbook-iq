from decimal import Decimal
from types import SimpleNamespace
import pytest


def route(**overrides):
    from runbook_iq.config import ModelRoute
    values=dict(provider='nebius',model='offline-test-model',billing='paid',account_verified=True,pricing_verified=True,billable_bounds_verified=True,context_window_tokens=32000,max_output_tokens=100,input_usd_per_million=Decimal('1'),output_usd_per_million=Decimal('2'))
    return ModelRoute(**{**values,**overrides})

class Client:
    def __init__(self,error=False,usage=True):self.chat=SimpleNamespace(completions=self);self.error=error;self.usage=usage;self.calls=[]
    def create(self,**kwargs):
        self.calls.append(kwargs)
        if self.error:raise TimeoutError('private-secret')
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{}',refusal=None),finish_reason='stop')],usage=SimpleNamespace(prompt_tokens=10,completion_tokens=20,completion_tokens_details=SimpleNamespace(reasoning_tokens=5)) if self.usage else None)


def test_nebius_schema_and_usage_contract(tmp_path):
    from runbook_iq.nebius import NebiusProvider,maximum_request_cost
    from runbook_iq.budget import BudgetLedger
    r=route();c=Client();ledger=BudgetLedger(tmp_path/'usage',Decimal(3))
    result=NebiusProvider(r,ledger,c).generate('q',[])
    assert result.finish_reason=='STOP' and result.usage.output_tokens==20 and result.usage.reasoning_tokens==5
    assert result.usage.estimated_usd==Decimal('0.00005') and ledger.total()==Decimal('0.00005')
    assert maximum_request_cost(r)==Decimal('0.0322')
    assert c.calls[0]['response_format']['type']=='json_schema' and c.calls[0]['max_tokens']==100

@pytest.mark.parametrize('changes',[{'pricing_verified':False},{'billable_bounds_verified':False},{'context_window_tokens':None},{'input_usd_per_million':None},{'output_usd_per_million':Decimal('NaN')},{'model':''}])
def test_unverified_price_or_token_bounds_block_before_call(tmp_path,changes):
    from runbook_iq.nebius import NebiusProvider
    from runbook_iq.budget import BudgetLedger
    c=Client()
    with pytest.raises((ValueError,RuntimeError)):NebiusProvider(route(**changes),BudgetLedger(tmp_path/'u',Decimal(3)),c).generate('q',[])
    assert not c.calls


def test_unknown_outcome_retains_paid_reservation(tmp_path):
    from runbook_iq.nebius import NebiusProvider
    from runbook_iq.budget import BudgetLedger
    from runbook_iq.usage import CallFailure
    ledger=BudgetLedger(tmp_path/'u',Decimal(3))
    with pytest.raises(CallFailure):NebiusProvider(route(),ledger,Client(error=True)).generate('q',[])
    assert ledger.total()==Decimal('0.0322')
    result=NebiusProvider(route(),ledger,Client(usage=False)).generate('q',[])
    assert result.usage.estimated_usd is None and ledger.total()==Decimal('0.0644')


def test_independent_expansion_and_answer_routes():
    from runbook_iq.config import Settings,resolve_route
    s=Settings(model='gemini-test',expansion=route())
    assert resolve_route(s,'generate').provider=='gemini'
    assert resolve_route(s,'expand').provider=='nebius'


def test_nebius_secrets_do_not_enter_state_or_errors(tmp_path,monkeypatch):
    from runbook_iq.nebius import NebiusProvider
    from runbook_iq.budget import BudgetLedger
    from runbook_iq.config import credentials
    monkeypatch.setenv('PINECONE_API_KEY','unrelated-private')
    with pytest.raises(ValueError,match='NEBIUS_API_KEY'):credentials('nebius')
    with pytest.raises(RuntimeError) as e:NebiusProvider(route(),BudgetLedger(tmp_path/'u',Decimal(3)),Client(error=True)).generate('q',[])
    assert 'private' not in str(e.value)


def test_client_endpoint_retries_and_refusal(tmp_path,monkeypatch):
    import openai
    from runbook_iq.nebius import NebiusProvider,BASE_URL
    from runbook_iq.budget import BudgetLedger
    captured={}
    class Refused(Client):
        def create(self,**kwargs):
            raw=super().create(**kwargs);raw.choices[0].message.refusal='refused';raw.choices[0].message.content=None
            return raw
    def factory(**kwargs):captured.update(kwargs);return Refused()
    monkeypatch.setattr(openai,'OpenAI',factory);monkeypatch.setenv('NEBIUS_API_KEY','test-only')
    r=NebiusProvider(route(),BudgetLedger(tmp_path/'u',Decimal(3))).generate('q',[])
    assert captured['base_url']==BASE_URL and captured['max_retries']==0
    assert r.finish_reason=='REFUSAL' and r.text=='' and r.operation.attempted
