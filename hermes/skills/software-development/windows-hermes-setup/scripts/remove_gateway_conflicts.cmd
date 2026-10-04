@echo off
REM ===========================================================================
REM Remove ALL conflicting gateway auto-start sources.
REM Run as Administrator (UAC will prompt).
REM
REM After this script, the only auto-start is the new "Hermes Gateway Single"
REM Scheduled Task that this script creates. Run with UAC elevation:
REM   powershell -Command "Start-Process cmd -ArgumentList '/c','%~f0' -Verb RunAs -Wait"
REM ===========================================================================

setlocal EnableDelayedExpansion

echo === Step 1: Disable Hermes Gateway Scheduled Task ===
schtasks /Change /TN "\Hermes Gateway" /Disable 2>&1
if errorlevel 1 (
    echo   - Disable failed, attempting delete
    schtasks /Delete /TN "\Hermes Gateway" /F 2>&1
)

echo.
echo === Step 2: Remove Hermes.lnk from Startup folder ===
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set HERMES_LNK=!STARTUP_DIR!\Hermes.lnk
if exist "!HERMES_LNK!" (
    del /F /Q "!HERMES_LNK!" 2>&1
    echo   - Deleted: !HERMES_LNK!
) else (
    echo   - Hermes.lnk not found
)

echo.
echo === Step 3: Disable Hermes_Gateway.cmd restart script ===
set CMD_SCRIPT=C:\Users\tukum\AppData\Local\hermes\gateway-service\Hermes_Gateway.cmd
if exist "!CMD_SCRIPT!" (
    ren "!CMD_SCRIPT!" "!CMD_SCRIPT!.disabled" 2>&1
    echo   - Renamed to .disabled
) else (
    echo   - Hermes_Gateway.cmd not found
)

echo.
echo === Step 4: Create single Scheduled Task for the bash restart script ===
schtasks /Create /TN "Hermes Gateway Single" /TR "C:\Users\tukum\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe gateway run" /SC ONLOGON /RL HIGHEST /F 2>&1

echo.
echo === Step 5: Verify ===
schtasks /Query /TN "Hermes Gateway Single" 2>&1 | findstr /C:"Ready" >nul
if errorlevel 1 (
    echo   - WARNING: New task creation may have failed
) else (
    echo   - "Hermes Gateway Single" task is Ready
)
if exist "!HERMES_LNK!" (
    echo   - WARNING: Hermes.lnk still exists
) else (
    echo   - Hermes.lnk removed
)

echo.
echo === Done ===
pause
