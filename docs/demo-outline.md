# RunbookIQ demo outline (4 minutes 30 seconds)

- **0:00–0:30 — Purpose and boundaries.** Introduce the fictional order service and
  two incident categories. Explain that the app recommends documented checks;
  it neither diagnoses live systems nor executes actions.
- **0:30–1:10 — Corpus and ingestion.** Show a runbook and historical incident,
  canonical metadata/IDs and the explicit ingestion command. Mention Pinecone
  integrated embeddings and unchanged-ingestion idempotence.
- **1:10–2:00 — Live question.** Ask what distinguishes pool exhaustion from an
  inventory timeout. Expand cited sources and compare the 500 ms and 1500 ms
  meanings with the returned checks. If the response is cached, say so.
- **2:00–2:40 — LangGraph lesson.** Open `graph.py`; explain state, node updates,
  conditional fallback, one bounded generation call and citation validation.
- **2:40–3:15 — Unavailable information.** Ask for a current root cause or a
  production password; show abstention and missing information. Explain why
  retrieved passages alone do not establish answerability.
- **3:15–4:00 — Evaluation.** Show the actual 15-case report, denominators, held-out
  split, failures and manual claim support. Avoid claiming synthetic success means
  production readiness. Mention the model-list/generation availability mismatch.
- **4:00–4:30 — Engineering and next phase.** Explain how AI assistance was used
  for implementation and tests, how results were checked, credential privacy and
  the persistent budget guard. Outline the planned Phase 2 comparisons without
  claiming those features exist.

Never show `.env`, API console key values, or private account screens. This is an
outline; no video has been recorded by the agent.
