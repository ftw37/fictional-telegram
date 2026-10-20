@echo off
setlocal
cd /d "%~dp0"
set "GAME_NODE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not exist "%GAME_NODE%" (
  echo Node.js was not found. Ask Codex to update this launcher.
  pause
  exit /b 1
)
"%GAME_NODE%" --test tests/game.test.js
set "GAME_RESULT=%ERRORLEVEL%"
pause
exit /b %GAME_RESULT%
