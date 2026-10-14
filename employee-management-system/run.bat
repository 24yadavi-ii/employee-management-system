@echo off
title Employee Management System
cd /d "%~dp0"

echo ==========================================================
echo       EMPLOYEE MANAGEMENT SYSTEM - LOCAL SERVER
echo ==========================================================
echo.
echo Starting Flask backend...
echo Opening browser at http://127.0.0.1:5000 ...
echo.

:: Open default browser after a 1.5 second delay
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

:: Run the Python Flask application
python app.py

echo.
echo Server stopped.
pause
