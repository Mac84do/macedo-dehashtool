@echo off
echo ==================================================
echo Macedo Dehashing Tool Installation (Windows)
echo ==================================================

echo.
echo Choose installation option:
echo 1. Install v1 only (basic version)
echo 2. Install v2 only (enhanced version) 
echo 3. Install both versions (recommended)
echo.

set /p choice=Enter choice (1-3): 

if "%choice%"=="1" goto install_v1
if "%choice%"=="2" goto install_v2
if "%choice%"=="3" goto install_both

echo Invalid choice. Installing both versions by default.
goto install_both

:install_v1
echo Installing v1 dependencies...
pip install requests python-dotenv
echo.
echo ✓ v1 dependencies installed successfully!
echo Usage: python main.py [options]
goto end

:install_v2
echo Installing v2 dependencies...
pip install requests python-dotenv numpy pandas rich reportlab typer
echo.
echo ✓ v2 dependencies installed successfully!
echo Usage: python main_v2.py [options]
goto end

:install_both
echo Installing both v1 and v2 dependencies...
pip install requests python-dotenv numpy pandas rich reportlab typer
echo.
echo ✓ Both versions installed successfully!
echo Usage:
echo   v1: python main.py [options]
echo   v2: python main_v2.py [options]
goto end

:end
echo.
echo Installation complete!
echo.
echo Note: For v2 hash cracking features, you may also need to install:
echo   - hashcat: https://hashcat.net/hashcat/
echo   - john the ripper: https://www.openwall.com/john/
echo.
pause
