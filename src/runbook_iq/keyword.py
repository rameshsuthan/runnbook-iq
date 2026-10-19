"""Small deterministic BM25 index over the active canonical records."""
import math
import re
from collections import Counter
from .schemas import Candidate, RetrievalOrigin

TOKENIZER_VERSION = 'identifiers-v1'


def tokenize(text: str) -> list[str]:
    result=[]
    for token in re.findall(r'\w+(?:[-.]\w+)*', text.casefold()):
        result.extend(dict.fromkeys([token, *re.split(r'[_\-.]+',token)]))
    return result


class BM25Retriever:
    def __init__(self, snapshot):
        self.snapshot=snapshot
        self.records=sorted(snapshot.chunks,key=lambda c:c.chunk_id)
        self.terms=[Counter(tokenize(' '.join([c.title,c.section,c.text]))) for c in self.records]
        self.lengths=[sum(t.values()) for t in self.terms]
        self.average=sum(self.lengths)/len(self.lengths) if self.lengths else 0
        self.df=Counter(t for terms in self.terms for t in terms)

    def search(self, query, filters):
        if not set(filters)<={'service','environment'} or not all(isinstance(v,str) and v.strip() for v in filters.values()):
            raise ValueError('Only explicit service/environment filters are allowed')
        if not self.average:return []
        scored=[]
        for chunk,terms,length in zip(self.records,self.terms,self.lengths):
            if any(getattr(chunk,key)!=value for key,value in filters.items()):continue
            score=0.0
            for token in set(tokenize(query)):
                tf=terms[token]
                if not tf:continue
                idf=math.log(1+(len(self.records)-self.df[token]+.5)/(self.df[token]+.5))
                score+=idf*tf*2.5/(tf+1.5*(.25+.75*length/self.average))
            if score>0:scored.append((chunk,score))
        scored.sort(key=lambda pair:(-pair[1],pair[0].chunk_id))
        return [Candidate(chunk=chunk,method='keyword',rank=rank,scores={'keyword':score},
            provenance=[RetrievalOrigin(query_id='q0',method='keyword',rank=rank,score=score)])
            for rank,(chunk,score) in enumerate(scored[:5],1)]
