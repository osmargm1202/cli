from rich.console import Console
from rich.prompt import Prompt
import questionary
import sys
import subprocess
console = Console()

def menu():
    """Menú interactivo para comandos de IA."""
    
    console.print("[bold blue]===== Menú de Configuración =====[/bold blue]")
    
    opciones = [
        {"name": "🔍 Verificar URLs", "value": "check"},
        {"name": "🔍 Cargar variables de entorno", "value": "env-file"},
        {"name": "📋 Editar variables de entorno", "value": "env-edit"},
        {"name": "📤 Subir Herramienta a Pypi (Dev)", "value": "upload"},
        {"name": "🔍 Ayuda General", "value": "ayuda"},
        {"name": "📝 Ayuda", "value": "conf -h"},
        {"name": "❌ Salir", "value": "exit"}
    ]
    
    try:
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in opciones],
            use_indicator=True
        ).ask()
        
        if seleccion is None:  # Usuario presionó Ctrl+C
            return "exit"
        elif comando == "ai -h":
            subprocess.run(["orgm", "conf", "-h"])
            return menu()
        # Obtener el valor asociado a la selección
        comando = next(opcion["value"] for opcion in opciones if opcion["name"] == seleccion)
        
        if comando == "exit":
            console.print("[yellow]Saliendo...[/yellow]")
            sys.exit(0)
        elif comando == "check":
            from orgm.apps.conf.check import check_urls
            check_urls()
            return menu()
        elif comando == "env-file":
            from orgm.apps.conf.env_file import env_file
            # Preguntar por la ruta del archivo
            ruta_archivo = questionary.text(
                "Introduce la ruta del archivo .env:",
                default=".env"
            ).ask()

            if ruta_archivo is None:  # Usuario canceló (Ctrl+C)
                console.print("[yellow]Operación cancelada.[/yellow]")
                return menu()
            env_file(ruta_archivo)
            return menu()
        elif comando == "env-edit":
            from orgm.apps.conf.env_edit import env_edit
            env_edit()
            return menu()
        elif comando == "upload":
            # Crear configuración
            from orgm.apps.dev.upload import upload
            upload()
            return menu()
        elif comando == "ayuda":
            # Editar configuración
            from orgm.apps.conf.ayuda import mostrar_ayuda
            mostrar_ayuda()
            return menu()
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"