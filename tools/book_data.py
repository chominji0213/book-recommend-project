"""
알라딘 Open API 호출 모듈 - 베스트셀러/도서 목록을 가져와서 data/books.json으로 저장.
"""
import os
import json
import time
import requests
from dotenv import load_dotenv
from rich import print as rprint
load_dotenv()

BASE_URL = "https://www.aladin.co.kr/ttb/api/ItemList.aspx"
TTBKEY = os.getenv('TTBKEY')

def fetch_books(max_pages: int = 5, max_results: int = 50) -> list[dict]:
    """
    알라딘의 "베스트셀러" 목록을 여러 페이지 가져와서 필요한 필드만 정리해 반환.
    """
    books = []
    seen_ids = set()

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

        for attempt in range(3):
            try:
                res = requests.get(BASE_URL, params=params, timeout=10)
                res.raise_for_status()
                data = res.json()['item']
                break
            except requests.exceptions.RequestException as e:
                print(f"page={page} 요청 실패 ({attempt+1}/3): {e}")
                time.sleep(2)
        else:
            print(f"page={page} 최종 실패, 건너뜀")
            continue

        time.sleep(0.5)

        for d in data:
            if d['itemId'] in seen_ids:
                continue
            seen_ids.add(d['itemId'])

            description = d.get('description', '')
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
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    books = fetch_books(max_pages=5, max_results=50)
    save_books_to_json(books)
    print(f"{len(books)}개 도서 저장 완료")
