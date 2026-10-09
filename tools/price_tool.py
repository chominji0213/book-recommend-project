import os
import requests
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
TTBKEY = os.getenv("TTBKEY")


def check_price(item_id: str) -> dict:
    """
    도서 하나의 실시간 가격/재고 정보를 조회.
    """
    params = {
        "ttbkey": TTBKEY,
        "ItemId": item_id,
        "ItemIdType": "ItemId", 
        "output": "js",
        "Version": "20131101",
    }
    res = requests.get(BASE_URL, params=params, timeout=5)
    res.raise_for_status()
    data = res.json()

    if not data.get('item'):
        return {'error': '검색결과가 없습니다.'}
    
    salePrice = data['item'][0]['priceSales']

    if data['item'][0]['stockStatus'] == '':
        stockStatus = '정상'
    else:
        stockStatus = data['item'][0]['stockStatus']
        

    return {'판매가': salePrice, '재고상태': stockStatus}
    
