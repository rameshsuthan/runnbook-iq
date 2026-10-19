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

## Targeted development follow-up — prompt v2, 2026-10-18

After preserving the baseline in Git, one uncached q06 diagnostic reproduced an
actual cause: its response listed valid source IDs but had **no inline citations**.
This is a correctly rejected model output, unlike the earlier comma-group parser
bug. Raw synthetic diagnostic data stays in ignored local storage.

The validator now reports value-free categories (including
`missing_inline_citations`, `citation_mismatch`, `invalid_schema` and
`incomplete_response`). The CLI offers explicit `--save-invalid-response` for
local mode-0600 files containing the failed response and exact evidence, without
serializing clients, headers or environment variables. Default output excludes the
raw rejected answer. No automatic repair/retry was introduced.

Prompt `incident-evidence-v2` and schema guidance clarify inline citations,
requested-fact coverage and unknown-live-cause status. Prompt/schema cache versions
changed so previous answers cannot mask the new behavior. Three development cases
were run once each; results are in `phase1-followup-v2.json`:

| Case | Outcome | Source review |
|---|---|---|
| q06 | answered | Inline citations now present; historical cause/correction supported and requested points covered. |
| q08 | answered | Citation supported, but still incomplete: omitted requested correlation/telemetry fields. Selected evidence contains them. |
| q10 | insufficient_evidence | Correct status, supported uncertainty, explicit missing current observations. |

All three passed structural validation; **two of three** met the substantive
expectations. This is targeted development verification, not a new 15-case score
or evidence that all seven original failures are fixed. The old baseline is intact.

This continuation used four new generation calls: one diagnostic, then three
follow-up cases (3,212 input / 821 output tokens for the follow-up). A q03 check
used the existing cache and made no generation call. Estimated paid usage remains
USD 0. At the final snapshot the local ledger had 38 attempts, 36 known usage
records and two older unknown outcomes; it also includes user runs between turns.

Verification: 60 offline tests pass, including all eight validation categories,
no raw-response leakage in normal results, opt-in diagnostic permissions, and
unchanged one-call graph termination. CLI help exposes the diagnostic flag.
The next quality issue is q08's incomplete use of already-retrieved evidence;
additional prompt changes or Phase 2 retrieval must not be claimed as fixes until
measured. No full answer rerun or Phase 2 implementation was performed.

## Telemetry correction and full v3 baseline — 2026-10-18

q08's relevant telemetry passages were already selected at ranks 1 and 5. Two
single-call experiments reused that exact evidence. Moving the question to the
end improved measurement-field coverage but still omitted correlation IDs; that
layout change was rejected. A clearer `documented_evidence` schema description
explicitly requesting exact field names and meanings covered all expected fields.
No literal expected answer or field name was added to the production prompt.
Both experiments are retained in `q08-coverage-experiments.json`.

The adopted production change is the schema description, with prompt/schema cache
versions advanced to v3; system text, message layout, model, retrieval and call
bounds are unchanged. The actual graph follow-up q01/q08/q10 met all three
substantive expectations (`phase1-followup-v3.json`). The original q08 name-coverage
check failed for request_id, trace_id, db_pool_acquire_ms and inventory_request_ms;
the graph's new answer passed, and source review verified their meanings and the
same-window/process constraint. These observations are not a guarantee of future
model behavior.

A final full run used the frozen 15 cases once, with three v3 cache hits and twelve
new calls (`phase1-baseline-v3.json`). It recorded **10 answered / 5 insufficient_evidence**
and no generation-format failures under the validator at run time. Retrieval
hit@5 and macro section recall@5 remain **1.0 across 12 answerable cases**. Exact
status agreement was **13/15**. Full per-case assistant source review is attached
to the JSON rows; remaining discrepancies are deliberately preserved:

| Case | Finding |
|---|---|
| q02 | Correct deadline and checks; omits the frozen expected caveat that the error alone does not establish cause. |
| q04 | Correctly explains 503 ambiguity and asks for observations, but abstains rather than returning the frozen expected answered status. |
| q09 | Correctly withholds the unavailable password, but recommends a vault/environment secret manager absent from the sources and without a citation. |
| q11 | Gives documented duration/concurrency/traces checks while noting missing definitive criteria; abstains rather than returning the frozen expected answered status. |

q04 and q11 reveal a status-rubric distinction between providing documented checks
and claiming a live diagnosis. The original expectations are unchanged; clarify
that distinction prospectively before interpreting later comparative scores.
q08 now covers the expected fields. No false live diagnosis was found in source
review. q09's unsupported recommendation is a real grounding failure despite its
otherwise appropriate abstention.

### Section-level citation hardening after the run

The q09 output exposed a validation gap: a cited evidence section allowed an
entirely uncited checks section. Every nonempty evidence/checks section now needs
its own inline citation. Three regression tests failed first and then passed,
including rejection of an old cached answer without another model call. The
full offline suite now has **63 passing tests**.

An offline replay of the 15 saved answer bodies against their exact selected
evidence accepted **14** and rejected **q09** as `missing_inline_citations`; no
service calls or regenerated answers were involved. See
`phase1-baseline-v3-validation-audit.json`, which records the source report hash.
The full live run predates this additional validation, so do not describe the
14/15 replay result as a newly generated baseline. Real IDs and a citation in each
section still do not establish sentence-by-sentence entailment or completeness.

### Usage and verification

The full v3 run used **12 new calls**, 3 cache hits, **12,977 input / 4,309 output**
known tokens. Median uncached summed node time was **1.815 seconds**, excluding
composition and pauses. This continuation used **17 new generation calls total**:
two experiments, three targeted graph checks and twelve full-baseline calls.
Combined known usage for those calls: **18,505 input / 6,267 output** tokens.
Estimated paid usage remains USD 0 on the user-confirmed free route.

Local ledger snapshot: 56 attempts, 54 known usage records, two earlier unknown
outcomes; 54,102 input / 15,636 output known tokens, USD 0 estimated paid usage.
The ledger also includes user activity; it is not a provider invoice audit.
No paid fallback, repair loop, Phase 2 feature, or model upgrade was added.
