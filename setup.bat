@echo off
setlocal

:: Set the name of the virtual environment
set "ENV_NAME=.venv"

:: Check if Python is installed
python --version
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3 first.
    exit /b 1
)

:: Create the virtual environment
python -m venv %ENV_NAME%

:: Activate the virtual environment
call %ENV_NAME%\Scripts\activate

:: Install the required packages from requirements.txt
pip install -r requirements.txt

:: Deactivate the virtual environment
deactivate

echo Virtual environment setup complete!
endlocal
