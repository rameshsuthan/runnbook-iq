"""Dedicated hosted reranking; returned text is never trusted as canonical."""
import math
import time
from .schemas import SelectionResult,OperationRecord
from .usage import CallFailure
from .quota import month
from .pinecone_store import plain

MODEL='bge-reranker-v2-m3'

class PineconeReranker:
    def __init__(self,settings,client,quota):self.settings,self.client,self.quota=settings,client,quota
    def rerank(self,question,candidates):
        if not candidates:return SelectionResult(evidence=[])
        if len(candidates)>15:raise ValueError('Reranking accepts at most 15 candidates')
        reservation=self.quota.reserve('rerank',1,self.settings.rerank_monthly_limit,month())
        operation=OperationRecord(stage='rerank',provider='pinecone',model=MODEL,attempted=True)
        started=time.perf_counter()
        try:
            raw=plain(self.client.rerank(model=MODEL,query=question,
                documents=[{'id':c.chunk.chunk_id,'text':c.chunk.text} for c in candidates],
                rank_fields=['text'],top_n=min(5,len(candidates)),return_documents=False,parameters={'truncate':'NONE'}))
            unit=raw.get('usage',{}).get('rerank_units')
            self.quota.settle(reservation,unit);operation.units={'rerank_units':unit}
            rows=raw['data'];seen=set();ranked=[]
            if len(rows)!=min(5,len(candidates)):raise ValueError('Incomplete reranking')
            for row in rows:
                row=plain(row);index=row['index'];score=row['score']
                if type(index) is not int or index in seen or not 0<=index<len(candidates) or not math.isfinite(score):
                    raise ValueError('Invalid reranking')
                seen.add(index)
                original=candidates[index]
                ranked.append(original.model_copy(update={'method':'reranker','scores':{**original.scores,'reranker':score}}))
            ranked.sort(key=lambda c:(-c.scores['reranker'],c.chunk.chunk_id))
            ranked=[c.model_copy(update={'rank':i}) for i,c in enumerate(ranked,1)]
            operation.elapsed_seconds=time.perf_counter()-started
            return SelectionResult(evidence=ranked,operations=[operation])
        except Exception:
            operation.status='error';operation.elapsed_seconds=time.perf_counter()-started
            raise CallFailure('Reranking failed; check access, quota, input limits and response mapping',operation) from None
