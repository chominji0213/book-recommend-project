import streamlit as st
import uuid
from llm_client import build_agent, ask

# TODO: movie-recommend-project의 app.py를 그대로 복사해서 가져오고 아래 2가지만 바꾸기
#   1) st.title("...")을 "도서 추천 챗봇"으로 변경
#   2) st.chat_input(...) 안내 문구를 책 취향을 물어보는 문구로 변경
#      예: st.chat_input("어떤 책을 찾으세요?")
#
# 사이드바 "새 대화 시작" 버튼, session_state 초기화, 메시지 히스토리 렌더링 부분은
# 영화 프로젝트 그대로 재사용하면 됨 (바뀌는 게 없음).
