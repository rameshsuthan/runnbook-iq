from runbook_iq.config import Settings
from runbook_iq.schemas import Candidate
from test_ingestion import snapshot


def test_metrics_denominators_and_no_chat_calls():
    from runbook_iq.evaluation import EvaluationCase,evaluate
    cases=[EvaluationCase(id='one',split='dev',question='q',expected_status='answered',expected_sources=[{'document_id':'doc','section':'Checks'},{'document_id':'other','section':'Other'}],expected_points=['fact']),EvaluationCase(id='two',split='dev',question='unavailable',expected_status='insufficient_evidence',expected_sources=[],expected_points=[])]
    class Retriever:
        def search(self,*args):return [Candidate(chunk=snapshot().chunks[0],rank=1)]
    result=evaluate(cases,Retriever(),None,Settings())
    assert result['metrics']['answerable_cases']==1
    assert result['metrics']['hit_at_5']==1
    assert result['metrics']['macro_evidence_recall_at_5']==0.5
    assert result['cases'][0]['first_relevant_rank']==1
    assert result['cases'][1]['evidence_recall_at_5'] is None
    assert all(row['manual_review']=='unreviewed' and row['answer'] is None for row in result['cases'])


def test_full_corpus_and_frozen_questions():
    from runbook_iq.evaluation import load_cases,validate_cases
    from runbook_iq.corpus import build_corpus
    from pathlib import Path
    from test_corpus import Counter
    settings=Settings();snap=build_corpus(settings.source_dir,settings,Counter())
    cases=load_cases(Path('eval/questions.json'))
    assert len(snap.source_hashes)==9 and len(cases)==15
    assert sum(c.split=='heldout' for c in cases)==5
    validate_cases(cases,snap)


def test_answer_evaluation_uses_only_graph_retrieval(tmp_path):
    from runbook_iq.evaluation import EvaluationCase,evaluate
    from runbook_iq.graph import build_graph
    from runbook_iq.cache import AnswerCache
    from test_graph import Provider
    class ChangingRetriever:
        calls=0
        def search(self,*args):
            self.calls+=1
            return [Candidate(chunk=snapshot().chunks[0],rank=1)] if self.calls==1 else []
    retriever=ChangingRetriever()
    graph=build_graph(retriever,Provider(),AnswerCache(tmp_path/'c.db'),Settings(model='test'),'v1')
    case=EvaluationCase(id='one',split='dev',question='q',expected_status='answered',expected_sources=[{'document_id':'doc','section':'Checks'}],expected_points=['fact'])
    report=evaluate([case],retriever,lambda q,f:graph.invoke({'question':q,'filters':f})['result'],Settings())
    assert retriever.calls==1
    row=report['cases'][0]
    assert row['answer']['status']=='answered'
    assert row['retrieval'][0]['chunk']['chunk_id']==row['answer']['sources'][0]['chunk_id']
    assert row['selected_evidence']==row['answer']['selected_evidence']
