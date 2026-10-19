import json
import stat
from runbook_iq.cli import invoke_question
from runbook_iq.schemas import ProviderResponse, Usage
from test_graph import Provider, Retriever, evidence, run


def test_invalid_response_saved_only_with_explicit_opt_in(tmp_path):
    class MissingInline(Provider):
        def generate(self,q,evidence):
            self.calls+=1
            return ProviderResponse(text=json.dumps({'status':'answered',
                'documented_evidence':'synthetic diagnostic fact','recommended_checks':'Check metrics',
                'missing_information':[], 'citations':['c-v1']}),usage=Usage(calls=1))
    provider=MissingInline()
    graph,_=run(tmp_path,provider,Retriever(evidence()))
    directory=tmp_path/'diagnostics'
    result=invoke_question(graph,'q',{})
    assert result.status=='invalid_output' and not directory.exists()
    result=invoke_question(graph,'q',{},diagnostics_dir=directory)
    files=list(directory.glob('*.json'))
    assert len(files)==1
    record=json.loads(files[0].read_text())
    assert record['validation_error']=='missing_inline_citations'
    assert record['response']['text'].find('synthetic diagnostic fact')>=0
    assert record['selected_evidence'][0]['chunk']['chunk_id']=='c-v1'
    assert set(record)=={'question','provider','model','corpus_version','validation_error','response','selected_evidence'}
    assert stat.S_IMODE(files[0].stat().st_mode)==0o600
    assert 'synthetic diagnostic fact' not in result.model_dump_json()


def test_successful_answer_does_not_create_invalid_diagnostic(tmp_path):
    graph,_=run(tmp_path,Provider(),Retriever(evidence()))
    directory=tmp_path/'diagnostics'
    result=invoke_question(graph,'q',{},diagnostics_dir=directory)
    assert result.status=='answered' and not directory.exists()
