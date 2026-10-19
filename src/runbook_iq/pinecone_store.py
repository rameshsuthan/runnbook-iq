"""Thin SDK boundary for the dedicated RunbookIQ index."""
import json
import time
from filelock import FileLock
from .config import credentials

def plain(value):
    return value.to_dict() if hasattr(value,'to_dict') else value

def create_pinecone_client(key):
    from pinecone import Pinecone
    client=Pinecone(api_key=key)
    # SDK 8 has no constructor option for retries. Set its configuration before
    # lazy inference/index transports are built; pinned transport tests guard this.
    client._openapi_config.retries=0
    return client

class PineconeStore:
    def __init__(self,settings,create=False):
        if not settings.pinecone_starter_verified:raise ValueError('Confirm Pinecone Starter entitlement before live access')
        self.settings=settings
        self.pc=create_pinecone_client(credentials('pinecone'))
        if create and not self.pc.has_index(name=settings.index_name):
            self.pc.create_index_for_model(name=settings.index_name,cloud='aws',region=settings.region,
                embed={'model':settings.embedding_model,'field_map':{'text':'text'},
                       'read_parameters':{'input_type':'query','truncate':'NONE'},
                       'write_parameters':{'input_type':'passage','truncate':'NONE'}},
                tags={'application':'runbook-iq'},deletion_protection='enabled',timeout=30)
        self.validate()
        self.index=self.pc.Index(host=self.description['host'])
    def validate(self):
        desc=plain(self.pc.describe_index(name=self.settings.index_name))
        embed=desc.get('embed',{})
        if desc.get('tags',{}).get('application')!='runbook-iq':raise ValueError('Index is not tagged as owned by RunbookIQ')
        if embed.get('model')!=self.settings.embedding_model or embed.get('field_map')!={'text':'text'}:
            raise ValueError('Index embedding configuration mismatch')
        serverless=desc.get('spec',{}).get('serverless',{})
        if serverless.get('cloud')!='aws' or serverless.get('region')!=self.settings.region:
            raise ValueError('Index region does not match Starter setup')
        for field in ('read_parameters','write_parameters'):
            if embed.get(field,{}).get('truncate')!='NONE':raise ValueError('Index must disable silent embedding truncation')
        if not desc.get('status',{}).get('ready'):raise ValueError('Index is not ready; retry the explicit command later')
        self.description=desc
    def record(self,operation,response=None):
        path=self.settings.runtime_dir/'pinecone-usage.jsonl'; path.parent.mkdir(parents=True,exist_ok=True)
        value=plain(response) if response is not None else {}
        usage=value.get('usage') if isinstance(value,dict) else None
        with FileLock(str(path)+'.lock'):
            with path.open('a') as stream:stream.write(json.dumps({'operation':operation,'time':time.time(),'usage':usage,'account':'Starter'})+'\n')
    def upsert(self,records):
        result=self.index.upsert_records(namespace=self.settings.namespace,records=records)
        self.record('upsert',result)
    def delete(self,ids):
        result=self.index.delete(ids=ids,namespace=self.settings.namespace)
        self.record('delete',result)
    def fetch(self,ids):
        result={}
        for i in range(0,len(ids),100):
            raw=plain(self.index.fetch(ids=ids[i:i+100],namespace=self.settings.namespace))
            self.record('fetch',raw)
            for key,record in raw.get('vectors',{}).items():result[key]=plain(record).get('metadata',{})
        return result
    def search(self,query,filters,top_k):
        return self.search_with_usage(query,filters,top_k)[0]
    def search_with_usage(self,query,filters,top_k):
        from .schemas import OperationRecord
        from .usage import CallFailure
        from .quota import QuotaLedger,month
        quota=QuotaLedger(self.settings.runtime_dir/'quotas.db')
        embed=quota.reserve('embedding',self.settings.embedding_max_tokens,self.settings.embedding_monthly_limit,month())
        # Read units are monitored from responses, not guessed as a hard cost bound.
        read=quota.reserve('read',0,self.settings.read_monthly_limit,month())
        payload={'inputs':{'text':query},'top_k':top_k}
        if filters:payload['filter']={k:{'$eq':v} for k,v in filters.items()}
        started=time.perf_counter()
        operation=OperationRecord(stage='dense_search',provider='pinecone',model=self.settings.embedding_model,attempted=True)
        try:
            raw=plain(self.index.search(namespace=self.settings.namespace,query=payload,fields=['text','corpus_version','content_hash']))
            self.record('search',raw)
            units=raw.get('usage',{})
            operation.units={k:units.get(k) for k in ('read_units','embed_total_tokens')}
            quota.settle(embed,units.get('embed_total_tokens'));quota.settle(read,units.get('read_units'))
            hits=[{'id':hit['_id'],'score':hit['_score'],**hit.get('fields',{})} for hit in raw['result']['hits']]
            operation.elapsed_seconds=time.perf_counter()-started
            return hits,operation
        except Exception:
            operation.status='error';operation.elapsed_seconds=time.perf_counter()-started
            operation.units={'read_units':None,'embed_total_tokens':None}
            raise CallFailure('Dense search failed; no automatic retry',operation) from None

def describe_embedding_model(client, name):
    return plain(client.inference.get_model(model_name=name))
