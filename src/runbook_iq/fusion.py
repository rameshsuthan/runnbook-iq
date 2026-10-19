"""Rank fusion never adds incomparable raw model scores."""
from .schemas import Candidate


def fuse(ranked_lists: list[list[Candidate]], limit: int = 15) -> list[Candidate]:
    if not 1<=limit<=15:raise ValueError('Fusion limit must be between 1 and 15')
    records={}; scores={}; origins={}
    for candidates in ranked_lists:
        seen=set()
        for candidate in candidates:
            key=candidate.chunk.chunk_id
            if key in records and records[key]!=candidate.chunk:
                raise ValueError('Conflicting canonical records')
            records[key]=candidate.chunk
            if key in seen:continue
            seen.add(key)
            scores[key]=scores.get(key,0)+1/(60+candidate.rank)
            origins.setdefault(key,[]).extend(candidate.provenance)
    ordered=sorted(scores,key=lambda key:(-scores[key],key))[:limit]
    return [Candidate(chunk=records[key],method='fusion',rank=rank,
        scores={'fusion':scores[key]},provenance=origins[key]) for rank,key in enumerate(ordered,1)]
