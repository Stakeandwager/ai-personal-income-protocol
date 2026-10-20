@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\private_console.py
) else (
  python scripts\private_console.py
)
endlocal
