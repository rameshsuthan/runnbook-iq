# Phase 2 Native execution record

Gemini implementation, fixed evaluation, independent review and branch publication
are complete. Nebius live acceptance remains incomplete by user readiness; this is
not full Phase2 acceptance. The chronological ledger below records decisions and
observed checks; earlier pending lines describe their original checkpoints.

# SDD ledger — plan: docs/superpowers/plans/2026-10-18-phase-2.md
Spec and plan approved; Native execution confirmed. Baseline HEAD 95d2ed0; 63 offline tests pass.
Ruling: execute in existing dedicated phase-2 checkout, as allowed by approved plan — local active snapshot, keys and shared USD3 ledger must remain visible — risk is concurrent edits, mitigated by explicit staging and preserving user files.
Pre-flight: 1→2 Candidate provenance / pipeline: compatible additive field.
Pre-flight: 2→3 batch/selection gain default operations; canonical pipeline retained.
Pre-flight: 3→4 usage and quota records used by reranker; no repeated search.
Pre-flight: 3→5→6 operation-aware providers used by expansion and repair; counters at invocation boundary.
Pre-flight: 5→7 ModelRoute and structured interface support explicit Nebius route; unavailable live access does not block other tasks.
Pre-flight: 2,3,5,6→8,9 results and evaluation use same pipeline and current operations.
Tasks 1–9 pending; Task 7 live acceptance deferred by user readiness.
Task 1: complete (commits 95d2ed0..22a3d7f, tests: .venv/bin/pytest -q tests/test_keyword.py tests/test_fusion.py tests/test_retrieval.py → 8 passed in 0.05s)
Task 2: Ruling: retain dense-only legacy retriever support in build_graph — preserves old tests and simple public adapters while production uses mandatory snapshot-verified pipeline — risk: two dispatch paths; feature activation rejects legacy hybrid use and tests cover both.
Task 2: Ruling: retrieve CLI now emits a RunResult including selected evidence — required for inspectable shared graph prefix — consumers of the old bare list must use retrieved_candidates; README will document the change.
Task 2 offline: seven added tests RED then 26 targeted PASS; full suite 77 PASS. Live comparison in progress.
Task 2: complete (commits 22a3d7f..9b7b721, tests: .venv/bin/pytest -q → 77 passed in 0.72s)

Task 3: Ruling: normalize post-invocation snapshot/parse failures to safe CallFailure carrying previous operations — the old ValueError assertion failed because this deliberately changes exception type, not failure behavior — callers must catch the normalized type; graph does.
Task 3: Ruling: local read-unit quota is response-based monitoring, not a preflight billable maximum — Pinecone does not give an enforced per-query read bound here — unknown units stay visible and account quota remains authoritative.
Task 3: complete (commits 9b7b721..716115b, tests: .venv/bin/pytest -q → 85 passed in 0.69s)

Task 4: Ruling: disable Pinecone SDK 8 transport retries via its private configuration before lazy transports initialize — SDK constructor silently lacks a retry setting and defaults to five retries — risk is SDK compatibility, guarded by an actual inference/index transport test and pinned dependency. SDK normalizes integer zero to Retry(total=0); test asserts the effective total.
Task 4: complete (commits 716115b..91b258b, tests: .venv/bin/pytest -q → 94 passed in 0.66s)
Task 5 audit script initially summed a cache-hit unknown token field; no product error. Commit did not occur, so premature task-done line removed; complete only after corrected audit and commit.
Task 5: complete (commits 91b258b..9579397, tests: .venv/bin/pytest -q → 107 passed in 0.77s)
Task 6: Ruling: put sequence-provider repair cases in tests/test_repair.py instead of enlarging test_graph.py — isolated test fixture responsibility — no behavioral scope change.
Task 6: complete (commits 9579397..5e0106f, tests: .venv/bin/pytest -q → 113 passed in 0.70s)

Task 7: offline implementation complete; 124 offline tests pass. Live acceptance deferred by explicit user readiness; do not mark full Phase 2 complete.
Task 7: Ruling: continue Tasks 8–9 with Gemini while leaving live Nebius acceptance unchecked — explicitly approved design fallback — cost is incomplete second-provider verification, prominently recorded.
Task 9 preflight finding: newly added nullable context_window_tokens changes full-route expansion-cache hashes; preserve identity for unset field before frozen-query comparisons, with regression test.
Task 8: complete (commits 69bc3d6..3b4da08, tests: .venv/bin/pytest -q tests/test_app.py → 3 passed in 0.40s)

Task 9: Ruling: preserve the stopped q01–q06 report and run one explicit q06–q15 continuation with required cached expansions — local quotas remain below caps, no automatic retry, and q06 succeeded on continuation — cost is one extra failed search with unknown units; initial failure remains in attempt-level reporting.

Final review: fresh read-only gpt-6-astra reviewer, base e15502e..f408c08, independently ran129 passing tests and checked all five Review Focus items. No Critical findings; two Important expansion defects and one Minor operation-loss finding. Verdict with fixes. No re-review dispatched.
Final: Ruling: regrade malformed-hit operation loss as Important — losing known completed usage violates the promised audit trail despite a rare malformed response — cost if wrong is a small amount of additional failure-path handling, covered by a regression.
Final: fixed protected-token extensions — test_expansion_rejects_extended_identifiers_and_numbers (three cases) RED→GREEN, suite135/135.
Final: fixed cached alternatives bypassing current embedding limits — test_cached_expansion_rechecks_current_embedding_limit (ordinary/required modes) RED→GREEN, suite135/135. Ordinary mode returns original-only with warning; required mode stops before retrieval. No expansion regeneration.
Final: fixed completed search usage loss on canonical normalization failure — test_malformed_canonical_hit_preserves_completed_search_usage RED→GREEN, suite135/135. Both earlier and failed normalization operations retain known units; raw errors remain private.
Final: Ruling: Nebius live compatibility/prices/bounds remain unaccepted — user explicitly deferred readiness; offline adapter tests cannot establish live behavior — cost is an incomplete second-provider milestone, clearly blocked until verification.
Final: Ruling: retain q08 semantic failure and lexical-guard limitations without adding a semantic judge — frozen comparison and approved scope prohibit unplanned answer tuning/judging — risk is structurally valid but factually wrong answers; source review makes that limitation explicit.
Final: Ruling: retain local Pinecone response-based read monitoring — no verified provider-enforced per-request read maximum, and counts exclude other project usage — risk is account quota exhaustion; free Starter entitlement remains a user assertion, not an invoice guarantee.
Final: Ruling: accept AppTest evidence without a visual-appearance claim — structured browser control was unavailable — cost is possible unobserved visual defects; native visual validation remains unperformed.
Final: Ruling: defer deployment/authentication/large-corpus scalability — approved application remains local and synthetic — cost is that this branch is not production-ready beyond that boundary.
Final: deferred minors: none; sole reviewer Minor was regraded and fixed for audit-trail correctness.
Post-review offline replay:15 exact cached query sets unchanged using the real pinned embedding tokenizer; provider invocation forbidden; zero API calls. Saved15 final answers pass structural validation. Live reports retain pre-review hashes; no new live run is claimed.
Task 9: complete (commits 3b4da08..4cab6fc, tests: .venv/bin/pytest -q → 135 passed in 1.44s)

Publication: origin/phase-2 verified at4cab6fcffd5c4033ffe556c02fc1ae1d9faea21e; origin/phase-1 remains e15502eda4dac8217b067cebde41da09c2b6ca1c. Final Task9 completion gate135 passed in1.44s. This record is archived before deleting only this plan's scratch workspace. Task7 live acceptance remains incomplete; no paid/Nebius calls were made. Final documentation-only commit follows the verified implementation publication.
