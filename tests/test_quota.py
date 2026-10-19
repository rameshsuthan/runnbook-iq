from concurrent.futures import ThreadPoolExecutor
import pytest


def test_quota_reservations_are_atomic_and_month_scoped(tmp_path):
    from runbook_iq.quota import QuotaLedger,QuotaExceeded
    path=tmp_path/'quota.db';q=QuotaLedger(path)
    def reserve(_):
        try:return q.reserve('rerank',1,1,'2026-10')
        except QuotaExceeded:return None
    with ThreadPoolExecutor(max_workers=2) as pool: ids=list(pool.map(reserve,range(2)))
    assert sum(i is not None for i in ids)==1
    q.settle(next(i for i in ids if i),None)
    with pytest.raises(QuotaExceeded):QuotaLedger(path).reserve('rerank',1,1,'2026-10')
    other=q.reserve('rerank',1,1,'2026-11');q.settle(other,0)
    assert q.reserve('rerank',1,1,'2026-11')
