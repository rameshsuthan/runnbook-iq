# RunbookIQ demo script — target 4:35, hard limit 5:00

Read only the blockquoted narration. Screen actions are stage directions, not
spoken text. Speak at about 120–135 words/minute and leave time for clicks. Rehearse
once with a timer; actual narration pace and service latency determine duration.

## 0:00–0:20 · Purpose

**Screen:** Streamlit home page. Keep the question and button visible.

> RunbookIQ helps engineers answer troubleshooting questions from synthetic
> runbooks and incident reports. It finds documented checks, shows cited sources,
> and explains missing information. It cannot inspect a live system or perform
> remediation.

## 0:20–0:50 · Architecture

**Screen:** [System overview](../diagrams/system-overview.svg). Point to the local
snapshot, LangGraph, Pinecone and Gemini. Do not tour every component.

> The corpus contains nine Markdown documents and twenty-one canonical chunks.
> Explicit ingestion sends text to Pinecone for integrated embeddings. Local BM25
> uses the same chunks. LangGraph orchestrates the question workflow, and Gemini
> generates structured answers. Caches and usage ledgers stay local. Ingestion is
> separate: asking a question never rebuilds the index.

## 0:50–1:45 · Demonstrate an answer and verify its sources

**Screen:** Return to Streamlit. Paste this exact question and click **Find evidence**:

```text
What documented checks distinguish database pool exhaustion from an inventory dependency timeout in order-api?
```

Read what the app actually returns before speaking. Show the two deadline values,
then open a pool-runbook source and a dependency-runbook source. If the result
fails or omits something, use the contingency wording in README.md rather than
claiming it showed the expected behavior.

> This question spans two runbooks. The documented distinction is a five-hundred
> millisecond wait for a database pool slot versus a fifteen-hundred millisecond
> inventory request deadline. The answer should identify the different metrics and
> spans to inspect. I can open each citation and compare the claim with its source.
> Neither error code alone establishes the underlying cause.

## 1:45–2:20 · Explain retrieval and caching

**Screen:** Expand **Retrieval inspection**, then **Usage and timing**. Highlight
true feature flags, query variants, selected IDs and the actual cache statuses.
Do not scroll through every candidate. Use this narration for either a fresh or
cached response; add the applicable short line below.

> This explicit Phase Two profile enables hybrid retrieval, reranking and
> multi-query. BM25 finds exact terms; dense search finds semantic matches. RRF
> combines their ranks, then BGE selects up to five passages. Inspection shows what
> actually ran. Chat usage and Pinecone units are separate, so zero new Gemini
> tokens can still accompany retrieval work.

**Choose only if observed:** “This answer was cached.” Or: “This request made a
fresh generation call.” A cached answer is not a fresh model-generation demo.

## 2:20–2:55 · Explain LangGraph and bounded repair

**Screen:** [Question workflow](../diagrams/langgraph-flow.svg). Trace the main path
and the repair loop. Do not force an invalid response during the recording.

> In LangGraph, state carries the question, evidence and operations. Nodes return
> state updates, and conditional edges choose the next step. Fresh output is
> validated for schema and citation IDs. If enabled, one repair can reuse the same
> question and evidence. A second invalid result stops. This validates structure,
> not the truth of every claim.

## 2:55–3:25 · Demonstrate an unavailable answer

**Screen:** Return to the app and submit:

```text
What is the confirmed root cause of our live incident right now?
```

Show **insufficient evidence** and missing observations if that is the actual result.

> This question requests a live fact the corpus cannot establish. The expected
> behavior is an explicit abstention with the current observations that are
> missing. Historical incidents can suggest investigative checks, but they cannot
> prove what is happening now.

## 3:25–4:10 · Show measured outcomes and a real limitation

**Screen:** Open [evaluation source review](../../eval/results/phase2-review.md).
Show the comparison summary and q08 row. These are recorded results, not this
recording's live requests. Keep the text large enough to read.

> I evaluated fifteen fixed questions. All four retrieval configurations found
> every expected section for the twelve answerable cases, so I cannot claim a
> retrieval improvement. The completed answer results matched twelve of fifteen
> expected statuses; first attempts matched eleven because one search failed.
> One answer incorrectly denied fields present in its evidence. That failure is
> preserved: valid citation IDs do not guarantee semantic support.

## 4:10–4:35 · Engineering, AI assistance and close

**Screen:** GitHub `phase-2` README or local project summary. Keep the repo and
report links visible; no credentials, account dashboard or terminal environment.

> I used Codex to implement small runnable milestones, explain LangGraph decisions
> and develop regression tests. Independent review found three edge defects that
> were fixed. The last application test gate passed one hundred thirty-five tests.
> The project keeps an estimated three-dollar usage guard, explicit failures and
> recorded limitations. Nebius is optional future work.

## Delivery notes

- The script describes actual implemented behavior and retained experiments. It
  does not claim a human-scored faithfulness percentage or generalization to unseen
  questions. All fifteen evaluation cases have already been observed.
- One real q15 evaluation needed a repair and ended in a supported abstention. If
  asked, show the saved continuation report's `repair_attempts: 1`; this is a
  recorded example. The initial rejected raw output was not retained.
- Two live question submissions can make up to six chat attempts if both caches
  miss and both outputs require repair, plus up to six dense searches/two reranks.
  Cache hits usually reduce calls but are not guaranteed. Do not clear caches or
  reset ledgers to manufacture a cold run. No new API calls were made to write this
  script or render its visuals.
- If the first take exceeds five minutes, cut the RRF explanation to one sentence
  and shorten the source expansion. Keep the live question, abstention, honest
  results and AI-assistance disclosure.
