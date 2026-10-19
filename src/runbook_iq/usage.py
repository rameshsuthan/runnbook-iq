"""Explicit attempts and incomplete totals, independent of provider billing."""
from .schemas import Usage

class CallFailure(RuntimeError):
    def __init__(self,code,operation=None):
        super().__init__(code)
        self.code,self.operation=code,operation
        self.operations=[operation] if operation else []


def summarize_operations(records):
    calls=[r for r in records if r.stage in ('generate','expand','repair') and r.attempted]
    total={};known={};complete=True
    for field in ('input_tokens','output_tokens','reasoning_tokens','estimated_usd'):
        values=[getattr(r.usage,field) for r in calls]
        known[field]=sum(v for v in values if v is not None)
        total[field]=known[field] if all(v is not None for v in values) else None
        if field!='reasoning_tokens' and total[field] is None:complete=False
    return {'usage':Usage(**total,calls=len(calls)),
            'known_usage_subtotal':Usage(**known,calls=len(calls)),'usage_complete':complete}
