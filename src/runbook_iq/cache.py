import json
import sqlite3
from pathlib import Path
from .corpus import digest
from .providers import PROMPT_VERSION
from .schemas import RunResult

def answer_cache_key(settings, question, filters, corpus_version, evidence):
    return digest({'provider':settings.provider,'model':settings.model,'prompt':PROMPT_VERSION,
        'schema':'answer-v3','question':question,'filters':filters,'corpus_version':corpus_version,
        'retrieval':{'top_k':settings.top_k,'embedding':settings.embedding_model,'method':'dense'},
        'generation':{'temperature':0 if settings.model.startswith('gemini-2.5') else 'provider_default','max_output':settings.max_output_tokens,'thinking':settings.thinking_budget if settings.model.startswith('gemini-2.5') else 'minimal'},
        'evidence':[(c.chunk.chunk_id,c.chunk.content_hash) for c in evidence]})

class AnswerCache:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as db: db.execute('CREATE TABLE IF NOT EXISTS answers (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
    def get(self,key):
        with sqlite3.connect(self.path) as db: row=db.execute('SELECT value FROM answers WHERE key=?',(key,)).fetchone()
        return RunResult.model_validate_json(row[0]) if row else None
    def put(self,key,result):
        if result.status not in ('answered','insufficient_evidence') or result.answer is None:
            raise ValueError('Only validated answer results may be cached')
        with sqlite3.connect(self.path) as db:
            db.execute('INSERT OR REPLACE INTO answers VALUES (?,?)',(key,result.model_dump_json()))
