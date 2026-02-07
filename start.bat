@echo off
:: E1 Assistant - Start Script for Windows
echo.
echo  Starting E1 Assistant...
echo.

:: Start MongoDB if local (optional - comment out if using cloud)
:: start "MongoDB" mongod

:: Start Backend
start "E1 Backend" cmd /k "cd backend && python -m uvicorn server:app --reload --host 0.0.0.0 --port 8001"

:: Wait for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Frontend
start "E1 Frontend" cmd /k "cd frontend && npm start"

echo.
echo  ========================================
echo   E1 Assistant Starting...
echo  ========================================
echo.
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:3000 (opens automatically)
echo.
echo   Press any key to stop all services...
echo.

pause

:: Kill processes on exit
taskkill /FI "WINDOWTITLE eq E1 Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq E1 Frontend*" /F >nul 2>&1

echo Services stopped.
