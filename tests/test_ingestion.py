import pytest
from runbook_iq.config import Settings
from runbook_iq.schemas import Chunk
from runbook_iq.corpus import CorpusSnapshot


def snapshot(version='v1', text='evidence'):
    return CorpusSnapshot(version=version,source_hashes={'doc':version},fingerprint='f',chunks=[Chunk(chunk_id='c-'+version,document_id='doc',title='Title',section='Checks',text=text,service='order-api',document_type='runbook',revision='2026-10-18',corpus_version=version,content_hash=version)])

class Store:
    def __init__(self): self.records={}; self.upserts=0; self.deletes=[]; self.fail=False; self.description={'host':'first-host'}
    def validate(self): pass
    def upsert(self,records):
        self.upserts+=len(records)
        for r in records: self.records[r['id']]=r
        if self.fail: raise RuntimeError('interrupted')
    def fetch(self,ids): return {i:self.records[i] for i in ids if i in self.records}
    def delete(self,ids):
        self.deletes.extend(ids)
        for i in ids:self.records.pop(i,None)


def test_idempotence_and_scoped_deletion(tmp_path):
    from runbook_iq.ingestion import sync_corpus
    s=Settings(processed_dir=tmp_path,readiness_attempts=1)
    store=Store(); store.records['foreign']={'id':'foreign'}
    sync_corpus(snapshot(),s,store)
    report=sync_corpus(snapshot(),s,store)
    assert report.upserted == 0 and store.upserts==1
    sync_corpus(snapshot('v2'),s,store)
    assert store.deletes==['c-v1'] and 'foreign' in store.records


def test_interruption_blocks_queries_and_can_resume(tmp_path):
    from runbook_iq.ingestion import sync_corpus,load_active_snapshot
    s=Settings(processed_dir=tmp_path,readiness_attempts=1)
    store=Store(); store.fail=True
    with pytest.raises(RuntimeError): sync_corpus(snapshot(),s,store)
    with pytest.raises(ValueError,match='incomplete'): load_active_snapshot(s)
    store.fail=False
    sync_corpus(snapshot(),s,store)
    assert load_active_snapshot(s).version=='v1'


def test_freshness_timeout_never_publishes(tmp_path):
    from runbook_iq.ingestion import sync_corpus
    class Stale(Store):
        def fetch(self,ids): return {}
    s=Settings(processed_dir=tmp_path,readiness_attempts=1)
    with pytest.raises(TimeoutError):sync_corpus(snapshot(),s,Stale())
    assert not (tmp_path/'active.json').exists()

@pytest.mark.parametrize('change',[{'namespace':'runbook-iq-other'},{'index_name':'runbook-iq-other'}, {'host':'different-host'}])
def test_destination_change_rejected_without_remote_mutation(tmp_path,change):
    from runbook_iq.ingestion import sync_corpus,load_active_snapshot
    s=Settings(processed_dir=tmp_path,readiness_attempts=1)
    first=Store();first.description={'host':'first-host'}
    sync_corpus(snapshot(),s,first)
    second=Store();second.description={'host':change.get('host','first-host')}
    changed=s.model_copy(update={k:v for k,v in change.items() if k!='host'})
    with pytest.raises(ValueError,match='destination'):
        sync_corpus(snapshot(),changed,second)
    assert second.upserts==0 and second.deletes==[]
    if 'host' not in change:
        with pytest.raises(ValueError,match='destination'):load_active_snapshot(changed)


def test_pending_journal_cannot_move_to_another_destination(tmp_path):
    from runbook_iq.ingestion import sync_corpus
    s=Settings(processed_dir=tmp_path,readiness_attempts=1)
    first=Store();first.fail=True
    with pytest.raises(RuntimeError):sync_corpus(snapshot(),s,first)
    second=Store()
    with pytest.raises(ValueError,match='destination'):
        sync_corpus(snapshot(),s.model_copy(update={'namespace':'runbook-iq-other'}),second)
    assert second.upserts==0 and not second.deletes
