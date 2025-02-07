@echo off
chcp 936
echo Cleaning previous builds...
if exist "dist" (rd /s /q "dist")
if exist "build" (rd /s /q "build")
if exist "FullScreenTrackSetup.exe" (del "FullScreenTrackSetup.exe")

echo Building application with PyInstaller...
pyinstaller --name=ScreenTrack ^
            --windowed ^
            --icon=src\app\ui\resources\icon.ico ^
            --add-data="src\app\ui\resources;resources" ^
            --hidden-import=PyQt5.QtSvg ^
            --hidden-import=PyQt5.QtXml ^
            --collect-all=PyQt5 ^
            --noconfirm ^
            --clean ^
            --onedir ^
            main.py

if errorlevel 1 (
    echo PyInstaller build failed!
    pause
    exit /b 1
)

echo Creating installer...
cd installer
"C:\Program Files (x86)\NSIS\makensis.exe" setup.nsi
if errorlevel 1 (
    echo NSIS build failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo Installation package created successfully!
pause
