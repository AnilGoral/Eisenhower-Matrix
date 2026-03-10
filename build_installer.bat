@echo off
echo ============================================
echo  Eisenhower Matrix - Build Installer
echo ============================================
echo.

echo [1/2] Building standalone .exe with PyInstaller...
python -m PyInstaller eisenhower.spec --clean
if %ERRORLEVEL% neq 0 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)
echo.

echo [2/2] Creating installer with Inno Setup...
echo NOTE: Inno Setup must be installed. Download from https://jrsoftware.org/isinfo.php
echo.

where iscc >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Inno Setup compiler (iscc) not found in PATH.
    echo Trying default install location...
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    ) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
        "C:\Program Files\Inno Setup 6\ISCC.exe" installer.iss
    ) else (
        echo.
        echo Inno Setup not found. The PyInstaller build is complete.
        echo You can run the app from: dist\EisenhowerMatrix\EisenhowerMatrix.exe
        echo To create the installer, install Inno Setup and run: iscc installer.iss
        pause
        exit /b 0
    )
) else (
    iscc installer.iss
)

if %ERRORLEVEL% neq 0 (
    echo ERROR: Inno Setup compilation failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Build complete!
echo  Installer: installer_output\EisenhowerMatrix_Setup_1.0.0.exe
echo ============================================
pause
