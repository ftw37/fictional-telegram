@echo off
setlocal
cd /d "%~dp0"
set "GAME_NODE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not exist "%GAME_NODE%" set "GAME_NODE=node"
"%GAME_NODE%" --test tests/game.test.js
set "GAME_RESULT=%ERRORLEVEL%"
pause
exit /b %GAME_RESULT%
