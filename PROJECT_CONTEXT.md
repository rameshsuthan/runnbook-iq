# RunbookIQ project context

Updated: 2026-10-18 (America/Chicago).

## Current continuation

The user explicitly authorized pushing history and starting next steps. Phase 1
through `e15502e` is published on `origin/phase-1`; remote SHA was verified.
`phase-2` branches from that baseline. The user approved the written
[Phase 2 design](docs/superpowers/specs/2026-10-18-phase-2-design.md) and requested
proceeding. The [implementation plan](docs/superpowers/plans/2026-10-18-phase-2.md)
is approved; Gemini milestones are implemented and independently reviewed.
Native execution remains selected; do not request the execution method again.
Earlier no-push statements and Phase 1 exclusions below describe prior checkpoints.

First implementation milestone: local BM25 on the active canonical snapshot, RRF with
separate per-query/method provenance, then one cited graph answer. No re-embedding
is needed. Subsequent milestones add Starter-compatible BGE reranking, query
expansion, Nebius, bounded repair and comparative inspection/evaluation. Public
reranker terms were checked; actual access and Nebius model/rates remain live-use
prerequisites. Preserve the existing USD 3 ledger and all frozen evaluation history.

User confirmed Nebius is **not ready** and instructed continuing with Gemini.
Use Gemini for upcoming answer, expansion and repair milestones. Defer Nebius
live verification until readiness changes; preserve its provider interface and
record second-provider acceptance as incomplete. The readiness reply was separate
from the subsequent explicit written-design approval.

The implementation plan has nine tasks. Tasks 1–2 deliver the first hybrid answer;
usage accounting precedes additional model calls, and Gemini repair work precedes
Nebius live acceptance. Task 7 may deliver an offline-tested adapter, but no Nebius
call is allowed until account/model/rate/bound prerequisites are verified. Finish
with one independent whole-branch review under the selected Native workflow.

## Phase 2 implementation checkpoints

- Tasks 1–6 and 8 are implemented and committed: canonical BM25/RRF, dedicated
  BGE reranking, bounded cached Gemini expansion, per-operation accounting, one
  repair edge, and Streamlit inspection. Default feature switches remain off.
- All four fixed retrieval arms retain full expected-section recall on the 12
  answerable cases. This is no measured recall gain; all 15 cases were seen before.
- Task 7's Nebius adapter is offline-tested; no Nebius calls or paid fallback are
  enabled. Verified account/model/rates/enforced billable bounds remain prerequisites.
- Pinecone SDK 8 retries are disabled before lazy transport creation using pinned
  private configuration; actual transport tests guard dependency upgrades.
- Cache hits retain current request work; unknown usage stays unknown. Pinecone
  units are separate from chat dollars. Local counters are not account balances.
- Expansion preserves the original query and guarded identifiers/numbers/negation.
  Guards are lexical, not semantic proof; punctuation-only alternatives may survive.
- Task 9 adds code/rubric hashes and separate composition/request latency. Existing
  Gemini expansion keys omit an unset optional context bound for compatibility.
- Final evaluation stopped at q06 on a Pinecone search error. Preserve the partial
  artifact; one explicit bounded continuation starts at q06 with cached expansions.
  Do not classify its cause from the generic saved error. q06 succeeded on continuation.
- Final source review already found q08 falsely denying documented correlation
  fields despite correct selected evidence. Keep this failure; no answer tuning.
- Continuation completed:9 answers/6 abstentions,12/15 frozen status matches; q15
  used one real repair. Final evaluation used16 free-tier calls,estimated USD0.
  Detailed source review and first-attempt failure metrics are retained.
- Independent review found three edge defects; all fixed with six RED→GREEN
  regressions. Full suite135 passes. Offline replay preserves all15 cached queries.
  Final code was not rerun live; original evaluated code hashes remain recorded.
- Reviewed implementation4cab6fc is published on origin/phase-2; origin/phase-1
  remains e15502e. Execution/review records are archived under docs/.
- Next action is Nebius live acceptance only after the user reports readiness and
  model/rates/enforced token bounds are verified. Until then Gemini stays active.
  Full Phase2 acceptance is incomplete; q08 remains a separate quality limitation.

## Authority and accepted direction

`RunbookIQ-Codex-Handoff.md` is the consolidated brief. The two-phase direction, LangGraph learning requirement, Pinecone integrated embeddings, fictional incident domain and advanced Phase 2 scope are agreed. Do not restart broad brainstorming or copy the reference solution's implementation, prompts, corpus or answers.

Build a local evidence-based troubleshooting assistant for database pool exhaustion and dependency timeouts. It recommends documented checks and identifies missing information; it cannot diagnose a live system or execute remediation.

## Decisions

- User selected **Gemini** as the Phase 1 chat provider on 2026-10-18. Nebius is deferred to Phase 2. Verified route: Gemini Developer API `gemini-3.5-flash-lite`, user-confirmed free tier; live generation succeeded. The listed 2.5 Flash-Lite model returned 404 and is not used.
- Keep Python, LangGraph, Pinecone integrated `llama-text-embed-v2`, and minimal Streamlit. Python 3.12.15; dependencies resolved and locked with uv.
- Canonical local chunk records drive Pinecone now and BM25 later. Preserve IDs, citation metadata, corpus versions and separate retrieval scores.
- Phase 1: original query only, dense retrieval, deduplicated top five, one generation call, citation/schema validation, explicit fallback and errors. No response repair or automatic model retries.
- Phase 2 interfaces remain, but BM25/RRF, reranking, query expansion, second-provider implementation and bounded repair are not built now. Unsupported switches fail clearly.
- First checkpoint: three original synthetic documents → real Pinecone retrieval → one real cited Gemini answer through LangGraph, available through a CLI.
- Then nine documents, 15 fixed evaluation cases, Streamlit, baseline report and reproducible README/demo outline.
- Budget from brief: USD 1–2 target; USD 3 estimated paid-usage guard across both phases. The persistent SQLite guard is implemented and tested; paid provider calls fail closed until rates and token bounds are verified. Paid fallback remains disabled. Never silently treat missing usage/pricing as zero.
- Credentials remain local and private. Keys are configured locally in ignored `.env`; only presence checks are logged. Tracing is disabled.

## Review artifacts and continuation

Design: [Phase 1 spec](docs/superpowers/specs/2026-10-18-phase-1-design.md), explicitly approved by the user on 2026-10-18. The user selected native execution of the [implementation plan](docs/superpowers/plans/2026-10-18-phase-1.md). Design and plan review are complete; continue implementation without asking again.

The user confirmed Pinecone Starter and Gemini free tier on 2026-10-18. Pinecone integrated embedding metadata, indexing/retrieval and Gemini generation have been live-verified. Account tier flags are user assertions, not billing API verification. Use only the synthetic corpus. Python 3.12 dependencies are locked and installed. Git is initialized on `phase-1`; origin is `git@github.com:rameshsuthan/runnbook-iq.git`. The user authorized local author `rameshsuthan`; verified GitHub ID 8152097 gives `8152097+rameshsuthan@users.noreply.github.com`. No remote push is implied.

The workspace began with three Markdown planning/reference documents. Phase 1 now includes the CLI, graph, nine-document corpus, evaluation runner and Streamlit. The first three-document live milestone is retained in `eval/results/m1-*.json`. See PROGRESS.md and the baseline report for actual verification and remaining limitations.

Read this file, `PROGRESS.md`, the handoff and current implementation before continuing. Keep decisions here; record actual commands, outcomes, blockers and the next action in `PROGRESS.md`.

## Implementation decisions

- Gemini 3.5 uses minimal thinking and provider-default sampling; no temperature override. Responses are not deterministic. Maximum output is 1500 tokens; SDK retries and paid fallback are disabled.
- Citation validation accepts `[id]` and `[id1, id2]`, checks each against selected evidence, and requires the inline/listed sets to match. It does not verify entailment. No response-repair feature has been added.
- Nine documents produce 21 chunks. Fifteen cases were frozen before retrieval evaluation (10 development, 5 held out); all have now been observed. Do not describe future comparisons against them as unseen testing.
- The local UI never ingests on startup or question submission. Form submissions invoke the graph; ordinary reruns retain the previous result.
- No real production documents, live infrastructure, automatic remediation or advanced Phase 2 retrieval are in scope. The demo outline is written; no video has been recorded.

- Final review fixed fenced Markdown preservation (splitter sections-v2), destination-bound ingestion and single-search answer evaluation. Existing live corpus/results retain their original version; rebuilding changes the version and requires explicit ingestion.
- Current baseline quality is limited: 7/15 validation failures, one incomplete answer and one incorrect abstention status. Preserve these observations; the next quality work is targeted diagnosis, not Phase 2 implementation.

## Phase 1 quality follow-up — 2026-10-18

- User approved retaining the baseline history and proceeding. Existing commits
  `82de23b` and `40150f4` remain intact; no remote push was requested.
- A live q06 diagnostic demonstrated missing inline citations despite a populated
  source-ID array. Validation remains strict and now emits safe error categories.
- `ask --save-invalid-response` explicitly opts into private local failed-response
  diagnostics. Default results exclude raw rejected text. No retry/repair loop.
- Prompt `incident-evidence-v2` plus schema descriptions reinforce citation,
  completeness and abstention instructions; cache versions change with them.
- Three-case development follow-up: q06 citation/cause answer and q10 abstention
  improved; q08 remains incomplete despite relevant selected evidence. This is
  not a replacement full baseline. Next quality issue: use of retrieved fields.

## Telemetry coverage correction — 2026-10-18

- q08 had both required telemetry passages at ranks 1 and 5. Its failure was
  incomplete generation from available evidence. A question-last presentation
  experiment improved measurement coverage but still omitted correlation IDs;
  that change was rejected and the original message layout remains.
- The adopted change only clarifies the `documented_evidence` schema description:
  enumerate requested exact field names/meanings and use all relevant selected
  passages. No expected field names or evaluation answers are inserted into the
  production prompt. Prompt/schema identities are now incident-evidence-v3 /
  answer-v3, with the existing response fields and graph interfaces preserved.
- A real three-case graph follow-up covered q08 correctly and preserved q01's
  supported answer and q10's abstention. Full v3 baseline is recorded separately;
  prior baselines and failed experiments remain available. No Phase 2 features.

- Full v3 baseline: 10 answers / 5 abstentions; 13/15 match frozen status expectations.
  q02 omits an expected caveat; q04/q11 have conservative status disagreements;
  q09 adds an unsupported uncited check. Current validator additionally requires
  citations in each nonempty evidence/checks section and rejects that q09 output,
  including from cache, without regeneration. Offline saved-response audit: 14/15
  accepted, one rejected. These numbers are not a new live run after the guard.
- Status-rubric clarification is prospective work before Phase 2 comparisons; do
  not rewrite frozen baseline expectations to erase disagreements. Citation checks
  remain structural, not semantic entailment. The full corpus and graph contracts
  stay available for later advanced retrieval work.
