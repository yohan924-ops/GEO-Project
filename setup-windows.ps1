# GEO Analyzer — Windows 설치 도우미 (PowerShell)
# 사용법: PowerShell에서  powershell -ExecutionPolicy Bypass -File setup-windows.ps1

Write-Host "=== GEO Analyzer 설치 도우미 ===" -ForegroundColor Cyan

# 1) uv (Python 패키지 매니저 — Python도 자동 설치)
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "[OK] uv 이미 설치됨"
} else {
    Write-Host "[..] uv 설치 중..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}

# 2) Node.js LTS
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Node.js 이미 설치됨"
} else {
    Write-Host "[..] Node.js LTS 설치 중 (winget)..."
    winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
    Write-Host "Node 설치 후 PATH 반영을 위해 이 창을 닫고 새로 연 뒤 다시 실행하세요." -ForegroundColor Yellow
}

# 3) pnpm
if (Get-Command pnpm -ErrorAction SilentlyContinue) {
    Write-Host "[OK] pnpm 이미 설치됨"
} elseif (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "[..] pnpm 설치 중..."
    npm install -g pnpm
} else {
    Write-Host "[!] npm을 찾을 수 없습니다. 터미널을 새로 연 뒤 이 스크립트를 다시 실행하세요." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== 완료 ===" -ForegroundColor Green
Write-Host "터미널을 새로 연 다음:"
Write-Host "  1) start-backend.bat  더블클릭  (http://localhost:8000)"
Write-Host "  2) start-frontend.bat 더블클릭  (http://localhost:3000)"
Write-Host "브라우저에서 http://localhost:3000 접속"
