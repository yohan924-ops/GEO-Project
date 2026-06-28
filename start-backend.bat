@echo off
REM GEO Analyzer 백엔드 실행 (더블클릭 또는 cmd에서 실행)
cd /d "%~dp0backend"
if not exist .env copy .env.example .env
echo 백엔드 시작 중...  http://localhost:8000  (이 창은 켜둔 채로 두세요)
uv run uvicorn app.main:app --reload
pause
