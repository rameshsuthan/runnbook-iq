from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Filters = dict[str, str]


class Record(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Chunk(Record):
    chunk_id: str
    document_id: str
    title: str
    section: str
    text: str
    service: str
    document_type: str
    revision: str
    corpus_version: str
    content_hash: str
    environment: str | None = None


class RetrievalOrigin(Record):
    query_id: str
    method: Literal['dense', 'keyword']
    rank: int = Field(ge=1)
    score: float = Field(allow_inf_nan=False)


class Candidate(Record):
    chunk: Chunk
    method: str = 'dense'
    rank: int = Field(ge=1)
    scores: dict[str, float] = Field(default_factory=dict)
    provenance: list[RetrievalOrigin] = Field(default_factory=list)


class Usage(Record):
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    estimated_usd: Decimal | None = None
    calls: int = 0


class OperationRecord(Record):
    stage: Literal['expand','generate','repair','dense_search','rerank']
    provider: str = ''
    model: str = ''
    status: Literal['ok','error','blocked','cache_hit'] = 'ok'
    attempted: bool = False
    usage: Usage = Field(default_factory=Usage)
    reservation_usd: Decimal | None = None
    units: dict[str, float | None] = Field(default_factory=dict)
    elapsed_seconds: float = 0


class RetrievalBatch(Record):
    query_variants: list[str]
    candidates: list[Candidate]
    operations: list[OperationRecord] = Field(default_factory=list)


class SelectionResult(Record):
    evidence: list[Candidate]
    operations: list[OperationRecord] = Field(default_factory=list)


class QueryAlternatives(Record):
    alternatives: list[str] = Field(max_length=2)


class QueryPlan(Record):
    queries: list[str]
    warnings: list[str] = Field(default_factory=list)
    operations: list[OperationRecord] = Field(default_factory=list)


class GeneratedAnswer(Record):
    status: Literal['answered', 'insufficient_evidence'] = Field(description='Use insufficient_evidence if the requested fact or live cause cannot be established from these passages.')
    documented_evidence: str = Field(description='Direct answer to the original question, using all relevant selected passages. When asked which fields, enumerate the exact field names and their meanings, including correlation identifiers and measurement fields where documented. For other questions, supply the requested facts directly. Every factual sentence must include inline [chunk_id] references using exact evidence IDs.')
    recommended_checks: str = Field(description='Documented checks with inline [chunk_id] references in this text. Nonempty for answered responses.')
    missing_information: list[str] = Field(description='Specific unavailable facts or observations; required when status is insufficient_evidence.')
    citations: list[str] = Field(description='Unique exact chunk IDs used inline in documented_evidence, recommended_checks or missing_information. This array does not replace inline references.')


class ProviderResponse(Record):
    text: str
    usage: Usage = Field(default_factory=Usage)
    finish_reason: str = 'STOP'
    operation: OperationRecord | None = None


class RunResult(Record):
    status: Literal['retrieved', 'answered', 'insufficient_evidence', 'invalid_request', 'retrieval_error', 'provider_error', 'invalid_output', 'budget_exceeded']
    answer: GeneratedAnswer | None = None
    sources: list[Chunk] = Field(default_factory=list)
    query_variants: list[str] = Field(default_factory=list)
    retrieval_configuration: dict = Field(default_factory=dict)
    retrieved_candidates: list[Candidate] = Field(default_factory=list)
    selected_evidence: list[Candidate] = Field(default_factory=list)
    provider: str | None = None
    model: str | None = None
    usage: Usage = Field(default_factory=Usage)
    timings: dict[str, float] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    validation_error: Literal['incomplete_response','invalid_schema','duplicate_citations','unknown_citation','missing_inline_citations','citation_mismatch','missing_answer_sections','missing_information'] | None = None
    warnings: list[str] = Field(default_factory=list)
    operations: list[OperationRecord] = Field(default_factory=list)
    known_usage_subtotal: Usage = Field(default_factory=Usage)
    usage_complete: bool = False
    cache_hit: bool = False
    corpus_version: str = ''
