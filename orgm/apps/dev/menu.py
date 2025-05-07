from rich.console import Console
import questionary
import sys
import subprocess
from orgm.qstyle import custom_style_fancy
from orgm.apps.dev.install_desktop import crear_desktop_entry
from orgm.apps.dev.install_desktop_windows import crear_acceso_directo_windows
from orgm.apps.dev.upload import upload

console = Console()


def menu():
    """Menú interactivo para comandos de IA."""

    console.print("[bold blue]===== Menú de Configuración =====[/bold blue]")

    opciones = [
        {"name": "📤 Subir Herramienta a Pypi (Dev)", "value": "upload"},
        {"name": "🔗 Instalar acceso directo en Windows", "value": "shortcut_windows"},
        {"name": "🔗 Instalar acceso directo en Linux", "value": "shortcut"},
        {"name": "📝 Ayuda", "value": "dev -h"},
        {"name": "❌ Salir", "value": "exit"},
    ]

    try:
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in opciones],
            use_indicator=True,
            style=custom_style_fancy,
        ).ask()

        if seleccion is None:  # Usuario presionó Ctrl+C
            return "exit"

        # Obtener el valor asociado a la selección
        comando = next(
            opcion["value"] for opcion in opciones if opcion["name"] == seleccion
        )

        if comando == "exit":
            console.print("[yellow]Saliendo...[/yellow]")
            sys.exit(0)

        elif comando == "dev -h":
            subprocess.run(["orgm", "dev", "-h"])
            return menu()
        elif comando == "upload":
            upload()
            return menu()
        elif comando == "shortcut_windows":
            crear_acceso_directo_windows()
            return menu()
        elif comando == "shortcut":
            crear_desktop_entry()
            return menu()


    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"
