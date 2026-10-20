@echo off
echo Starting E2M Solutions FastAPI Backend on http://localhost:8000 ...
cd /d "%~dp0backend"
call .venv\Scripts\activate.bat
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
