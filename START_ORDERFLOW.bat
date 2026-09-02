@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title OrderFlow Enterprise - Iniciar
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0orderflow_manager.ps1" -Action Start
if errorlevel 1 (
  echo.
  echo No se pudo iniciar OrderFlow.
  pause
  exit /b 1
)
