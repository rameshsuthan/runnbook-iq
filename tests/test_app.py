from streamlit.testing.v1 import AppTest


def test_form_only_submits_once_and_persists_answer():
    script='''
import streamlit as st
from app import render_app
from runbook_iq.schemas import RunResult,GeneratedAnswer
if 'calls' not in st.session_state:st.session_state.calls=0
def answer(question,filters):
    st.session_state.calls+=1
    return RunResult(status='insufficient_evidence',answer=GeneratedAnswer(status='insufficient_evidence',documented_evidence='',recommended_checks='',missing_information=['Need current traces'],citations=[]))
render_app(answer)
'''
    at=AppTest.from_string(script).run()
    assert not at.exception and at.session_state.calls==0
    at.text_area[0].set_value('What caused this?')
    at.button[0].click().run()
    assert not at.exception and at.session_state.calls==1
    assert any('Need current traces' in item.value for item in at.markdown)
    at.run()
    assert at.session_state.calls==1


def inspection_app():
    return AppTest.from_string('''
import streamlit as st
from app import render_app
from runbook_iq.schemas import RunResult,Usage,OperationRecord
if 'calls' not in st.session_state:st.session_state.calls=0
def answer(question,filters):
    st.session_state.calls+=1
    return RunResult(status='insufficient_evidence',cache_hit=True,query_variants=[question,'query variant'],repair_attempts=0,
      usage=Usage(calls=1,input_tokens=10,output_tokens=5,estimated_usd=0),
      operations=[OperationRecord(stage='expand',attempted=True,usage=Usage(calls=1))])
render_app(answer)
''').run()


def test_inspection_reruns_do_not_call_services():
    at=inspection_app();at.text_area[0].set_value('pool');at.button[0].click().run()
    assert not at.exception and at.session_state.calls==1
    assert any(e.label=='Retrieval inspection' for e in at.expander)
    assert any('query variant' in j.value for j in at.json)
    at.run();assert at.session_state.calls==1


def test_cached_answer_displays_current_expansion_usage():
    at=inspection_app();at.text_area[0].set_value('pool');at.button[0].click().run()
    assert any('Chat calls this request: 1' in c.value for c in at.caption)
    assert any('answer cache' in c.value.lower() for c in at.caption)
