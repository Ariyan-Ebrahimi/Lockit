@echo off
setlocal
cd /d "%~dp0"
title LockIt Installer Builder
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_installer.ps1"
if errorlevel 1 (
  echo.
  echo ============================================================
  echo BUILD FAILED. Read the error above.
  echo ============================================================
  pause
  exit /b 1
)
echo.
echo Build completed successfully.
pause
