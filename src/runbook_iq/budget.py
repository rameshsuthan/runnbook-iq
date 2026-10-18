"""Atomic local reservations. Unknown outcomes never release reserved dollars."""
import sqlite3
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

class BudgetExceeded(RuntimeError): pass

@dataclass(frozen=True)
class Reservation:
    request_id: str

def micros(value):
    value = Decimal(value)
    if not value.is_finite() or value < 0: raise ValueError('Cost must be finite and nonnegative')
    return int((value * 1_000_000).to_integral_value(rounding=ROUND_CEILING))

class BudgetLedger:
    def __init__(self, path: Path, limit: Decimal):
        self.path, self.limit = Path(path), micros(limit)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, reserved INTEGER NOT NULL, cost INTEGER, usage TEXT)')
    def connect(self): return sqlite3.connect(self.path, timeout=10)
    def reserve(self, request_id, maximum_usd):
        amount = micros(maximum_usd)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            total = db.execute('SELECT COALESCE(SUM(COALESCE(cost,reserved)),0) FROM requests').fetchone()[0]
            if total + amount > self.limit: raise BudgetExceeded('Estimated USD 3 application budget exhausted')
            db.execute('INSERT INTO requests(id,reserved) VALUES (?,?)',(request_id,amount))
        return Reservation(request_id)
    def settle(self, reservation, usage, cost_usd):
        cost = None if cost_usd is None else micros(cost_usd)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT reserved,cost FROM requests WHERE id=?',(reservation.request_id,)).fetchone()
            if row is None: raise ValueError('Unknown reservation')
            if row[1] is not None: raise ValueError('Reservation already settled')
            db.execute('UPDATE requests SET cost=?,usage=? WHERE id=?',
                       (cost,usage.model_dump_json(),reservation.request_id))
    def total(self):
        with self.connect() as db:
            n=db.execute('SELECT COALESCE(SUM(COALESCE(cost,reserved)),0) FROM requests').fetchone()[0]
        return Decimal(n)/1_000_000
