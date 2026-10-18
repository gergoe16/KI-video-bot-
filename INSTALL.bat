@echo off
chcp 65001 >nul
title KI Video Bot - Einrichtung
cd /d "%~dp0"
echo ============================================
echo   KI VIDEO BOT - EINMALIGE EINRICHTUNG
echo ============================================
echo.
python --version
if errorlevel 1 (
  echo FEHLER: Python wurde nicht gefunden.
  echo Installiere Python von https://www.python.org/downloads/windows/
  echo Aktiviere beim Installieren "Add Python to PATH".
  pause
  exit /b 1
)
echo.
echo Installiere benoetigte Python-Pakete...
python -m pip install --upgrade pip
if errorlevel 1 (
  echo Fehler beim Aktualisieren von pip. Versuche es trotzdem weiter...
)
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo FEHLER: Python-Pakete konnten nicht installiert werden.
  pause
  exit /b 1
)
echo.
where ollama >nul 2>nul
if errorlevel 1 (
  echo HINWEIS: Ollama wurde nicht gefunden.
  echo Installiere es von https://ollama.com/download/windows
  echo Starte danach INSTALL.bat erneut.
  pause
  exit /b 1
)
echo Lade das lokale KI-Modell llama3.2 herunter...
ollama pull llama3.2
if errorlevel 1 (
  echo Das Modell konnte nicht geladen werden.
  echo Pruefe deine Internetverbindung und ob Ollama installiert ist.
  pause
  exit /b 1
)
echo.
echo FERTIG! Starte den Bot mit START.bat.
pause
