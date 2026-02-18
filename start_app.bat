@echo off
echo Starting IdeaSA System...

start "IdeaSA Backend" cmd /c "cd backend && call .venv\Scripts\activate && uvicorn main:app --reload --port 8000"
timeout /t 5 >nul

start "IdeaSA Frontend" cmd /c "cd frontend && npm run dev"

echo System started!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo Press any key to exit launcher...
pause
