@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "PROJECT_DIR=%~dp0.."
for %%I in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fI"
set "PROJECT=%PROJECT_DIR%\LastFrontier.uproject"
if "%CONFIG%"=="" set "CONFIG=Development"
if "%PLATFORM%"=="" set "PLATFORM=Win64"
set "LOG_DIR=%PROJECT_DIR%\Saved\M47Logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

if not exist "%PROJECT%" (
  echo M47_COMPILE_STATUS=BLOCKED_OR_FAILED
  echo REASON=uproject not found: %PROJECT%
  exit /b 3
)

if "%UE_ROOT%"=="" (
  if exist "C:\Program Files\Epic Games\UE_5.8\Engine" set "UE_ROOT=C:\Program Files\Epic Games\UE_5.8"
)
if "%UE_ROOT%"=="" (
  echo M47_COMPILE_STATUS=BLOCKED_OR_FAILED
  echo REASON=UE 5.8 root not found. Set UE_ROOT.
  exit /b 2
)

set "BUILD_BAT=%UE_ROOT%\Engine\Build\BatchFiles\Build.bat"
if not exist "%BUILD_BAT%" (
  echo M47_COMPILE_STATUS=BLOCKED_OR_FAILED
  echo REASON=Build.bat missing: %BUILD_BAT%
  exit /b 4
)

echo [M47] Compiling LastFrontierEditor
call "%BUILD_BAT%" LastFrontierEditor %PLATFORM% %CONFIG% "%PROJECT%" -Progress -NoHotReloadFromIDE
if errorlevel 1 exit /b %errorlevel%

echo [M47] Compiling LastFrontier
call "%BUILD_BAT%" LastFrontier %PLATFORM% %CONFIG% "%PROJECT%" -Progress -NoHotReloadFromIDE
if errorlevel 1 exit /b %errorlevel%

if not exist "%PROJECT_DIR%\Binaries" (
  echo M47_COMPILE_STATUS=BLOCKED_OR_FAILED
  echo REASON=No Binaries directory produced
  exit /b 10
)
echo M47_COMPILE_STATUS=PASS
exit /b 0
