"""
알라딘 Open API 호출 모듈 - 베스트셀러/도서 목록을 가져와서 data/books.json으로 저장.

movie_data.py랑 거의 같은 구조야. TMDB -> 알라딘으로 API만 바뀐다고 생각하면 돼.
"""
import os
import json
import requests
from dotenv import load_dotenv
from rich import print as rprint
load_dotenv()

BASE_URL = "http://www.aladin.co.kr/ttb/api/ItemList.aspx"
TTBKEY = os.getenv('TTBKEY')


def fetch_books(max_pages: int = 20, max_results: int = 50) -> list[dict]:
    """
    알라딘의 "베스트셀러" 목록을 여러 페이지 가져와서 필요한 필드만 정리해 반환.
    """
    books = []

    for page in range(1, max_pages + 1):
      start = (page - 1) * max_results + 1 
      params = {
            "ttbkey": TTBKEY,
            "QueryType": "Bestseller",
            "MaxResults": max_results,
            "start": start,
            "SearchTarget": "Book",
            "output": "js",
            "Version": "20131101",
        }
      res = requests.get(BASE_URL, params=params, timeout=5)
      res.raise_for_status()
      data = res.json()['item']

      for d in data:
          description = d.get('description', '')

          #description이 빈 문자열인 책은 건너뛰기
          if not description:
              continue
          
          books.append({
              'id': d['itemId'],
              '제목': d['title'],
              '줄거리': description,
              '저자': d['author'],
              '출간일': d['pubDate'],
              '정가': d['priceStandard']
          })

    return books  


def save_books_to_json(books: list[dict], path: str = "data/books.json"):
    """
    가져온 book api 결과를 json 파일로 저장
    """
    os.makedirs(os.path.dirname(path), exist_ok=True) #데이터없으면 디렉토리 생성

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 터미널에서 python -m tools.book_data 로 실행
    books = fetch_books(max_pages=5)
    save_books_to_json(books)
    print(f"{len(books)}개 도서 저장 완료")
