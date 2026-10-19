# Demo preparation and recording kit

Target: a **4:35 screen recording with your own narration**, leaving 25 seconds
before the assignment's five-minute limit. This kit prepares the recording; it is
not a recorded video. No recording, upload, public deployment or form submission
has been performed.

Start with [the timed script](demo-script.md). For the complete technical reference,
use [architecture.md](../architecture.md). For the assignment documentation, copy
[the project summary](project-summary.md) into your Google Doc and personalize it.
The supplied local Week 2 handout requests a live demo, project documentation and
code/evaluation assets. Verify the submission form's current access requirements
when you actually submit; the kit makes no current deadline claim.

## Files to have open

1. Streamlit app at `http://127.0.0.1:8501` (or its actual printed port).
2. [System overview SVG](../diagrams/system-overview.svg).
3. [LangGraph workflow SVG](../diagrams/langgraph-flow.svg).
4. [Evaluation review](../../eval/results/phase2-review.md), rendered Markdown.
5. [GitHub phase-2 branch](https://github.com/rameshsuthan/runnbook-iq/tree/phase-2).

The [visual gallery](../diagrams/index.html) links five 1920×1080 diagrams. Open
individual SVGs in a browser or PNGs in Preview for a clean recording view. The
seven `.mmd` sources and Mermaid blocks in architecture.md are the detailed
editable diagrams. The gallery uses local files only, with no CDN or API calls.

## Start the correct app profile

From the repository root, stop an older Streamlit process with Ctrl+C in its
terminal, then use:

```sh
RUNBOOK_IQ_CONFIG=config.phase2-repair.yaml uv run streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

This enables hybrid, reranking, multi-query and optional repair. A plain
`uv run streamlit run app.py` loads `config.yaml`, whose feature switches are all
false. Flags are configuration, not decisions made from your question. Submit
again after restarting; a displayed old result is not evidence of a newly used
profile. Do not rebuild/ingest the already-active corpus for the recording.

Optional **offline** preflight:

```sh
uv run runbook-iq --config config.phase2-repair.yaml doctor --offline
uv run pytest -q
```

Doctor deliberately does not load `.env` in offline mode: “missing” shell key
presence is not proof that locally configured `.env` credentials are absent.
The recorded prior test gate was135 passing tests; report your new command's
actual outcome if you choose to run it. Do not run the full live evaluation again.

## One rehearsal

- [ ] Use a clean desktop/browser window and readable app zoom; avoid tiny JSON.
- [ ] Keep `.env`, terminal environment dumps, private diagnostics, notifications
      and unrelated tabs outside the captured area.
- [ ] Use the exact two questions in the script. Rehearsal submissions access real
      services and consume allowance even if generation is cached.
- [ ] Confirm the first result's source passages support the displayed claims.
- [ ] Confirm the inspection flags are true and label actual cache behavior.
- [ ] Confirm the unavailable-current-cause question abstains, or report any failure.
- [ ] Practice switching among app, two visuals, evaluation and repository.
- [ ] Time one spoken pass. Aim for 4:35, not 4:59.

## Record on this Mac

1. Press **Shift–Command–5**, choose **Record Selected Portion**, and frame only the
   app/diagram area. Use a consistent browser window across screen changes.
2. Under **Options**, select the microphone, save location and optionally visible
   mouse clicks. Record a short audio test and listen before the full take.
3. Start recording and follow the script. Stop with the menu-bar Stop control or
   **Command–Control–Esc**. Watch the saved file before sharing it.

These controls follow [Apple's recording instructions](https://support.apple.com/en-us/102618).
No additional recording software is required. Screenshot can also be launched via
QuickTime's New Screen Recording command if preferred.

## What to say when the run differs

| What you see | Honest response |
|---|---|
| Answer cache hit, zero chat tokens | “The answer is cached; retrieval still ran. Pinecone usage is shown separately.” |
| Fewer than three queries | “The original is always retained; alternatives must pass the guards. The cap is three, not a required count.” |
| Feature flags false | Restart with the explicit profile before the take. Do not narrate disabled features as running. |
| Provider/quota/network error | “This live request stopped explicitly.” Stop the experiment; don't upgrade or repeatedly retry. Show a retained result only if clearly labeled recorded. |
| Citation-valid but unsupported answer | State the discrepancy and show the source. Don't call citation validation a truth check. |
| Repair count zero | Explain the edge using the diagram; don't manufacture a model failure. |
| Model answer differs from script | Read the actual answer and adjust your narration. Never narrate an expected value as if it appeared. |

## Final submission checklist

- [ ] Video is no longer than five minutes; voice is audible and sources/flags readable.
- [ ] At least one actual app interaction is shown; cached generation is disclosed.
- [ ] Explain the corpus, RAG workflow, LangGraph role and how AI coding tools helped.
- [ ] Show the known failure and distinguish retrieval recall from answer support.
- [ ] Check video/document/repository access using the intended viewer permissions.
- [ ] Google Doc includes overview, dataset, prompts/instructions, iterations,
      learnings and links. The supplied copy-ready summary covers these headings.
- [ ] Include repository branch and [evaluation report](../../eval/results/phase2-review.md).
- [ ] Upload and submit yourself using the supplied assignment form; no submission
      is made by this kit. You decide which artifacts should be public.

## Optional deeper explanation after the five-minute demo

Use the ingestion diagram to explain canonical versions and atomic publication;
the retrieval diagram for RRF versus reranking; and the cache/usage diagram for the
null values and zero chat tokens you observed. These are appendix visuals; showing
all five in the short recording would crowd out the live demonstration.
