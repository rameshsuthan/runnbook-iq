"""Structural citation validity only; entailment is reviewed separately."""
import re
from .schemas import GeneratedAnswer

def validate_answer(response,evidence):
    if response.finish_reason not in ('STOP','stop','FinishReason.STOP'):
        raise ValueError('Incomplete or blocked provider response')
    answer=GeneratedAnswer.model_validate_json(response.text)
    cited=set(answer.citations)
    groups=re.findall(r'\[([^\[\]\n]+)\]',answer.documented_evidence+'\n'+answer.recommended_checks+'\n'+'\n'.join(answer.missing_information))
    inline={identifier.strip() for group in groups for identifier in group.split(',')}
    available={c.chunk.chunk_id for c in evidence}
    if len(cited)!=len(answer.citations) or inline!=cited or not cited<=available:
        raise ValueError('Citation identifiers do not match selected evidence and inline references')
    if answer.status=='answered' and (not cited or not answer.documented_evidence.strip() or not answer.recommended_checks.strip()):
        raise ValueError('Answered output requires evidence, checks and citations')
    if answer.status=='insufficient_evidence' and not answer.missing_information:
        raise ValueError('Insufficient evidence must explain missing information')
    return answer
