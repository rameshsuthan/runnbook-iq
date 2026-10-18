"""An explicit, bounded workflow: state is data; nodes return partial updates."""
import time
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from .budget import BudgetExceeded
from .cache import answer_cache_key
from .generation import validate_answer
from .schemas import Candidate, GeneratedAnswer, ProviderResponse, RunResult, Usage

class GraphState(TypedDict,total=False):
    question: str
    filters: dict[str,str]
    query_variants: list[str]
    candidates: list[Candidate]
    selected_evidence: list[Candidate]
    response: ProviderResponse
    result: RunResult
    status: str
    citations: list[str]
    errors: list[str]
    timings: dict[str,float]
    usage: Usage
    retrieval_retries: int
    generation_retries: int
    repair_retries: int
    path: list[str]
    cache_key: str


def build_graph(retriever,provider,cache,settings,corpus_version):
    def terminal(status,message=None,usage=None):
        return RunResult(status=status,provider=settings.provider,model=settings.model,
            errors=[message] if message else [],usage=usage or Usage(),corpus_version=corpus_version)
    def measured(name,fn):
        def node(state):
            start=time.perf_counter(); update=fn(state)
            path=[] if name=='prepare_request' else state.get('path',[])
            timings={} if name=='prepare_request' else state.get('timings',{})
            update['path']=[*path,name]
            update['timings']={**timings,name:time.perf_counter()-start}
            if 'result' in update:
                update['result'].retrieved_candidates=state.get('candidates',[])
                update['result'].selected_evidence=state.get('selected_evidence',[])
                update['result'].timings=update['timings']
                update['status']=update['result'].status
                update['errors']=update['result'].errors
                update['usage']=update['result'].usage
            return update
        return node
    def prepare(state):
        q=state.get('question',''); filters=state.get('filters',{})
        update={'candidates':[],'selected_evidence':[],'citations':[],'errors':[],
                'retrieval_retries':0,'generation_retries':0,'repair_retries':0}
        if not isinstance(q,str) or not q.strip() or len(q)>8000 or not isinstance(filters,dict) or not set(filters)<={'service','environment'} or not all(isinstance(v,str) and v.strip() for v in filters.values()):
            update['result']=terminal('invalid_request','Provide a nonempty question and explicit service/environment filters only')
        else:update.update(question=q.strip(),filters=filters)
        return update
    def queries(state):return {'query_variants':[state['question']]}
    def retrieve(state):
        try:return {'candidates':retriever.search(state['query_variants'][0],state['filters'])}
        except Exception:return {'result':terminal('retrieval_error','Retrieval failed; verify active corpus, input limits and Pinecone access')}
    def select(state):
        seen=set(); selected=[]
        for candidate in state['candidates']:
            if candidate.chunk.chunk_id not in seen:
                selected.append(candidate); seen.add(candidate.chunk.chunk_id)
        return {'selected_evidence':selected[:settings.top_k]}
    def fallback(state):
        result=terminal('insufficient_evidence')
        result.answer=GeneratedAnswer(status='insufficient_evidence',documented_evidence='',recommended_checks='',
            missing_information=['No matching source passages were found. Provide a documented service/question or additional source material.'],citations=[])
        return {'result':result}
    def generate(state):
        key=answer_cache_key(settings,state['question'],state['filters'],corpus_version,state['selected_evidence'])
        try:
            cached=cache.get(key)
            if cached:
                validate_answer(ProviderResponse(text=cached.answer.model_dump_json()),state['selected_evidence'])
                cached.cache_hit=True; cached.usage=Usage(calls=0,input_tokens=0,output_tokens=0,estimated_usd=0)
                return {'result':cached,'citations':cached.answer.citations}
            return {'response':provider.generate(state['question'],state['selected_evidence']),'cache_key':key}
        except BudgetExceeded:return {'result':terminal('budget_exceeded','Paid-usage budget guard blocked the request')}
        except Exception:return {'result':terminal('provider_error','Generation failed; check model/access/quota. No automatic retry.',Usage(calls=1))}
    def validate(state):
        response=state['response']
        try:
            answer=validate_answer(response,state['selected_evidence'])
            sources={c.chunk.chunk_id:c.chunk for c in state['selected_evidence']}
            result=terminal(answer.status,usage=response.usage); result.answer=answer
            result.sources=[sources[i] for i in answer.citations]
            cache.put(state['cache_key'],result)
            return {'result':result,'citations':answer.citations}
        except Exception:return {'result':terminal('invalid_output','Answer schema/citation validation failed; no repair attempted',response.usage)}
    graph=StateGraph(GraphState)
    nodes={'prepare_request':prepare,'prepare_queries':queries,'retrieve':retrieve,'select_evidence':select,'fallback':fallback,'generate':generate,'validate':validate}
    for name,fn in nodes.items():graph.add_node(name,measured(name,fn))
    graph.add_edge(START,'prepare_request')
    graph.add_conditional_edges('prepare_request',lambda s:END if s.get('result') else 'prepare_queries')
    graph.add_edge('prepare_queries','retrieve')
    graph.add_conditional_edges('retrieve',lambda s:END if s.get('result') else 'select_evidence')
    graph.add_conditional_edges('select_evidence',lambda s:'generate' if s['selected_evidence'] else 'fallback')
    graph.add_conditional_edges('generate',lambda s:END if s.get('result') else 'validate')
    graph.add_edge('fallback',END);graph.add_edge('validate',END)
    return graph.compile()
