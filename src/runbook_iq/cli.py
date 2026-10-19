"""Explicit local commands. Ordinary questions never build or ingest a corpus."""
import argparse
import json
import os
from pathlib import Path
from .config import load_settings
from .corpus import build_corpus, read_snapshot, write_snapshot
from .tokenization import load_embedding_tokenizer, setup_tokenizer


def compose(settings,*,mode='answers'):
    from .ingestion import load_active_snapshot
    from .pinecone_store import PineconeStore
    from .retrieval import PineconeRetriever,RetrievalPipeline
    from .keyword import BM25Retriever
    from .budget import BudgetLedger
    from .cache import AnswerCache
    from .graph import build_graph
    from .providers import create_provider
    snapshot=load_active_snapshot(settings)
    dense=PineconeRetriever(settings,snapshot,PineconeStore(settings))
    reranker=None
    if settings.reranking:
        from .reranking import PineconeReranker
        from .quota import QuotaLedger
        reranker=PineconeReranker(settings,dense.client.pc.inference,QuotaLedger(settings.runtime_dir/'quotas.db'))
    retriever=RetrievalPipeline(settings,snapshot,dense,BM25Retriever(snapshot) if settings.hybrid else None,reranker)
    class LazyProvider:
        def generate(self,question,evidence):
            ledger=BudgetLedger(settings.runtime_dir/'usage.db',settings.budget_usd)
            return create_provider(settings,ledger).generate(question,evidence)
    graph=build_graph(retriever,LazyProvider() if mode=='answers' else None,AnswerCache(settings.runtime_dir/'answers.db') if mode=='answers' else None,settings,snapshot.version,mode=mode)
    return retriever,graph


def invoke_question(graph,question,filters,*,diagnostics_dir=None):
    from langsmith import tracing_context
    with tracing_context(enabled=False):
        state=graph.invoke({'question':question,'filters':filters},config={'recursion_limit':12})
    result=state['result']
    if diagnostics_dir is not None and result.status=='invalid_output' and 'response' in state:
        import sys
        import uuid
        record={'question':question,'provider':result.provider,'model':result.model,
                'corpus_version':result.corpus_version,'validation_error':result.validation_error,
                'response':state['response'].model_dump(mode='json'),
                'selected_evidence':[c.model_dump(mode='json') for c in state.get('selected_evidence',[])]}
        try:
            directory=Path(diagnostics_dir)
            directory.mkdir(parents=True,exist_ok=True,mode=0o700)
            path=directory/f'{uuid.uuid4().hex}.json'
            with open(path,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:
                json.dump(record,stream,indent=2)
            print(f'Invalid response saved locally: {path}',file=sys.stderr)
        except OSError:
            print('Could not save local diagnostic; original result is unchanged.',file=sys.stderr)
    return result


def output(value,path=None):
    if hasattr(value,'model_dump_json'):text=value.model_dump_json(indent=2)
    else:text=json.dumps(value,indent=2,default=str)
    if path:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text+'\n')
    print(text)


def main(argv=None):
    parser=argparse.ArgumentParser(description='RunbookIQ — synthetic evidence-based troubleshooting')
    parser.add_argument('--config',type=Path,default=Path('config.yaml'))
    sub=parser.add_subparsers(dest='command',required=True)
    doctor=sub.add_parser('doctor');doctor.add_argument('--offline',action='store_true');doctor.add_argument('--pinecone',action='store_true');doctor.add_argument('--gemini',action='store_true')
    sub.add_parser('tokenizer-setup')
    corpus=sub.add_parser('corpus');corpus.add_argument('action',choices=['build','inspect'])
    ingest=sub.add_parser('ingest');ingest.add_argument('--dry-run',action='store_true')
    for cmd in ('retrieve','ask'):
        p=sub.add_parser(cmd);p.add_argument('--question',required=True);p.add_argument('--service');p.add_argument('--environment');p.add_argument('--output',type=Path)
        if cmd=='ask':p.add_argument('--save-invalid-response',action='store_true',help='Opt in to private local raw-response/evidence files for validation failures')
    evaluation=sub.add_parser('evaluate');evaluation.add_argument('--mode',choices=['retrieval','answers'],required=True);evaluation.add_argument('--split',choices=['dev','heldout','all'],default='all');evaluation.add_argument('--output',type=Path,required=True);evaluation.add_argument('--pause-seconds',type=float,default=15)
    args=parser.parse_args(argv)
    try:
        settings=load_settings(args.config)
        if not (args.command=='doctor' and args.offline):
            from dotenv import load_dotenv
            load_dotenv(args.config.parent/'.env',override=False)
        if args.command=='doctor':
            report={'configuration':'valid','provider':settings.provider,'model':settings.model,
                'credentials':{name:'present' if os.getenv(name) else 'missing' for name in ['PINECONE_API_KEY','GEMINI_API_KEY','GOOGLE_API_KEY']},
                'billing':settings.billing,'live_verified':False}
            if args.pinecone:
                from pinecone import Pinecone
                from .config import credentials
                pc=Pinecone(api_key=credentials('pinecone'))
                from .pinecone_store import describe_embedding_model
                model=describe_embedding_model(pc,settings.embedding_model)
                report['pinecone']={'embedding_model':{k:model.get(k) for k in ('model','max_sequence_length','max_batch_size','supported_parameters')},'index_exists':pc.has_index(name=settings.index_name)}
            if args.gemini:
                from google import genai
                from .config import credentials
                client=genai.Client(api_key=credentials('gemini'),vertexai=False)
                report['gemini_models']=[m.name for m in client.models.list() if 'generateContent' in (m.supported_actions or []) and 'flash' in m.name]
                client.close()
            output(report);return 0
        if args.command=='tokenizer-setup':
            setup_tokenizer(settings);output({'tokenizer':'ready'});return 0
        if args.command=='corpus':
            if args.action=='build':
                snapshot=build_corpus(settings.source_dir,settings,load_embedding_tokenizer(settings));write_snapshot(snapshot,settings.processed_dir)
            else:snapshot=read_snapshot(settings.processed_dir/'candidate.json')
            output({'documents':len(snapshot.source_hashes),'chunks':len(snapshot.chunks),'corpus_version':snapshot.version});return 0
        if args.command=='ingest':
            from .ingestion import sync_corpus
            snapshot=read_snapshot(settings.processed_dir/'candidate.json')
            if args.dry_run:
                output({'candidate_documents':len(snapshot.source_hashes),'candidate_chunks':len(snapshot.chunks),'remote_calls':0});return 0
            from .pinecone_store import PineconeStore
            output(sync_corpus(snapshot,settings,PineconeStore(settings,create=True)));return 0
        if args.command=='evaluate':
            from .evaluation import load_cases,validate_cases,evaluate
            retriever,graph=compose(settings,mode=args.mode)
            cases=load_cases(Path('eval/questions.json'))
            validate_cases(cases,retriever.snapshot)
            cases=[c for c in cases if args.split=='all' or c.split==args.split]
            answer=(lambda q,f:invoke_question(graph,q,f)) if args.mode=='answers' else None
            report=evaluate(cases,retriever,answer,settings,output_path=args.output,pause_seconds=max(0,args.pause_seconds),retrieval_run=(lambda q,f:invoke_question(graph,q,f)) if args.mode=='retrieval' else None)
            output(report['metrics'])
            return 1 if report.get('stopped_reason') else 0
        filters={key:getattr(args,key) for key in ('service','environment') if getattr(args,key)}
        retriever,graph=compose(settings,mode='retrieval' if args.command=='retrieve' else 'answers')
        if args.command=='retrieve':
            result=invoke_question(graph,args.question,filters);output(result,args.output);return 0 if result.status=='retrieved' else 1
        result=invoke_question(graph,args.question,filters,diagnostics_dir=settings.runtime_dir/'diagnostics' if args.save_invalid_response else None);output(result,args.output)
        return 0 if result.status in ('answered','insufficient_evidence') else 1
    except Exception as error:
        # Do not expose provider exceptions (URLs/headers may contain credentials).
        output({'status':'setup_error','error_type':type(error).__name__,
                'message':'Command could not complete. Check local credentials, model/account settings, tokenizer and corpus/index readiness. No automatic retry.'})
        return 1
