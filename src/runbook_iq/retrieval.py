from typing import Protocol
from .ingestion import corpus_lock, load_active_snapshot, check_destination
from .schemas import Candidate
from .tokenization import load_embedding_tokenizer

class Retriever(Protocol):
    def search(self,query,filters)->list[Candidate]: ...

class PineconeRetriever:
    def __init__(self,settings,snapshot,client,counter=None):
        self.settings,self.snapshot,self.client=settings,snapshot,client
        self.counter=counter or load_embedding_tokenizer(settings)
    def search(self,query,filters):
        return self.search_with_usage(query,filters)[0]
    def search_with_usage(self,query,filters):
        if not set(filters)<= {'service','environment'}:raise ValueError('Only explicit service/environment filters are allowed')
        if self.counter.count(query)>self.settings.embedding_max_tokens:raise ValueError('Question exceeds embedding token bound')
        with corpus_lock(self.settings):
            check_destination(self.settings,self.client)
            active=load_active_snapshot(self.settings)
            if active.version!=self.snapshot.version:raise ValueError('Corpus changed; rebuild request context')
            records={c.chunk_id:c for c in active.chunks}
            if hasattr(self.client,'search_with_usage'):
                hits,operation=self.client.search_with_usage(query,filters,self.settings.top_k)
            else:
                from .schemas import OperationRecord
                hits=self.client.search(query,filters,self.settings.top_k)
                operation=OperationRecord(stage='dense_search',provider='pinecone',attempted=True)
            result=[]
            for rank,hit in enumerate(hits,1):
                chunk=records.get(hit['id'])
                if chunk is None or hit.get('text')!=chunk.text:continue
                if any(getattr(chunk,k)!=v for k,v in filters.items()):continue
                if hit.get('corpus_version',active.version)!=active.version:continue
                if hit.get('content_hash',chunk.content_hash)!=chunk.content_hash:continue
                result.append(Candidate(chunk=chunk,rank=rank,scores={'dense':hit['score']}))
            return result,operation


def retrieval_configuration(settings):
    return {'hybrid':settings.hybrid,'reranking':settings.reranking,'multi_query':settings.multi_query,
            'top_k':settings.top_k,'embedding':settings.embedding_model,'rrf_k':60,
            'keyword_version':'identifiers-v1','candidate_limit':15}


class RetrievalPipeline:
    def __init__(self,settings,snapshot,dense,keyword=None,reranker=None,verify_snapshot=None):
        self.settings,self.snapshot,self.dense=settings,snapshot,dense
        self.keyword,self.reranker=keyword,reranker
        if verify_snapshot is None and not isinstance(dense,PineconeRetriever):
            raise ValueError('A snapshot verifier is required')
        self.verify_snapshot=verify_snapshot or self._verify

    def _verify(self):
        with corpus_lock(self.settings):
            check_destination(self.settings,self.dense.client)
            if load_active_snapshot(self.settings).version!=self.snapshot.version:
                raise ValueError('Corpus changed; rebuild request context')

    def retrieve(self,queries,filters):
        from .schemas import RetrievalBatch,RetrievalOrigin
        from .fusion import fuse
        if not 1<=len(queries)<=3 or any(not isinstance(q,str) or not q.strip() for q in queries):
            raise ValueError('Use one to three nonempty queries')
        if not set(filters)<={'service','environment'}:raise ValueError('Unsupported filter')
        self.verify_snapshot()
        lists=[];operations=[]
        from .usage import CallFailure
        try:
            for index,query in enumerate(queries):
                methods=[('dense',self.dense)]
                if self.settings.hybrid:
                    if self.keyword is None:raise ValueError('Keyword retrieval is unavailable')
                    methods.append(('keyword',self.keyword))
                for method,search in methods:
                    candidates=[]
                    if hasattr(search,'search_with_usage'):
                        hits,operation=search.search_with_usage(query,filters)
                        operations.append(operation)
                    else:hits=search.search(query,filters)
                    for c in hits[:5]:
                        candidates.append(c.model_copy(update={'provenance':[RetrievalOrigin(
                            query_id=f'q{index}',method=method,rank=c.rank,score=c.scores[method])]}))
                    lists.append(candidates)
            self.verify_snapshot()
        except CallFailure as error:
            error.operations=[*operations,*error.operations]
            raise
        except Exception:
            error=CallFailure('Retrieval failed; verify snapshot, filters and service access')
            error.operations=operations
            raise error from None
        candidates=lists[0] if len(lists)==1 else fuse(lists)
        return RetrievalBatch(query_variants=queries,candidates=candidates,operations=operations)

    def select(self,question,batch):
        from .schemas import SelectionResult
        if self.settings.reranking:
            if self.reranker is None:raise ValueError('Reranker unavailable')
            return self.reranker.rerank(question,batch.candidates)
        seen=set();selected=[]
        for c in batch.candidates:
            if c.chunk.chunk_id not in seen:selected.append(c);seen.add(c.chunk.chunk_id)
        return SelectionResult(evidence=selected[:self.settings.top_k])

    def search(self,query,filters):
        return self.retrieve([query],filters).candidates[:5]
