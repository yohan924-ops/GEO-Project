@echo off
REM GEO Analyzer 프론트엔드 실행 (더블클릭 또는 cmd에서 실행)
cd /d "%~dp0frontend"
echo 의존성 설치 중...
call pnpm install
echo 프론트엔드 시작 중...  http://localhost:3000  (이 창은 켜둔 채로 두세요)
call pnpm dev
pause
