# -*- coding: utf-8 -*-
import questionary
from rich.console import Console
import typer
import sys

# Importar funciones de commands
from orgm.commands.env import env_edit, env_file

# Crear consola para salida con Rich
console = Console()

# Crear la aplicación Typer para env
env_app = typer.Typer(help="Administrar variables de entorno")

# Configurar comandos de env
env_app.command(name="edit")(env_edit)
env_app.command(name="file")(env_file)

# Configurar callback para mostrar menú si no se especifican subcomandos
@env_app.callback(invoke_without_command=True)
def env_callback(ctx: typer.Context):
    """
    Administra las variables de entorno. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de variables de entorno
        env_menu()

def env_menu():
    """Menú interactivo para comandos de variables de entorno."""
    
    console.print("[bold blue]===== Menú Variables de Entorno =====[/bold blue]")
    
    opciones = [
        {"name": "📝 Editar variables (.env)", "value": "env edit"},
        {"name": "📂 Cargar archivo como .env", "value": "env_file"},
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
        elif comando == "env edit":
            # Ejecutar comando directamente
            env_edit()
            return env_menu()  # Volver al mismo menú después
        elif comando == "env_file":
            # Solicitar entrada adicional para el archivo
            archivo = questionary.text("Introduce la ruta al archivo:").ask()
            if archivo:
                env_file(archivo)
            return env_menu()  # Volver al mismo menú después
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"

if __name__ == "__main__":
    # Para pruebas
    env_menu() 