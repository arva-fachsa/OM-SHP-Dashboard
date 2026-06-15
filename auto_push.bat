@echo off
REM =============================================================
REM  Auto-Push Script für Shipping Operations Dashboard
REM  
REM  Dieses Script pusht alle Änderungen automatisch zu GitHub.
REM  Die Live-URL aktualisiert sich dann in ~1 Minute.
REM
REM  NUTZUNG:
REM  - Doppelklick auf diese Datei
REM  - Oder als Alteryx Post-Event einbinden
REM =============================================================

cd /d "c:\Data Warehouse FY26\streamlit_cloud_app"

REM Prüfe ob es überhaupt Änderungen gibt
git status --porcelain >nul 2>nul
git diff --quiet 2>nul && git diff --cached --quiet 2>nul && (
    echo [INFO] Keine Aenderungen gefunden - nichts zu tun.
    pause
    exit /b 0
)

REM Timestamp für Commit-Message
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATUM=%%c-%%b-%%a
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set ZEIT=%%a:%%b

REM Stage ALLES, Commit, Push
git add -A
git commit -m "update %DATUM% %ZEIT%"
git push origin main

if %errorlevel%==0 (
    echo.
    echo [OK] Erfolgreich gepusht!
    echo [OK] Dashboard aktualisiert sich in ~1 Minute.
    echo [OK] URL: https://om-shp-dashboard.streamlit.app/
) else (
    echo [FEHLER] Push fehlgeschlagen. Pruefe Internetverbindung/GitHub-Auth.
)

echo.
pause
