"""Conservative lexical expansion guards; they do not prove semantic equivalence."""
import re
from .schemas import QueryAlternatives,QueryPlan,OperationRecord
from .cache import expansion_cache_key
from .config import resolve_route
from .usage import CallFailure
from .budget import BudgetExceeded

EXPANSION_PROMPT='''Produce at most two search alternatives for the original incident question. Preserve all identifiers, service names, quoted literals, numeric values and negation. Do not add a diagnosis, cause, observation or fact. Return alternatives only in the supplied JSON schema. Prefer no alternatives when a safe rewrite is unclear.'''

class ExpansionCacheMiss(RuntimeError):pass


def validate_alternatives(original,alternatives,services):
    base=original.casefold()
    protected_tokens=set(re.findall(r'\b\w+(?:[_\-.]\w+)+\b|\b\d+(?:\.\d+)?\b',base))
    protected_tokens.update(s.casefold() for s in services if s.casefold() in base)
    protected=set()
    protected.update(re.findall(r'\b(?:not|no|never|without|cannot|can\x27t|don\x27t|isn\x27t|doesn\x27t)\b',base))
    protected.update(re.findall(r'["\x27]([^"\x27]+)["\x27]',base))
    negation_pattern=r"\b(?:not|no|never|without|cannot|can't|don't|isn't|doesn't)\b"
    original_negations=set(re.findall(negation_pattern,base))
    diagnoses=('exhaustion','leak','deadlock','outage','dependency timeout','root cause')
    seen={' '.join(base.split())};result=[original]
    for alt in alternatives[:2]:
        if not isinstance(alt,str) or not alt.strip() or len(alt)>8000:continue
        alt=' '.join(alt.split());lower=alt.casefold()
        # Internal dots/hyphens belong to the token; trailing punctuation does not.
        tokens=set(re.findall(r'\w+(?:[.-]\w+)*',lower))
        if not protected_tokens<=tokens:continue
        if set(re.findall(negation_pattern,lower))!=original_negations:continue
        if lower in seen or any(not re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)',lower) for t in protected):continue
        if any(t in lower and t not in base for t in diagnoses):continue
        seen.add(lower);result.append(alt)
    return result


class QueryPreparer:
    def __init__(self,settings,provider,cache,corpus_version,services,*,require_cache=False,counter=None):
        self.settings,self.provider,self.cache=settings,provider,cache
        self.corpus_version,self.services=corpus_version,services
        self.require_cache,self.counter=require_cache,counter
    def prepare(self,question,filters):
        route=resolve_route(self.settings,'expand');key=expansion_cache_key(self.settings,question,filters,self.corpus_version)
        cached=self.cache.get(key)
        if cached is not None:
            if not isinstance(cached,list) or not cached or cached[0]!=question or len(cached)>3:raise ExpansionCacheMiss('Invalid expansion cache')
            checked=validate_alternatives(question,cached[1:],self.services)
            if checked!=cached:raise ExpansionCacheMiss('Invalid expansion cache')
            operation=OperationRecord(stage='expand',provider=route.provider,model=route.model,status='cache_hit')
            if self.counter and any(self.counter.count(q)>self.settings.embedding_max_tokens for q in cached[1:]):
                if self.require_cache:raise ExpansionCacheMiss('Cached expansion exceeds current token limit')
                return QueryPlan(queries=[question],warnings=['expansion_cache_token_limit'],operations=[operation])
            return QueryPlan(queries=cached,operations=[operation])
        if self.require_cache:raise ExpansionCacheMiss('Required expansion cache entry missing')
        operations=[]
        try:
            response=self.provider.invoke_structured(EXPANSION_PROMPT,{'question':question,'filters':filters},QueryAlternatives,'expand')
            operations.append(response.operation or OperationRecord(stage='expand',provider=route.provider,model=route.model,attempted=True,usage=response.usage))
            if response.finish_reason not in ('STOP','stop'):raise ValueError('Incomplete expansion')
            alternatives=QueryAlternatives.model_validate_json(response.text).alternatives
            queries=validate_alternatives(question,alternatives,self.services)
            if self.counter:queries=[question,*[q for q in queries[1:] if self.counter.count(q)<=self.settings.embedding_max_tokens]]
            self.cache.put(key,queries)
            return QueryPlan(queries=queries,operations=operations)
        except CallFailure as error:
            return QueryPlan(queries=[question],warnings=['expansion_provider_error'],operations=[*operations,*error.operations])
        except BudgetExceeded:
            return QueryPlan(queries=[question],warnings=['expansion_budget_blocked'],operations=operations)
        except Exception:
            return QueryPlan(queries=[question],warnings=['expansion_invalid_or_setup_failed'],operations=operations)
