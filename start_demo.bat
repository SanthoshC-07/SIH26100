@echo off
title SIH26100 - Integrated Bid Compliance Verification Platform
color 0A

echo ===============================================================================
echo   SIH26100: AI-POWERED INTEGRATED BID COMPLIANCE VERIFICATION PLATFORM
echo   Ministry of Petroleum & Natural Gas - Petroleum Pipeline Procurement (GeM)
echo ===============================================================================
echo.

echo [1/3] Resetting & Seeding Demo Database (Idempotent)...
python scripts/seed_demo.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Demo data seeding failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Starting Backend API Server (FastAPI + SQLite 3 + ML Services)...
start "SIH26100 Backend (Port 8000)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo [3/3] Starting Frontend Client (React + Vite + TypeScript)...
start "SIH26100 Frontend (Port 5173)" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo ===============================================================================
echo   SYSTEM LAUNCHED SUCCESSFULLY!
echo ===============================================================================
echo.
echo   Frontend Application: http://localhost:5173
echo   Backend API Docs:     http://localhost:8000/docs
echo.
echo   DEMO CREDENTIALS:
echo   - Role: Procurement Officer
echo   - Username: procurement_officer
echo   - Password: officer123
echo.
echo   - Role: System Administrator
echo   - Username: admin
echo   - Password: admin123
echo.
echo   PRIMARY DEMO TENDER: MOPNG/PIPE/2026/017
echo   CANONICAL BIDDER:    PRAVEEN B S ENGINEERING SERVICES (100%% Compliant, Low Risk)
echo ===============================================================================
echo.
echo Opening browser in 4 seconds...
timeout /t 4 /nobreak >nul
start http://localhost:5173/login

echo Done. Keep the backend and frontend terminal windows open during presentation.
pause
