@echo off
echo Starting AutoDoc Agent Backend...

REM Navigate to backend directory
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\fastapi" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check for .env file
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
    echo Please edit .env file and add your OpenAI API key
    pause
)

REM Start the server
echo Starting FastAPI server...
uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
