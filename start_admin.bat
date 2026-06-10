@echo off
chcp 65001 > nul
echo.
echo  France Leads - Admin Launcher
echo  ==============================
echo.

set BUSINESSES_DIR=%USERPROFILE%\أعمالي
set PORT=3001

if "%1"=="" (
    echo  Available businesses:
    for /d %%d in ("%BUSINESSES_DIR%\*") do (
        if exist "%%d\admin\package.json" (
            echo    - %%~nd
        )
    )
    echo.
    set /p SLUG=Enter business slug:
) else (
    set SLUG=%1
)

set ADMIN_DIR=%BUSINESSES_DIR%\%SLUG%\admin

if not exist "%ADMIN_DIR%" (
    echo  ERROR: Admin not found at %ADMIN_DIR%
    pause
    exit /b 1
)

echo.
echo  Starting admin for: %SLUG%
echo  URL: http://localhost:%PORT%/admin
echo  Login: admin / admin123
echo.

cd /d "%ADMIN_DIR%"
npm run dev -- --port %PORT%
