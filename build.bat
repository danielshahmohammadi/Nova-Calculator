
@echo off

title NOVA Calculator Builder

echo.
echo =====================================
echo       NOVA Calculator Builder
echo =====================================
echo.

echo Installing required packages...

python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    pause
    exit /b 1
)

echo.
echo Building NOVA Calculator...

python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name NOVA-Calculator ^
    --add-data "styles;styles" ^
    --add-data "assets;assets" ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo =====================================
echo       BUILD COMPLETED!
echo =====================================
echo.
echo Your application is inside:
echo dist\NOVA-Calculator.exe
echo.

pause
