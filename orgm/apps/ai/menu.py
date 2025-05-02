from rich.console import Console
from rich.prompt import Prompt
import questionary
import sys
import subprocess

console = Console()

def menu():
    """Menú interactivo para comandos de IA."""
    
    console.print("[bold blue]===== Menú de Inteligencia Artificial =====[/bold blue]")
    
    opciones = [
        {"name": "🤖 Hacer consulta a la IA", "value": "ai prompt"},
        {"name": "📋 Listar configuraciones de IA", "value": "ai configs"},
        {"name": "📤 Subir configuración de IA", "value": "ai upload"},
        {"name": "✏️ Crear configuración de IA", "value": "ai create"},
        {"name": "📝 Editar configuración de IA", "value": "ai edit"},
        {"name": "🔍 Ayuda", "value": "ai -h"},
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

        elif comando == "ai -h":
            subprocess.run(["orgm", "ai", "-h"])
            return menu()
        elif comando == "ai prompt":
            from orgm.apps.ai.prompt import ai_prompt

            # Pedir el prompt al usuario
            prompt_input = questionary.text("Introduce tu consulta para la IA:").ask()

            if prompt_input is None: # Usuario canceló (Ctrl+C)
                console.print("[yellow]Consulta cancelada.[/yellow]")
                return menu() # Volver al menú

            if not prompt_input.strip():
                console.print("[red]La consulta no puede estar vacía.[/red]")
                return menu() # Volver al menú

            # Dividir el prompt en una lista de palabras
            prompt_list = prompt_input.split()

            ai_prompt(prompt=prompt_list) # Pasar la lista como argumento
            return menu()
        elif comando == "ai configs":
            # Listar configuraciones
            from orgm.apps.ai.configs_list import ai_configs_list
            ai_configs_list()
            return menu()
        elif comando == "ai upload":
            # Subir configuración
            from orgm.apps.ai.config_upload import ai_config_upload
            ai_config_upload()
            return menu()
        elif comando == "ai create":
            # Crear configuración
            from orgm.apps.ai.config_create import ai_config_create
            ai_config_create()
            return menu()
        elif comando == "ai edit":
            # Editar configuración

            from orgm.apps.ai.config_edit import ai_config_edit
            ai_config_edit()
            return menu()
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"