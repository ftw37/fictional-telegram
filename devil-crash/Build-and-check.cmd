@echo off
setlocal
cd /d "%~dp0"
if not defined DEVIL_PYTHON set "DEVIL_PYTHON=python"
if not defined DEVIL_ZIG set "DEVIL_ZIG=zig"
"%DEVIL_PYTHON%" -u build_and_check.py
set "BUILD_RESULT=%ERRORLEVEL%"
pause
exit /b %BUILD_RESULT%
