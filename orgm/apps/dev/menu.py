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
        {"name": "📤 Subir Herramienta a Pypi (Dev)", "value": "upload"},
        {"name": "📝 Ayuda", "value": "dev -h"},
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
            
        # Obtener el valor asociado a la selección
        comando = next(opcion["value"] for opcion in opciones if opcion["name"] == seleccion)
        
        if comando == "exit":
            console.print("[yellow]Saliendo...[/yellow]")
            sys.exit(0)

        elif comando == "dev -h":
            subprocess.run(["orgm", "dev", "-h"])
            return menu()
        elif comando == "docker":
            from orgm.apps.docker.docker import docker
            docker()
            return menu()
        
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"