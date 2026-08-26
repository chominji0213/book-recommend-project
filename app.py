import streamlit as st
import uuid
from llm_client import build_agent, ask

with st.sidebar:
    if st.button('새 대화 시작'):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

st.title('도서 추천 챗봇')

if 'agent' not in st.session_state:
    st.session_state.agent = build_agent()

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.write(msg['content'])

user_input = st.chat_input('어떤 책을 찾으세요?')

if user_input and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        answer = ask(st.session_state.agent, user_input, st.session_state.thread_id)
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
