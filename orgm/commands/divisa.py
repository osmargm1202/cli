# -*- coding: utf-8 -*-
import typer
from rich.console import Console
from orgm.apis.divisa import obtener_tasa_divisa

console = Console()

def tasa_divisa_command(
    desde: str = typer.Argument('USD', help="Moneda de origen (ej. USD, EUR, RD$)"),
    a: str = typer.Argument('RD$', help="Moneda de destino (ej. USD, EUR, RD$)"),
    cantidad: float = typer.Argument(1.0, help="Cantidad a convertir")
):
    """Obtiene la tasa de cambio entre dos divisas."""
    console.print(f"Obteniendo tasa de {desde.upper()} a {a.upper()} para {cantidad}...")
    resultado = obtener_tasa_divisa(desde.upper(), a.upper(), cantidad)

    if resultado is None:
        console.print("[bold red]Error al obtener la tasa de cambio.[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold green]{cantidad:.2f} {desde.upper()} = {resultado:.2f} {a.upper()}[/bold green]") 

def convertir_command(
    desde: str = typer.Argument('USD', help="Moneda de origen (ej. USD, EUR, RD$)"),
    a: str = typer.Argument('RD$', help="Moneda de destino (ej. USD, EUR, RD$)"),
    monto: float = typer.Argument(1, help="Monto a convertir")
):
    """Convierte un monto entre dos divisas."""
    console.print(f"Convirtiendo {monto:.2f} {desde.upper()} a {a.upper()}...")
    resultado = obtener_tasa_divisa(desde.upper(), a.upper(), monto)

    if resultado is None:
        console.print("[bold red]Error al obtener la tasa de cambio.[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold green]{monto:.2f} {desde.upper()} = {resultado:.2f} {a.upper()}[/bold green]") 