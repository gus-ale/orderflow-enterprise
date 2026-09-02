@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title OrderFlow Enterprise - Detener
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0orderflow_manager.ps1" -Action Stop
if errorlevel 1 pause
