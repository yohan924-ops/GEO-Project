# 배포 가이드 — GEO Analyzer

프론트엔드(Next.js)와 백엔드(FastAPI)를 분리 배포한다. 프론트는 **Vercel**, 백엔드는
**Render**(Railway·Fly.io도 동일 Dockerfile로 가능)를 기준으로 설명한다.

> 기본값 `GEO_TEST_MODE=true`에서는 mock으로 동작해 **3rd-party 과금이 없다**. 실제 검색을
> 쓰려면 API 키를 설정하고 `GEO_TEST_MODE=false`로 바꾼다.

---

## 1. 백엔드 → Render

1. Render Dashboard → **New → Blueprint** → 이 저장소 선택. 루트의 `render.yaml`을 자동 인식한다.
   (수동으로 하려면 New → Web Service → Docker, **Root Directory = `backend`**.)
2. 환경변수 설정:
   - `CORS_ORIGINS` = 배포된 프론트 URL (예: `https://geo-analyzer.vercel.app`)
   - 실제 검색을 쓸 경우: `GEO_TEST_MODE=false` + **구독 중인 엔진의 키만** 설정
     (`OPENAI_API_KEY` / `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY`).
   - **3개를 다 구독하지 않아도 된다.** 키를 넣은 엔진만 자동으로 사용된다.
     특정 엔진만 강제하려면 `ENABLED_PROVIDERS=anthropic` 처럼 지정.
   - 활성 엔진은 `GET /providers` 로 확인할 수 있다.
3. 배포되면 백엔드 URL을 받는다 (예: `https://geo-analyzer-backend.onrender.com`). `/{health}` 와
   `/docs` 로 동작을 확인한다.

> Render는 `$PORT`를 주입하며 Dockerfile이 이를 사용한다. SQLite는 단일 사용자엔 충분하지만
> 디스크가 휘발성일 수 있으니, 영속이 필요하면 Render Postgres + `DATABASE_URL`로 교체한다.

## 2. 프론트엔드 → Vercel

1. Vercel → **New Project** → 이 저장소 import.
2. **Root Directory = `frontend`** 로 지정 (모노레포라 필수). 프레임워크는 Next.js 자동 인식.
3. 환경변수 추가:
   - `NEXT_PUBLIC_API_BASE` = 위 백엔드 URL (예: `https://geo-analyzer-backend.onrender.com`)
4. Deploy. 완료되면 `https://<app>.vercel.app` 로 접속한다.

> `NEXT_PUBLIC_API_BASE`는 빌드 타임에 번들로 들어가므로, 값을 바꾼 뒤에는 **재배포**해야 한다.

## 3. 두 서비스 연결 (CORS)

- 프론트가 백엔드를 브라우저에서 호출하므로, 백엔드 `CORS_ORIGINS`에 **프론트 도메인**이 반드시
  포함되어야 한다. 누락 시 브라우저가 요청을 차단한다.
- 양쪽 URL이 확정된 뒤: Render의 `CORS_ORIGINS` ↔ Vercel의 `NEXT_PUBLIC_API_BASE`를 서로의
  실제 도메인으로 맞추고 각각 재배포한다.

## 4. 로컬 실행 (참고)

```bash
# backend
cd backend && uv sync && cp .env.example .env
uv run uvicorn app.main:app --reload      # http://localhost:8000

# frontend
cd frontend && pnpm install && pnpm dev    # http://localhost:3000
```

기본 `.env`는 `CORS_ORIGINS=http://localhost:3000`, 프론트는 `NEXT_PUBLIC_API_BASE` 미설정 시
`http://localhost:8000`을 사용한다.
