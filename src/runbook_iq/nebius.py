"""Explicit Nebius route; offline verified until account/model live checks pass."""
import json
import time
import uuid
from decimal import Decimal
from .config import credentials
from .schemas import GeneratedAnswer,ProviderResponse,Usage,OperationRecord
from .providers import SYSTEM_PROMPT,REPAIR_PROMPT,answer_payload,ProviderError

BASE_URL='https://api.tokenfactory.nebius.com/v1/'


def maximum_request_cost(route):
    if not route.account_verified or not route.model or route.billing!='paid':
        raise ProviderError('Verify Nebius account/model and explicit paid billing first')
    if not route.pricing_verified or not route.billable_bounds_verified or not route.context_window_tokens:
        raise ProviderError('Verified prices and provider-enforced billable bounds are required')
    rates=(route.input_usd_per_million,route.output_usd_per_million)
    if any(rate is None or not rate.is_finite() or rate<0 for rate in rates):
        raise ProviderError('Configure finite nonnegative verified prices')
    return (route.context_window_tokens*rates[0]+route.max_output_tokens*rates[1])/Decimal(1000000)


class NebiusProvider:
    def __init__(self,route,ledger,client=None):
        self.route,self.ledger=route,ledger
        self.maximum=maximum_request_cost(route)
        if client is None:
            from openai import OpenAI
            client=OpenAI(base_url=BASE_URL,api_key=credentials('nebius'),max_retries=0,timeout=45)
        self.client=client

    def generate(self,question,evidence):
        return self.invoke_structured(SYSTEM_PROMPT,answer_payload(question,evidence),GeneratedAnswer,'generate')

    def repair(self,question,evidence,rejected,validation_error):
        payload=answer_payload(question,evidence)
        payload.update(rejected_response=rejected.text,validation_error=validation_error)
        return self.invoke_structured(REPAIR_PROMPT,payload,GeneratedAnswer,'repair')

    def invoke_structured(self,system,payload,schema,stage):
        text=json.dumps(payload,ensure_ascii=False)
        if len((system+text).encode())>self.route.max_input_tokens*3:
            raise ProviderError('Request exceeds local size limit')
        # Dollar reservation uses the verified model context ceiling, NOT the local
        # byte heuristic, plus the verified all-billable-output maximum.
        reservation=self.ledger.reserve(uuid.uuid4().hex,self.maximum)
        operation=OperationRecord(stage=stage,provider='nebius',model=self.route.model,
            attempted=True,reservation_usd=self.maximum,usage=Usage(calls=1))
        started=time.perf_counter()
        try:
            raw=self.client.chat.completions.create(model=self.route.model,
                messages=[{'role':'system','content':system},{'role':'user','content':text}],
                response_format={'type':'json_schema','json_schema':{'name':schema.__name__,'strict':True,'schema':schema.model_json_schema()}},
                max_tokens=self.route.max_output_tokens)
            meta=raw.usage
            input_tokens=getattr(meta,'prompt_tokens',None);output_tokens=getattr(meta,'completion_tokens',None)
            if type(input_tokens) is not int or input_tokens<0:input_tokens=None
            if type(output_tokens) is not int or output_tokens<0:output_tokens=None
            cost=None if input_tokens is None or output_tokens is None else (
                input_tokens*self.route.input_usd_per_million+output_tokens*self.route.output_usd_per_million)/Decimal(1000000)
            usage=Usage(calls=1,input_tokens=input_tokens,output_tokens=output_tokens,
                reasoning_tokens=getattr(getattr(meta,'completion_tokens_details',None),'reasoning_tokens',None),estimated_usd=cost)
            operation.usage=usage
            self.ledger.settle(reservation,usage,cost)
            choice=raw.choices[0]
            refused=getattr(choice.message,'refusal',None)
            operation.elapsed_seconds=time.perf_counter()-started
            return ProviderResponse(text=choice.message.content or '',usage=usage,
                finish_reason='REFUSAL' if refused else str(choice.finish_reason).upper(),operation=operation)
        except Exception:
            operation.status='error';operation.elapsed_seconds=time.perf_counter()-started
            raise ProviderError('Nebius request failed; no automatic retry',operation) from None
