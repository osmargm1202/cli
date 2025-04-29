# -*- coding: utf-8 -*-
from pathlib import Path
import typer
from rich.console import Console

# Importaciones locales del proyecto
from orgm.stuff.variables import edit_env_variables

# Crear consola para salida con Rich
console = Console()

def env_edit() -> None:
    """Editar variables de entorno en una interfaz TUI"""
    console.print("Abriendo editor de variables de entorno...")
    edit_env_variables()

def env_file(archivo: str = typer.Argument(..., help="Ruta al archivo a cargar")) -> None:
    """Leer un archivo y guardarlo como .env"""
    try:
        archivo_path = Path(archivo)
        if not archivo_path.exists():
            console.print(f"[bold red]Error: El archivo '{archivo}' no existe[/bold red]")
            return

        with open(archivo_path, "r", encoding="utf-8") as f:
            contenido = f.read()

        with open(".env", "w", encoding="utf-8") as f:
            f.write(contenido)

        console.print(f"[bold green]Archivo '{archivo}' guardado como .env[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error al procesar el archivo: {e}[/bold red]") 