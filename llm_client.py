from typing import TypedDict
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from tools.vector_store import search_books
from tools.price_tool import check_price
from rich import print as rprint

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
    history = state.get('history', [])
    recent_queries = ' '.join([h['query'] for h in history[-2:]]) #최근 2턴만 가져옴
    search_query = f"{recent_queries} {state['query']}".strip()

    result = search_books(search_query)

    return {'search_results': result}


def check_price_node(state):
    """
    가격 조회 노드
    """
    prices = []
    books = state['search_results'].get('결과', [])

    for book in books:
        try:
          bookId = book['id']
          result = check_price(bookId)
        except Exception as e:
          rprint(f"[check_price_node] 가격조회 실패: {e}")
          result = {'error': '가격 정보를 가져오지 못했어요.'}
          
        prices.append(result)

    return {'price_info': prices}
    

def generate_node(state):
    """
    답변 생성 노드: 검색 결과 + 가격 정보를 종합해서 LLM이 추천 답변을 만들게 함.
    """
    if 'error' in state['search_results']:
        return {'answer': '죄송합니다. 취향에 맞는 책을 찾지 못했습니다. 다른 분위기나 키워드로 재검색하시길 바랍니다'}

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
