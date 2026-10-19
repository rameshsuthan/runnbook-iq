# RunbookIQ progress

## Current status — 2026-10-18

M1 and the Phase 1 baseline are complete and published on `origin/phase-1` through `e15502e`. Phase 2 design is approved; its nine-task implementation plan is prepared on `phase-2` and awaiting plan review. Gemini remains active; Nebius live verification is deferred. Latest application checkpoint remains prompt/schema v3, 63 passing tests at the prior verification, a full 15-case live report and a separate offline validation audit. Earlier sections are chronological history, not current blockers.

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
