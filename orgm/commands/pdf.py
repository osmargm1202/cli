# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

# Importaciones locales del proyecto
from orgm.apps.utils.firma import firmar_pdf, seleccionar_y_firmar_pdf

# Crear consola para salida con Rich
console = Console()

def pdf_firmar(
    archivo_pdf: str = typer.Argument(..., help="Ruta al archivo PDF a firmar"), 
    x_pos: int = typer.Option(..., "--x", "-x", help="Posición X donde colocar la firma"),
    y_pos: int = typer.Option(..., "--y", "-y", help="Posición Y donde colocar la firma"),
    ancho: int = typer.Option(..., "--ancho", "-a", help="Ancho de la firma"),
    salida: Optional[str] = typer.Option(None, "--salida", "-s", help="Nombre del archivo de salida")
) -> None:
    """Firma un archivo PDF"""
    try:
        archivo_path = Path(archivo_pdf)
        if not archivo_path.exists():
            console.print(f"[bold red]Error: El archivo '{archivo_pdf}' no existe[/bold red]")
            return

        resultado = firmar_pdf(archivo_pdf, x_pos, y_pos, ancho, salida)
        if resultado:
            console.print(f"[bold green]Archivo firmado: {resultado}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error al firmar el PDF: {e}[/bold red]")

def pdf_firmar_interactivo(
    x_pos: int = typer.Option(100, "--x", "-x", help="Posición X donde colocar la firma (default: 100)"),
    y_pos: int = typer.Option(100, "--y", "-y", help="Posición Y donde colocar la firma (default: 100)"),
    ancho: int = typer.Option(200, "--ancho", "-a", help="Ancho de la firma (default: 200)")
) -> None:
    """Firma un archivo PDF de forma interactiva utilizando un selector de archivos"""
    try:
        resultado = seleccionar_y_firmar_pdf(x_pos, y_pos, ancho)
        if resultado:
            console.print(f"[bold green]Archivo firmado: {resultado}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error al firmar el PDF: {e}[/bold red]") 