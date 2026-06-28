# 윈도우에서 로컬로 실행하기

이미 `git clone` 으로 사본이 있으면 아래만 따라 하면 된다. **설치는 최초 1회만.**

## 1) 최초 설치 (한 번만)

저장소 폴더에서 PowerShell을 열고:

```powershell
powershell -ExecutionPolicy Bypass -File setup-windows.ps1
```

이 스크립트가 **uv · Node.js · pnpm** 을 자동 설치한다.
설치가 끝나면 **터미널 창을 닫고 새로 연다** (PATH 반영).

> winget이 없어서 Node 설치가 안 되면 https://nodejs.org 에서 LTS를 직접 설치한 뒤
> 스크립트를 다시 실행한다.

## 2) 실행 (매번)

탐색기에서 저장소 폴더의 두 파일을 차례로 **더블클릭**:

1. `start-backend.bat`  → 백엔드 (http://localhost:8000) — 창을 켜둔다
2. `start-frontend.bat` → 프론트엔드 (http://localhost:3000) — 창을 켜둔다

두 창을 모두 켜둔 채, 브라우저에서 **http://localhost:3000** 접속.

기본은 테스트 모드(mock)라 API 키 없이 동작하고 **과금이 없다**.
실제 검색을 쓰려면 `backend\.env` 에서 키를 채우고 `GEO_TEST_MODE=false` 로 바꾼다.

## 문제 해결

- **'uv'/'pnpm'을 찾을 수 없음** → 설치 후 터미널(또는 탐색기)을 새로 열지 않은 것. 창을 새로 연다.
- **포트 충돌** → 8000/3000을 쓰는 다른 프로그램을 끄거나, 해당 포트를 사용하는 프로세스를 종료한다.
