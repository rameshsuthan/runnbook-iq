"""Structural citation validity only; entailment is reviewed separately."""
import re
from pydantic import ValidationError
from .schemas import GeneratedAnswer

class AnswerValidationError(ValueError):
    """A stable category, without embedding provider output in an exception."""
    def __init__(self, code):
        self.code=code
        super().__init__(code)

def validate_answer(response,evidence):
    if response.finish_reason not in ('STOP','stop','FinishReason.STOP'):
        raise AnswerValidationError('incomplete_response')
    try:
        answer=GeneratedAnswer.model_validate_json(response.text)
    except ValidationError:
        raise AnswerValidationError('invalid_schema') from None
    cited=set(answer.citations)
    groups=re.findall(r'\[([^\[\]\n]+)\]',answer.documented_evidence+'\n'+answer.recommended_checks+'\n'+'\n'.join(answer.missing_information))
    inline={identifier.strip() for group in groups for identifier in group.split(',')}
    available={c.chunk.chunk_id for c in evidence}
    if len(cited)!=len(answer.citations):
        raise AnswerValidationError('duplicate_citations')
    if not cited<=available:
        raise AnswerValidationError('unknown_citation')
    if cited and not inline:
        raise AnswerValidationError('missing_inline_citations')
    if inline!=cited:
        raise AnswerValidationError('citation_mismatch')
    for section in (answer.documented_evidence,answer.recommended_checks):
        if section.strip() and not re.search(r'\[([^\[\]\n]+)\]',section):
            raise AnswerValidationError('missing_inline_citations')
    if answer.status=='answered' and (not cited or not answer.documented_evidence.strip() or not answer.recommended_checks.strip()):
        raise AnswerValidationError('missing_answer_sections')
    if answer.status=='insufficient_evidence' and not answer.missing_information:
        raise AnswerValidationError('missing_information')
    return answer
