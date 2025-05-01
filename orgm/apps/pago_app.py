# -*- coding: utf-8 -*-
import questionary
from rich.console import Console
from datetime import datetime
import typer
import sys

# Importar funciones de commands
from orgm.commands.pago import pago_registrar_command, pago_listar_command, pago_asignar_command

# Crear consola para salida con Rich
console = Console()

# Crear la aplicación Typer para pagos
pago_app = typer.Typer(help="Gestión de pagos y asignaciones")

# Comandos de Pagos
pago_app.command(name="register")(pago_registrar_command)
pago_app.command(name="list")(pago_listar_command)
pago_app.command(name="assign")(pago_asignar_command)

# Configurar callback para 'payment' para mostrar menú si no se especifican subcomandos
@pago_app.callback(invoke_without_command=True)
def payment_callback(ctx: typer.Context):
    """
    Gestión de pagos y asignaciones. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de pagos
        pago_menu()

def pago_menu():
    """Menú interactivo para gestión de pagos."""
    
    console.print("[bold blue]===== Menú de Gestión de Pagos =====[/bold blue]")
    
    opciones = [
        {"name": "💰 Registrar nuevo pago", "value": "payment register"},
        {"name": "📋 Listar pagos registrados", "value": "payment list"},
        {"name": "🔄 Asignar pago a proyecto/factura", "value": "payment assign"},
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
        elif comando == "payment register":
            # Registrar nuevo pago
            pago_registrar_command()
            return pago_menu()
        elif comando == "payment list":
            # Listar pagos
            pago_listar_command()
            return pago_menu()
        elif comando == "payment assign":
            # Asignar pago
            pago_asignar_command()
            return pago_menu()
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"

if __name__ == "__main__":
    # Para pruebas
    pago_menu() 