"""
도서 추천 RAG 에이전트 - StateGraph 3단계 버전 (retrieve -> check_price -> generate).

영화 프로젝트의 2단계(retrieve -> generate)에서 한 단계 더 늘어난 구조야.
+ 영화 프로젝트에서 발견된 "멀티턴 맥락 유지 안 됨" 문제를 개선하는 게 이번 프로젝트의
  설계 목표 중 하나니까, State에 history 필드도 추가해볼 것.
"""

# TODO: import
#   from typing import TypedDict
#   from langchain.chat_models import init_chat_model
#   from langchain_core.messages import HumanMessage
#   from langgraph.graph import StateGraph, START, END
#   from langgraph.checkpoint.sqlite import SqliteSaver
#   import sqlite3
#   from tools.vector_store import search_books
#   from tools.price_tool import check_price
#   from rich import print as rprint


# TODO: State 정의
#   class BookState(TypedDict):
#       query: str              # 사용자 질문
#       search_results: dict    # search_books() 검색 결과
#       price_info: list        # check_price() 결과들을 담은 리스트
#       answer: str             # 최종 답변
#       history: list           # (설계 개선) 이전 대화 요약을 담아 멀티턴 맥락 유지에 활용
#         - 영화 프로젝트에서는 이 필드가 없어서 "다섯개 더 보여줘" 같은 후속 질문에서
#           이전 맥락(장르 등)을 잃어버렸음. 이번엔 generate_node가 answer를 만들 때
#           history에 (질문, 답변) 같은 걸 누적해서 함께 프롬프트에 넣어줄 것.


def retrieve_node(state):
    """
    검색 노드: state["query"]로 벡터DB를 검색해서 state["search_results"]를 채워 반환.
    영화 프로젝트의 retrieve_node와 완전히 동일한 패턴 (search_movies -> search_books만 바뀜).
    """
    pass


def check_price_node(state):
    """
    가격 조회 노드 (이번 프로젝트에서 새로 추가되는 부분):
    state["search_results"]에 담긴 책들 각각에 대해 check_price()를 호출해서
    실시간 가격/재고 정보를 모아 state["price_info"]에 채워 반환.

    TODO 1: state["search_results"]["결과"] 리스트를 순회 (검색 결과 없으면 빈 리스트로 처리)

    TODO 2: 각 책의 id로 check_price(book_id) 호출해서 결과 리스트에 담기
      - book_data.py에서 도서 딕셔너리에 "id" 필드를 저장해뒀는지 확인 (알라딘 itemId)

    TODO 3: {"price_info": 가격정보_리스트} 형태로 반환
    """
    pass


def generate_node(state):
    """
    답변 생성 노드: 검색 결과 + 가격 정보를 종합해서 LLM이 추천 답변을 만들게 함.

    영화 프로젝트에서 배운 에러 처리 패턴(검색 결과 없으면 LLM 호출 스킵, LLM 호출
    try/except 감싸기)을 여기서도 그대로 재사용할 것.

    TODO 1: llm = init_chat_model('gemini-3.1-flash-lite', model_provider='google_genai')

    TODO 2: 프롬프트에 검색 결과 + 가격 정보를 모두 포함시켜서 LLM 호출
      - 사용자 질문에서 요청한 개수만큼 추천하도록 지시 (영화 프로젝트에서 고친 패턴 재사용)
      - (설계 개선) state.get("history")가 있다면 프롬프트에 이전 대화 맥락도 같이 포함

    TODO 3: response.content 형태 확인 후 텍스트 추출

    TODO 4: {"answer": 추출한_텍스트} 형태로 반환
      - (설계 개선) history에 이번 질문/답변을 추가해서 같이 반환할지도 고려
    """
    pass


def build_agent():
    """
    retrieve_node -> check_price_node -> generate_node 3단계로 연결된 그래프를 만들고 컴파일.

    TODO 1: SqliteSaver 체크포인터 준비 (영화 프로젝트와 동일)

    TODO 2: graph = StateGraph(BookState)

    TODO 3: 노드 3개 등록 (retrieve, check_price, generate)

    TODO 4: 엣지 연결
      graph.add_edge(START, "retrieve")
      graph.add_edge("retrieve", "check_price")
      graph.add_edge("check_price", "generate")
      graph.add_edge("generate", END)

    TODO 5: return graph.compile(checkpointer=memory)
    """
    pass


def ask(agent, user_message: str, thread_id: str) -> str:
    """
    영화 프로젝트의 ask()와 동일한 역할 (외부 진입점).

    TODO 1: config = {"configurable": {"thread_id": thread_id}}
    TODO 2: agent.invoke({"query": user_message}, config)
    TODO 3: result["answer"] 반환
    """
    pass


if __name__ == "__main__":
    agent = build_agent()
    print(ask(agent, "출퇴근길에 가볍게 읽을 에세이 추천해줘", "test-thread"))
