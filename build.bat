@echo off
setlocal enabledelayedexpansion
title Blender Render Manager - Build

echo.
echo  ============================================================
echo   Blender Render Manager v1.0.0 - Build Script
echo   Franco Basualdo - Tryhard VFX
echo  ============================================================
echo.

:: ── 1. Verificar Python ──────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado en el PATH.
    echo         Instala Python 3.10+ desde https://www.python.org/downloads/
    echo         Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] %PYVER% detectado.
echo.

:: ── 2. Ir al directorio del script ───────────────────────────────────────────
cd /d "%~dp0"

:: ── 3. Actualizar pip ────────────────────────────────────────────────────────
echo [1/4] Actualizando pip...
python -m pip install --upgrade pip --quiet
echo.

:: ── 4. Instalar dependencias de la app ───────────────────────────────────────
echo [2/4] Instalando dependencias de la app (PyQt6, Pillow)...
python -m pip install PyQt6 Pillow --quiet
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

:: ── 5. Instalar PyInstaller ──────────────────────────────────────────────────
echo [3/4] Instalando PyInstaller...
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de PyInstaller.
    pause
    exit /b 1
)
echo [OK] PyInstaller listo.
echo.

:: ── 6. Limpiar builds anteriores ─────────────────────────────────────────────
echo [4/4] Construyendo ejecutable...
if exist "dist\BlenderRenderManager" (
    echo       Limpiando build anterior...
    rmdir /s /q "dist\BlenderRenderManager"
)
if exist "build\BlenderRenderManager" (
    rmdir /s /q "build\BlenderRenderManager"
)

:: ── 7. Ejecutar PyInstaller ──────────────────────────────────────────────────
pyinstaller BlenderRenderManager.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller fallo. Revisa los mensajes de error arriba.
    pause
    exit /b 1
)

:: ── 8. Verificar resultado ───────────────────────────────────────────────────
if not exist "dist\BlenderRenderManager\BlenderRenderManager.exe" (
    echo [ERROR] No se encontro el ejecutable en dist\BlenderRenderManager\
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   BUILD EXITOSO!
echo.
echo   Ejecutable:  dist\BlenderRenderManager\BlenderRenderManager.exe
echo.
echo   Para distribuir: copia toda la carpeta
echo     dist\BlenderRenderManager\
echo   o usa installer.iss con Inno Setup para crear un instalador .exe
echo  ============================================================
echo.

:: ── 9. Abrir carpeta de salida ───────────────────────────────────────────────
set /p OPEN="Abrir carpeta dist\BlenderRenderManager\ ? [S/N]: "
if /i "!OPEN!"=="S" (
    explorer "dist\BlenderRenderManager"
)

endlocal
pause
