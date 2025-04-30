# -*- coding: utf-8 -*-
import questionary
from rich.console import Console
import typer
import sys

# Crear consola para salida con Rich
console = Console()

def pdf_menu():
    """Menú interactivo para comandos de operaciones con PDF."""
    
    console.print("[bold blue]===== Menú Operaciones PDF =====[/bold blue]")
    
    opciones = [
        {"name": "✍️ Firmar PDF (interactivo)", "value": "sign"},
        {"name": "📝 Firmar PDF (especificar archivo)", "value": "sign_file"},
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
        elif comando == "sign":
            # Ejecutar firma interactiva
            console.print("Iniciando selección interactiva de PDF...")
            from orgm.commands.pdf import pdf_firmar_interactivo
            
            # Obtener parámetros opcionales mediante questionary
            use_defaults = questionary.confirm(
                "¿Desea usar valores predeterminados (x=100, y=100, ancho=200)?",
                default=True
            ).ask()
            
            if use_defaults:
                pdf_firmar_interactivo()
            else:
                x_pos = int(questionary.text("Posición X:", default="100").ask() or "100")
                y_pos = int(questionary.text("Posición Y:", default="100").ask() or "100")
                ancho = int(questionary.text("Ancho:", default="200").ask() or "200")
                pdf_firmar_interactivo(x_pos, y_pos, ancho)
                
            return pdf_menu()  # Volver al mismo menú después
            
        elif comando == "sign_file":
            # Solicitar parámetros necesarios
            archivo_pdf = questionary.text("Ruta al archivo PDF:").ask()
            if not archivo_pdf:
                console.print("[yellow]Operación cancelada: No se especificó un archivo[/yellow]")
                return pdf_menu()
                
            x_pos = int(questionary.text("Posición X:", default="100").ask() or "100")
            y_pos = int(questionary.text("Posición Y:", default="100").ask() or "100")
            ancho = int(questionary.text("Ancho:", default="200").ask() or "200")
            
            salida = questionary.text("Nombre del archivo de salida (opcional):").ask()
            
            from orgm.commands.pdf import pdf_firmar
            pdf_firmar(archivo_pdf, x_pos, y_pos, ancho, salida)
            
            return pdf_menu()  # Volver al mismo menú después
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"

if __name__ == "__main__":
    # Para pruebas
    pdf_menu() 