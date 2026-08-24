@echo off
chcp 65001 >nul
title Hisob-kitob boti
cd /d "%~dp0"

echo.
echo ==========================================================
echo    HISOB-KITOB BOTI
echo ==========================================================
echo.

rem --- Python bormi? ---
set PY=
where py >nul 2>&1 && set PY=py
if not defined PY (
    where python >nul 2>&1 && set PY=python
)

if not defined PY (
    echo  [!] Python topilmadi.
    echo.
    echo  Python o'rnatish kerak. Hozir sayt ochiladi:
    echo    1. Sariq "Download Python" tugmasini bosing
    echo    2. Faylni ishga tushiring
    echo    3. MUHIM: "Add python.exe to PATH" katagiga belgi qo'ying
    echo    4. Install Now bosing
    echo    5. Keyin shu faylni qaytadan ishga tushiring
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b
)

echo  [1/3] Python topildi.
%PY% --version

rem --- kutubxonalar ---
echo.
echo  [2/3] Kerakli kutubxonalar tekshirilmoqda...
%PY% -c "import aiogram, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo        O'rnatilmoqda, biroz kuting...
    %PY% -m pip install --quiet --upgrade pip
    %PY% -m pip install --quiet aiogram openpyxl
    if errorlevel 1 (
        echo.
        echo  [!] Kutubxonalarni o'rnatib bo'lmadi.
        echo      Internetni tekshiring va qaytadan urinib ko'ring.
        echo.
        pause
        exit /b
    )
)
echo        Tayyor.

rem --- ishga tushirish ---
echo.
echo  [3/3] Bot ishga tushmoqda...
echo.
%PY% bot.py

echo.
echo ==========================================================
echo   Bot to'xtadi. Oynani yopishingiz mumkin.
echo ==========================================================
pause
