# Phase 1 baseline review — 2026-10-18

## Scope and result

The first checkpoint succeeded: three synthetic documents, real Pinecone retrieval,
and a grounded cited answer through LangGraph (`m1-answer.json`). Phase 1 now has
nine documents, 21 chunks, a CLI, Streamlit, and 15 recorded baseline cases.
This is a runnable learning baseline with measurable answer-quality failures.

The full retrieval-only baseline (`phase1-retrieval.json`) found all expected
sections for all 12 answerable cases: hit@5 **12/12**, macro section recall@5 **1.0**.
The three unanswerable cases are excluded. Source expectations were frozen before
retrieval; no retrieval tuning was performed. The five held-out cases are now seen.

The corrected answer run (`phase1-answers.json`) recorded **6 answered,
2 insufficient_evidence, 7 invalid_output**. Valid citations do not imply complete
answers: q08 omitted requested fields, and q10 gave a supported refusal to diagnose
but incorrectly labeled it answered and left missing_information empty.

## Actual run history and provenance

- Initial full answer run: 15 new calls, 11 invalid_output, 2 answered, 2 abstentions.
  Preserved unchanged in `phase1-answers-initial.json`.
- One guarded diagnostic revealed valid comma-grouped citations were rejected as
  one ID. The deterministic validator was fixed and regression-tested; no model
  repair, retry loop or prompt tuning was added.
- Corrected full run: 11 new calls and 4 cached successes. Seven responses still
  failed validation. Their raw responses were not retained, so their precise
  schema/citation failure categories are **unknown**, not attributed to a specific
  model defect. A separate diagnostic q02 response succeeded; it does not replace
  the recorded failed q02 baseline.
- Both full answer runs used two searches per case: one recorded by evaluation,
  another inside the graph. This was found in final review and fixed. These old
  rows' retrieval fields cannot prove the exact evidence used for generation.
  Their returned cited source passages remain available for manual claim review.
  The independent retrieval-only baseline is unaffected.
- Current answer evaluation records candidates and selected evidence from the
  same graph invocation. A changing-retriever regression proves one search and
  correct evidence provenance. No full live rerun was made solely to rewrite history.
- `final-cache-smoke.json` verifies the reviewed graph against real Pinecone,
  including actual candidates/selection, cached answer, and zero new chat calls.
  `final-empty-fallback.json` verifies real empty retrieval with an explicit
  unmatched filter: insufficient evidence and zero chat calls.

## Manual claim and answer review

Reviewed all 15 recorded outcomes against each returned source passage and frozen
expected points. Structural validation is separate from this semantic review.
No unsupported factual claim was identified in the six returned answered texts;
this is a small manual review, not an automated entailment guarantee.

| Case | Recorded outcome | Manual assessment |
|---|---|---|
| q01 | answered | Supported 500 ms acquisition meaning and pool/waiter/latency checks; requested points covered. |
| q02 | invalid_output | No returned answer to assess; coverage failed. Later diagnostic success does not replace this row. |
| q03 | invalid_output | No returned answer; comparison coverage failed. The separate three-document M1 comparison succeeded. |
| q04 | answered | Supported ambiguity of 503 and requested request/interval/error/process information in checks; missing_information itself empty. |
| q05 | answered | Supported zero automatic stock-reservation retries and outcome/idempotency checks. |
| q06 | invalid_output | No returned answer; historical incident explanation failed. |
| q07 | invalid_output | No returned answer; historical/current comparison failed. |
| q08 | answered | Claims/checks supported by cited runbook, but omitted request_id, trace_id and requested field distinctions. Incomplete answer. |
| q09 | insufficient_evidence | Appropriate abstention: corpus contains no production password. |
| q10 | answered | Correctly says live cause is unknown and asks for current observations. Incorrect status versus expected abstention; missing_information empty. No fabricated diagnosis. |
| q11 | answered | Supported leak/slow-work/concurrency ambiguity, checkout/transaction durations and correlated observations; requested points covered. |
| q12 | invalid_output | No returned answer; configuration values not delivered. |
| q13 | invalid_output | No returned answer; incident timeline not delivered. |
| q14 | invalid_output | No returned answer; missing upstream status explanation failed. |
| q15 | insufficient_evidence | Appropriate abstention: no Kafka offset-reset instructions. |

Answerable cases with supported, substantially complete returned answers: **4/12**
(q01, q04, q05, q11). Supported but incomplete answer: q08. Structurally valid
outputs: **8/15** including two abstentions. Exact abstention status: **2/3**;
all three unavailable-information answers avoided inventing the requested fact.
No threshold or prompt was tuned on held-out results.

## Usage and latency

| Run | New chat calls | Cache hits | Input tokens | Output tokens | Median uncached node time |
|---|---:|---:|---:|---:|---:|
| Initial full answer run | 15 | 0 | 14,208 | 3,167 | 1.319 s |
| Corrected full answer run | 11 | 4 | 10,443 | 2,705 | 1.336 s |

Node time excludes client composition, evaluation's extra search and inter-case
pauses. Cached timing is excluded. Gemini output totals include reasoning when
reported by the integration; separate reasoning counts were unavailable.

Session ledger: **31 reserved request attempts**, 29 with known token usage,
2 model-not-found attempts with unknown usage; **27,607 input / 6,770 output**
known tokens. The 31 include M1, both full runs and two guarded validation
diagnostics. Estimated paid cost and outstanding dollar reservations are **USD 0**
on the user-confirmed free route. This is not an account invoice audit. Pinecone
Starter embedding/search usage is separate and locally recorded. No plan upgrade,
paid fallback, repair loop or Phase 2 feature was enabled.

## Final verification and remaining limitations

- 49 offline tests pass; network is prohibited in ordinary tests.
- Locked offline dependency sync passes (89 packages, Python 3.12).
- Independent review: three Important issues fixed with observed RED→GREEN tests:
  fence preservation, ingestion destination binding and evaluation provenance.
- Existing 21 remote records were fetched and matched before migrating the local
  destination binding. Unchanged ingestion then skipped 21 records with zero writes.
- Fence parser fingerprint is now sections-v2. Existing baseline used sections-v1;
  the current corpus's text/IDs are unaffected. A future rebuild changes the version
  and requires explicit ingestion; old results are retained with their original version.
- Streamlit AppTest verified submission/rerun behavior and rendered the saved live
  M1 answer with two inspectable passages. Native visual browser QA is unverified
  because no browser was available. No video was recorded; a demo outline exists.
- Adversarial fixture verifies untrusted text stays in the human evidence payload,
  separate from the system instruction, and simulated abstention is accepted.
  This does not establish real-model prompt-injection resistance.
- Deferred minor: setup/cache failures on the generation path may overcount one
  attempted chat call; unknown token usage remains unknown. No paid path is enabled.

Next focused quality task: preserve safe validation categories and synthetic rejected
outputs in an opt-in local diagnostic, then investigate the seven failures and
q08/q10 behavior on development cases. Do not add advanced retrieval or retry logic
as a substitute for understanding this baseline. Phase 2 remains unimplemented.
