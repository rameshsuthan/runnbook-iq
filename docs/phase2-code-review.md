# Phase 2 independent code review

Reviewed range: `e15502e..f408c08`. One fresh read-only reviewer (gpt-6-astra),
following the approved Native execution plan; no implementer agents or re-review.
Independent suite:129 passed. Reviewer checked the five plan focus areas and
verified stored artifact hashes, status/token totals and operation counts.

Strengths: canonical batch checks, bounded BM25/RRF/reranking and repair, current
cache-operation metadata, and honest interrupted-evaluation reporting.
No Critical findings. Verdict before fixes: with fixes.

| Finding at reviewed revision | Severity and disposition | Verification |
|---|---|---|
| queries.py:28 accepted DB_POOL_TIMEOUT.extra, order-api-prod and500.7 as preserving shorter protected tokens. | Important; compare whole identifier/numeric tokens, preserving sentence punctuation. | Three literal regression cases RED→GREEN. |
| queries.py:44 cached alternatives bypassed changed embedding token limits. | Important; recheck current bounds. Required cache fails before search; ordinary mode uses original-only with warning, no model call. | Both modes RED→GREEN. |
| retrieval.py:36 dropped a completed search operation if canonical candidate construction failed. | Reviewer Minor, executor regraded Important because promised usage evidence was lost. Preserve operation/known units in safe CallFailure. | Two-search malformed-hit regression RED→GREEN. |

Full suite after fixes:135 passed in1.49s. CLI help, offline doctor and diff whitespace
checks passed. An offline required-cache replay with the pinned embedding tokenizer
kept all15 evaluated query sets unchanged, with zero API calls. Live artifacts retain
the original code hashes; there is no claim of a post-fix live evaluation.

Reviewer declined to judge, and executor retained with explicit limits:
- Nebius live compatibility/model/prices/bounds: user deferred; acceptance incomplete.
- q08 semantic fix/full semantic equivalence: no semantic judge in approved scope;
  factual failure retained and reported, lexical checks are not semantic proof.
- Account-wide Pinecone invoice ceiling/read-unit preflight bound: local monitoring
  does not establish other project usage or actual account balance.
- Browser appearance: AppTest coverage only; no native visual inspection claimed.
- Deployment/authentication/scaling: outside local synthetic project scope.

Deferred minors: none. All identified code findings were fixed in one test-first
pass; there was no second independent review. See [the execution record](phase2-execution-record.md) for rulings
and their consequences, and the evaluation source review for remaining quality gaps.
