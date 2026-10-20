@echo off
echo =========================================================
echo   Starting E2M Solutions AI Renovation & Cost Estimator  
echo =========================================================
start "E2M Backend (FastAPI)" cmd /k "%~dp0run_backend.bat"
start "E2M Frontend (Vite+React)" cmd /k "%~dp0run_frontend.bat"
echo Servers launched!
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:5173
echo =========================================================
