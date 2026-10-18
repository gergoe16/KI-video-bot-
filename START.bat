@echo off
chcp 65001 >nul
title KI Video Bot
cd /d "%~dp0"
python bot.py
if errorlevel 1 (
  echo.
  echo Der Bot wurde mit einem Fehler beendet. Lies die Meldung oben.
)
echo.
pause
