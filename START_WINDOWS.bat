@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%\src"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher 'py' was not found. Install Python 3.10+ and try again.
  pause
  exit /b 1
)
py -m recruitment_engine.engine generate --out data/generated --seed 20261022 --scale 1
if errorlevel 1 goto :failed
py -m recruitment_engine.engine audit --data data/generated
if errorlevel 1 goto :failed
echo.
echo Generation and audit commands completed. To run tests, use: py -m pytest -q
pause
exit /b 0
:failed
echo A command failed. Review the message above and the README setup instructions.
pause
exit /b 1
