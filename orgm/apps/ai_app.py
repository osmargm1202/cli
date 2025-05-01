# -*- coding: utf-8 -*-
import questionary
from rich.console import Console
import typer
import sys

# Importar funciones de commands
from orgm.commands.ai import ai_prompt, ai_configs, ai_config_upload, ai_config_create, ai_config_edit

# Crear consola para salida con Rich
console = Console()

# Crear la aplicación Typer para AI
ai_app = typer.Typer(help="Operaciones relacionadas con la IA")

# Comandos de AI
ai_app.command(name="prompt")(ai_prompt)
ai_app.command(name="configs")(ai_configs)
ai_app.command(name="upload")(ai_config_upload)
ai_app.command(name="create")(ai_config_create)
ai_app.command(name="edit")(ai_config_edit)

# Configurar callback para 'ai' para mostrar menú si no se especifican subcomandos
@ai_app.callback(invoke_without_command=True)
def ai_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con la IA. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de IA
        ai_menu()

def ai_menu():
    """Menú interactivo para comandos de IA."""
    
    console.print("[bold blue]===== Menú de Inteligencia Artificial =====[/bold blue]")
    
    opciones = [
        {"name": "🤖 Hacer consulta a la IA", "value": "ai prompt"},
        {"name": "📋 Listar configuraciones de IA", "value": "ai configs"},
        {"name": "📤 Subir configuración de IA", "value": "ai upload"},
        {"name": "✏️ Crear configuración de IA", "value": "ai create"},
        {"name": "📝 Editar configuración de IA", "value": "ai edit"},
        {"name": "⬅️ Volver al menú principal", "value": "volver"},
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
        elif comando == "volver":
            from orgm.commands.menu import menu_principal
            return menu_principal()
        elif comando == "ai prompt":
            # Ejecutar comando de prompt de IA
            consulta = questionary.text("Introduce tu consulta para la IA:").ask()
            if consulta:
                ai_prompt(consulta)
            return ai_menu()
        elif comando == "ai configs":
            # Listar configuraciones
            ai_configs()
            return ai_menu()
        elif comando == "ai upload":
            # Subir configuración
            ruta = questionary.text("Introduce la ruta al archivo de configuración:").ask()
            if ruta:
                ai_config_upload(ruta)
            return ai_menu()
        elif comando == "ai create":
            # Crear configuración
            nombre = questionary.text("Nombre de la configuración:").ask()
            if nombre:
                ai_config_create(nombre)
            return ai_menu()
        elif comando == "ai edit":
            # Editar configuración
            nombre = questionary.text("Nombre de la configuración a editar:").ask()
            if nombre:
                ai_config_edit(nombre)
            return ai_menu()
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"

if __name__ == "__main__":
    # Para pruebas
    ai_menu() 