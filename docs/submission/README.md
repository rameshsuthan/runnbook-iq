# Submission document

`RunbookIQ-Project-Submission.docx` is the requested Word deliverable. It covers
implemented architecture, five flow diagrams, design decisions, prompt/schema
instructions, five real application captures, the retained fifteen-case evaluation,
development iterations and reproduction steps. The supplied Enterprise Policy
sample was read as a reference, not copied as a template or implementation.

The document builder uses `python-docx` from the Codex bundled artifact runtime.
Run `build_document.py` from the repository root with that runtime. It reads existing
diagrams, source prompts, frozen questions and the saved screenshots. It does not
invoke model/index services. Every document revision requires `render_docx.py` and
visual inspection of every rendered page before delivery. Rendered PDF/PNGs remain
temporary QA files, not submission outputs. The project dependency lock is unchanged.

## Screenshot provenance

Captured on 2026-10-19 with the user's explicit permission to use a temporary
automated browser after native computer access was unavailable. These are actual
screens from the unmodified local Streamlit app, not fabricated screens or fixture
replays. The first form image uses native Word cropping to remove empty margins;
the original PNG is retained. Other images are directly captured viewport regions
or the expanded source element. No UI text was rewritten for the screenshots.

- q03 ran in the existing default dense app on port8501. It returned `answered`:
  one Gemini generation,1129 input/541 output tokens, estimated chat USD0,
  one Pinecone read unit and19 embedding tokens, zero repairs.
- q10 ran in a separate `config.phase2-repair.yaml` app on port8502. It returned
  `insufficient_evidence` with expansion and answer cache hits: zero new Gemini
  calls, one dense search (16 embedding tokens/one read unit), one rerank unit,
  one effective original query, zero repairs.
- Exactly two question submissions were made. Opening expanders made no further
  submissions. No ingestion, cache clearing, ledger reset or frozen evaluation
  rerun was performed. Total walkthrough activity: one Gemini call,1129 input/
  541 output tokens, estimated chat USD0; two Pinecone reads,35 embedding tokens,
  one rerank unit. These are request observations, not account-wide totals.
- The temporary browser and port8502 server were stopped. The user's original
  port8501 server remained running. Screenshots contain no credentials.

The screenshots and walkthrough usage do not replace or alter frozen evaluation
reports. Earlier historical review notes about pending visual inspection remain
preserved; this documents the later limited browser walkthrough.

Recording and external submission are separate steps. The existing 4:35 narration
is in `docs/demo/demo-script.md`. No video or external submission was produced by
the document preparation task.
