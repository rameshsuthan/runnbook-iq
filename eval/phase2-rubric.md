# Phase 2 prospective review rubric

Frozen before Phase 2 live comparison on 2026-10-18. Original questions, expected
statuses, answer prompt and all Phase 1 results remain unchanged. All fifteen cases
have already been observed; these are regression comparisons, not unseen tests.

Review each actual response on separate axes:
- Coverage: includes the requested documented facts and expected caveats.
- Support: every factual claim/check follows from the selected passages.
- Citations: identifiers resolve and cited passages support the associated claims.
- Clarification: names unavailable observations without inventing a live cause.
- Status: compare exactly against the frozen expected status; additionally explain
  whether a conservative abstention still supplies useful supported information.

An answer to a request for documented checks can be answered while requesting
missing live observations. A request to establish an unavailable current cause
requires insufficient_evidence. Retrieval relevance and structurally valid citation
identifiers do not establish semantic support. Unsupported checks fail support even
if the overall answer correctly abstains. Never erase failures by revising expected
statuses after seeing responses.

q04 asks whether a 503 means PostgreSQL is down. The frozen status is answered;
its expected content is that a 503 cannot choose the cause. A supported abstention
is a conservative status disagreement, not a fabricated diagnosis. q11 asks for
evidence distinguishing a leak from slow work: supported documented checks can
answer that request without establishing the cause. Its frozen status also stays
answered. Record both exact status agreement and the separate qualitative assessment.

Reaudit of Phase 1 v3 is saved as a separate supplemental artifact, tied to the
source report hash. The stronger validator's offline audit remains separate from
that original live run. Future arms use this rubric without answer-prompt changes.
