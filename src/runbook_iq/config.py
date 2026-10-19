"""Nonsecret configuration; secrets are resolved only at integration boundaries."""
import os
from decimal import Decimal
from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelRoute(BaseModel):
    model_config = ConfigDict(extra='forbid')
    provider: Literal['gemini','nebius'] = 'gemini'
    model: str = ''
    billing: Literal['unknown','free','paid'] = 'unknown'
    account_verified: bool = False
    pricing_verified: bool = False
    input_usd_per_million: Decimal | None = None
    output_usd_per_million: Decimal | None = None
    max_input_tokens: int = Field(default=10000,gt=0)
    max_output_tokens: int = Field(default=1500,gt=0,le=4096)
    thinking_budget: int = 0
    billable_bounds_verified: bool = False


class Settings(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expansion: ModelRoute | None = None
    provider: Literal['gemini'] = 'gemini'
    model: str = ''
    billing: Literal['unknown', 'free', 'paid'] = 'unknown'
    account_verified: bool = False
    pricing_verified: bool = False
    input_usd_per_million: Decimal | None = None
    output_usd_per_million: Decimal | None = None
    budget_usd: Decimal = Field(default=Decimal('3'), gt=0, le=3)
    max_output_tokens: int = Field(default=1500, gt=0, le=4096)
    max_input_tokens: int = Field(default=10000, gt=0, le=32000)
    thinking_budget: int = 0
    retries: Literal[0] = 0
    paid_fallback: Literal[False] = False
    hybrid: bool = False
    reranking: bool = False
    multi_query: bool = False
    repair: bool = False
    rerank_monthly_limit: int = Field(default=100, ge=1, le=500)
    embedding_monthly_limit: int = Field(default=5000000, ge=1, le=5000000)
    read_monthly_limit: int = Field(default=1000000, ge=1, le=1000000)
    top_k: int = Field(default=5, ge=1, le=5)
    index_name: str = 'runbook-iq'
    namespace: str = 'runbook-iq-v1'
    pinecone_starter_verified: bool = False
    region: Literal['us-east-1'] = 'us-east-1'
    embedding_model: Literal['llama-text-embed-v2'] = 'llama-text-embed-v2'
    chunk_target_tokens: int = Field(default=400, ge=64, le=1800)
    embedding_max_tokens: int = Field(default=2048, ge=400, le=2048)
    tokenizer_revision: str = ''
    source_dir: Path = Path('data/docs')
    processed_dir: Path = Path('data/processed')
    runtime_dir: Path = Path('.runbook_iq')
    readiness_attempts: int = Field(default=10, ge=1, le=20)

    @model_validator(mode='after')
    def baseline(self):
        if not self.namespace.startswith('runbook-iq-') or not self.index_name.startswith('runbook-iq'):
            raise ValueError('Use a dedicated RunbookIQ index and namespace')
        for rate in (self.input_usd_per_million, self.output_usd_per_million):
            if rate is not None and (not rate.is_finite() or rate < 0):
                raise ValueError('Prices must be finite and nonnegative')
        return self


def load_settings(path: Path = Path('config.yaml')) -> Settings:
    return Settings.model_validate(yaml.safe_load(path.read_text()) or {}) if path.exists() else Settings()


def credentials(provider: str) -> str:
    if provider == 'gemini':
        first, second = os.getenv('GEMINI_API_KEY'), os.getenv('GOOGLE_API_KEY')
        if first and second and first != second:
            raise ValueError('Set only one of GEMINI_API_KEY or GOOGLE_API_KEY')
        key = first or second
        name = 'GEMINI_API_KEY'
    else:
        key, name = os.getenv('PINECONE_API_KEY'), 'PINECONE_API_KEY'
    if not key or not key.strip():
        raise ValueError(f'Missing {name}; configure it in your local .env')
    return key


def resolve_route(settings,task='generate'):
    if task not in ('generate','expand','repair'):raise ValueError('Unsupported model task')
    if task=='expand' and settings.expansion is not None:route=settings.expansion.model_copy()
    else:route=ModelRoute(**{k:getattr(settings,k) for k in ModelRoute.model_fields if hasattr(settings,k)})
    if task=='expand':route.max_output_tokens=min(route.max_output_tokens,512)
    return route
