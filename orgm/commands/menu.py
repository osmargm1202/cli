# -*- coding: utf-8 -*-
import questionary
from rich.console import Console
import typer
import os
from pathlib import Path

# Crear consola para salida con Rich
console = Console()

def menu_principal():
    """Muestra un menú interactivo para los comandos principales de orgm."""
    console.print("[bold blue]===== ORGM CLI - Menú Principal =====[/bold blue]")
    
    # Definimos las categorías de comandos disponibles
    opciones = [
        {"name": "🧩 Clientes", "value": "client"},
        {"name": "📋 Proyectos", "value": "project"},
        {"name": "💰 Cotizaciones", "value": "quotation"},
        {"name": "💵 Pagos", "value": "payment"},
        {"name": "🐳 Docker", "value": "docker"},
        {"name": "🔑 Variables de entorno", "value": "env"},
        {"name": "📄 Operaciones PDF", "value": "pdf"},
        {"name": "🤖 Inteligencia Artificial", "value": "ai"},
        {"name": "🔍 Buscar empresa", "value": "find-company"},
        {"name": "💱 Tasa de divisa", "value": "currency-rate"},
        {"name": "🔄 Actualizar", "value": "update"},
        {"name": "⚙️ Verificar URLs", "value": "check"},
        {"name": "📦 Instalar", "value": "install"},
        {"name": "❓ Ayuda", "value": "help"},
        {"name": "❌ Salir", "value": "exit"}
    ]
    
    try:
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in opciones],
            use_indicator=True,
            use_shortcuts=True
        ).ask()
        
        if seleccion is None:  # Usuario presionó Ctrl+C
            return "exit"
            
        # Obtener el valor asociado a la selección
        comando = next(opcion["value"] for opcion in opciones if opcion["name"] == seleccion)
        
        if comando == "exit":
            console.print("[yellow]Saliendo...[/yellow]")
            return "exit"
        elif comando == "help":
            # Mostrar el contenido del archivo comandos.md
            mostrar_ayuda()
            return menu_principal()  # Volver al menú principal después de mostrar la ayuda
        elif comando == "find-company":
            # Solicitar el nombre de la empresa
            nombre_empresa = questionary.text("Nombre o RNC de la empresa a buscar:").ask()
            if not nombre_empresa:
                console.print("[yellow]Búsqueda cancelada[/yellow]")
                return menu_principal()
                
            # Preguntar por el estado (activo/inactivo)
            estado = questionary.select(
                "¿Buscar empresas activas o inactivas?",
                choices=[
                    "Activas",
                    "Inactivas",
                    "Todas (sin filtro)"
                ]
            ).ask()
            
            # Construir el comando con el argumento correspondiente
            if estado == "Activas":
                return f"find-company {nombre_empresa} --activo"
            elif estado == "Inactivas":
                return f"find-company {nombre_empresa} --inactivo"
            else:
                return f"find-company {nombre_empresa}"
        else:
            # Para comandos directos, ejecutar el comando
            return comando
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"

def mostrar_ayuda():
    """Muestra el contenido del archivo comandos.md"""
    try:
        # Obtener la ruta del script actual
        script_dir = Path(__file__).parent
        # Construir la ruta al archivo comandos.md (está en el directorio principal de orgm)
        orgm_dir = script_dir.parent # Subir un nivel desde 'commands' a 'orgm'
        comandos_path = orgm_dir / "comandos.md"
        
        # Leer y mostrar el archivo
        with open(comandos_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        console.print(contenido)
    except Exception as e:
        console.print(f"[bold red]Error al mostrar la ayuda: {e}[/bold red]")

if __name__ == "__main__":
    # Para pruebas
    resultado = menu_principal()
    console.print(f"Seleccionado: {resultado}") 