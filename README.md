# BlenderRenderManager

Gestor de renders para Blender. Aplicación desktop en Python con GUI para manejar trabajos de renderizado distribuidos usando workers.

## Características
- Interfaz gráfica (main_window.py)
- Modelos de datos (models.py)
- Workers para renderizado (worker.py)
- Construido con PyInstaller (exe disponible en build/)
- Soporte para jobs JSON (render_jobs.json)

## Instalación
1. Instalar Python 3.10+
2. `pip install -r requirements.txt` (si existe)
3. Ejecutar `python app.py`

## Build

### Opción recomendada (automática)
Ejecutar:

- `build.bat`

Este script ahora:
1. Crea/usa un entorno virtual local `.venv`
2. Instala dependencias en `.venv` (`PyQt6`, `Pillow`, `pyinstaller`)
3. Compila el ejecutable con `BlenderRenderManager.spec`
4. Si detecta Inno Setup 6 (`ISCC.exe`), compila también el instalador automáticamente desde `installer.iss`

Salidas esperadas:
- App: `dist\BlenderRenderManager\BlenderRenderManager.exe`
- Instalador: `dist\BlenderRenderManager_Setup_v1.0.0.exe` (si ISCC está disponible)

### Opción manual
- `pyinstaller BlenderRenderManager.spec --clean --noconfirm`
- Compilar `installer.iss` con Inno Setup Compiler (ISCC o GUI)

## Archivos principales
- **app.py**: Entrada principal
- **main_window.py**: Ventana principal
- **models.py**: Modelos Pydantic/SQLAlchemy?
- **worker.py**: Lógica de worker

Proyecto en desarrollo - ver TODO.md para pendientes.

Logo by [creator if known].
