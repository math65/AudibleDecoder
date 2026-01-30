@echo off
color 0B
title CONSTRUCTION FINALE - Audible Decoder (Sans Terminal)

echo ========================================================
echo  1. GRAND NETTOYAGE (Pour une version propre)
echo ========================================================

if exist "src\build" rd /s /q "src\build"
if exist "src\dist" rd /s /q "src\dist"
if exist "src\AudibleDecoder.spec" del "src\AudibleDecoder.spec"

echo.
echo ========================================================
echo  2. ACTIVATION
echo ========================================================
call venv\Scripts\activate

echo.
echo ========================================================
echo  3. FABRICATION DE L'EXE (Version Silencieuse)
echo ========================================================
cd src

:: L'option magique ici est : --noconsole
:: Cela supprime totalement la fenetre noire.
pyinstaller --noconsole --onefile --clean --paths="." --hidden-import="gui" --hidden-import="gui.main_frame" --hidden-import="core" --hidden-import="core.decoder" --name "AudibleDecoder" main.py

if %errorlevel% neq 0 (
    color 0C
    echo ERREUR FATALE !
    pause
    exit /b
)

echo.
echo ========================================================
echo  TERMINE !
echo ========================================================
echo.
echo Ton application finale est ici : src\dist\AudibleDecoder.exe
echo.
echo N'oublie pas l'ultime etape :
echo Copier le dossier 'bin' a cote de l'exe.
echo.
pause