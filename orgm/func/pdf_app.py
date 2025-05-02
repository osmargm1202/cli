# -*- coding: utf-8 -*-
import questionary
from rich.console import Console
import typer
import sys

# Importar funciones de commands
from orgm.commands.pdf import pdf_firmar, pdf_firmar_interactivo

# Crear consola para salida con Rich
console = Console()

# Crear la aplicación Typer para PDF
pdf_app = typer.Typer(help="Operaciones con archivos PDF")

# Comandos de PDF
pdf_app.command(name="sign-file")(pdf_firmar)
pdf_app.command(name="sign")(pdf_firmar_interactivo)

# Configurar callback para 'pdf' para mostrar menú si no se especifican subcomandos
@pdf_app.callback(invoke_without_command=True)
def pdf_callback(ctx: typer.Context):
    """
    Operaciones con archivos PDF. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de PDF
        pdf_menu()

def pdf_menu():
    """Menú interactivo para comandos de PDF."""
    
    console.print("[bold blue]===== Menú Operaciones PDF =====[/bold blue]")
    
    opciones = [
        {"name": "📝 Firmar PDF interactivamente", "value": "pdf_firmar_interactivo"},
        {"name": "📂 Firmar PDF con archivo existente", "value": "pdf_firmar"},
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
        elif comando == "pdf_firmar_interactivo":
            # Ejecutar comando directamente
            pdf_firmar_interactivo()
            return pdf_menu()  # Volver al mismo menú después
        elif comando == "pdf_firmar":
            # Solicitar entradas para el comando
            pdf_path = questionary.text("Introduce la ruta al archivo PDF:").ask()
            if pdf_path:
                firma_path = questionary.text("Introduce la ruta al archivo de firma:").ask()
                if firma_path:
                    pdf_firmar(pdf_path, firma_path)
            return pdf_menu()  # Volver al mismo menú después
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"

if __name__ == "__main__":
    # Para pruebas
    pdf_menu() 