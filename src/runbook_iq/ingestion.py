"""Recoverable project-scoped synchronization; only explicit IDs are removed."""
import json
import time
from filelock import FileLock
from .corpus import CorpusSnapshot, atomic_write, read_snapshot
from .schemas import Record

class IngestionReport(Record):
    upserted: int = 0
    deleted: int = 0
    skipped: int = 0
    verified: bool = False

def corpus_lock(settings):
    settings.processed_dir.mkdir(parents=True,exist_ok=True)
    return FileLock(settings.processed_dir / 'corpus.lock',timeout=10)

def destination_identity(settings, client=None):
    identity={'index_name':settings.index_name,'namespace':settings.namespace,'embedding_model':settings.embedding_model}
    if client is not None:identity['host']=client.description['host']
    return identity

def check_destination(settings, client=None):
    path=settings.processed_dir/'destination.json'
    if not path.exists():raise ValueError('Ingestion destination is unbound; use a fresh processed directory or verify and migrate the legacy manifest')
    saved=json.loads(path.read_text())
    if any(saved.get(k)!=v for k,v in destination_identity(settings,client).items()):
        raise ValueError('Ingestion destination mismatch; use a separate processed directory')

def load_active_snapshot(settings):
    check_destination(settings)
    if (settings.processed_dir/'journal.json').exists(): raise ValueError('Ingestion incomplete; rerun ingest with the same corpus')
    path=settings.processed_dir/'active.json'
    if not path.exists():raise ValueError('No active corpus; run ingest first')
    return read_snapshot(path)

def remote_record(chunk):
    return {'id':chunk.chunk_id, **chunk.model_dump(exclude={'chunk_id','environment'}),
            **({'environment':chunk.environment} if chunk.environment else {})}

def sync_corpus(snapshot, settings, client):
    with corpus_lock(settings):
        client.validate()
        active=settings.processed_dir/'active.json'; journal=settings.processed_dir/'journal.json'
        destination=settings.processed_dir/'destination.json'
        if not destination.exists() and not active.exists() and not journal.exists():
            atomic_write(destination,json.dumps(destination_identity(settings,client)))
        check_destination(settings,client)
        old=read_snapshot(active) if active.exists() else None
        if journal.exists():
            pending=json.loads(journal.read_text())
            if pending['target']!=snapshot.version:raise ValueError('Ingestion incomplete; restore the previous target corpus first')
            obsolete=pending['obsolete']
        else:
            if old and old.version==snapshot.version:return IngestionReport(skipped=len(snapshot.chunks),verified=True)
            ids={c.chunk_id for c in snapshot.chunks}
            obsolete=[c.chunk_id for c in old.chunks if c.chunk_id not in ids] if old else []
            atomic_write(journal,json.dumps({'target':snapshot.version,'obsolete':obsolete}))
        records=[remote_record(c) for c in snapshot.chunks]
        for i in range(0,len(records),96): client.upsert(records[i:i+96])
        if obsolete: client.delete(obsolete)
        for attempt in range(settings.readiness_attempts):
            found=client.fetch([c.chunk_id for c in snapshot.chunks]+obsolete)
            valid=all(found.get(c.chunk_id,{}).get('content_hash')==c.content_hash and
                      found.get(c.chunk_id,{}).get('corpus_version')==snapshot.version for c in snapshot.chunks)
            if valid and not any(i in found for i in obsolete):
                atomic_write(active,snapshot.model_dump_json(indent=2)); journal.unlink()
                return IngestionReport(upserted=len(records),deleted=len(obsolete),verified=True)
            if attempt+1<settings.readiness_attempts:time.sleep(2)
        raise TimeoutError('Pinecone freshness verification timed out; ingestion remains incomplete')
