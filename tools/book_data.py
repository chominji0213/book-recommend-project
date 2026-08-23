"""
알라딘 Open API 호출 모듈 - 베스트셀러/도서 목록을 가져와서 data/books.json으로 저장.

movie_data.py랑 거의 같은 구조야. TMDB -> 알라딘으로 API만 바뀐다고 생각하면 돼.
"""

# TODO: import
#   import os
#   import json
#   import requests
#   from dotenv import load_dotenv
#   load_dotenv()

# TODO: 상수 정의
#   BASE_URL = "http://www.aladin.co.kr/ttb/api/ItemList.aspx"
#   TTBKEY = os.getenv("TTBKEY")


def fetch_books(max_pages: int = 5) -> list[dict]:
    """
    알라딘의 "베스트셀러" 목록을 여러 페이지 가져와서 필요한 필드만 정리해 반환.

    TODO 1: 빈 리스트 만들기 (결과 담을 곳)

    TODO 2: 1페이지부터 max_pages까지 for문으로 반복하면서
      - GET {BASE_URL}
      - params = {
            "ttbkey": TTBKEY,
            "QueryType": "Bestseller",   # 베스트셀러 목록 조회
            "MaxResults": 50,             # 한 번에 최대 50개
            "start": 현재_페이지_번호,       # 페이지네이션
            "SearchTarget": "Book",
            "output": "js",               # JSON으로 응답받기
            "Version": "20131101",
        }
      - res.raise_for_status(), data = res.json()
      - data["item"]이 그 페이지에 있는 도서 리스트

    TODO 3: data["item"]의 각 도서에서 필요한 필드만 뽑아서 딕셔너리로 만들고 리스트에 추가
      - itemId -> "id"
      - title -> "제목"
      - description -> "줄거리"   (임베딩/검색에 쓸 핵심 텍스트)
      - author -> "저자"
      - pubDate -> "출간일"
      - priceStandard -> "정가"
      - 주의: description이 빈 문자열인 책은 건너뛰기 (movie_data.py의 overview 필터링과 동일한 이유)

    TODO 4: 완성된 리스트 반환
    """
    pass


def save_books_to_json(books: list[dict], path: str = "data/books.json"):
    """
    movie_data.py의 save_movies_to_json()이랑 완전히 동일한 로직이야. 그대로 재사용해서 짜면 돼.

    TODO 1: os.makedirs(os.path.dirname(path), exist_ok=True)로 data 폴더가 없으면 생성

    TODO 2: json.dump(books, f, ensure_ascii=False, indent=2)로 저장
    """
    pass


if __name__ == "__main__":
    # 터미널에서 python -m tools.book_data 로 실행 (최초 1회, 데이터 수집용)
    books = fetch_books(max_pages=5)
    save_books_to_json(books)
    print(f"{len(books)}개 도서 저장 완료")
