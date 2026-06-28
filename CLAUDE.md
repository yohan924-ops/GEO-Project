# CLAUDE.md — GEO 분석 도구 (GEO Analyzer)

> 이 문서는 Claude Code가 이 저장소에서 작업할 때 따라야 할 **기준 문서**다.
> 아키텍처·데이터 모델·개발 규칙·로드맵을 정의한다. 코드를 추가/수정하기 전에 이 문서를 먼저 확인할 것.

---

## 1. 프로젝트 개요

**GEO(Generative Engine Optimization) 분석 도구**다. 제품/브랜드를 입력하면 생성형 검색엔진
(ChatGPT·Gemini·Claude)에서의 **노출·인용 현황을 측정**하고, 점유율을 높이기 위한 **전략을 제공**한다.

기존 SEO가 "검색결과 순위"를 노렸다면, GEO는 **"AI가 생성한 답변에 인용·언급되는 것"**을 목표로 한다.
이 도구는 그 노출도를 정량 측정하는 분석 플랫폼이다.

- **형태:** 내부 도구 / 단일 사용자 (인증·결제·멀티테넌시 **없음**)
- **방향:** MVP부터 단계적 구축 (로드맵은 §8)

---

## 2. 제공 서비스 (기능 명세)

| # | 기능 | 입력 | 처리 | 출력 |
|---|------|------|------|------|
| 1 | **키워드·프롬프트 생성** | 제품/브랜드명 | 국내 소비자가 연관 검색할 키워드·질문 프롬프트를 LLM으로 생성 (검색 트렌드 보강 권장) | 키워드 100개 + 질문 프롬프트 100개 |
| 2 | **순위 분석** | 1의 프롬프트 | 각 프롬프트를 ChatGPT·Gemini·Claude에 **각 10회** 검색 → 답변에 등장하는 브랜드/서비스 추출·집계 | 브랜드/서비스 노출 순위 + 등장 빈도/안정성 |
| 3 | **온드미디어 인용 점유율 분석** | 1의 프롬프트 | 동일 10회 검색에서 **인용 소스 URL** 수집 → 도메인 추출 → 브랜드 온드미디어(웹/Instagram/블로그/Facebook 등) 매핑 | 브랜드별 인용 점유율 순위 |
| 4 | **GEO 전략 제공** | 2·3 결과 | 갭 분석 → 해당 분야에서 GEO 점유율을 높이기 위한 실행 전략을 LLM으로 생성 | 우선순위가 매겨진 전략 리포트 |

> **핵심 원칙:** 서비스 2·3의 "검색"은 **소비자용 채팅 UI 자동화/스크래핑이 아니라, 웹검색 기능이
> 켜진 공식 API**로 수행한다 (약관 준수 + 인용 데이터의 안정적 확보). 자세한 내용은 §6.

---

## 3. 기술 스택

| 영역 | 선택 | 비고 |
|------|------|------|
| Backend | **Python 3.12+ / FastAPI** | LLM 오케스트레이션·비동기 잡·데이터 분석에 최적 |
| Frontend | **Next.js (App Router) / TypeScript** | 대시보드·시각화 |
| DB | **SQLite (MVP) → PostgreSQL (확장)** | 단일 사용자라 SQLite로 시작 |
| ORM | **SQLModel** (SQLAlchemy 기반) | 모델 = 테이블 + Pydantic |
| 비동기 | `asyncio` + 동시성 제한 (MVP) → RQ/Celery + Redis (확장) | §6의 잡 러너 참고 |
| 차트 | **Recharts** | 순위/점유율 시각화 |
| LLM SDK | `anthropic`, `openai`, `google-genai` | 공식 SDK 사용 |
| 패키지 매니저 | Backend: **uv** · Frontend: **pnpm** | |
| 데이터 분석 | `pandas` | 집계·점유율 계산 |

---

## 4. 아키텍처

### 디렉터리 구조

```
.
├── CLAUDE.md
├── backend/
│   ├── pyproject.toml
│   ├── .env.example
│   ├── app/
│   │   ├── main.py            # FastAPI 엔트리포인트
│   │   ├── config.py          # Settings (env 로드)
│   │   ├── db.py              # SQLModel engine / session
│   │   ├── models/            # DB 모델 (§5)
│   │   ├── schemas/           # Pydantic 요청/응답
│   │   ├── api/               # FastAPI 라우터 (brands, analyses, ...)
│   │   ├── providers/         # LLM 어댑터 (§6)
│   │   │   ├── base.py        # ProviderAdapter 인터페이스 + 정규화 타입
│   │   │   ├── openai_adapter.py
│   │   │   ├── gemini_adapter.py
│   │   │   └── anthropic_adapter.py
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── prompt_gen.py  # 서비스 1: 키워드/프롬프트 생성
│   │   │   ├── search_runner.py  # 비동기 검색 잡 러너
│   │   │   ├── ranking.py     # 서비스 2: 순위 집계
│   │   │   ├── citation.py    # 서비스 3: 인용→도메인→브랜드 매핑·점유율
│   │   │   └── strategy.py    # 서비스 4: 전략 생성
│   │   └── jobs/              # 잡 큐 / 진행률 추적
│   └── tests/                 # pytest
└── frontend/
    ├── package.json
    ├── app/                   # Next.js App Router (페이지)
    ├── components/            # 차트·테이블 등
    └── lib/                   # 백엔드 API 클라이언트
```

### 데이터 흐름

```
브랜드 입력
   ↓  services/prompt_gen.py
프롬프트 100개 생성 (서비스 1)
   ↓  services/search_runner.py  (비동기 잡: 프롬프트 × 3 provider × 10회)
검색 실행 → providers/*  (웹검색 API 호출, 결과 정규화)
   ↓  ProviderRun 저장 (answer_text + citations)
   ├─ services/ranking.py   → 등장 브랜드 추출·순위 집계 (서비스 2)
   └─ services/citation.py  → 인용 URL → 도메인 → 브랜드 매핑·점유율 (서비스 3)
   ↓  services/strategy.py
전략 리포트 생성 (서비스 4)
   ↓
대시보드 (Next.js): 프롬프트 목록 · 순위 차트 · 점유율 차트 · 전략
```

---

## 5. 데이터 모델

| 모델 | 핵심 필드 | 설명 |
|------|-----------|------|
| **Brand** | `id`, `name`, `industry` | 분석 대상 브랜드 |
| **OwnedMedia** | `id`, `brand_id`, `media_type`(web/instagram/blog/facebook), `domain_or_handle` | 브랜드↔온드미디어 **매핑 레지스트리** (서비스 3 핵심) |
| **Analysis** | `id`, `brand_id`, `status`(pending/running/done/failed), `progress`, `total_calls`, `cost_usd`, `created_at` | 분석 1건(run) |
| **Prompt** | `id`, `analysis_id`, `type`(keyword/question), `text` | 생성된 키워드·질문 (서비스 1) |
| **ProviderRun** | `id`, `prompt_id`, `provider`, `model`, `run_index`(0~9), `answer_text`, `usage`, `cost_usd`, `latency_ms`, `raw` | 프롬프트 1개를 1개 provider에 1회 호출한 결과 |
| **Mention** | `id`, `provider_run_id`, `brand_or_service`, `rank` | 답변에 등장한 브랜드/서비스 (서비스 2) |
| **Citation** | `id`, `provider_run_id`, `url`, `title`, `snippet`, `domain`, `matched_brand_id`(nullable), `media_type` | 답변의 인용 소스 (서비스 3) |
| **Strategy** | `id`, `analysis_id`, `priority`, `title`, `rationale`, `action_items` | 전략 리포트 항목 (서비스 4) |

> **집계 규칙:** 순위/점유율은 ProviderRun을 raw로 저장한 뒤 `pandas`로 집계한다. 원본을 보존해야
> provider별·반복별 변동성(안정성) 분석이 가능하다.

---

## 6. LLM 연동 규칙 (가장 중요)

### 6.1 Provider Adapter 패턴

3사 호출을 **공통 인터페이스**로 정규화한다. `providers/base.py`:

```python
from dataclasses import dataclass, field

@dataclass
class Citation:
    url: str
    title: str | None
    snippet: str | None
    domain: str           # urllib.parse로 추출

@dataclass
class ProviderResult:
    provider: str         # "openai" | "gemini" | "anthropic"
    model: str
    answer_text: str
    citations: list[Citation] = field(default_factory=list)
    usage: dict = field(default_factory=dict)   # 입력/출력 토큰
    cost_usd: float = 0.0
    latency_ms: int = 0
    raw: dict = field(default_factory=dict)      # 원본 응답(디버깅)

class ProviderAdapter:
    """모든 provider 어댑터가 구현하는 비동기 인터페이스."""
    async def search(self, prompt: str, *, model: str) -> ProviderResult: ...
```

각 어댑터는 웹검색을 켜고 호출한 뒤 답변 텍스트와 인용 URL을 `ProviderResult`로 변환한다.

### 6.2 3사 웹검색 API 요점

| Provider | 호출 | 인용(citation) 위치 |
|----------|------|---------------------|
| **OpenAI (ChatGPT)** | Responses API + `web_search` 툴 | 응답 메시지의 출처 주석(annotations)의 URL |
| **Gemini (Google)** | `google_search` grounding 툴 | `groundingMetadata.groundingChunks[].web.uri` (및 title) |
| **Anthropic (Claude)** | `web_search_20260209` 툴 | `web_search_tool_result` 블록의 인용 URL·제목·인용문 |

> OpenAI/Gemini의 정확한 필드명·SDK 시그니처는 각 공식 문서로 최종 확인할 것(버전에 따라 변동).
> Anthropic은 §6.3 참고.

### 6.3 Anthropic(Claude) 어댑터 — 검증된 사용법

- 모델은 웹검색 지원 모델을 쓴다: `claude-opus-4-8`, `claude-sonnet-4-6` 등 (`web_search_20260209`는
  Opus 4.8/4.7/4.6·Sonnet 4.6 지원).
- 웹검색 결과의 인용은 자동으로 결과 블록에 포함된다. 답변 텍스트와 인용을 분리 수집한다.

```python
# anthropic 공식 SDK
resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=[{"type": "web_search_20260209", "name": "web_search"}],
    messages=[{"role": "user", "content": prompt}],
)
# resp.content 를 순회하며:
#  - type == "text"                     → answer_text 누적
#  - type == "web_search_tool_result"   → .content 의 각 결과에서 url/title 수집
```

### 6.4 모델·단가 설정

- provider별 모델은 **env/설정으로 교체 가능**하게 한다 (`config.py`).
- **검색 시뮬레이션(서비스 2·3):** 소비자 경험을 대표하는 모델. 1회 분석당 호출이 많으므로(아래)
  비용/품질 균형 모델을 기본값으로 (예: Claude는 `claude-sonnet-4-6`), 고정밀이 필요하면 상향.
- **내부 생성(서비스 1·4):** 강한 모델 + **구조화 출력(structured output)**으로 안정적 파싱
  (예: `claude-opus-4-8`).

Anthropic 단가(참고, 입력/출력 per 1M tokens): Opus 4.8 `$5/$25` · Sonnet 4.6 `$3/$15` · Haiku 4.5 `$1/$5`.
웹검색 툴은 검색 횟수 기반 추가 비용이 있으므로 비용 추적에 포함한다.

### 6.5 비동기 잡 처리 (필수)

- **규모:** 분석 1건 = 프롬프트 100 × 3 provider × 10회 = **약 3,000 호출**. 동기 처리 불가.
- **MVP:** `asyncio` + `Semaphore`로 **provider별 동시성 제한** + **지수 백오프 재시도** + `Analysis.progress` 갱신.
- **확장:** RQ 또는 Celery + Redis로 분리.
- **반드시:** rate limit(429)·일시 오류는 재시도, 영구 오류는 해당 ProviderRun만 실패 처리하고 잡은 계속.
- **비용 추적:** ProviderRun마다 `usage`·`cost_usd` 기록, Analysis에 합산.

### 6.6 인용 → 브랜드 매핑 (서비스 3)

1. 인용 URL에서 도메인 추출 (`urllib.parse`, 서브도메인 정규화).
2. `OwnedMedia` 레지스트리와 매칭 → `Citation.matched_brand_id`/`media_type` 설정.
3. SNS는 핸들(@handle)·경로로 매핑 (instagram.com/{handle} 등).
4. `pandas`로 브랜드별 인용 수/점유율 집계.

---

## 7. 개발 규칙 (Conventions)

**Python (backend)**
- 전부 **type hint** 사용. I/O 바운드(LLM·HTTP)는 `async def`.
- 린트/포맷: **ruff**. 테스트: **pytest** (provider 어댑터는 **mock**으로 단위 테스트 — 실 호출 비용/불안정성 회피).
- 비밀키는 코드에 하드코딩 금지. `config.py`가 env에서 로드. `.env`는 커밋 금지, `.env.example` 유지.
- 외부 응답 원본(`raw`)을 보존해 디버깅·재집계 가능하게 한다.

**TypeScript (frontend)**
- ESLint 적용. 백엔드 호출은 `lib/`의 API 클라이언트로 일원화.
- 차트는 Recharts. 상태는 단순 fetch + 캐싱(예: SWR/React Query)로 시작.

**공통**
- API 키: `OPENAI_API_KEY`, `GOOGLE_API_KEY`(또는 Gemini용), `ANTHROPIC_API_KEY`.
- 커밋: 작고 명확하게. 기본 브랜치에 직접 커밋하지 말고 작업 브랜치 사용.
- 모델 ID는 추측하지 말 것 — 위 명시된 ID 사용, 변경 시 공식 문서 확인.

---

## 8. 단계별 로드맵 (MVP-first)

> 각 Phase는 독립 실행 가능한 결과물을 낸다. **Phase 1부터 시작.**
> **진행 상태:** Phase 1~4 MVP 구현 완료 (전 과정 테스트 모드/mock으로 무과금 개발 가능).

- **Phase 1 — 기반 + 프롬프트 생성 + 어댑터 검증** ✅ 완료
  - 프로젝트 스캐폴딩(`backend/`, `frontend/`), DB·설정.
  - 서비스 1: 브랜드 입력 → 키워드·질문 프롬프트 100개씩 생성.
  - Provider Adapter 3종 골격 + **단일 프롬프트를 3사에 1회씩 호출**해 답변·인용 파싱 검증.
  - 산출물: 프롬프트 목록 화면 + "3사 1회 검색" 결과/인용 확인.

- **Phase 2 — 순위 분석 (서비스 2)** ✅ 완료
  - 비동기 잡 러너(10회 반복, 동시성 제한, 진행률).
  - 답변 내 브랜드/서비스 추출 → 노출 순위·빈도·안정성 집계 + 차트.

- **Phase 3 — 온드미디어 인용 점유율 분석 (서비스 3)** ✅ 완료
  - `OwnedMedia` 레지스트리 관리 UI.
  - 인용 URL → 도메인 → 브랜드 매핑 → 점유율 순위 + 차트.

- **Phase 4 — 전략 리포트 (서비스 4)** ✅ 완료
  - 2·3 결과를 컨텍스트로 갭 분석 → 우선순위 전략 생성.

- **공통(점진 적용):** 비용 추적, 잡 진행률 표시, 대시보드 시각화 고도화.

---

## 9. 실행 방법

```bash
# Backend
cd backend
uv sync
cp .env.example .env          # API 키 입력
uv run uvicorn app.main:app --reload   # http://localhost:8000

# Frontend
cd frontend
pnpm install
pnpm dev                      # http://localhost:3000
```

**필수 환경변수** (`backend/.env`)

```
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
DATABASE_URL=sqlite:///./geo.db
# provider별 모델 (선택, 미설정 시 기본값 사용)
SEARCH_MODEL_ANTHROPIC=claude-sonnet-4-6
GEN_MODEL_ANTHROPIC=claude-opus-4-8
```

---

## 참고

- 비용이 큰 작업(3,000 호출)이므로 개발 중에는 **프롬프트 수·반복 횟수를 줄인 테스트 모드**를 두고,
  provider 호출은 가능한 한 **mock**으로 단위 테스트할 것.
- 모델 ID·웹검색 툴 버전·단가는 변동될 수 있으니 의심되면 각 provider 공식 문서로 확인할 것.
