@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title OrderFlow Enterprise - Instalacion
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0orderflow_manager.ps1" -Action Install
if errorlevel 1 (
  echo.
  echo La instalacion no pudo completarse.
  pause
  exit /b 1
)
echo.
echo Instalacion completada. Desde ahora usa START_ORDERFLOW.bat.
pause
