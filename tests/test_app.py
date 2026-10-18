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
