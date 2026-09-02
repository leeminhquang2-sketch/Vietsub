@echo off
echo =====================================
echo  Tool Reup Pro - Cài Dat Tu Dong
echo =====================================
echo.

echo [1/3] Dang kiem tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Chua cai Python!
    echo Vui long tai va cai tu: https://python.org
    pause
    exit
)
echo [OK] Python da duoc cai dat

echo [2/3] Dang cai thu vien...
pip install customtkinter faster-whisper edge-tts requests Pillow

echo [3/3] Kiem tra FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [!] Chua cai FFmpeg!
    echo Tai tu: https://ffmpeg.org
)

echo.
echo =====================================
echo  Cai dat hoan tat!
echo  Chay 'python reup_tool.py' de bat dau
echo =====================================
pause
