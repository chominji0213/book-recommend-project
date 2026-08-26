#!/bin/bash
set -e

# 컨테이너가 처음 켜질 때(또는 재시작으로 파일이 사라졌을 때)만 데이터/벡터DB를 새로 구축.
# 이미 만들어져 있으면 건너뛰어서, 슬립->웨이크업마다 불필요하게 알라딘/임베딩 API를
# 다시 호출하지 않도록 함 (API 호출 비용/시간 절약).

if [ ! -f "data/books.json" ]; then
    echo "[entrypoint] 도서 데이터 수집 중 (알라딘 API)..."
    python -c "from tools.book_data import fetch_books, save_books_to_json; save_books_to_json(fetch_books())"
fi

if [ ! -d "vectorstore" ]; then
    echo "[entrypoint] 벡터DB 구축 중 (Gemini 임베딩)..."
    python -c "from tools.vector_store import build_vector_store; build_vector_store()"
fi

echo "[entrypoint] Streamlit 앱 시작..."
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.fileWatcherType=none
