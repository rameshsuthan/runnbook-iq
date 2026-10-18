# SDD ledger — plan: docs/superpowers/plans/2026-10-18-phase-1.md
Execution: native, approved 2026-10-18.
Ruling: initialize the new repository in place on phase-1 — no existing branch/work to isolate — no existing application is put at risk.
Ruling: Git has no configured author identity; defer commits and script helpers requiring HEAD rather than invent identity — files and tests remain available; history checkpoints pending.
Pre-flight: Tasks 1→2/3/4/5 share Settings/schema; compatible.
Pre-flight: Tasks 2→4 share CorpusSnapshot; compatible.
Pre-flight: Tasks 3/4→5 share provider/cache/retriever; compatible after planning correction.
Pre-flight: Tasks 5→6/7 share RunResult/compiled graph; compatible.
Pre-flight: Tasks 6/7→8 share results/UI; compatible.
Task 1: started. Four tests RED due to missing config/CLI modules. Python 3.12 lock/install succeeded (65 packages). Git init required escalation and succeeded.
Task 1: offline implementation verified — four tests RED→GREEN; doctor lists key presence only. Commit blocked by absent author identity.
Task 2: offline implementation verified — four tests RED→GREEN; real pinned tokenizer built 3 docs / 9 chunks, largest 122 conservative tokens. No inference calls.
Task 3: seven tests RED; first implementation had two import failures. Root cause: tracing_context is exported by langsmith, not langchain_core.tracers.context; corrected against installed SDK.
Ruling: selected free-tier provider route only; paid calls explicitly fail closed until model-specific billing/token bounds are verified — prevents speculative billing with unknown prices — paid-tier use requires that follow-up.
Tasks 3–5 offline checks: 32 tests GREEN; no live success claimed. Task 4 integration is in pinecone_store.py to isolate SDK payloads from synchronization. SDK field_map and truncate parameters inspected in installed package.
M1 complete: real 9-chunk ingestion, expected evidence at ranks 1/2, cited Gemini 3.5 Flash-Lite answer reviewed, repeated ingest 0 upserts. 34 tests pass. Artifacts in eval/results/m1-*.json.
Ruling: Gemini 2.5 Flash-Lite listed but returned 404; explicit model change to Gemini 3.5 Flash-Lite free tier — verified public free pricing and live generation — model response may differ, tracked with exact ID/config.
Ruling: Gemini 3.5 uses provider sampling defaults and minimal thinking, not temperature=0/legacy thinking budget — installed SDK warning/source evidence — reproducibility is observational, not deterministic.
Ruling: accept comma-grouped inline citation IDs while validating each ID against evidence — live diagnostic revealed valid grouped references were rejected — no claim-grounding guarantee is added; malformed/unknown IDs still fail.
Tasks 6–7: implemented UI and frozen 15-case evaluation; 40 offline tests pass after grouped-citation regression RED→GREEN. First full answer baseline retained as phase1-answers-initial.json: 11 invalid_output, 2 answered, 2 insufficient_evidence. One guarded diagnostic isolated the parser defect. No generation repair/retry was added.
Final review: one fresh-context reviewer (gpt-6-astra), read-only; independently ran 40 tests. Three Important findings accepted; no Critical findings.
Final: fixed fenced Markdown corruption — indented/long/adjacent fence regressions RED→GREEN; parser uses one fence grammar; splitter fingerprint advances to sections-v2.
Final: fixed destination-unbound ingestion — namespace/index/host and pending-journal regressions RED→GREEN; destination.json is checked before reads or mutation; legacy state requires verified migration.
Final: fixed duplicate evaluation retrieval — changing-retriever regression RED→GREEN; RunResult retains actual candidates/selected evidence, answer evaluation uses the one graph invocation.
Final suite: 49/49 pass. Adversarial-source fixture verifies system/data boundary and simulated abstention, not live injection immunity. Saved live M1 result rendered through Streamlit AppTest: two inspectable source passages; no service calls.
Final: minor (deferred): generation-path setup/cache errors can overcount one attempted chat call; token usage remains unknown and no paid request is enabled.
Final: Ruling: production multi-user/distributed/power-loss guarantees remain out of scope — local synthetic app with process locks only — concurrent deployment would require stronger isolation/durability.
Final: Ruling: account tier comes from user confirmation plus public model documentation; no billing API assertion — free-only route remains explicit — external account billing changes require rechecking configuration.
Final: Ruling: parent manually reviews real answers and completes docs; reviewer did not assess their semantic grounding — reviewed claim support is recorded separately — small synthetic samples do not establish production quality.
Final: Ruling: paid model requests stay disabled — approved fail-closed route — paid experimentation requires verified rates/token bounds later.
Ruling: preserve the actual pre-provenance-fix answer baseline with its two-search limitation, not another full generation run — quota conservation and honest history — retrieval-only metrics and cited-source manual review remain separately interpretable.
Ruling: consolidate deferred task commits into one reviewed Phase 1 baseline commit after the user supplied author identity — no author was invented and no work is lost — history has fewer runnable intermediate commits than planned.
Ruling: retain the local phase-1 branch without publication — new root repository has no base branch and the plan excludes implied GitHub publishing — user decides when to publish.
Task 1: complete; actual evidence in PROGRESS.md and phase1-review.md; consolidated baseline commit 82de23b.
Task 2: complete; actual evidence in PROGRESS.md and phase1-review.md; consolidated baseline commit 82de23b.
Task 3: complete; actual evidence in PROGRESS.md and phase1-review.md; consolidated baseline commit 82de23b.
Task 4: complete; actual evidence in PROGRESS.md and phase1-review.md; consolidated baseline commit 82de23b.
Task 5: complete; actual evidence in PROGRESS.md and phase1-review.md; consolidated baseline commit 82de23b.
Task 6: complete; actual evidence in PROGRESS.md and phase1-review.md; consolidated baseline commit 82de23b.
Task 7: complete; actual evidence in PROGRESS.md and phase1-review.md; consolidated baseline commit 82de23b.
Task 8: complete; actual evidence in PROGRESS.md and phase1-review.md; consolidated baseline commit 82de23b.
