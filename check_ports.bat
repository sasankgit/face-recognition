@echo off
echo Checking for processes using ports 3000 and 3001...
echo.

echo Checking port 3000:
netstat -ano | findstr :3000
if %errorlevel% equ 0 (
    echo Port 3000 is in use. Killing processes...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        taskkill /PID %%a /F >nul 2>&1
        echo Killed process with PID %%a
    )
) else (
    echo Port 3000 is available
)

echo.
echo Checking port 3001:
netstat -ano | findstr :3001
if %errorlevel% equ 0 (
    echo Port 3001 is in use. Killing processes...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
        taskkill /PID %%a /F >nul 2>&1
        echo Killed process with PID %%a
    )
) else (
    echo Port 3001 is available
)

echo.
echo Port check complete!
pause
