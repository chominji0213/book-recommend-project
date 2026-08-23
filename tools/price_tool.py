"""
알라딘 ItemLookUp API로 특정 책의 실시간 가격/재고 정보를 조회하는 모듈.

이번 프로젝트에서 새로 추가되는 Tool Calling 파트야 - retrieve_node가 벡터DB에서
찾아낸 책들을, 이 모듈로 "지금 실제로 얼마에 파는지/재고 있는지" 확인하는 역할.
"""

# TODO: import
#   import os
#   import requests
#   from dotenv import load_dotenv
#   load_dotenv()

# TODO: 상수 정의
#   BASE_URL = "http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
#   TTBKEY = os.getenv("TTBKEY")


def check_price(item_id: str) -> dict:
    """
    도서 하나의 실시간 가격/재고 정보를 조회.

    TODO 1: params = {
                "ttbkey": TTBKEY,
                "ItemId": item_id,
                "ItemIdType": "ItemId",   # book_data.py에서 저장해둔 알라딘 itemId 그대로 사용
                "output": "js",
                "Version": "20131101",
            }

    TODO 2: GET {BASE_URL}, res.raise_for_status(), data = res.json()

    TODO 3: data["item"][0]에서 필요한 필드 추출
      - salePrice -> "판매가"
      - stockStatus -> "재고상태"  (예: "정상", "품절" 등)

    TODO 4: {"판매가": ..., "재고상태": ...} 형태로 반환
      - 조회 실패/결과 없음이면 {"error": "..."} 반환

    참고: retrieve_node가 검색해온 여러 책마다 이 함수를 반복 호출하게 될 거야
    (check_price_node에서 for문으로 돌면서 각 책의 id로 호출).
    """
    pass
