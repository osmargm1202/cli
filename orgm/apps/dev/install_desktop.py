import os
import subprocess
from rich.console import Console

console = Console()

def crear_desktop_entry():
    # Definir el contenido del archivo .desktop
    contenido = """[Desktop Entry]
Version=1.0
Type=Application
Name=ORGM CLI
Exec=orgm
Icon=
Terminal=true
Categories=Utility;"""

    # Obtener la ruta del directorio de aplicaciones del usuario
    ruta_desktop = os.path.expanduser("~/.local/share/applications/orgm.desktop")

    try:
        # Crear el archivo .desktop
        with open(ruta_desktop, "w") as archivo:
            archivo.write(contenido)

        # Dar permisos de ejecución
        subprocess.run(['chmod', '+x', ruta_desktop])

        console.print("✓ Archivo .desktop creado exitosamente", style="bold green")
        console.print(f"  Ubicación: {ruta_desktop}", style="dim")

    except Exception as e:
        console.print(f"✗ Error al crear el archivo .desktop: {str(e)}", style="bold red")

if __name__ == "__main__":
    crear_desktop_entry()
