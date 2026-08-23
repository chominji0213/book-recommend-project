"""
도서 데이터를 임베딩으로 변환해 Chroma 벡터DB에 저장하고, 의미 기반으로 검색하는 모듈.

영화 프로젝트의 vector_store.py랑 구조가 완전히 동일해. 필드명만 도서에 맞게 바꾸면 돼
(이번엔 새로 배울 개념 없이 거의 복붙 + 이름만 바꾸는 복습 성격이야).

- build_vector_store(): books.json을 읽어서 벡터DB를 "구축"하는 함수 (최초 1회 실행)
- search_books(): 벡터DB에서 "검색"하는 함수
"""

# TODO: import (영화 프로젝트 vector_store.py랑 동일)
#   import json
#   from dotenv import load_dotenv
#   from langchain_google_genai import GoogleGenerativeAIEmbeddings
#   from langchain_chroma import Chroma
#   from langchain_core.documents import Document
#   load_dotenv()

PERSIST_DIR = "vectorstore"
EMBEDDING_MODEL = "gemini-embedding-2-preview"  # 영화 프로젝트에서 이미 검증된 모델명 그대로 사용


def build_vector_store(books_path: str = "data/books.json"):
    """
    TODO 1: books_path 파일을 열어서 json.load로 도서 리스트 읽기

    TODO 2: 각 책을 Document 객체로 변환해서 리스트에 담기
      documents.append(Document(
          page_content=book["줄거리"],
          metadata={
              "제목": book["제목"],
              "저자": book["저자"],
              "출간일": book["출간일"],
              "정가": book["정가"],
          },
      ))

    TODO 3: 임베딩 모델 준비 (GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL))

    TODO 4: Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=PERSIST_DIR)
      - 주의: vectorstore/ 폴더가 이미 있는 상태에서 다시 실행하면 중복 저장됨
        (영화 프로젝트에서 겪었던 문제) - 재구축 전엔 vectorstore/ 폴더 먼저 삭제할 것
    """
    pass


def load_vector_store():
    """
    TODO: return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL),
    )
    """
    pass


def search_books(query: str, k: int = 5) -> dict:
    """
    TODO 1: load_vector_store()로 벡터DB 인스턴스 가져오기

    TODO 2: vector_store.similarity_search(query, k=k) 호출

    TODO 3: 검색된 각 Document에서 필요한 정보를 꺼내 딕셔너리로 정리
      - doc.page_content -> "줄거리"
      - doc.metadata["제목"], doc.metadata["저자"], doc.metadata["출간일"], doc.metadata["정가"]

    TODO 4: {"검색어": query, "결과": 정리된_리스트} 형태로 반환
      - 검색 결과가 없으면 {"error": "..."} 반환
    """
    pass


if __name__ == "__main__":
    # 터미널에서 python -m tools.vector_store 로 최초 1회 실행해서 벡터DB 구축
    build_vector_store()
    print("벡터DB 구축 완료")
