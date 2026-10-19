# RunbookIQ demo outline (4 minutes 30 seconds)

- **0:00–0:25 — Purpose.** Fictional order service, database pool waits and inventory
  timeouts. Recommend documented checks; never claim access to live systems.
- **0:25–0:55 — Evidence.** Show a runbook and historical incident, canonical chunk
  IDs and explicit ingestion. Pinecone dense and local BM25 share the same chunks.
- **0:55–1:45 — One question.** Use the multi-query profile and ask how to distinguish
  the two wait types. Expand sources; verify the 500 ms / 1500 ms meanings. Show
  queries, retrieval provenance, RRF scores and reranked selection in inspection.
  State whether expansion/answer came from cache; do not hide current request usage.
- **1:45–2:35 — LangGraph lesson.** State is data; nodes return updates; conditional
  edges select fallback, validation or repair. Show the one-repair counter and a
  saved deterministic failure test. END is termination, not proof of correctness.
- **2:35–3:00 — Missing information.** Use a saved unavailable-fact example or submit
  once; show abstention and missing observations. Explain that passage relevance
  and citation-ID validity do not prove every generated claim.
- **3:00–3:55 — Measured comparisons.** Show all four fixed retrieval configurations:
  dense, hybrid, reranked hybrid and multi-query reranked hybrid. The small corpus
  already had full expected-section recall; advanced retrieval showed no recall
  gain. Show actual final answer failures/status differences and manual source review.
  All 15 cases have been observed; none is a fresh unseen test now.
- **3:55–4:30 — Engineering and limits.** Persistent USD3 guard, unknown-usage
  reservations, zero SDK retries, bounded calls, and offline tests. Gemini is live;
  Nebius adapter is offline-tested and live verification remains pending. Mention
  how AI-assisted implementation was checked with tests, services and code review.

Use retained synthetic results when time or free-tier quota is tight. Never show
.env, rejected private diagnostics, key values, or private account screens. This
is an outline; no video has been recorded by the agent.
