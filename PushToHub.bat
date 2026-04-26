@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "CFG=.hubconfig"

if not exist ".git" (
    echo Not a git repo. Run InitHub.bat first.
    pause
    exit /b 1
)

if not exist "%CFG%" (
    echo No .hubconfig found.
    pause
    exit /b 1
)

for /f "usebackq delims=" %%i in ("%CFG%") do set "REPO=%%i"
echo Repo: %REPO%

git status --porcelain | findstr . >nul || (
    echo Nothing to commit.
    pause
    exit /b 0
)

set "MSG=Auto update %date% %time%"
git add .
git commit -m "%MSG%"
git push origin main

echo.
echo ✅ Pushed.
pause