# 📚 도서 추천 챗봇 (RAG + Tool Calling + StateGraph)

사용자가 원하는 책 취향을 말하면, 벡터DB에서 의미적으로 가장 비슷한 책을 검색하고, 알라딘 API로 실시간 가격/재고를 조회한 뒤, LLM이 이 둘을 종합해 추천 이유와 함께 답변해주는 챗봇입니다.

영화 추천 챗봇(RAG) 프로젝트를 그대로 복습하면서, 두 가지를 새로 얹었습니다. 하나는 **Tool Calling** — 벡터DB에 저장된 정가가 아니라, 답변 직전에 알라딘 API로 실시간 판매가/재고를 다시 조회하는 것. 다른 하나는 **StateGraph 확장** — 영화 프로젝트의 2단계(`retrieve → generate`)에 `check_price` 노드를 추가해 3단계(`retrieve → check_price → generate`)로 구성한 것입니다. 또한 영화 프로젝트에서 발견했던 "멀티턴 대화에서 맥락을 잃는" 한계를 개선하기 위해 State에 `history` 필드를 추가했습니다.

## 기술 스택

- **LLM**: Gemini API (`gemini-3.1-flash-lite`, via LangChain `init_chat_model`)
- **임베딩**: Gemini 임베딩 모델 (`gemini-embedding-2-preview`)
- **벡터DB**: Chroma (로컬 파일 기반)
- **오케스트레이션**: LangGraph `StateGraph` (retrieve → check_price → generate, 3단계)
- **대화 저장**: LangGraph `SqliteSaver` 체크포인터
- **데이터 소스**: 알라딘(Aladin) Open API (도서 목록 + 실시간 가격/재고 조회)
- **UI**: Streamlit

## 주요 기능

- 자연어로 원하는 책 취향/분위기를 입력하면 벡터 검색 기반으로 추천
- 추천된 책마다 알라딘 API로 실시간 판매가/재고 상태를 함께 안내
- 대화 히스토리 저장 및 "새 대화 시작" 기능 (스레드 단위로 대화 구분)
- **멀티턴 맥락 유지**: 이전 질문(예: "경제 관련 책 추천해줘")의 맥락을 기억해서, 후속 질문(예: "다섯 개쯤 더 추천해줘")에도 이어서 답변
- 검색 결과가 없거나, 가격 조회가 실패하거나, LLM 호출이 실패해도 앱이 죽지 않고 안내 메시지 표시

## 아키텍처

```
사용자 질문
   │
   ▼
[retrieve_node]    ── 최근 history(최대 2턴)의 질문 + 이번 질문을 합쳐 검색어 구성
   │                  → search_books() 호출 → Chroma 벡터DB에서 의미 유사도 기반 검색
   ▼
[check_price_node] ── 검색된 책마다 check_price() 호출 → 알라딘 ItemLookUp API로
   │                  실시간 판매가/재고 조회 (Tool Calling)
   ▼
[generate_node]    ── 검색 결과 + 가격 정보 + 이전 대화 기록을 프롬프트에 담아
   │                  LLM 호출 → 추천 답변 생성, history에 (질문, 답변) 누적
   ▼
최종 답변 반환 (SqliteSaver가 스레드별 대화 기록 + history 저장)
```

데이터 흐름은 별도로 다음과 같이 준비됩니다 (최초 1회 실행):

```
알라딘 ItemList API → book_data.py → data/books.json
                                          │
                                          ▼
                                vector_store.py (임베딩)
                                          │
                                          ▼
                                Chroma 벡터DB (vectorstore/)
```

## 프로젝트 구조

```
book-recommend-project/
├── tools/
│   ├── book_data.py       # 알라딘 ItemList API로 베스트셀러 데이터 수집 → data/books.json 저장
│   ├── vector_store.py    # 임베딩 변환 + Chroma 벡터DB 구축/검색
│   └── price_tool.py      # 알라딘 ItemLookUp API로 실시간 가격/재고 조회 (Tool Calling)
├── llm_client.py           # StateGraph 기반 에이전트 (retrieve → check_price → generate)
├── app.py                  # Streamlit UI
├── requirements.txt
└── .env.example
```

## 로컬 실행 방법

```bash
# 1. 가상환경 및 의존성 설치
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. .env 파일 생성 (.env.example 참고)
#    GOOGLE_API_KEY=...
#    TTBKEY=...

# 3. 도서 데이터 수집 및 벡터DB 구축 (최초 1회)
python -m tools.book_data
python -m tools.vector_store

# 4. 앱 실행
streamlit run app.py
```

### Docker로 실행

```bash
docker build -t book-recommend-project .
docker run -p 8501:8501 --env-file .env book-recommend-project
```

`entrypoint.sh`가 컨테이너 시작 시 `data/books.json`, `vectorstore/`가 없으면 자동으로 생성합니다. 이미 존재하면 알라딘 API와 임베딩 API를 재호출하지 않고 건너뜁니다.

## 알게 된 점 / 한계

- **알라딘 API의 페이지네이션은 TMDB와 다르다**: TMDB는 `page=1,2,3...`처럼 페이지 번호로 넘어가지만, 알라딘의 `start` 파라미터는 아이템 인덱스 오프셋이라 `start = (page - 1) * max_results + 1` 공식으로 직접 계산해야 합니다.
- **`http://`로 요청하면 리다이렉트가 한 번 더 발생한다**: 알라딘 서버가 `http://`를 `https://`로 자동 리다이렉트시켜 요청이 2번 나가고, 그만큼 타임아웃 위험이 커집니다. `BASE_URL`을 처음부터 `https://`로 지정해 해결했습니다.
- **벡터 검색은 카테고리로 필터링하지 못한다** (영화 프로젝트와 동일한 한계): "자기개발서 추천해줘"라고 물어도 의미적으로 가까운 철학 에세이나 소설이 함께 검색될 수 있습니다. 이는 데이터 풀이 작을수록(48권) 더 두드러집니다.
- **멀티턴 맥락 유지, 부분적으로 개선**: State에 `history` 필드를 추가하고 `generate_node`가 이전 (질문, 답변)을 프롬프트에 포함하도록 했더니, 답변 레벨에서는 맥락을 기억합니다. 하지만 처음엔 `retrieve_node`가 그 턴의 질문 텍스트만으로 검색해서, "다섯 개쯤 추천해줘" 같은 후속 질문은 여전히 엉뚱한 검색 결과를 가져왔습니다. `retrieve_node`가 최근 history의 질문들과 이번 질문을 합쳐 검색어를 재구성하도록 고쳐서, 검색 단계에서도 맥락이 이어지도록 개선했습니다. 다만 원본 데이터 풀 자체가 작다 보니(48권), 특정 주제(예: 경제)를 정확히 다루는 책이 애초에 없으면 검색 품질에는 한계가 남습니다.


## 향후 개선 아이디어

- QueryType/카테고리를 다양화해 데이터 풀을 늘리고, 카테고리 메타데이터 기반 하이브리드 검색(벡터 유사도 + 카테고리 필터) 추가
- Render로 배포 (영화 프로젝트와 동일한 패턴)
- 스트리밍 응답 지원 (`ask_stream`)
