@echo off
SETLOCAL

:: Check if the virtual environment exists
if not exist "..\venv_tweet\" (
    echo Creating Python virtual environment...
    py -m venv ..\venv_tweet
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b %ERRORLEVEL%
    )
) else (
    echo Virtual environment already exists
)

:: Activate the virtual environment
echo Activating virtual environment...
call ..\venv_tweet\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment
    pause
    exit /b %ERRORLEVEL%
)

:: Install required packages
echo Installing required Python packages...
pip install selenium psutil requests
if %ERRORLEVEL% neq 0 (
    echo Failed to install packages
    pause
    exit /b %ERRORLEVEL%
)

:: Run the Python program
echo Running tweet_automate.py...
py tweet_automate.py
if %ERRORLEVEL% neq 0 (
    echo The Python script exited with an error
    pause
    exit /b %ERRORLEVEL%
)

echo All tasks completed successfully
pause
ENDLOCAL