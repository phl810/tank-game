@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "NODE=node"
where node >nul 2>nul || set "NODE=C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"

echo 正在启动战机大乱斗 ...
start "战机大乱斗服务器" /min cmd /c ""%NODE%" server.js"
timeout /t 1 /nobreak >nul
start "" "http://localhost:8181"
exit
