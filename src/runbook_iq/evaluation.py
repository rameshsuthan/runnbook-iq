"""Frozen expected evidence, retrieval metrics and honest manual-review slots."""
import json
import time
from datetime import datetime,timezone
from pathlib import Path
from typing import Literal
from pydantic import Field
from .schemas import Record
from .corpus import digest

class EvaluationCase(Record):
    id: str
    split: Literal['dev','heldout']
    question: str
    filters: dict[str,str] = Field(default_factory=dict)
    expected_status: Literal['answered','insufficient_evidence']
    expected_sources: list[dict[str,str]]
    expected_points: list[str]
    expected_clarification: list[str] = Field(default_factory=list)

def load_cases(path):return [EvaluationCase.model_validate(c) for c in json.loads(Path(path).read_text())]

def validate_cases(cases,snapshot):
    if len({c.id for c in cases})!=len(cases):raise ValueError('Duplicate evaluation case IDs')
    available={(c.document_id,c.section) for c in snapshot.chunks}
    for case in cases:
        expected={(s['document_id'],s['section']) for s in case.expected_sources}
        if not expected<=available:raise ValueError(f'{case.id}: missing expected source section')
        if case.expected_status=='answered' and not expected:raise ValueError('Answerable cases require expected evidence')

def evaluate(cases,retrieve,answer,settings,*,output_path=None,pause_seconds=0,retrieval_run=None):
    rows=[];corpus_version=getattr(getattr(retrieve,'snapshot',None),'version',None)
    report={'created_at':datetime.now(timezone.utc).isoformat(),'mode':'answers' if answer else 'retrieval',
        'configuration':settings.model_dump(mode='json'),'corpus_version':corpus_version,
        'questions_hash':digest([c.model_dump() for c in cases]),'prompt_version':None,'cases':rows,'metrics':{}}
    from .providers import PROMPT_VERSION
    report['prompt_version']=PROMPT_VERSION
    for position,case in enumerate(cases):
        started=time.perf_counter();error=None
        result=answer(case.question,case.filters) if answer else (retrieval_run(case.question,case.filters) if retrieval_run else None)
        if result is not None:
            candidates=result.retrieved_candidates[:5]
            seconds=result.timings.get('retrieve')
            error='retrieval_error' if result.status=='retrieval_error' else None
        else:
            try:candidates=retrieve.search(case.question,case.filters)[:5]
            except Exception:candidates=[];error='retrieval_error'
            seconds=time.perf_counter()-started
        selected=result.selected_evidence if result else candidates
        pool=result.retrieved_candidates[:15] if result else candidates
        expected={(s['document_id'],s['section']) for s in case.expected_sources}
        actual=[(c.chunk.document_id,c.chunk.section) for c in candidates]
        hits=expected.intersection(actual)
        answerable=case.expected_status=='answered'
        selected_hits=expected.intersection((c.chunk.document_id,c.chunk.section) for c in selected[:5])
        pool_hits=expected.intersection((c.chunk.document_id,c.chunk.section) for c in pool)
        row={'case':case.model_dump(),'retrieval':[c.model_dump(mode='json') for c in candidates],
             'selected_evidence':[c.model_dump(mode='json') for c in result.selected_evidence] if result else None,
             'retrieval_seconds':seconds,'retrieval_error':error,
             'operations':[o.model_dump(mode='json') for o in result.operations] if result else [],
             'warnings':result.warnings if result else [],
             'query_variants':result.query_variants if result else [case.question],
             'retrieval_configuration':result.retrieval_configuration if result else {},
             'selected_hit_at_5':bool(selected_hits) if answerable else None,
             'selected_recall_at_5':len(selected_hits)/len(expected) if answerable and expected else None,
             'pool_recall_at_15':len(pool_hits)/len(expected) if answerable and expected else None,
             'candidate_pool':[c.model_dump(mode='json') for c in pool],
             'hit_at_5':bool(hits) if answerable else None,
             'evidence_recall_at_5':len(hits)/len(expected) if answerable and expected else None,
             'first_relevant_rank':next((i for i,pair in enumerate(actual,1) if pair in expected),None),
             'answer':result.model_dump(mode='json') if result and answer else None,'manual_review':'unreviewed'}
        rows.append(row)
        answerable_rows=[r for r in rows if r['hit_at_5'] is not None]
        report['metrics']={'answerable_cases':len(answerable_rows),
            'hit_at_5':sum(r['hit_at_5'] for r in answerable_rows)/len(answerable_rows) if answerable_rows else None,
            'macro_evidence_recall_at_5':sum(r['evidence_recall_at_5'] for r in answerable_rows)/len(answerable_rows) if answerable_rows else None,
            'recorded_cases':len(rows),'manual_grounding':'unreviewed'}
        for metric in ('selected_hit_at_5','selected_recall_at_5','pool_recall_at_15'):
            report['metrics'][metric]=sum(r[metric] for r in answerable_rows)/len(answerable_rows) if answerable_rows else None
        if output_path:
            from .corpus import atomic_write
            atomic_write(Path(output_path),json.dumps(report,indent=2))
            print(f"Recorded {case.id}: {result.status if result else 'retrieval'}",flush=True)
        if result and result.status in ('budget_exceeded','provider_error'):
            report['stopped_reason']=result.status
            break
        if result and any(w in result.warnings for w in ('expansion_provider_error','expansion_budget_blocked')):
            report['stopped_reason']='expansion_service_or_budget_failure'
            break
        if result and result.usage.calls and position+1<len(cases) and pause_seconds:time.sleep(pause_seconds)
    if output_path:
        from .corpus import atomic_write
        atomic_write(Path(output_path),json.dumps(report,indent=2))
    return report
