@echo off
:: E1 Assistant - Windows Installer
:: Run this in PowerShell or CMD as: curl -sL [your-raw-github-url]/install.bat | cmd

echo.
echo  ========================================
echo   E1 Assistant - Local Installation
echo  ========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9+ from python.org
    exit /b 1
)

:: Check for Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18+ from nodejs.org
    exit /b 1
)

echo [OK] Prerequisites found
echo.

:: Clone or update repo
if exist "e1-assistant" (
    echo [INFO] Updating existing installation...
    cd e1-assistant
    git pull
) else (
    echo [INFO] Cloning E1 Assistant...
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git e1-assistant
    cd e1-assistant
)

echo.
echo [INFO] Installing backend dependencies...
cd backend
pip install -r requirements.txt -q

echo.
echo [INFO] Installing frontend dependencies...
cd ..\frontend
call npm install --silent

:: Create .env files if they don't exist
cd ..\backend
if not exist ".env" (
    echo.
    set /p MONGO_URL="Enter MongoDB URL (press Enter for local): "
    set /p EMERGENT_KEY="Enter your Emergent LLM Key: "
    
    if "%MONGO_URL%"=="" set MONGO_URL=mongodb://localhost:27017
    
    echo MONGO_URL="%MONGO_URL%" > .env
    echo DB_NAME="e1_assistant" >> .env
    echo CORS_ORIGINS="*" >> .env
    echo EMERGENT_LLM_KEY=%EMERGENT_KEY% >> .env
    echo [OK] Backend .env created
)

cd ..\frontend
if not exist ".env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > .env
    echo [OK] Frontend .env created
)

cd ..

echo.
echo  ========================================
echo   Installation Complete!
echo  ========================================
echo.
echo  To start E1 Assistant, run:
echo    cd e1-assistant
echo    start.bat
echo.
echo  Or manually:
echo    Terminal 1: cd backend ^&^& python -m uvicorn server:app --reload --port 8001
echo    Terminal 2: cd frontend ^&^& npm start
echo.
echo  Then open: http://localhost:3000
echo.

pause
