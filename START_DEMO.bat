@echo off
setlocal
set "ROOT=%~dp0"
echo ============================================================
echo  OrderFlow Enterprise - Portfolio Demo
echo ============================================================
call "%ROOT%START_ORDERFLOW.bat"
if errorlevel 1 (
  echo.
  echo OrderFlow no pudo iniciarse. Revisa Docker Desktop y STATUS_ORDERFLOW.bat
  pause
  exit /b 1
)
timeout /t 3 /nobreak >nul
start "" http://localhost:4200
start "" http://localhost:8000/docs
start "" http://localhost:8088
start "" http://localhost:3000
start "" "%ROOT%DEMO_SCRIPT_8_MIN.md"
echo.
echo Demo preparada. Usa DEMO_SCRIPT_8_MIN.md como guia.
endlocal
