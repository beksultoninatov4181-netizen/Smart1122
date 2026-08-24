@echo off
chcp 65001 >nul
title Mini App
echo.
echo   Mini App brauzerda ochilmoqda...
echo   (bot ishlab turgan bo'lishi kerak)
echo.
start "" "http://localhost:8080/?dev=1"
timeout /t 3 >nul
