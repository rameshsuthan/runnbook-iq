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


class Candidate(Record):
    chunk: Chunk
    method: str = 'dense'
    rank: int = Field(ge=1)
    scores: dict[str, float] = Field(default_factory=dict)


class Usage(Record):
    input_tokens: int | None = None
    output_tokens: int | None = None  # Includes reasoning when returned by LangChain.
    reasoning_tokens: int | None = None
    estimated_usd: Decimal | None = None
    calls: int = 0


class GeneratedAnswer(Record):
    status: Literal['answered', 'insufficient_evidence']
    documented_evidence: str
    recommended_checks: str
    missing_information: list[str]
    citations: list[str]


class ProviderResponse(Record):
    text: str
    usage: Usage = Field(default_factory=Usage)
    finish_reason: str = 'STOP'


class RunResult(Record):
    status: Literal['answered', 'insufficient_evidence', 'invalid_request', 'retrieval_error', 'provider_error', 'invalid_output', 'budget_exceeded']
    answer: GeneratedAnswer | None = None
    sources: list[Chunk] = Field(default_factory=list)
    retrieved_candidates: list[Candidate] = Field(default_factory=list)
    selected_evidence: list[Candidate] = Field(default_factory=list)
    provider: str | None = None
    model: str | None = None
    usage: Usage = Field(default_factory=Usage)
    timings: dict[str, float] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    cache_hit: bool = False
    corpus_version: str = ''
