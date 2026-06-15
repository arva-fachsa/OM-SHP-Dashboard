@echo off
echo ========================================
echo   Dashboard Auto-Push
echo ========================================
echo.

cd /d "c:\Data Warehouse FY26\streamlit_cloud_app"

echo Aenderungen werden gepusht...
echo.

git add -A
git commit -m "dashboard update"
git push origin main

echo.
echo ========================================
if %errorlevel%==0 (
    echo   FERTIG! Dashboard aktualisiert sich in 1 Min.
    echo   https://om-shp-dashboard.streamlit.app/
) else (
    echo   FEHLER - Pruefe Internetverbindung
)
echo ========================================
echo.
echo Druecke eine beliebige Taste zum Schliessen...
pause >nul
