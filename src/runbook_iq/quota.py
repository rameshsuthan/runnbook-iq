"""Local monthly inference reservations; not an account-wide balance API."""
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime,timezone

class QuotaExceeded(RuntimeError):pass

def month():return datetime.now(timezone.utc).strftime('%Y-%m')

class QuotaLedger:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS quota(id TEXT PRIMARY KEY,kind TEXT,period TEXT,reserved INTEGER,actual INTEGER)')
    def connect(self):return sqlite3.connect(self.path,timeout=10)
    def reserve(self,kind,maximum,limit,period):
        if not isinstance(maximum,int) or maximum<0 or limit<1:raise ValueError('Invalid quota bound')
        id=uuid.uuid4().hex
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            used=db.execute('SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM quota WHERE kind=? AND period=?',(kind,period)).fetchone()[0]
            if used+maximum>limit or used>=limit:raise QuotaExceeded('Local monthly quota guard blocked request')
            db.execute('INSERT INTO quota VALUES(?,?,?,?,NULL)',(id,kind,period,maximum))
        return id
    def settle(self,reservation_id,actual):
        if actual is not None and (not isinstance(actual,int) or actual<0):raise ValueError('Invalid units')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT actual FROM quota WHERE id=?',(reservation_id,)).fetchone()
            if row is None or row[0] is not None:raise ValueError('Unknown or settled quota reservation')
            db.execute('UPDATE quota SET actual=? WHERE id=?',(actual,reservation_id))
