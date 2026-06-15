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

REM Timestamp für Commit-Message
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATUM=%%c-%%b-%%a
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set ZEIT=%%a:%%b

REM Stage alle Änderungen (falls vorhanden)
git add -A

REM Commit (falls es was zu committen gibt)
git diff --cached --quiet 2>nul
if not %errorlevel%==0 (
    git commit -m "update %DATUM% %ZEIT%"
    echo [OK] Aenderungen committed.
) else (
    echo [INFO] Nichts Neues zu committen.
)

REM IMMER pushen (auch wenn nur alte commits noch nicht gepusht waren)
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
