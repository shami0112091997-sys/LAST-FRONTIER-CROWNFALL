@echo off
setlocal
set "PROJECT_DIR=%~dp0.."
for %%I in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fI"
if "%UE_ROOT%"=="" (echo M44_COMPILE_STATUS=BLOCKED_OR_FAILED& echo REASON=UE_ROOT is not set& exit /b 2)
if "%PLATFORM%"=="" set "PLATFORM=Win64"
if "%CONFIG%"=="" set "CONFIG=Development"
set "PROJECT=%PROJECT_DIR%\LastFrontier.uproject"
set "UBT=%UE_ROOT%\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe"
if not exist "%UBT%" (echo M44_COMPILE_STATUS=BLOCKED_OR_FAILED& echo REASON=UBT not found: %UBT%& exit /b 3)
if not exist "%PROJECT%" (echo M44_COMPILE_STATUS=BLOCKED_OR_FAILED& echo REASON=uproject not found& exit /b 4)
echo [M44 Recovery] Compile Editor target
"%UBT%" LastFrontierEditor %PLATFORM% %CONFIG% -Project="%PROJECT%" -Progress -NoHotReloadFromIDE
if errorlevel 1 exit /b 10
echo [M44 Recovery] Compile Game target
"%UBT%" LastFrontier %PLATFORM% %CONFIG% -Project="%PROJECT%" -Progress -NoHotReloadFromIDE
if errorlevel 1 exit /b 11
echo M44_COMPILE_STATUS=PASS
exit /b 0
