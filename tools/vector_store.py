"""
도서 데이터를 임베딩으로 변환해 Chroma 벡터DB에 저장하고, 의미 기반으로 검색하는 모듈.
"""

import json
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
load_dotenv()

PERSIST_DIR = "vectorstore"
EMBEDDING_MODEL = "gemini-embedding-2-preview"  

def build_vector_store(books_path: str = "data/books.json"):
    """
    도서 데이터를 읽어서 임베딩으로 변환하고, Chroma에 저장,
    벡터 DB  구축
    """
    with open(books_path, 'r', encoding='utf-8') as f:
        books = json.load(f)
    
    documents = []
    for book in books:
        documents.append(Document(
            page_content=book['줄거리'],
            metadata={
                'id': book['id'],
                '제목': book['제목'],
                '저자': book['저자'],
                '출간일': book['출간일'],
                '정가': book['정가']
            }
        ))

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=PERSIST_DIR) #persist_directory: 만든 벡터DB를 이 폴더에 파일로 저장(영구저장)
   

def load_vector_store():
    """
    build_vector_store()로 만들어둔 벡터DB를 다시 불러오는 함수
    """
    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    )


def search_books(query: str, k: int = 5) -> dict:
    """
    사용자의 취향/질문과 의미적으로 비슷한 도서를 벡터DB에서 검색.
    LLM이 Tool Calling으로 호출할 함수
    """
    vector = load_vector_store()
    results = vector.similarity_search(query, k=k)

    if not results:
        return {'error': '검색결과가 없습니다.' }
    
    books = []
    for doc in results:
        books.append({
            'id': doc.metadata['id'],
            '제목': doc.metadata['제목'],
            '줄거리': doc.page_content,
            '저자': doc.metadata['저자'],
            '출간일': doc.metadata['출간일'],
            '정가': doc.metadata['정가']
        })

    return {'검색어': query, '결과': books}

if __name__ == "__main__":
    build_vector_store()
    print("벡터DB 구축 완료")
