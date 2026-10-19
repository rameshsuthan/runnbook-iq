import json
import sqlite3
from pathlib import Path
from .corpus import digest
from .providers import PROMPT_VERSION
from .schemas import RunResult

def answer_cache_key(settings, question, filters, corpus_version, evidence, *, query_variants=None, retrieval_configuration=None):
    from .retrieval import retrieval_configuration as configuration
    return digest({'namespace':'phase2-v1','repair':settings.repair,'repair_prompt':'repair-v1','expansion_route':settings.expansion.model_dump(mode='json') if settings.expansion else None,'queries':query_variants or [question],'provider':settings.provider,'model':settings.model,'prompt':PROMPT_VERSION,
        'schema':'answer-v3','question':question,'filters':filters,'corpus_version':corpus_version,
        'retrieval':retrieval_configuration if retrieval_configuration is not None else configuration(settings),
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


def expansion_cache_key(settings,question,filters,corpus_version):
    from .config import resolve_route
    return digest({'prompt':'query-expand-v1','schema':'alternatives-v1','question':question,
        'filters':filters,'corpus_version':corpus_version,'route':resolve_route(settings,'expand').model_dump(mode='json')})

class ExpansionCache:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as db:db.execute('CREATE TABLE IF NOT EXISTS expansions(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
    def get(self,key):
        with sqlite3.connect(self.path) as db:row=db.execute('SELECT value FROM expansions WHERE key=?',(key,)).fetchone()
        return json.loads(row[0]) if row else None
    def put(self,key,queries):
        with sqlite3.connect(self.path) as db:db.execute('INSERT OR REPLACE INTO expansions VALUES(?,?)',(key,json.dumps(queries)))
