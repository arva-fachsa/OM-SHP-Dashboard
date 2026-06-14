@echo off
REM =============================================================
REM  Auto-Push Script für Shipping Operations Dashboard
REM  
REM  Dieses Script pusht neue Daten automatisch zu GitHub.
REM  Die Live-URL aktualisiert sich dann in ~1 Minute.
REM
REM  NUTZUNG:
REM  1. Alteryx schreibt neue CSVs nach: 
REM     c:\Data Warehouse FY26\streamlit_cloud_app\data\
REM  2. Dieses Script aufrufen (manuell oder als Alteryx Post-Event)
REM  3. Dashboard aktualisiert sich automatisch
REM =============================================================

cd /d "c:\Data Warehouse FY26\streamlit_cloud_app"

REM Prüfe ob es Änderungen gibt
git diff --quiet data\ 2>nul
if %errorlevel%==0 (
    echo [INFO] Keine Änderungen in data\ - nichts zu tun.
    exit /b 0
)

REM Timestamp für Commit-Message
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATUM=%%c-%%b-%%a
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set ZEIT=%%a:%%b

REM Stage, Commit, Push
git add data\
git commit -m "data: update %DATUM% %ZEIT%"
git push origin main

if %errorlevel%==0 (
    echo.
    echo [OK] Daten erfolgreich gepusht!
    echo [OK] Dashboard aktualisiert sich in ~1 Minute.
    echo [OK] URL: https://appapppy-gbbjb4iqesfc4yvt6jmv6a.streamlit.app/
) else (
    echo [FEHLER] Push fehlgeschlagen. Prüfe Internetverbindung/GitHub-Auth.
)
