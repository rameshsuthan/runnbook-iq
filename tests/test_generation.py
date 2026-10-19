import json
import pytest
from runbook_iq.schemas import ProviderResponse,Candidate
from test_ingestion import snapshot

@pytest.mark.parametrize('kind',['malformed','truncated','unmatched','missing_citation'])
def test_invalid_outputs_rejected(kind):
    from runbook_iq.generation import validate_answer
    body={'status':'answered','documented_evidence':'Fact [c-v1]','recommended_checks':'Check [c-v1]','missing_information':[],'citations':['c-v1']}
    if kind=='unmatched':body['citations']=[]
    if kind=='missing_citation':body.update(documented_evidence='Fact',recommended_checks='Check',citations=[])
    response=ProviderResponse(text='broken' if kind=='malformed' else json.dumps(body),finish_reason='MAX_TOKENS' if kind=='truncated' else 'STOP')
    with pytest.raises(ValueError):validate_answer(response,[Candidate(chunk=snapshot().chunks[0],rank=1)])

@pytest.mark.parametrize('second',['c-v2','unknown',''])
def test_grouped_citations_validate_each_identifier(second):
    from runbook_iq.generation import validate_answer
    first=snapshot().chunks[0]
    other=first.model_copy(update={'chunk_id':'c-v2'})
    body={'status':'answered','documented_evidence':f'Fact [c-v1, {second}]',
          'recommended_checks':'Check [c-v1]','missing_information':[],
          'citations':['c-v1','c-v2']}
    response=ProviderResponse(text=json.dumps(body))
    evidence=[Candidate(chunk=first,rank=1),Candidate(chunk=other,rank=2)]
    if second=='c-v2':
        assert validate_answer(response,evidence).citations==['c-v1','c-v2']
    else:
        with pytest.raises(ValueError):validate_answer(response,evidence)

@pytest.mark.parametrize('kind,expected',[
    ('schema','invalid_schema'),('finish','incomplete_response'),
    ('duplicate','duplicate_citations'),('unknown','unknown_citation'),
    ('no_inline','missing_inline_citations'),('mismatch','citation_mismatch'),
    ('no_checks','missing_answer_sections'),('abstention','missing_information'),
])
def test_validation_categories_do_not_echo_response(kind,expected):
    from runbook_iq.generation import validate_answer
    body={'status':'answered','documented_evidence':'Fact [c-v1]',
          'recommended_checks':'Check [c-v1]','missing_information':[], 'citations':['c-v1']}
    if kind=='duplicate':body['citations']=['c-v1','c-v1']
    if kind=='unknown':body.update(documented_evidence='Fact [unknown]',recommended_checks='Check [unknown]',citations=['unknown'])
    if kind=='no_inline':body.update(documented_evidence='Fact',recommended_checks='Check')
    if kind=='mismatch':body['citations']=[]
    if kind=='no_checks':body['recommended_checks']=''
    if kind=='abstention':body['status']='insufficient_evidence'
    response=ProviderResponse(text='private-sentinel' if kind=='schema' else json.dumps(body),finish_reason='MAX_TOKENS' if kind=='finish' else 'STOP')
    with pytest.raises(ValueError) as caught:
        validate_answer(response,[Candidate(chunk=snapshot().chunks[0],rank=1)])
    assert getattr(caught.value,'code',None)==expected
    assert 'private-sentinel' not in str(caught.value)
