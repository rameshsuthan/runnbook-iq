"""Thin SDK boundary for the dedicated RunbookIQ index."""
import json
import time
from filelock import FileLock
from .config import credentials

def plain(value):
    return value.to_dict() if hasattr(value,'to_dict') else value

class PineconeStore:
    def __init__(self,settings,create=False):
        if not settings.pinecone_starter_verified:raise ValueError('Confirm Pinecone Starter entitlement before live access')
        from pinecone import Pinecone
        self.settings=settings
        self.pc=Pinecone(api_key=credentials('pinecone'))
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
        payload={'inputs':{'text':query},'top_k':top_k}
        if filters:payload['filter']={k:{'$eq':v} for k,v in filters.items()}
        raw=plain(self.index.search(namespace=self.settings.namespace,query=payload,fields=['text','corpus_version','content_hash']))
        self.record('search',raw)
        return [{'id':hit['_id'],'score':hit['_score'],**hit.get('fields',{})} for hit in raw['result']['hits']]

def describe_embedding_model(client, name):
    return plain(client.inference.get_model(model_name=name))
