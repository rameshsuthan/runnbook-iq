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
        if not set(filters)<= {'service','environment'}:raise ValueError('Only explicit service/environment filters are allowed')
        if self.counter.count(query)>self.settings.embedding_max_tokens:raise ValueError('Question exceeds embedding token bound')
        with corpus_lock(self.settings):
            check_destination(self.settings,self.client)
            active=load_active_snapshot(self.settings)
            if active.version!=self.snapshot.version:raise ValueError('Corpus changed; rebuild request context')
            records={c.chunk_id:c for c in active.chunks}
            hits=self.client.search(query,filters,self.settings.top_k)
            result=[]
            for rank,hit in enumerate(hits,1):
                chunk=records.get(hit['id'])
                if chunk is None or hit.get('text')!=chunk.text:continue
                if any(getattr(chunk,k)!=v for k,v in filters.items()):continue
                if hit.get('corpus_version',active.version)!=active.version:continue
                if hit.get('content_hash',chunk.content_hash)!=chunk.content_hash:continue
                result.append(Candidate(chunk=chunk,rank=rank,scores={'dense':hit['score']}))
            return result
