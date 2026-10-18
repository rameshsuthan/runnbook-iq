# RunbookIQ Phase 1 design

Date: 2026-10-18 (America/Chicago). Status: user approved on 2026-10-18; implementation has not begun.

## Brief and scope

`RunbookIQ-Codex-Handoff.md` is the consolidated brief. Its two-phase direction is accepted. Build a local, evidence-based troubleshooting assistant for a fictional order-processing service, covering database connection-pool exhaustion and dependency timeouts. The user is learning AI engineering, particularly LangGraph. Explain each runnable increment and its failure paths.

Phase 1 delivers dense retrieval, cited answers, explicit failure/insufficient-evidence states, a minimal Streamlit UI, and a recorded 15-case baseline. Phase 2 retains the agreed BM25, RRF, reranking, query expansion, second provider, and bounded repair scope, but none is implemented now. No live-system access, remediation, deployment, authentication, or autonomous loops.

## Workspace and runtime

The initial workspace contains only the handoff, the assignment Markdown, and the reference solution Markdown. There is no Git repository, application, virtual environment, corpus, or `.env`. No applicable `AGENTS.md` was found in the workspace or its ancestor directories. The reference solution is not a source for code, prompts, corpus, or evaluation answers.

Machine: macOS ARM64. Python 3.12.15 is already installed through uv; Python 3.13.12 and 3.14.3 are also present. Target Python 3.12 in a project-local virtual environment; resolve and lock actual dependencies during setup. `uv 0.12.23` is installed. Its default cache is sandbox-restricted; use a writable project cache or `--no-cache`.

Use LangGraph, Pydantic, Pinecone's SDK, the native LangChain Gemini integration, a matching embedding tokenizer, pytest, and later Streamlit. Keep package choices small; verify SDK capabilities before pinning. The user selected **Gemini** for Phase 1. Nebius remains the intended second provider for Phase 2.

## Architecture

Offline: synthetic Markdown → section-aware token-bounded chunks → canonical JSONL and manifest → Pinecone integrated `llama-text-embed-v2` indexing.

Online: request → prepare original query → dense retrieval → deduplicate/select five passages → conditional fallback or Gemini generation → validate response/citation IDs → terminal result.

CLI and Streamlit call the same compiled graph. Ingestion is an explicit command, never a side effect of application startup or a question. Clients and credentials are supplied outside graph state. Local canonical records are also the future BM25 input.

### Stable contracts

| Contract | Fields / behavior |
|---|---|
| Chunk | Stable `chunk_id`, `document_id`, title, section, text, service, document type, revision/date, corpus version, content hash; optional explicit environment |
| Candidate | Chunk ID, text, metadata, retrieval method, 1-based rank, separate optional dense/keyword/fusion/reranker scores; future provenance can represent several methods |
| Generation input | Original question and selected evidence, independent of retrieval method |
| Answer | Status, documented evidence, recommended checks, missing information, cited chunk IDs, resolved source passages, provider/model, usage availability and timing |

Use validated models at external boundaries and a `TypedDict` for graph state. Canonical IDs derive from document identity, section, normalized content and relevant source metadata; do not include the global corpus version in chunk identity. The corpus version hashes the complete normalized source set and chunking configuration. Never treat a dense score as a probability or combine raw scores from different methods.

### Corpus and ingestion

The first three documents will be `svc-order-api` (architecture), `rb-db-pool` (connection-pool runbook), and `rb-dependency-timeouts` (dependency-timeout runbook). All are explicitly synthetic and describe the same fictional `order-api` service, PostgreSQL dependency, and `inventory-api` dependency. Establish shared configuration facts before writing questions.

Initial checkpoint question: “What documented checks distinguish database pool exhaustion from an inventory dependency timeout in order-api?” Expected sources are both runbooks, established before retrieval tuning. The answer must distinguish documented checks from a claim about a current incident.

Expand to nine documents: the first three, two historical incident reports, an error reference, a configuration reference, a triage guide, and a telemetry-field guide. Historical incidents have explicit dates and historical configuration; they never silently override current runbook instructions.

Split at Markdown headings and paragraph boundaries. Initial target: approximately 400 embedding-model tokens including citation headers, without overlap unless splitting a long section requires it. Verify the exact tokenizer, special-token overhead, and service maximum before ingestion; fail closed if this cannot be established. Preserve fenced code blocks; reject an individually oversized block with its source location and instructions to edit the source. Do not silently truncate documents or queries.

Use one project-owned index and dedicated namespace. Verify embedding model, field mapping, region and index ownership before writing. Record intended upserts/deletions in an ingestion journal. Unchanged ingestion makes no embedding/upsert calls. Changed ingestion updates the active corpus metadata and removes only obsolete IDs recorded in this project's previous manifest; never delete an entire shared index. Reconcile after interruption, and publish the local active manifest only after the intended remote state is verified. Block questions while ingestion is incomplete. Bound readiness/freshness polling and report timeout honestly.

Retrieved IDs and text must agree with the active canonical manifest. Reject unknown/stale records rather than supplying them to generation. Source passages shown to users come from that canonical snapshot.

## LangGraph behavior and learning checkpoints

State contains question, explicit filters, query variants, candidates, selected evidence, answer, citations, status, sanitized errors, per-node timings, usage, and separate counters reserved for retries/repair. Counters remain zero in Phase 1.

1. `prepare_request`: validate nonempty bounded input and allowlisted filters; initialize a fresh request state.
2. `prepare_queries`: return `[original_question]` only.
3. `retrieve`: search Pinecone for five candidates; apply only explicit service/environment filters. Service errors terminate as `retrieval_error`, not “no evidence.”
4. `select_evidence`: validate canonical membership, deduplicate IDs and retain up to five in rank order. Empty selection routes to deterministic `insufficient_evidence`, with no chat call.
5. `generate`: one bounded Gemini request, after cache and budget checks. Treat source text as untrusted evidence. The model may return `insufficient_evidence` even when retrieval found passages.
6. `validate`: check schema, allowed statuses, required answer sections, nonempty citations for an answered result, and agreement between inline references, citation lists and selected IDs. Resolve sources in application code. Malformed/truncated output or unknown IDs produces `invalid_output`; no repair call in Phase 1.
7. Terminal result: `answered`, `insufficient_evidence`, `invalid_request`, `retrieval_error`, `provider_error`, `invalid_output`, or `budget_exceeded`.

Every node returns explicit state updates; this sequential graph uses replacement semantics, avoiding accidental append/duplication on repeated invocations. Conditional edges choose terminal fallback/error paths. `END` ends execution; it does not certify grounding. SDK and application generation retries are disabled in Phase 1, so an ordinary uncached supported question makes at most one chat call. Tests assert termination and call counts. No persistent conversation memory or checkpointer is needed for single-question requests.

Teach state/nodes/edges with the first graph, compilation/invocation with the CLI, conditional routing with empty evidence, and the difference between citation validity and semantic grounding during evaluation. Valid IDs alone do not demonstrate that claims are supported.

## Provider, budget, privacy, and cache

Centralize model creation; implement one Gemini adapter with normalized text, structured output, errors and usage. Use Gemini Developer API explicitly, avoiding accidental Vertex/ambient-cloud credential selection. Exact model selection requires account access and current model documentation; prefer an eligible stable Flash/Flash-Lite model with structured output. Missing credentials should give setup instructions, never expose environment values.

The cross-phase estimated paid-usage guard is **USD 3**, with a **USD 1–2 target**. This guard is not yet configured or implemented. Default to verified free access and no paid fallback. Unknown account billing status or unknown model pricing blocks chargeable calls. Public availability of a free tier does not establish the user's eligibility. Never upgrade a provider plan automatically.

Persist usage and reservations in a local SQLite ledger shared across CLI/UI processes. Reserve a conservative maximum cost atomically before a paid request; reconcile known input/output/thinking tokens afterward. Unresolved requests after crashes/timeouts retain their reservation; unknown usage is explicitly unknown, never zero. Block further paid requests if reliable reconciliation or conservative bounding is impossible. Count all application model calls, including service probes; record Pinecone operations/quotas separately, and block paid Pinecone use unless its cost can be covered by the same guard. Provider billing and external account usage remain outside the application's guarantee.

Cache only validated completed generation results. Key by provider, exact model, generation parameters, prompt/schema version, question, filters, corpus version, retrieval settings, and ordered evidence IDs/content hashes. Report cache hits separately from uncached latency and current-call usage. Keep traces off by default. Secrets stay in the environment or ignored `.env`, never in Git, graph state, logs, screenshots, or reports. Commit `.env.example` with placeholders only.

## Files and extension boundaries

Use `src/runbook_iq/` modules for config/schemas, ingestion, Pinecone retrieval, providers/budget, generation/validation, graph, CLI, and evaluation. Add modules as used, not empty frameworks. Use `data/docs/` for sources, `data/processed/` for reproducible generated chunks/manifests, `eval/questions.json` for expectations, and `eval/results/` for sanitized actual evidence. Runtime ledgers, caches, secrets and generated local processing files are ignored by Git; source documents, tests, dependency lock and intentional evaluation reports are committed.

Phase 2 replaces query preparation, retrieval and evidence selection behind these contracts. Configuration flags for hybrid retrieval, reranking, multi-query and repair must raise a clear unsupported-feature error if enabled now. The generation contract and embedding index stay independent of chat-provider choice.

## Runnable milestone sequence

This is the design's delivery sequence; the task-level implementation plan follows written-spec review.

| Checkpoint | Deliverable | Acceptance evidence |
|---|---|---|
| M1: first cited answer | Safe configuration/budget boundary, three synthetic documents, canonical ingestion, Pinecone retrieval, Gemini adapter, CLI and LangGraph | Offline tests pass; real expected sources retrieved; one real cited answer inspected against passages; unchanged reingestion performs zero upserts; save sanitized result, settings and usage |
| M2: reliable baseline | Nine consistent documents, 15 fixed questions (10 development, 5 held out), failure-path tests | Expected facts/source sections recorded before tuning; empty evidence makes zero chat calls; invalid IDs/provider failures terminate explicitly; unsupported live example recorded |
| M3: inspectable UI | Local Streamlit form, status, rendered answer and expandable cited passages | Manual UI check; reruns do not automatically generate/index; each citation resolves to displayed evidence |
| M4: evaluation/package | Retrieval-first baseline, full-answer baseline, manual claim review, README and ≤5-minute demo outline | Fifteen actual records with failures; reproducible commands; configuration/corpus version; honest limitations and cost/latency report |

Ordinary tests use fakes and make no network or paid calls. Live integration commands are explicit and use the same budget guard. Freeze held-out cases before tuning; record any exposure. Define hit@5 as the fraction of answerable cases with any expected evidence in top five; evidence recall@5 as expected evidence units found divided by all expected units per answerable case, then macro-average. Match section-level expectations to canonical chunk IDs. Record first relevant rank, abstention/clarification, manual claim support and citation correctness separately. Unanswerable cases have no retrieval-miss denominator. Cache-hit timing is excluded from uncached latency summaries.

## Material prerequisites and review

- User selected Gemini, but no key is set in the current shell. Confirm account tier, accessible model, quota, current token rates/thinking controls, and structured-output behavior before a live call.
- Pinecone key, actual account plan/remaining allowance and index setup are unverified. Proposed Starter region is AWS `us-east-1`; confirm the account before creation.
- Resolve the exact embedding tokenizer/maximum during setup. Do not substitute a character limit or arbitrary tokenizer silently.
- Dependency compatibility will be established by the lock/install and imports under Python 3.12, not assumed from installed Python alone.

Self-review completed for scope, interfaces, failure paths, billing unknowns and acceptance evidence. This is a focused realization of the agreed brief, not a reopening of project direction. Written-spec approval is followed by a task-level plan and its required review before product implementation. No claim of live integration success is made.

## Documentation checked on 2026-10-18

- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api): state, node updates, edges and compilation.
- [Pinecone integrated model](https://docs.pinecone.io/models/llama-text-embed-v2) and [index creation](https://docs.pinecone.io/guides/index-data/create-an-index): integrated model field mapping and text upsert/search.
- [Pinecone pricing](https://www.pinecone.io/pricing/): public Starter region/allowances agree with the brief; account entitlements remain unverified.
- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) and [limits](https://ai.google.dev/gemini-api/docs/rate-limits): free access depends on model/tier; paid output pricing includes thinking tokens.
- [LangChain Gemini integration](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai): native integration reference for setup verification.
