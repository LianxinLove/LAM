@echo off
echo ========================================
echo Lab Asset Management - Database Reset
echo ========================================
echo.

echo [1/4] Stopping backend server...
taskkill /F /IM python.exe /T 2>/dev/null
timeout /t 2 /nobreak >/dev/null

echo [2/4] Deleting old database files...
del /F /Q lab_asset_management.db 2>/dev/null
del /F /Q backend\lab_asset_management.db 2>/dev/null
rd /S /Q backend\instance 2>/dev/null
echo Database files deleted.

echo [3/4] Initializing new database...
cd backend
python reset_db.py

echo [4/4] Starting backend server...
echo Starting backend...
start python run.py

echo.
echo ========================================
echo Reset complete!
echo Login info:
echo   Admin: admin / admin123
echo   Test: test / test123
echo ========================================
pause
