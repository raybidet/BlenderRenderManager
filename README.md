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
- `pyinstaller BlenderRenderManager.spec`
- Installer: installer.iss (Inno Setup)

## Archivos principales
- **app.py**: Entrada principal
- **main_window.py**: Ventana principal
- **models.py**: Modelos Pydantic/SQLAlchemy?
- **worker.py**: Lógica de worker

Proyecto en desarrollo - ver TODO.md para pendientes.

Logo by [creator if known].
