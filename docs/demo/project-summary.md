# RunbookIQ — submission documentation draft

Copy this into your project Google Doc, adapt it to your own experience, and insert
your video link after recording. This draft has not been uploaded or submitted.

## Overview

RunbookIQ helps engineers answer documented troubleshooting questions about a
fictional order-processing service from synthetic runbooks, incident reports and
reference guides. Its local Streamlit interface returns cited evidence,
recommended checks and missing information. It cannot inspect a live incident or
perform remediation. The project uses Python, LangGraph, Pinecone and Gemini.

## Dataset and ingestion

I used nine original synthetic Markdown documents covering order-api architecture,
database pool waits, inventory dependency timeouts, two historical incidents,
configuration, error meanings, telemetry and triage. They contain no real
production records or credentials. The retained evaluation corpus has 21 canonical
chunks. Section-aware chunking targets 400 tokens and enforces the 2048-token
embedding bound. Canonical records preserve IDs, document/section metadata,
revision, text hashes and corpus version.

Explicit ingestion publishes to a dedicated Pinecone index with integrated
`llama-text-embed-v2` embeddings. Destination binding, a journal and freshness
checks prevent ordinary questions from using an incomplete synchronization.
There is no automatic refresh; questions and UI rerenders never ingest.

## Retrieval and generation decisions

The baseline uses dense retrieval. Optional Phase 2 profiles combine dense and
local BM25 results with Reciprocal Rank Fusion, rerank with
`bge-reranker-v2-m3`, and use one bounded Gemini call for at most two alternative
queries. All methods share the active canonical snapshot. Selection supplies at
most five chunks to Gemini `gemini-3.5-flash-lite` on the user-confirmed free tier.

LangGraph makes preparation, retrieval, selection, generation, validation and one
optional repair explicit. Application caches are separate from graph state.
Repair reuses the same question/evidence and can run once; SDK retries and paid
fallback are disabled. Nebius live acceptance is optional Phase 3, not part of
completed Phase 2 scope.

## Prompts and agent instructions

The answer prompt requires evidence-only claims, separates documented checks from
live diagnosis, requests exact source IDs inline, and permits abstention when the
requested fact is unavailable. The structured schema separates documented evidence,
recommended checks, missing information and citations. Expansion instructions
preserve identifiers, numbers and negation and prohibit adding diagnoses. Repair
receives the rejected response as untrusted data, the validation category and the
same selected evidence. Production prompt/schema versions for the final comparison
are `incident-evidence-v3` and `answer-v3`.

Prompts and schema are in `src/runbook_iq/providers.py`, `queries.py` and
`schemas.py`; deterministic validation is in `generation.py`. Citation validation
checks structure and IDs, not semantic entailment.

## Iterations and AI-assisted development

Codex helped translate an approved two-phase brief into small runnable milestones,
implement code, explain LangGraph concepts, diagnose failures and build regression
tests. Phase 1 first produced one cited answer from three documents, then expanded
to the nine-document corpus and fifteen fixed cases. Citation and telemetry-field
failures led to targeted prompt/schema work; failed experiments were retained.
Phase 2 added retrieval variants, accounting, bounded repair and inspection without
changing the answer prompt during retrieval comparisons. One independent branch
review identified three edge defects; six regression cases failed before the fixes
and passed afterward. The last application suite passed 135 tests.

## Evaluation and observations

All fifteen cases have been observed; these are regression experiments, not unseen
tests. Dense, hybrid, reranked hybrid and multi-query reranked hybrid each achieved
expected-section recall 1.0 on twelve answerable cases. This gives no measured
retrieval gain. The final resumed answer evaluation had nine answers and six
abstentions, with 12/15 frozen status matches. Counting first attempts gives 11/15
because one Pinecone search failed. Both attempts are preserved.

q08 incorrectly denied correlation fields present in selected evidence; q02 omitted
a cause caveat; q04/q11 returned conservative abstention statuses. One q15 response
used a real repair call successfully. These results show why relevance, citation
syntax, answer completeness and semantic support must be assessed separately.
The final experiment used 16 free-tier Gemini calls, 17,064 input tokens and 5,843
output tokens, with estimated chat cost USD0. This is not an account invoice or a
claim that hosted services have no resource consumption.

The persistent estimated paid-usage guard is USD3 across phases. Unknown usage
remains explicit, and Pinecone units are recorded separately. Credentials remain
local. Recorded live results predate the final edge-case fixes; an offline audit
confirmed all 15 cached query sets remain unchanged. No post-fix live rerun is claimed.

## Links and remaining work

- Code: https://github.com/rameshsuthan/runnbook-iq/tree/phase-2
- Architecture: `docs/architecture.md`
- Evaluation and source review: `eval/results/phase2-review.md`
- Independent code review: `docs/phase2-code-review.md`
- Demo: add your actual recording link after recording and checking access.

Remaining follow-ups are targeted answer-quality improvements and a visual UI
walkthrough. Production deployment/authentication and a semantic grading agent are
outside current scope. The demo assets and narration are prepared; the recording,
Google Doc publication and assignment submission still require completion.
