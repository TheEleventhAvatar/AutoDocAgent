@echo off
echo Starting AutoDoc Agent Frontend...

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Check for .env.local
if not exist ".env.local" (
    echo Creating .env.local file from example...
    copy .env.local.example .env.local
)

REM Start the development server
echo Starting Next.js development server...
npm run dev

pause
