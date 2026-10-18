"""Run with: uv run streamlit run app.py. No model/index calls at startup."""
import streamlit as st
from pathlib import Path
from runbook_iq.schemas import RunResult


def ask_live(question,filters):
    from dotenv import load_dotenv
    from runbook_iq.config import load_settings
    from runbook_iq.cli import compose,invoke_question
    load_dotenv('.env',override=False)
    try:
        _,graph=compose(load_settings())
        return invoke_question(graph,question,filters)
    except Exception:
        return RunResult(status='provider_error',errors=['Setup or service access failed. Check local configuration and run the CLI doctor.'])


def render_app(answer_fn=ask_live):
    st.set_page_config(page_title='RunbookIQ',page_icon='📖',layout='centered')
    st.title('RunbookIQ')
    st.caption('Evidence-based incident troubleshooting · Synthetic training corpus')
    st.write('Find documented checks and historical lessons. This app cannot inspect live systems or execute remediation.')
    with st.form('question_form'):
        question=st.text_area('Troubleshooting question',placeholder='What distinguishes a database pool wait from an inventory timeout?')
        with st.expander('Optional explicit filters'):
            service=st.text_input('Service',placeholder='order-api')
            environment=st.text_input('Environment',help='The synthetic corpus has no environment labels; a filter may return no evidence.')
        submitted=st.form_submit_button('Find evidence',type='primary')
    if submitted:
        if not question.strip():st.warning('Enter a question first.')
        else:
            filters={k:v.strip() for k,v in [('service',service),('environment',environment)] if v.strip()}
            with st.spinner('Retrieving passages and checking the answer…'):
                st.session_state['result']=answer_fn(question,filters)
                st.session_state['submitted_question']=question
    result=st.session_state.get('result')
    if result is None:return
    st.divider()
    st.caption(st.session_state.get('submitted_question',''))
    st.write(f"Status: **{result.status.replace('_',' ')}**")
    if result.errors:st.error(' '.join(result.errors))
    if result.answer:
        for title,body in [('Documented evidence',result.answer.documented_evidence),('Recommended checks',result.answer.recommended_checks)]:
            st.subheader(title);st.markdown(body or 'No supported content available.')
        st.subheader('Missing information')
        st.markdown('\n'.join('- '+item for item in result.answer.missing_information) or 'No additional information requested for this documented question.')
    if result.sources:
        st.subheader('Sources')
        for source in result.sources:
            with st.expander(f'{source.title} · {source.section}'):
                st.code(source.chunk_id,language=None)
                st.caption(f'{source.document_type} · revision {source.revision}')
                st.text(source.text)
    status='Cached answer; no new generation call.' if result.cache_hit else f'Chat calls: {result.usage.calls}'
    st.caption(status)
    if result.model:st.caption(f'{result.provider} / {result.model}')
    with st.expander('Usage and timing'):
        st.json({'input_tokens':result.usage.input_tokens,'output_tokens':result.usage.output_tokens,
                 'reasoning_tokens':result.usage.reasoning_tokens,'estimated_usd':str(result.usage.estimated_usd) if result.usage.estimated_usd is not None else 'unknown',
                 'node_seconds':result.timings})

if __name__=='__main__':render_app()
