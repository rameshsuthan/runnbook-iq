# RunbookIQ — Codex project handoff

Prepared October 18, 2026. This is the consolidated project brief and phased plan from the planning conversation. It supersedes earlier suggestions to use Chroma, local embeddings, or to omit advanced retrieval entirely.

## 1. Current status and intent

Planning only: no application, repository, credentials, corpus, or working integration has been created or verified in this conversation. Do not imply otherwise. Inspect the new workspace for any work the user may have done separately.

The user is a backend engineer transitioning into AI engineering. Build an independently designed application and explain key decisions while implementing. LangGraph is an explicit learning requirement. The sample solution is architectural reference only; do not copy its code, prompts, corpus, or evaluation answers.

Project name: **RunbookIQ — Evidence-Based Incident Troubleshooting with RAG**.

Purpose: help an on-call engineer find documented troubleshooting checks and lessons from past incidents. The application answers from evidence, cites source passages, and states missing information. It does not inspect live systems, establish an actual root cause, or execute remediation.

Use a fictional order-processing service with two incident categories:
- Database connection-pool exhaustion.
- Dependency timeouts.

Start with 8–10 clearly labeled synthetic Markdown documents: runbooks, historical incidents, service architecture, and error/configuration references. Maintain consistent service names, configuration facts, dates, and incident timelines. Historical incident facts are not automatically current operating instructions.

## 2. Constraints and milestones

- User has roughly 4–6 focused hours for the initial session, with other commitments.
- Phase 1 estimate: 5–7 focused hours; deliver a useful runnable milestone first.
- Phase 2 estimate: another 7–11 hours. Estimates assume AI-assisted implementation and include learning; allow troubleshooting buffer.
- Preserve credits for other projects over the following four weeks.
- Proposed paid-model target: $1–$2, with a $3 application budget guard across both phases. This is a planning limit, not a guaranteed invoice ceiling or price estimate.
- Run locally. No deployment, authentication system, live observability connectors, automated remediation, or open-ended agent loops.
- Build incrementally and keep Phase 1 runnable while adding Phase 2 features.

Assignment context from the supplied Week 2 handout: choose a corpus, clean/chunk/embed/store/retrieve it, generate cited answers, and evaluate failures. Submission includes project documentation, code/assets, and a video of five minutes or less. The handout listed October 18, 2026 at 11:59 p.m. Pacific for Builder of the Week; later submissions remain accepted for certification. Verify the original handout if submission details matter.

## 3. Agreed stack

| Responsibility | Choice |
|---|---|
| Language | Python; select a compatible version after inspecting the machine |
| Workflow | LangGraph with explicit state and conditional fallback paths |
| Integrations | LangChain where useful; do not over-abstract |
| Embeddings | Pinecone integrated `llama-text-embed-v2` |
| Dense storage/search | Pinecone Starter, one project index, Starter-supported region |
| Keyword retrieval, Phase 2 | Local BM25 over exactly the same chunks |
| Rank fusion, Phase 2 | Reciprocal Rank Fusion (RRF) |
| Reranking, Phase 2 | Dedicated reranker; exact provider/model still to select |
| Chat models | Provider-independent interface; Nebius and Gemini intended |
| UI | Minimal local Streamlit |
| Evaluation | Python runner, JSON questions/results, manual grounding review |
| Version control | Git; GitHub for final assets if user sets it up |
| Configuration | Config file plus secret environment variables; `.env.example` only in Git |

Phase 1 verifies ONE chat provider. Default to Nebius if its credentials are ready; an eligible Gemini free-tier model is also acceptable. Ask one focused question if needed, then choose based on actual access. Do not block Phase 1 on supporting both.

Previously checked public Pinecone pricing listed Starter allowances of 2 GB storage, 1M read units/month, 2M write units/month, and 5M embedding tokens/month for `llama-text-embed-v2`. These are planning references, not verified account entitlements. Confirm current terms and the account's plan. Do not upgrade plans automatically. The user's accounts and promotional balances have not been inspected.

User-reported resources: Nebius $25, Fireworks $15, LangSmith $100, Tavily $25, Toloka $50, Tendem $50, Mem0 three-month starter, ChatGPT active, Pinecone free tier awaiting possible Builder upgrade. None of the optional services is required for Phase 1. Do not spend credits simply because available.

## 4. Architecture and stable contracts

Offline ingestion: Markdown -> section-aware chunks -> canonical local chunk records -> Pinecone integrated embedding/indexing. Phase 2 builds BM25 from those SAME records.

Online graph:
1. Prepare request.
2. Prepare query list.
3. Retrieve candidates.
4. Select evidence.
5. Branch: no evidence -> deterministic insufficient-evidence response; otherwise generate.
6. Generate cited answer.
7. Validate output structure and citation identifiers.
8. Return answer or explicit validation failure.

### Canonical chunk contract

Persist a local JSONL artifact containing stable chunk ID, document ID, title, section, text, service, document type, revision/date, and corpus version. Use deterministic IDs/content hashes. Repeated unchanged ingestion must not duplicate records. On changed documents, replace affected chunks and remove obsolete records within the project scope only.

Preserve metadata for citations and optional explicit filters. Split using the embedding model's tokenizer limits, leaving room for headers; do not silently truncate. Keep complete code blocks where possible, with documented handling when oversized. Initial chunk sizes are hypotheses to evaluate, not universal rules.

### Retrieval-result contract

Normalize each result to chunk ID, text, metadata, method, rank, and optional scores. Keep raw dense, keyword, fusion, and reranker scores distinct. Similarity scores are not confidence probabilities. Do not add incompatible raw scores together.

Use service/environment filters only when supplied explicitly or reliably established. Do not filter on an assumed diagnosis. Runbooks and postmortems may both be relevant.

### Generation contract

Input: original question and selected evidence, independent of retrieval method.
Output: status, answer, cited source/chunk IDs, missing information, provider/model, and available usage metadata.

Answer sections: relevant documented evidence, recommended checks, missing information, sources. Inline references should resolve to displayed passages. Do not claim a live diagnosis. Treat document text as evidence, not instructions that can override system behavior.

Citation-ID validation checks existence, not entailment. A real ID can still support the wrong claim. Assess actual claim grounding manually in Phase 1 evaluation. Do not equate retrieved passages with sufficient evidence: generation can still return insufficient evidence.

### LangGraph state

Keep original question, filters, query variants, candidates, selected evidence, answer, citations, status, errors, timing, usage, and separate retry counters where needed. Keep API clients/secrets outside state. Each node returns explicit state updates. Make retries bounded and test their termination.

## 5. Phase 1: complete baseline

| Milestone | Work | Acceptance evidence |
|---|---|---|
| P1.1 Setup | Inspect workspace; select dependencies; configure Pinecone and one model provider | One minimal service check per integration succeeds; no secrets logged |
| P1.2 Corpus | Draft/review 8–10 consistent synthetic documents and 15 questions | Expected source IDs established before retrieval tuning |
| P1.3 Ingestion | Section-aware splitting, stable records, integrated embeddings | Indexed records retrieved; unchanged reingestion is idempotent |
| P1.4 Graph | Dense retrieval, evidence selection, generation, validation, fallback | End-to-end cited answer and unsupported-question behavior |
| P1.5 UI | Streamlit question box, answer, source passages, status | User can inspect each citation |
| P1.6 Evaluate/package | Run baseline, analyze failures, write README and demo outline | Actual results saved with settings and limitations |

First runnable checkpoint: three documents -> one question -> correct evidence -> cited answer through LangGraph. Then complete the corpus and evaluation.

Phase 1 implementations: query preparation returns only the original question; retrieval searches Pinecone; selection deduplicates and takes top five. Model creation is centralized but only one provider needs live verification. Phase 2 switches must fail clearly if enabled before implementation, not silently do nothing.

Phase 1 definition of done:
- Documented question answered with inspectable supporting citations.
- Unsupported question receives appropriate fallback.
- Invalid citation IDs and provider failures surface clearly.
- README instructions reproduce the run in a configured environment.
- Fifteen baseline cases recorded, including failures; unverified behavior labeled.
- No reindexing on app startup or ordinary queries.

## 6. Phase 2: advanced features without replacing the app

1. Add local BM25 retrieval behind the existing retrieval contract. Use the canonical chunk file, including code/error identifiers in tokenization. Fuse dense and keyword ranks with RRF, deduplicating by chunk ID. Preserve retrieval provenance.
2. Add a dedicated reranker behind evidence selection. Check current model availability, free allowance, request limits, and required input format before choosing. Pinecone's included reranking is a candidate, not a finalized decision. Relevance ranking is not a grounding verifier.
3. Extend query preparation: one chat-model call generates up to two alternatives; original always retained. Validate and deduplicate rewrites; preserve error codes, names, and negation; do not invent a root cause. On failure, use original only.
4. Add and verify the second chat provider. Query expansion and answer generation have independently configurable provider/model choices.
5. Add one bounded response repair when output structure/citation IDs fail and budget permits. Retry exhaustion ends with an explicit error/unverified state, never forced success. Optional semantic grounding checks are a later experiment, not required to finish Phase 2.
6. Add retrieval feature switches and a small inspection view; run comparative evaluations.

Initial bounds: 3 total queries, 5 results per query per method, at most 15 fused candidates to rerank, final 4–5 evidence chunks. Tune against evaluation and model context budgets.

Expected normal chat calls with multi-query: one expansion + one answer. Embedding/search and reranking are separate operations with their own quotas. Failures/repairs can add calls; record them.

## 7. Provider portability and cost controls

- A small model factory builds LangChain provider clients; do not add a gateway service or complex plugin framework.
- Use native provider integrations or a documented compatible API for supported functionality. Verify current SDK parameters and model IDs; do not copy stale names.
- Normalize text, structured outputs, errors, and usage; missing usage is unknown, not zero.
- Keep embeddings independent: switching chat providers does not require reindexing. Switching embedding models does.
- Keep credentials in local environment variables and outside Git, traces, screenshots, or chat.
- Gemini free-tier eligibility/quotas depend on model/account. Confirm in AI Studio. Free-tier data policies matter before using real internal documents; this project uses synthetic data.
- Paid fallback disabled by default. Bound retries in ONE layer to avoid multiplicative retries.
- Persist cumulative estimated paid usage across restarts. Preflight expected cost where possible, include retry/repair calls, record actual tokens, and stop calls at the configured guard. Account for reasoning tokens when applicable. Explain that provider billing, concurrent requests, and unknown usage can limit accuracy; use provider caps when available.
- Cache with provider/model, prompt version, question, corpus version, retrieval settings, and evidence identity. Do not reuse stale answers after changes. Report uncached latency separately.
- Cache query expansions during retrieval experiments so configurations can be compared consistently.
- Do not enable paid calls with unknown pricing silently; resolve the selected model's rate or use verified free access.

## 8. Evaluation plan

Create 15 cases covering exact identifiers, paraphrases, similar symptoms/different causes, multi-document questions, ambiguity, and unavailable information. Each case should have an expected answerability status, supporting source IDs/sections, expected factual points, and expected clarification where relevant. Hold back a subset from tuning and document the small sample limitation.

Compare dense only; hybrid; hybrid+reranking; hybrid+reranking+multi-query. Keep corpus, test questions, embedding model, and evaluation criteria fixed. Never assume every added feature helps.

Metrics: document/evidence hit@5, recall@5 where multiple sources are required, rank of first relevant result, manual claim support/citation correctness, appropriate abstention/clarification, latency, chat calls, tokens, and estimated cost. Define denominators; do not treat unanswerable cases as retrieval misses by default. Verify citation IDs separately from semantic support.

Run retrieval-only evaluations first. Generate full answers at important milestones to save credit. Save configuration and corpus version with every result. Do not fabricate outcomes or equate a small synthetic evaluation with production readiness.

## 9. Suggested small repository layout

- `README.md`: setup, commands, design, limitations, demo instructions.
- `PROJECT_CONTEXT.md`: agreed decisions and current scope.
- `PROGRESS.md`: completed work, blockers, test evidence, next exact action.
- `config.yaml`, `.env.example`, `.gitignore`, dependency manifest/lock.
- `data/docs/`: synthetic source documents.
- `data/processed/`: canonical chunks/ingestion manifest; decide what is generated versus committed.
- `eval/questions.json`, `eval/results/`: expected evidence and actual runs.
- `src/runbook_iq/`: config/schemas, ingestion, retrieval, providers, graph, generation, evaluation.
- `app.py`: Streamlit entry point.
- `tests/`: meaningful checks for chunk IDs, fusion/deduplication, citation validation, fallback termination, and provider contract behavior as those features are added.

Keep files/modules proportional to the app; this is a suggested organization, not a reason to create empty abstractions. Separate service integration tests from offline tests; no chargeable calls in ordinary tests.

## 10. Reference kit lessons and originality

Reviewed document: `Enterprise Policy Q&A Bot (Langchain and LangGraph).md`. Its linked repository was NOT inspected or executed. The document describes LLM namespace routing, MiniLM dense retrieval, per-chunk LLM grading, generation, grounding checking, retries, provider switching, and 15 evaluation questions.

RunbookIQ differentiates through incident-specific evidence, hybrid retrieval, multi-query search, reranking, passage citations, explicit failure states, and controlled evaluation. Provider switching or LangGraph alone is not a novel improvement.

Avoid adopting the documented kit behaviors of forcing grounded status at retry exhaustion, silently keeping chunks on grader parse failure, or cutting evidence to arbitrary character lengths. Its described retry counter increments only at the checker, potentially failing to bound the earlier retrieval loop; this is a documentation concern, not a verified repository defect. Claims that graph or agentic approaches are inherently faster/cheaper are not reliable without measurements.

## 11. Open decisions to resolve just in time

1. Actual machine/OS, Python compatibility, existing workspace state.
2. Which chat provider is ready for Phase 1; exact currently available model and pricing.
3. Pinecone account tier, allowance, and supported index setup for integrated embedding.
4. Dedicated reranker for Phase 2.
5. Chunk/token limits and citation output schema validated with the chosen services.

Do not reopen agreed choices (LangGraph, two phases, incident domain, Pinecone embeddings, advanced Phase 2 requirements) without a concrete blocker. Current documentation and account availability may require a clearly explained adjustment.

## 12. Sources to verify during implementation

- Pinecone pricing: https://www.pinecone.io/pricing/
- Pinecone embedding model: https://docs.pinecone.io/models/llama-text-embed-v2
- LangChain model integrations: https://docs.langchain.com/oss/python/integrations/chat
- Nebius quickstart: https://docs.tokenfactory.nebius.com/quickstart
- Gemini pricing: https://ai.google.dev/gemini-api/docs/pricing
- Gemini limits: https://ai.google.dev/gemini-api/docs/rate-limits

Original assignment PDF: `Week 2 Project Handout ( Oct 2026 ).pdf`. Attach it if available. The solution-kit document is optional reference and is not needed to begin.

## 13. Opening prompt for the new Codex session

Read `RunbookIQ-Codex-Handoff.md` completely and treat it as our consolidated project brief. Inspect this workspace and applicable project instructions first. The scope and two-phase direction have already been discussed; do not restart broad brainstorming. Summarize your understanding, surface only material gaps, and prepare the concise Phase 1 design and implementation plan required by your workflow. Follow any necessary review gates, then implement Phase 1 in small runnable milestones. Do not implement Phase 2 features yet, but preserve the contracts described in the brief so Phase 2 can extend them. Explain LangGraph decisions as we go because learning is an explicit goal. Keep credentials private and paid usage within the configured guard. First target: three synthetic documents, Pinecone retrieval, and one cited answer through LangGraph. Record actual tests, unresolved issues, and the next action in `PROGRESS.md` at every major checkpoint. Never claim completion based on code generation alone.

## 14. Session continuation procedure

After each milestone update `PROGRESS.md` with: current phase, completed work, exact run/test commands, observed results, known failures, provider/model choices, estimated usage, and next action. Put lasting decisions in `PROJECT_CONTEXT.md`. Neither file should contain secrets.

Resume prompt: Read `PROJECT_CONTEXT.md`, `PROGRESS.md`, and this handoff. Inspect current code before changing it. Continue from the next unfinished milestone; preserve existing work and do not repeat completed setup or chargeable checks without a reason.
