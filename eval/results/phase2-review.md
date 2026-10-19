# Phase 2 Gemini comparison and source review

The advanced retrieval features are runnable, but these experiments do not show
a quality gain. All four retrieval arms already find every frozen expected section
for the 12 answerable cases. A final answer incorrectly denies documented telemetry
fields (q08). Keep the dense default and treat advanced profiles as learning and
inspection tools, not evidence of more reliable answers.

## Experiment identity and service interruption

Nine synthetic documents, 21 canonical chunks, existing sections-v1 active corpus;
no reingestion. Fifteen previously observed cases, unchanged expected statuses,
Gemini `gemini-3.5-flash-lite`, prompt `incident-evidence-v3`, schema `answer-v3`.
The [prospective rubric](../phase2-rubric.md) separates coverage, support, citation
support, clarification and exact status agreement. No answer tuning was performed.

The [retrieval comparison](phase2-retrieval-comparison.json) hashes the retained
dense, hybrid, hybrid+rerank and hybrid+rerank+multi-query reports. All share corpus,
questions and prompt identities. Fused and selected hit/recall@5, and pool recall@15,
are 1.0 for the 12 answerable cases in each arm. Unanswerable cases are excluded.
Earlier arms predate full operation metadata; missing usage is not reconstructed.

Final answers use `config.phase2-repair.yaml`, with cached query expansions required.
The [first run](phase2-final-answers.json) stopped on q06's first dense search after
q01–q05 completed. Its attempted search has unknown units; its local reservation
remains held. No q06 chat call occurred. Local counters were below configured caps.
The safe error did not retain the provider-side cause, so it remains unclassified.
One explicit [continuation](phase2-final-answers-continuation.json) began at q06;
q06 succeeded. This is a resumed experiment, not a clean uninterrupted run.
Do not erase the failed attempt or count it as a successful answer.

Each report records source commit, dirty flag and source tree hash, rubric hash,
full nonsecret configuration and exact query sets. Request latency includes graph
invocation; client composition and intentional 15-second pauses are separate.
Recorded expansion cache hits mean these are not fully cold end-to-end runs.

## Manual review of actual selected sources

This is the implementing assistant's source review, not a separate human rating
or a model-based entailment score. Citation identifiers are structurally checked
by code; the judgments below additionally inspect the claims against passages.

| Case | Coverage and source support | Status / clarification |
|---|---|---|
| q01 | 500 ms pool wait and all three per-process metrics supported by the error reference and pool checks. | Matches; no live cause claimed. |
| q02 | Correct 1500 ms deadline and supported checks. Omits expected caveat that the error alone does not establish cause. | Matches, but incomplete coverage remains. |
| q03 | Both wait types/deadlines, separate metrics/spans and connection checkout checks supported. | Matches; describes documented signals. |
| q04 | 503 ambiguity and pool-contention caveat supported; asks for request ID, interval, identifier and process. | Conservative abstention differs from frozen `answered`. |
| q05 | Zero automatic stock retries, possible prior reservation, outcome and idempotency checks supported. | Matches. |
| q06 | September release, held connections, rollback and acquisition-order fix supported by timeline/findings; historical scope retained. | Matches on continuation; first attempt was a retrieval failure. |
| q07 | Historical 12 versus current 20, separate capacity review and revision/process checks supported. | Matches. |
| q08 | **Fails support and coverage:** says specific correlation fields are undocumented although selected telemetry guide explicitly gives request_id/trace_id and timing meanings. Checks partly repeat valid metrics but omit trace_id and meanings. Citations resolve but do not support the denial. | Incorrect abstention and fabricated missing-information claim. |
| q09 | Correctly says passwords are outside corpus; no unsupported vault advice. “None can be performed” is read within the stated corpus scope, not a universal claim about credential recovery. | Appropriate abstention; no secret invented. |
| q10 | Live observations unavailable; historical examples do not diagnose current events. Process/interval/metrics/trace checks supported. | Appropriate abstention with missing observations named. |
| q11 | Durations, checkout, concurrency and trace/pool checks supported. Definitive discriminating criteria are not supplied; the answer overemphasizes this instead of simply answering with documented checks. | Conservative abstention differs from frozen `answered`; useful checks retained. |
| q12 | Current 20 connections, 500 ms acquisition and 1500 ms inventory limits supported and correctly scoped. | Matches. |
| q13 | Historical route revert 14:12 UTC and recovery 14:20 UTC supported; correlation statement is historical. | Matches. |
| q14 | Missing HTTP status does not prove no stock reserved; outcome, trace and idempotency checks supported. | Matches; does not assert an actual outcome. |
| q15 | No Kafka command or related checks exist in selected evidence; no command invented. | Appropriate abstention after one live repair. |

[Final summary](phase2-final-summary.json): 9 answers, 6 abstentions, 12/15 exact
status matches across completed cases. Counting first attempts instead gives
8 answers, 6 abstentions, one retrieval error and 11/15 status matches. Completed
selected recall is 1.0; first-attempt recall is 11/12 because q06 failed. Across
both runs: 16 chat calls (15 generate, one repair), 17,064 input/5,843 output tokens,
estimated USD0, zero expansion calls, 16 expansion cache hits, 38 successful dense
searches plus one failed attempt, and 15 reranks. Unknown Pinecone units are not
converted to zero. All answers were generated fresh; expansions were cached.
Completed request latency is 1.62–4.45 seconds, median 2.23 seconds. This is not a
fully cold benchmark and does not imply a speed improvement across older arms.

The earlier Phase 1 v3 report remains unchanged (10 answers, 5 abstentions, 13/15
status matches). Its [supplemental rubric mapping](phase1-v3-prospective-rubric.json)
retains q02's omission, q04/q11's conservative statuses and q09's unsupported advice.
Phase 2 fixes neither completeness nor semantic grounding by construction. Small
stochastic changes across previously seen questions cannot establish generalization.

## Repair, provider and inspection boundaries

Injected-response tests prove invalid→valid, invalid→invalid termination, budget
denial, provider failure, invalid-cache refusal and maximum three chat attempts.
Repair validates schema/citation structure; it does not detect q08's semantic error.
q15 naturally took one live repair call and ended in a structurally valid,
source-supported abstention; both calls and repair count are recorded. The initial
rejected raw response/error category was not retained in the final artifact, so no
more specific claim about its defect is made. No forced live failure or additional
model-based grading was introduced.

Nebius adapter is offline-tested only. User deferred readiness; exact accessible
model, verified rates, provider-enforced billable bounds, one structured response
and one cited graph answer remain required. Phase 2 is not fully accepted yet.

Streamlit AppTest verifies inspection and reruns without new submissions. Native
visual inspection was not performed; no enabled structured browser was exposed.
The [4:30 demo outline](../../docs/demo-outline.md) is written; no video was recorded.

## Final engineering review

[Independent review](../../docs/phase2-code-review.md) found protected-token,
cached token-limit and malformed-hit accounting defects. All were fixed with six
RED→GREEN regression cases; the full suite passes135 tests. The
[post-review offline audit](phase2-post-review-audit.json) confirms all15 exact query
sets remain valid under the stricter guards. The live answers above were produced
before these fixes and retain their original source hashes. No live rerun was made.
