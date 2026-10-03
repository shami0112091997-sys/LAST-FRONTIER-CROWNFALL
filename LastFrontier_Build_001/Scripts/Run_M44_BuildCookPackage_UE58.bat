@echo off
setlocal
set "PROJECT_DIR=%~dp0.."
for %%I in ("%PROJECT_DIR%") do set "PROJECT_DIR=%%~fI"
if "%UE_ROOT%"=="" (echo M44_PACKAGE_STATUS=BLOCKED_OR_FAILED& echo REASON=UE_ROOT is not set& exit /b 2)
if "%PLATFORM%"=="" set "PLATFORM=Win64"
if "%CONFIG%"=="" set "CONFIG=Development"
if "%ARCHIVE_DIR%"=="" set "ARCHIVE_DIR=%PROJECT_DIR%\Packaged"
set "PROJECT=%PROJECT_DIR%\LastFrontier.uproject"
set "RUNUAT=%UE_ROOT%\Engine\Build\BatchFiles\RunUAT.bat"
set "MAP=%PROJECT_DIR%\Content\Maps\TestMap.umap"
if not exist "%RUNUAT%" (echo M44_PACKAGE_STATUS=BLOCKED_OR_FAILED& echo REASON=RunUAT not found& exit /b 3)
if not exist "%MAP%" (echo M44_PACKAGE_STATUS=BLOCKED_OR_FAILED& echo REASON=genuine TestMap.umap missing& exit /b 5)
call "%RUNUAT%" BuildCookRun -project="%PROJECT%" -noP4 -build -cook -stage -pak -archive -archivedirectory="%ARCHIVE_DIR%" -platform=%PLATFORM% -clientconfig=%CONFIG% -utf8output
if errorlevel 1 exit /b 20
echo M44_PACKAGE_STATUS=PASS
exit /b 0
