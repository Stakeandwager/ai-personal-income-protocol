@echo off
setlocal
cd /d "%~dp0.."
echo ==========================================
echo APIP Windows executable build
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher "py" was not found. Install Python 3.11+ from python.org and retry.
  pause
  exit /b 1
)
py -m pip install --upgrade pip
if errorlevel 1 goto failed
py -m pip install -r desktop\requirements-build.txt
if errorlevel 1 goto failed
py -m PyInstaller --noconfirm --clean --windowed --name APIP --onefile desktop\apip_desktop.py
if errorlevel 1 goto failed
echo.
echo BUILD COMPLETE: dist\APIP.exe
echo Launch it and verify the database persists after closing and reopening.
pause
exit /b 0
:failed
echo.
echo BUILD FAILED. Read the error above; no executable should be assumed to exist.
pause
exit /b 1
