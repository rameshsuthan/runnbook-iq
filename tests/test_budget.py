from decimal import Decimal
import pytest
from runbook_iq.schemas import Usage


def test_reservations_persist_and_enforce_guard(tmp_path):
    from runbook_iq.budget import BudgetLedger, BudgetExceeded
    path = tmp_path / 'usage.db'
    a = BudgetLedger(path, Decimal('3'))
    first = a.reserve('one', Decimal('2'))
    b = BudgetLedger(path, Decimal('3'))
    with pytest.raises(BudgetExceeded): b.reserve('two', Decimal('2'))
    a.settle(first, Usage(calls=1), None)
    assert b.total() == Decimal('2')
    with pytest.raises(BudgetExceeded): b.reserve('two', Decimal('2'))


def test_settlement_releases_only_known_difference(tmp_path):
    from runbook_iq.budget import BudgetLedger
    ledger = BudgetLedger(tmp_path / 'usage.db', Decimal('3'))
    r = ledger.reserve('one', Decimal('2'))
    ledger.settle(r, Usage(input_tokens=100, output_tokens=100, calls=1), Decimal('0.2'))
    assert ledger.total() == Decimal('0.2')
    with pytest.raises(ValueError): ledger.reserve('negative', Decimal('-1'))
    with pytest.raises(ValueError): ledger.reserve('nan', Decimal('NaN'))


def test_corrupt_ledger_fails_closed(tmp_path):
    from runbook_iq.budget import BudgetLedger
    p = tmp_path / 'bad.db'; p.write_text('corrupt')
    with pytest.raises(Exception): BudgetLedger(p, Decimal('3'))
