# RunbookIQ progress

## Main integration checkpoint — 2026-10-19

User authorized consolidation and push to `main`. Fetched origin and verified
that only `phase-1` and `phase-2` existed remotely, and that Phase 1 is an ancestor
of Phase 2. Created `main` from Phase 2, preserving both milestone branches and
their history. Added the submission report, builder, screenshots, provenance and
documentation updates. Unrelated user-owned reference files and
`eval/results/my-answer.json` remain local and untracked.

Actual verification before integration: `.venv/bin/pytest -q` — 135 passed in
1.49 seconds; `git diff --check` passed. No live provider requests or paid usage.
Next action: verify the final main tree, commit and push `main`, then confirm the
remote commit matches. Demo recording and external assignment submission remain
pending; known evaluation limitations are unchanged.

## Current status — 2026-10-19

Phase1 and revised Phase2 implementation, evaluation and review are complete and
published. Gemini remains active; Nebius is optional Phase3. Last engineering gate:
135 tests passed. The requested18-page Word submission report and limited browser
walkthrough are complete locally, with5 diagrams and5 real screenshots. Frozen
evaluation failures remain disclosed. Video recording and external submission are
pending. Earlier entries below are chronological history, not current blockers.

## Initial planning checkpoint — 2026-10-18

Phase 1 implementation-plan review. The user approved the design on 2026-10-18. Product implementation and live verification have not started.

### Completed work

- Read `RunbookIQ-Codex-Handoff.md` completely.
- Inspected all workspace filenames, ancestor instruction-file locations, Git state, installed runtimes, and presence-only credential flags. Inspected assignment requirements and reference-solution headings; did not copy reference content or inspect its linked repository.
- Recorded the user's choice of Gemini for Phase 1.
- Checked official LangGraph, Pinecone, Gemini pricing/limits and native Gemini integration documentation; public information is not account verification.
- Wrote and self-reviewed `docs/superpowers/specs/2026-10-18-phase-1-design.md`; created `PROJECT_CONTEXT.md` and this record.
- Recorded explicit user approval of the written design; prepared `docs/superpowers/plans/2026-10-18-phase-1.md` with eight tasks, offline verification steps, live acceptance commands and Phase 2 boundaries. Self-review corrected the generation/cache interface so cache writes occur only after the graph validation node.

### Actual verification results

| Command/check | Observed result |
|---|---|
| `cat RunbookIQ-Codex-Handoff.md` | Complete consolidated brief read |
| `ls -la` and `rg --files --hidden` with secret/build exclusions | Three Markdown documents only; no application, local `.env`, tests or dependency manifest |
| Ancestor/workspace `AGENTS.md` checks | None found in applicable locations |
| `git status --short --branch` | Failed: not a Git repository; no commits or branch exist |
| `uname -sm` | `Darwin arm64` |
| `python3 --version` | Python 3.14.3 |
| `python3.13 --version` | Python 3.13.12 |
| `uv --version` | uv 0.12.23 |
| `uv python list --only-installed` | Failed because default uv cache was outside allowed write locations |
| `uv --no-cache python list --only-installed` | Passed; found installed Python 3.12.15, 3.13.12, 3.14.3 and system 3.9.6 |
| Presence-only Python check of `PINECONE_API_KEY`, `NEBIUS_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY` | All false in current shell; no values printed |
| `python3` inline documentation check using `Path.read_text()`, heading/newline assertions and placeholder scan | Passed for all three new files: context 29 lines, progress 45 lines before this entry, spec 112 lines; no unresolved placeholder markers |
| `python3` inline plan check using `Path.read_text()` and regex assertions for task numbering, required sections, placeholder markers and approval state | Passed: eight sequential tasks, 54 planned steps, 3,090-word plan; no obsolete `AnswerGenerator` interface or unresolved markers; spec records user approval |

No application tests exist or have run. No live Pinecone query/indexing, Gemini generation, or provider health check has run. No application API usage incurred in this session; account balances and earlier usage are unknown. The USD 3 budget guard is specified but not implemented. No successful cited-answer milestone is claimed.

### Blockers / unresolved prerequisites

1. Design review is complete. Required implementation-plan review and execution-method selection are pending under the installed writing-plans workflow. No further design approval is needed.
2. Gemini local credential, exact accessible model, account tier/free eligibility, quota and pricing are unverified.
3. Pinecone local credential, actual Starter entitlement/allowance and project index are unverified.
4. Exact embedding tokenizer/limit and locked dependency compatibility must be verified during setup.
5. Spec has not been committed because this workspace has no Git repository; repository setup is deferred to implementation setup. No automatic-approval rejection occurred.

### Next action at the planning checkpoint (superseded below)

Obtain review of `docs/superpowers/plans/2026-10-18-phase-1.md` and execution-method selection. Recommend native implementation in this session with the required final independent review. After that review, start Task 1: set up Git/Python/dependencies and offline tests. Continue through the three-document corpus, guarded Gemini provider, Pinecone ingestion/retrieval and LangGraph answer. Guide local secret configuration without exposing values and resolve account/model prerequisites before live calls.

At each runnable checkpoint, append exact test/run commands, observed outcomes, failures, provider/model, estimated usage and next action. Preserve failed or unverified live checks as such.

## Native execution checkpoint — 2026-10-18

Design and plan approved; native execution selected. Git initialized on `phase-1` after sandbox escalation; no author identity is configured, so no commits fabricated. Python 3.12 virtual environment and dependency lock installed successfully. User confirmed Pinecone Starter and Gemini free tier. Keys now present locally; values never printed.

Actual checks: `uv --cache-dir .uv-cache run pytest -q` → 32 passed. Config tests first failed 4/4; corpus tests failed 4/4; budget/provider/cache tests failed 7/7; ingestion/retrieval tests failed 4/4; graph/validation tests failed 13/13 before their implementations. One incorrect tracing-context import caused 2 provider tests to fail; installed SDK inspection identified the export in `langsmith`, and the suite then passed.

`uv --cache-dir .uv-cache run runbook-iq corpus build` → 3 synthetic documents, 9 canonical chunks, version `d30253eea9c2323fa9dcd4bc6a4a051eb5a926a8d98c720c4541c3d6f6fae4c7`. Real pinned NVIDIA tokenizer: maximum conservative count 122 tokens/chunk. `ingest --dry-run` → 9 candidate chunks and zero remote calls. Tokenizer/config assets downloaded without model weights, revision `113abe4acafa848e77ead9c0623205e511932348`.

Ruling: free-tier Gemini is the selected Phase 1 path; paid Gemini calls fail closed until model-specific pricing and billable token bounds are verified. The persistent USD 3 reservation ledger exists and is tested; no paid calls have been made. A conservative 2048-token embedding ceiling and remote `truncate=NONE` prevent relying on the upstream model card's larger context window; verify actual Pinecone metadata before ingestion.

Next: metadata-only service checks, real three-document ingestion/retrieval, and the first cited answer. M1 is not yet live-verified. Git commits remain pending identity setup. Offline work is implemented, not a substitute for live acceptance.

## M1 live checkpoint — verified 2026-10-18

`doctor --pinecone --gemini` succeeded after fixing the installed Pinecone SDK's keyword-only `get_model(model_name=...)` requirement (regression test RED→GREEN). Pinecone reported a 2048-token limit, max batch 96, and supported `truncate=NONE`. Both secrets were detected by presence only. A dedicated `runbook-iq` index/namespace was created with ownership tag, AWS us-east-1, integrated llama-text-embed-v2, deletion protection, and truncation disabled.

Actual commands (using `.venv/bin/runbook-iq` with network permission):
- `ingest` → 9 upserts verified remotely; 0 deletions.
- `retrieve --question 'What documented checks distinguish database pool exhaustion from an inventory dependency timeout in order-api?' --output eval/results/m1-retrieval.json` → dependency and pool distinguishing-check sections at ranks 1 and 2.
- `ask` with the same question and `--output eval/results/m1-answer.json` → `answered`, 992 input / 340 output tokens, reasoning count unavailable, one call, estimated USD 0 on user-confirmed free tier. Node execution about 2.01 seconds excluding client composition. Manual review: all reported thresholds, identifiers and recommended checks match the cited passages; no actual live cause asserted. Missing-information list was empty for this documented comparison question.
- Second `ingest` → 0 upserts, 0 deletions, 9 skipped: idempotence verified.
- `uv --cache-dir .uv-cache run pytest -q` → 34 passed after SDK regressions.

Failure retained: `eval/results/m1-answer-failed-model.json`. Gemini listed gemini-2.5-flash-lite but both the first answer attempt and one guarded diagnostic attempt returned model-not-found HTTP 404 (no automatic retries). Ruling: explicitly switched configuration to listed/current free-tier `gemini-3.5-flash-lite`; generation succeeded. Provider warnings revealed fixed sampling defaults, so temperature is omitted for Gemini 3 and cache metadata records provider defaults; thinking level is minimal. Regression test verified these parameters. Failed calls have unknown token usage, not invented zeros. All three guarded attempts used user-confirmed free access; ledger has no paid spend.

Next: expand to nine documents and freeze 15 cases before retrieval tuning; implement evaluation runner and UI. No Phase 2 features implemented. Local Git author identity requested asynchronously; no commits yet.

## M2/M3 checkpoint — 2026-10-18

Expanded/froze 9 synthetic documents and 15 questions (10 development, 5 held out) before retrieval tuning. No tuning performed. Canonical corpus is 21 chunks, version `a5e854f2e00a6ed0d773d4899a0d4b25c8b3274b0e581e16a2d2b48db23da3e0`; explicit ingestion verified 21 upserts and 0 obsolete deletions (original chunk IDs retained).

Actual checks: `.venv/bin/pytest -q` → 37 passed, including evaluation denominators and Streamlit submit/rerun behavior. Streamlit installation first failed under restricted network, then succeeded with approved escalation and updated lock. Local server initially could not bind under sandbox; approved local-only startup succeeded at `http://127.0.0.1:8501`, usage telemetry disabled. AppTest verifies form submission and persistent answer rendering without repeated model calls. Visual browser inspection is unverified: the computer-use tool reports no available browser.

`evaluate --mode retrieval --split dev --output eval/results/phase1-dev-retrieval.json` → 10 cases, 8 answerable, hit@5=1.0, macro expected-section recall@5=1.0. Then `evaluate --mode retrieval --split all --output eval/results/phase1-retrieval.json` → 15 cases, 12 answerable, both metrics 1.0. Three unanswerable cases excluded from retrieval denominators. Held-out retrieval has now been observed; future tuning must label that exposure. No chat calls in either retrieval-only run.

User provided `git@github.com:rameshsuthan/runnbook-iq.git`; configured origin without pushing. Author identity still pending clarification. Full 15-case answer run started with 15-second inter-case spacing; every result is saved incrementally and provider errors stop the run. Manual grounding review follows actual results. Phase 1 not yet declared complete.

## Final Phase 1 checkpoint — 2026-10-18

Implemented the approved baseline and recorded all 15 cases, including failures.
M1 is verified; the full baseline is runnable with answer-quality limitations.
The detailed manual review and exact denominators are in `eval/results/phase1-review.md`.

Actual results: retrieval-only hit@5 12/12 and macro recall 1.0; corrected answer
run 6 answered / 2 insufficient_evidence / 7 invalid_output. q08 is grounded but
incomplete; q10 says the live cause is unknown but returns the wrong status.
Initial run (11 invalid outputs) is retained. A grouped-citation parser defect was
reproduced, fixed and tested. Remaining invalid responses were not retained raw,
so their precise failure categories are unknown. No repeated run was substituted
for a failed baseline case. No model repair or Phase 2 features were added.

The final independent reviewer found three Important issues, all fixed with
regressions observed failing then passing: valid Markdown fences could be split;
local ingestion state lacked destination binding; answer evaluation searched twice.
Now fence parsing is consistent, index/host/namespace ownership is persisted, and
answer evaluation records the actual graph retrieval/selection. The recorded full
answer baseline predates the last provenance fix; that limitation is explicit.
One minor remains: setup/cache errors may overcount an attempted chat call.

Final verification:
- `.venv/bin/pytest -q` → 49 passed.
- `uv --cache-dir .uv-cache sync --locked --offline` → resolved 89 packages and succeeded.
- Remote fetch of all 21 records matched canonical hash/version/text before local
  destination migration; subsequent synchronization → 21 skipped, 0 upserts/deletes.
- Final cached CLI question → answered, real retrieved/selected evidence retained,
  0 new chat calls (`eval/results/final-cache-smoke.json`).
- Explicit unmatched environment filter → empty retrieval, deterministic fallback,
  0 chat calls (`eval/results/final-empty-fallback.json`).
- AppTest rendered the saved live M1 answer and both source passages without
  exceptions or service calls. Visual browser QA remains unavailable.

Ledger totals: 31 attempts, 29 known usage records, 2 unknown model-not-found
outcomes; 27,607 input and 6,770 output tokens known, separate reasoning unknown.
Estimated paid spend USD 0 on user-confirmed free tier; paid route remains disabled.
The USD 3 atomic reservation guard is tested, not a provider invoice guarantee.

Git identity is configured locally as authorized: rameshsuthan,
8152097+rameshsuthan@users.noreply.github.com. Origin points to the user's repository.
No push/deployment is performed. Credentials remain ignored and private.

Next action: run the local UI and walk through the M1 example and documented
failure cases using `docs/demo-outline.md`. For further implementation, investigate
remaining validation failures and answer completeness on development cases before
starting Phase 2. No credential, design-approval or Git-identity blocker remains.

Local baseline committed as `82de23b` on `phase-1` using the authorized author.
Before commit: all 64 staged files checked against configured credential values
without printing them; no matches, private-key marker, .env or runtime artifacts.
`git diff --cached --check` passed. Original reference solution and assignment
handout remain untracked and untouched. No remote publication occurred.

## Phase 1 quality follow-up — 2026-10-18

User approved committing history and proceeding. Confirmed existing baseline
commits `82de23b` / `40150f4`. Preserved the user's newly created untracked
`eval/results/my-answer.json` and both original reference handouts without edits.

Investigation: q03 reused an existing valid cache entry (zero new generation).
One q06 live diagnostic failed: valid source-ID list but no inline references in
evidence/checks. The original response remains in ignored private local storage.
Root cause for this observed case is output-contract noncompliance, not retrieval
or the grouped-citation parser. Other old invalid outputs cannot be retrospectively
classified because their raw responses were not retained.

Implemented safe validation categories and explicit CLI opt-in for private local
failed-response diagnostics. Eight category tests plus graph redaction/termination
failed before the change, then passed. Two diagnostic tests first failed for the
missing option; an implementation mistake using Path.open(opener=...) was corrected
to built-in open after its TypeError. File permissions, default non-retention and
successful-response non-retention are verified. Prompt/schema guidance was clarified
and versioned (incident-evidence-v2 / answer-v2) to invalidate older cached answers.

Actual verification:
- `.venv/bin/pytest -q` → 60 passed.
- `.venv/bin/runbook-iq ask --help` → explicit `--save-invalid-response` documented.
- Targeted evaluation using the actual graph and frozen development cases q06,
  q08, q10 → answered / answered / insufficient_evidence; three new calls, all
  structurally valid, 3,212 input / 821 output tokens, estimated USD 0.
- Assistant source review: q06 covers supported historical cause/correction;
  q10 correctly abstains and names missing live observations; q08 remains incomplete
  despite relevant telemetry fields in selected evidence. Results saved in
  `eval/results/phase1-followup-v2.json`; baseline files unchanged.

This continuation used four new generation calls total (one diagnostic plus three
follow-up), no retry/repair and no paid fallback. Ledger snapshot: 38 attempts,
36 with known usage, two older unknown outcomes, USD 0 estimated paid usage;
includes intervening user activity. No keys or provider exception bodies logged.

Next action: inspect q08's selected telemetry passages and compare them with its
incomplete answer before considering another bounded development experiment.
All original Phase 2 exclusions remain. No broad brainstorming or new design
approval is needed for these Phase 1 contract fixes.

## Telemetry coverage milestone — 2026-10-18

Confirmed q08 selected both telemetry sections, including the required identifiers
and timing fields. Compared against the incomplete v2 answer. Two single-call
experiments used identical recorded evidence, unchanged model/settings and v2
system instructions: moving the question last still omitted request_id/trace_id;
clarifying the answer-field schema description included all requested fields.
Both observations are saved in `eval/results/q08-coverage-experiments.json`.
The unsuccessful layout change was not adopted. These are stochastic observations,
not a causal guarantee.

Adopted only the schema-description clarification plus prompt/schema cache-version
bumps (v3). A check against the saved v2 answer first failed for all four expected
names: request_id, trace_id, db_pool_acquire_ms, inventory_request_ms. The actual
v3 graph answer passed that check; assistant source review also checked meanings,
same-window/process scope and citations. The production prompt contains no literal
evaluation answer/field names. Existing interfaces, retrieval and one-call bound
are unchanged.

`.venv/bin/pytest -q` → 60 passed. No source-text/constant-only test was added for a
schema prose change. Actual targeted graph run q01/q08/q10 → answered / answered /
insufficient_evidence, all supported and substantively complete on review. Three
new calls, 3,301 input / 952 output tokens, estimated USD 0. Results retained in
`eval/results/phase1-followup-v3.json`.

Started one final fixed v3 baseline over all 15 cases, reusing the three current
cached answers, with at most twelve new free-tier calls and 15-second spacing.
No automatic repair/retry. Every outcome is saved incrementally; provider/quota
errors stop the run. Original reports are not overwritten.

### Full v3 outcome and final guard

Full v3 baseline completed all 15 fixed cases: 10 answered / 5 insufficient_evidence,
3 cache hits and 12 new calls; no format failure under the then-current validator.
Retrieval hit/recall stayed 1.0 for 12 answerable cases. Manual source review is saved
per case in `eval/results/phase1-baseline-v3.json`. Exact status agreement: 13/15.
q04/q11 conservatively abstained versus expected answered, q02 omitted a cause
caveat, and q09 included an unsupported/uncited vault recommendation. q08 now
includes the expected correlation and measurement fields with accurate meanings.

q09 revealed a real validation gap: citation presence in one section did not
require citation presence in the other. Tightened validation so each nonempty
evidence/checks section needs an inline citation. Old cached outputs are also
revalidated and rejected with a categorized failure and zero generation calls;
no automatic retry or cache regeneration. Three new tests observed RED→GREEN.
`.venv/bin/pytest -q` → **63 passed**.

Offline replay of all 15 saved answers under the strengthened validator → 14
accepted; q09 rejected as missing_inline_citations. The audit records the source
JSON hash in `eval/results/phase1-baseline-v3-validation-audit.json`. This is an
offline audit, not a second live run. No further model calls made after the full
baseline. Field-level citations still do not prove every claim or requested point.

Full run: 12,977 input / 4,309 output known tokens; median uncached summed node time
1.815 s (composition and pauses excluded). This continuation: 17 new calls total,
18,505 input / 6,267 output tokens, USD 0 estimated paid usage. Final ledger snapshot:
56 attempts, 54 known usage records, 2 earlier unknown outcomes; includes user
activity between checks. No Phase 2 features or paid fallback enabled.

Next action: use the v3 report and offline audit for the Phase 1 walkthrough.
Before comparative Phase 2 evaluation, clarify the answer-versus-abstention rubric
for q04/q11 prospectively, preserving these original expectations and outcomes.
Known limitations remain q02's caveat coverage, q09's rejected output, and the
absence of a semantic entailment verifier; no additional prompt-tuning loop is running.

## GitHub publication and Phase 2 design — 2026-10-18

User explicitly requested push and next steps. `git ls-remote origin` returned no
refs. `git push -u origin phase-1` succeeded and configured tracking.
`git ls-remote --heads origin phase-1` confirmed
`e15502eda4dac8217b067cebde41da09c2b6ca1c`. Created `phase-2` from that baseline.
User-owned untracked reference documents and `eval/results/my-answer.json` remain
untouched and unpublished.

Read the complete handoff and current graph, schemas, configuration, retrieval,
budget, cache and evaluation contracts. Wrote the Phase 2 design with six runnable
milestones, starting with BM25/RRF over the existing active chunks. Identified
per-query provenance, cumulative multi-call usage, and separate retrieval/selection
metrics as necessary interface extensions. Proposed prospective status rubric keeps
all frozen expectations and original failures intact.

Official public documentation checked: Pinecone Starter includes BGE reranking
(500 requests/month); BGE accepts at most 100 documents and 1024 tokens per
query/document pair, with `truncate=NONE` available. Design limits input to 15
documents, selects five and fails visibly on oversize/access/quota errors.
Nebius documents its compatible endpoint and model-dependent JSON-schema support;
no model/rates/account credit availability has been asserted or enabled. Readiness
question sent to the user; this does not block the BM25 milestone's design.

No product code/dependencies/configuration changed. No Pinecone/Gemini/Nebius API
calls or new application usage incurred. Existing offline test result remains
63 passed; tests were not rerun for this documentation-only checkpoint. Spec
self-review covers bounds, error exits, backwards-readable records, cache identity,
shared budget and evaluation limitations.

Documentation verification: `git diff --check` passed; Python assertions confirmed
six milestone IDs, balanced fenced blocks, no unresolved placeholder markers and
resolving local Markdown links. Only the spec and the two project tracking files
are included in this checkpoint's commit.

Next action: obtain review of the written Phase 2 spec, then write its detailed
implementation plan using the already-selected Native execution method. The
installed brainstorming workflow requires written-spec review before that plan;
Phase 1 approvals remain complete. After plan review, implement P2.1 in small
runnable steps. Later live prerequisites are reranker access and verified Nebius
credentials/model/rates/billable bounds; no plan upgrade or paid fallback is allowed.

## Provider readiness update — 2026-10-18

User replied: Nebius is not ready; continue with Gemini. Recorded Gemini as the
route for upcoming answer, expansion and repair work. Nebius live acceptance is
deferred, without blocking independent milestones or removing the second-provider
interface from scope. No credentials requested, configuration changes, or service
calls. Phase 2 spec approval remains pending; next action is unchanged.

## Phase 2 implementation-plan checkpoint — 2026-10-18

User approved the written design and requested proceeding. Marked the spec approved
and prepared `docs/superpowers/plans/2026-10-18-phase-2.md`: nine tasks, 53 checkable
steps, six runnable milestones. Native execution is preserved. No further project
clarification is needed to start the first milestone after plan review.

Inspected current CLI composition, graph/provider/retrieval/evaluation contracts,
Pinecone usage logging, schemas/config/cache/budget and offline/UI tests. The plan
defines exact module boundaries, new signatures, behavioral tests and acceptance
checks. Self-review added direct usage-return interfaces to avoid duplicate searches,
kept current-run usage on answer cache hits, and scheduled Gemini repair independently
of unavailable Nebius access. Shared runtime paths must preserve the existing budget
ledger when execution isolation is selected.

Actual documentation verification: Python checks passed for nine sequential task
numbers, nine Files/Interfaces blocks, 53 checkbox steps, balanced fences, no
unresolved placeholder markers and resolving local plan links. `git diff --check`
passed. Tests were not rerun because no product code, dependencies or runtime
configuration changed; the prior 63-test result is historical, not a new test run.
No application API calls or new estimated application cost incurred.

Next action: review the concrete implementation plan, then use Native execution
to establish a fresh offline baseline and implement Tasks 1–2 (BM25/RRF and one
cited hybrid graph answer). The writing-plans skill explicitly requires plan review
before implementation even when an execution method was selected earlier. Design
approval is complete and must not be requested again. Nebius readiness only blocks
its own later live acceptance, not the independent Gemini milestones.

## Phase 2 Native execution: Task 1 — 2026-10-18

User approved the plan and Native execution. Fresh baseline: `.venv/bin/pytest -q`
→ 63 passed. Existing dedicated phase-2 checkout retains the active canonical
snapshot and shared usage ledger; no secret copies or budget reset.

Implemented canonical BM25 with identifier-preserving tokenization, explicit
filters before top five, positive IDF and deterministic ties. Added additive
per-query/method provenance and RRF with raw-score separation and canonical-record
conflict rejection. New tests first failed 7/7 for absent behavior; then
`.venv/bin/pytest -q tests/test_keyword.py tests/test_fusion.py tests/test_retrieval.py`
→ 8 passed. No live calls or dependencies added. Next: wire the shared pipeline,
graph and evaluation to deliver the first hybrid cited answer.

## P2.1 hybrid graph milestone — 2026-10-18

Shared retrieval/selection pipeline now drives CLI, LangGraph and retrieval-only
evaluation. Default dense path retained. Active snapshot/destination checked around
the batch; original queries and per-method provenance recorded. Cache identities
include effective retrieval settings. Retrieval CLI now returns a RunResult with
retrieved_candidates and selected_evidence rather than a bare list.

Seven added behavioral tests observed RED→GREEN; 26 targeted tests and full suite
77 passed. Live dense and hybrid retrieval-only evaluations each completed all 15
cases on the unchanged active corpus: fused/selected hit@5 and recall@5 all 1.0 for
12 answerable cases; no chat calls in these comparisons. No measured gain claimed.

One hybrid graph answer: answered, two valid runbook citations, 1,132 input / 474
output tokens, one Gemini free-tier call, estimated USD0. Sources support deadlines,
metrics and wait-stage distinction; wording “verify pool exhaustion” is stronger
than the source's “supports investigating pool contention.” Manual review retained
in a separate artifact; no prompt tuning or semantic-verifier claim.

Prospective rubric and supplemental mapping of retained Phase 1 source reviews
added without modifying frozen expectations or results. Next: operation accounting
and dedicated reranker. No reingestion, new dependencies, paid calls or Nebius calls.

## Task 3 operation accounting — 2026-10-18

Added per-operation attempts, nullable usage, known subtotals and completion flags.
Setup/cache failures no longer imply model invocation. Cache hits retain current
retrieval operations; partial multi-query failures retain earlier calls. Gemini
timeouts retain the unresolved reservation and safe failure metadata. Pinecone
returns hit data and usage together, avoiding a second search. Added persistent
monthly quota reservations; read units are monitored from responses, not claimed
as a guaranteed request-cost bound or remaining account balance.

Six initial usage/quota tests failed before implementation, then passed; two
additional usage-return/partial-failure tests also observed RED→GREEN. Full suite:
85 passed. One legacy exception-type assertion was updated to the deliberate
safe CallFailure contract; snapshot-change rejection remains tested. No live calls.
Next: dedicated Starter BGE reranking, then Gemini query expansion.

## P2.2 dedicated reranker — 2026-10-18

BGE reranker adapter validates result counts/indices/finiteness, preserves canonical
text and provenance, uses original question and truncate=NONE. Eight new tests
observed RED→GREEN. SDK inspection found implicit Pinecone transport retries;
disabled via pinned SDK configuration with an actual inference/index transport test.
Full offline suite: 94 passed. SDK introspection found no close() on Pinecone 8;
no service call involved. Smoke script dotenv discovery initially failed under
stdin; explicit local path fixed it before any request.

Live metadata confirms BGE 1024-token pairs, max batch100 and NONE truncation. One
synthetic rerank smoke succeeded (1 unit). Full 15-case reranked retrieval comparison
completed; 12 answerable cases retain selected/fused hit and recall1.0. One real
graph answer succeeded, 1,140 input/619 output tokens, one Gemini free-tier call,
estimated USD0. Selected passages support deadline distinctions, pool/dependency
checks and the 503 caveat; no live cause claimed. These are small synthetic results,
not proof of improved answer quality. This milestone used 17 rerank requests total.
Next: one bounded Gemini expansion call, original-only fallback and expansion cache.

## P2.3 bounded query expansion — 2026-10-18

One structured Gemini expansion call returns up to two alternatives; original first.
Lexical guards preserve identifiers, numbers, quoted literals and negation, reject
new domain diagnoses and both dropped/added negation. They do not prove semantic
equivalence; one live alternative differed mostly by punctuation. Validated
expansions are cached independently; required-cache evaluation fails before search
on missing entries. Expansion errors fall back with warnings and recorded usage.

Initial ten tests failed before implementation; added-negation regression also
observed RED→GREEN. Full suite 107 passed. Live targeted graph returned answered
with two chat calls, 1,225 input/545 output combined tokens, estimated USD0;
source checks support the listed deadlines and recommended checks. Full 15-case
multi-query retrieval comparison completed with 14 new expansions and one cache
hit, 15-second spacing, no service errors, selected recall1.0 for all 12 answerable
cases. No retrieval gain claimed. Offline required-cache audit reused all 15 exact
query sets with a provider that raises if invoked: zero new calls. The audit script
first failed by summing a cache-hit null token field; corrected to count attempted
operations and report token completeness explicitly. No product result was altered.

Next: one bounded response-repair edge using Gemini. Nebius remains deferred.

## P2.5 bounded response repair — 2026-10-18

Added one explicit repair→validate graph edge. Counter increments before repair;
second invalid output ends invalid_output. Original question/evidence remain fixed,
provider failures do not trigger repair, invalid cache entries do not regenerate,
and budget denial preserves the initial validation category. Each call is accounted
for; repaired answers are cached only after successful validation.

Six sequence-provider tests observed RED→GREEN, including invalid→valid,
invalid→invalid, budget denial, transport failure, invalid cache and three-call
maximum with expansion. Targeted suite27 passed; full suite113 passed. Tests use
injected responses and make no network calls. No natural invalid fresh answer has
needed repair in the Phase 2 live samples, so live repair is not yet verified.
No extra live calls were made for this milestone. Next: offline Nebius adapter,
with its live acceptance deferred, then inspection and final comparison/review.

## P2.4 Nebius offline adapter — 2026-10-18

Implemented explicit compatible-API adapter with zero SDK retries, structured
responses, finish/refusal normalization, independent route selection and usage.
Paid preflight requires verified rates, account/model and provider-enforced context
plus total output bounds; reservation uses the full verified context ceiling, not
the local byte-size heuristic. Unknown usage retains the reservation. Promotional
credits are not treated as free. Current configuration remains Gemini.

Ten initial mocked tests observed RED→GREEN; additional SDK-configuration/refusal
check passes. Full offline suite124 passed. Added/locked openai2.54.0 and jiter0.17.0
only; original packages retained. Official Nebius quickstart/JSON docs rechecked.
No actual model ID or prices configured, no credentials requested, no Nebius calls.
P2.4 live acceptance remains incomplete because the user is not ready. Continue
independent inspection/evaluation tasks; do not declare all of Phase 2 complete.

## Inspection milestone — 2026-10-18

Streamlit inspection displays query variants, requested/effective settings, per-query
provenance, stage scores, selected IDs, repair count and operation usage. Cache-hit
caption reports all chat calls in the current request, including expansion. Profile
selection uses RUNBOOK_IQ_CONFIG; default config remains dense-only. README now
documents profiles, shared ledger paths, retrieval-only expansion costs and the
changed retrieve CLI result object. Added optional repair profile; offline doctor
validates it without loading keys or making service calls.

Two new AppTest cases failed before implementation and passed afterward; all three
UI tests pass, proving reruns do not resubmit and current expansion usage is shown.
Structured browser inventory exposes no enabled browsers; native visual inspection
was not performed. UI behavior is AppTest-verified, not visually verified.
Next: final comparison manifests/partial-failure tests, fixed answer evaluation,
manual source review and one independent whole-branch review. Nebius live remains
deferred. No new application API calls in this milestone.

## Final evaluation in progress — 2026-10-18

Task 9 manifest/cache tests observed two RED failures then GREEN; full suite129
passed in1.64s. CLI help, offline doctor and git diff --check passed. Offline
credential presence reports missing because doctor intentionally does not load .env.
Report manifests include source commit/dirty flag plus source tree hash, rubric,
schema, full settings and separate composition/request time. Frozen query cache
compatibility is preserved when the optional provider context bound is unset.

The answer evaluation saved q01–q05 then stopped at q06 with a dense-search error.
The attempted search has unknown units and retains its embedding reservation; no
chat call happened for q06. Local counts were 38 rerank units and 3,119 embedding
tokens including the unknown reservation, below configured caps. Original error
cause is unavailable in the safe saved report. One explicitly bounded continuation
from q06 reuses recorded expansions and stops on any service failure. Its initial
stdin dotenv discovery failed locally before any API calls; explicit .env path
corrected that script. q06 then succeeded. Preserve both artifacts, never overwrite
the original failure. q08 incorrectly denies documented telemetry correlation
fields despite the selected guide containing them; record this semantic failure.

Continuation completed all remaining ten cases without another service error.
Final combined results:9 answered/6 abstentions,12/15 status agreement; first
attempts:8 answered/6 abstentions/1 retrieval error,11/15 agreement. q02 caveat
omission and q04/q11 conservative statuses persist; q08 fails source support.
Manual source review is in eval/results/phase2-review.md. q15 naturally repaired
once and returned a supported abstention. Initial rejected text/category was not
retained; only the successful final result and both operation records are asserted.
Across final runs:16 Gemini calls,17,064 input/5,843 output tokens,estimated USD0;
38 successful dense searches+one failed,15 reranks,16 cached expansions. Local
shared ledger now has90 reservations:88 known and2 unknown historic chat outcomes,
estimated/reserved USD0. Local Pinecone counts:48 rerank units,95 known read units,
3,485 embedding tokens including one unknown2,048-token reservation. These counters
do not establish account-wide consumption. Next: independent branch review.

## Independent review and final fixes — 2026-10-18

One fresh reviewer independently ran129 passing tests and found two Important
expansion defects plus one Minor accounting defect. Regraded accounting loss as
Important because completed usage must not disappear. Six regression cases observed
RED (extensions3, cache limit modes2, malformed hit1) then GREEN. Whole suite135
passed in1.49s; CLI help, offline doctor and git diff --check passed.

Whole identifier/number tokens now reject punctuation extensions. Cache hits recheck
current embedding limits: required-cache stops early, ordinary mode returns the
original query with warning. Malformed canonical hits retain completed search units.
No additional live calls. Offline pinned-tokenizer replay preserves all15 recorded
query sets; all15 final saved answers pass structural validation. Exact configured
secret values were absent from109 tracked/candidate files and Git history. User
untracked handout and my-answer.json remain untouched. Review record is in
`docs/phase2-code-review.md`; live evaluation artifacts keep their pre-fix hashes.
Next: publish authorized phase-2 commits and verify the remote SHA. Nebius live
acceptance remains blocked by user readiness. q08 semantic quality remains a
recorded limitation, not an unreported passing result.

## Published Gemini milestones — 2026-10-18

Normal push succeeded; `git ls-remote` verified reviewed implementation4cab6fc on
origin/phase-2 and unchanged e15502e on origin/phase-1. Final Task9 completion gate:
135 passed in1.44s. All owned changes are committed; the untracked user handout and
my-answer.json are preserved. `docs/phase2-execution-record.md` archives decisions,
verification and the independent review dispositions before scratch cleanup.

Next action: when the user says Nebius is ready, verify accessible model/rates and
provider-enforced token bounds, then make the bounded structured-response and cited
answer acceptance calls through the existing shared USD3 ledger. Until then Gemini
profiles remain runnable and full Phase2 acceptance remains incomplete. q08's
incorrect denial of documented fields is a known quality limitation for a separate
targeted follow-up; do not rerun/tune frozen comparisons merely to improve scores.

## User scope update: Phase 2 complete; Nebius optional Phase 3

The user explicitly removed Nebius from Phase 2 and may revisit it in Phase 3.
This supersedes the earlier Nebius acceptance blocker and next-action entries.
All remaining Phase 2 implementation/evaluation/review tasks are complete and
published. Existing offline Nebius code remains inactive; no live verification is
claimed. Last code verification remains 135 passing tests; this update is docs-only,
with no test rerun, model calls, credential access or new charges.

Outstanding follow-ups, distinguished from implementation completion:
- Answer quality: q08 incorrectly denies available correlation fields; q02 omits
  the expected no-cause caveat. q04/q11 retain conservative status disagreements.
  Preserve the frozen baseline and report any future targeted work separately.
- Visual UI walkthrough: AppTest passes, but native visual inspection is undone.
- Assignment delivery: <=5-minute demo outline is ready; video recording and
  submission have not been performed. No deployment/auth work is in current scope.

Recommended next action is targeted q08 diagnosis, followed by UI/demo preparation.
Nebius requires a separate future decision and verified model/rate/bound setup.

## Architecture and demo kit prepared

Created docs/architecture.md with seven detailed Mermaid diagrams: system,
ingestion, graph control flow, retrieval, cache-hit sequence, data contracts and
usage/budget boundaries. Exported seven matching .mmd sources and five simplified
1920×1080 SVG/PNG visuals with an offline Pillow renderer using existing dependencies.
Added a local visual gallery with no external resources. No product code or profile
changed; no credentials read and no Pinecone/Gemini calls made.

Prepared a400-word narration with a4:35 storyboard, exact live questions, source
inspection steps, actual-cache wording, known-failure disclosure, Mac recording
instructions, contingency wording and submission checklist. Added a copy-ready
project summary addressing the supplied handout's Google Doc headings. Original
handout was read, not modified; no reference solution was consulted. Nebius is
correctly described as optional Phase3. Existing demo outline now points to this kit.

Verification: all7 Mermaid source files exactly match guide blocks; all5 SVG files
parse as XML and all5 PNGs are1920×1080. Visually inspected the five-PNG contact
sheet and the revised full-size runtime diagram; adjusted a crossing for clarity.
Checked18 local Markdown links plus gallery links. Compiled the real graph offline
with non-invoking adapters and verified its8 named nodes against the detailed flow;
all5 configuration profiles match the documented flags. Saved evaluation counts
match15 completed cases,12 status matches and16 chat calls. Renderer completed and
git diff --check passed. No automated Mermaid renderer/browser visual validation
was available; only the supplied SVG/PNG exports were render-checked. The application
suite was not rerun for this documentation-only change; last code gate remains135.

Next action: user rehearses and records the timed live walkthrough, checks audio,
legibility and <=5-minute duration, then publishes the video/Google Doc and submits.
No video, Google Doc or submission has been created by the agent. Native app visual
walkthrough and existing answer-quality issues remain outstanding.

## Word submission report and browser walkthrough — 2026-10-19

Created `docs/submission/RunbookIQ-Project-Submission.docx`:18 pages,5 architecture
and flow diagrams,5 actual app screenshots, node contracts/conditional decisions,
prompt/schema instructions, profile choices, usage/cache interpretation, all15
frozen questions with observed outcomes, iterations, known failures and reproduction
links. Read the supplied DOCX completely through OOXML text/tables and rendered it
for visual reference; did not copy its branding assets, implementation or claims.
Retained a reproducible document builder, source screenshots and their hash manifest.
README links the report; no product code, config, dependency or frozen report changed.

Native computer access was unavailable. User explicitly authorized a temporary
browser, which captured the real local app. Two submissions only:

- q03 in the existing dense session: `answered`, one new Gemini generation,
  1129 input/541 output tokens, estimated chat USD0, one Pinecone read and19
  embedding tokens, no repair. Expanded and visually checked the source passage.
- q10 in a separate full Phase2 session: `insufficient_evidence`, expansion/answer
  cache hits, zero new Gemini calls; one dense search (16 embedding tokens/one
  read), one rerank unit, one effective query, no repair. Verified true feature
  flags, actual answer and missing-information display. No ledger/cache reset,
  ingestion or full evaluation rerun. Existing USD3/shared quota guards remained.

Temporary browser and port8502 server were stopped; the original port8501 app
was preserved. These limited browser observations supersede the prior entirely
unperformed visual-walkthrough note, without claiming full browser regression QA.
No credentials were printed or captured; application clients loaded keys normally.

Actual document verification:
- Built with bundled Python3.12/python-docx and rendered using packaged
  `render_docx.py` and bundled LibreOffice. Final18 pages rendered successfully.
- Visually inspected every page. Removed inherited title border, a blank page,
  excess screenshot margins and a missing-font fallback. Re-rendered corrections;
  page-image hashes confirmed unaffected pages were identical to inspected pages.
-10 embedded images,11 tables; all15 exact questions present. No tracked changes,
  comments or paragraph borders. Eight hyperlinks checked against repository
  destinations. Credential-pattern scan of DOCX XML clear; screenshots inspected.
- Packaged accessibility audit:0 high,0 medium,0 low findings.
- Final DOCX SHA256:
  `27d3d6cc32d78cffdca677214acdbdc6de1bdfa5faab5d69dd26813bc6f2d992`.
- No full application tests rerun for this documentation-only change; last
  engineering result remains135 passing tests. Frozen metrics are unchanged.

No remaining document blocker. Next action: user reviews the Word report and
records the prepared4:35 demo, then checks access and submits the chosen files/links.
Video, Google Doc publication and assignment submission have not been performed.
Known q08/q02 answer-quality issues and q04/q11 status disagreements remain visible.
