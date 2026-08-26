from typing import TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from tools.vector_store import search_books
from tools.price_tool import check_price
from rich import print as rprint


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

class BookState(TypedDict):
    query: str    # 사용자 질문
    search_results: dict # search_books() 검색 결과
    price_info: list
    answer: str
    history: list


def retrieve_node(state):
    """
    질문 검색노드
    """
    result = search_books(state['query'])

    return {'search_results': result}


def check_price_node(state):
    """
    가격 조회 노드
    """
    prices = []
    books = state['search_results'].get('결과', [])

    for book in books:
        bookId = book['id']
        result = check_price(bookId)

        prices.append(result)

    return {'price_info': prices}
    

def generate_node(state):
    """
    답변 생성 노드: 검색 결과 + 가격 정보를 종합해서 LLM이 추천 답변을 만들게 함.
    """
    history = state.get('history', [])
    try:
      llm = init_chat_model('gemini-3.1-flash-lite', model_provider='google_genai')
      prompt = f'''
              이전 대화 기록: {history}
              사용자 질문: {state['query']}
              검색된 도서 목록: {state['search_results']}
              가격정보: {state['price_info']}

              가장 첫번째로 기억해야하는건 이전 대화 기록이 있다면 그 맥락(장르, 취향 등)을 참고해서 답변해줘.
              사용자의 질문에 맞는 도서를 추천해줘. 만약 사용자가 도서추천갯수를 요청하면 해당하는 갯수만큼 추천해주고. 개수를 특별히 언급하지 않았다면 질문에 가장 부합하는 도서 한개를 추천해줘. 그리고 추천하는 도서의 실시간 재고상태랑 가격도 같이 알려줘.
              또한 각 도서마다 추천하는 이유와 줄거리를 요약해서 설명해줘. 만약 검색결과에 사용자 질문에 부합하는 도서가 없다면 취향을 다시 한번 재질문해줘
          '''
      result = llm.invoke([HumanMessage(content=prompt)])
      answer = result.content[0]['text']
    except Exception as e:
        rprint(f"[generate_node] LLM 호출 실패: {e}")
        answer = "죄송해요, 지금 답변을 생성하는 중 문제가 생겼어요. 잠시 후 다시 시도해 주세요."

    new_history = history + [{'query': state['query'], 'answer': answer}]

    return {'answer': answer, 'history': new_history}



def build_agent():
    '''
    그래프 구축(조립)
    '''
    conn = sqlite3.connect('checkpoint.db', check_same_thread=False)
    memory = SqliteSaver(conn)

    graph = StateGraph(BookState)

    graph.add_node('retrieve', retrieve_node)
    graph.add_node('checkprice', check_price_node)
    graph.add_node('generate', generate_node)

    graph.add_edge(START, 'retrieve')
    graph.add_edge('retrieve', 'checkprice')
    graph.add_edge('checkprice', 'generate')
    graph.add_edge('generate', END)

    agent = graph.compile(checkpointer=memory)

    return agent

def ask(agent, user_message: str, thread_id: str) -> str:
    config = {'configurable': {'thread_id': thread_id}}
    result = agent.invoke({'query': user_message}, config)

    return result['answer']


if __name__ == "__main__":
    agent = build_agent()
    rprint(ask(agent, "출퇴근길에 가볍게 읽을 에세이 추천해줘", "test-thread"))
    rprint(ask(agent, "그 중에 제일 저렴한 거 하나만 다시 알려줘", "test-thread"))
