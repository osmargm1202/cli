# -*- coding: utf-8 -*-
import typer
from typing import List
from rich.console import Console
from rich.table import Table
from rich.pretty import pretty_repr
from orgm.apis.rnc import buscar_rnc_cliente

console = Console()

def buscar_empresa_command(
    busqueda_parts: List[str] = typer.Argument(..., help="Término de búsqueda para la empresa (nombre o RNC), puede contener espacios."),
    activo: bool = typer.Option(True, "--activo/--inactivo", help="Buscar solo empresas activas o suspendidas")
):
    """Busca información de una empresa por su nombre o RNC."""
    busqueda = " ".join(busqueda_parts)
    console.print(f"Buscando '{busqueda}' (Activo: {activo})...")
    resultado = buscar_rnc_cliente(busqueda, activo)

    if resultado is None:
        console.print("[bold red]Error al buscar la empresa.[/bold red]")
        raise typer.Exit(code=1)

    if not resultado:
        console.print("[yellow]No se encontraron empresas con ese criterio.[/yellow]")
        raise typer.Exit()

    # Crear tabla para mostrar resultados
    table = Table(title="Resultados de Búsqueda RNC", show_header=True, header_style="bold magenta")
    table.add_column("RNC/Cédula", style="dim", width=15)
    table.add_column("Nombre Comercial")
    table.add_column("Razón Social")
    table.add_column("Actividad")
    table.add_column("Estado", justify="right")

    for empresa in resultado:
        table.add_row(
            str(empresa.get("rnc", "N/A")),
            empresa.get("nombre", "N/A"),
            empresa.get("razon", "N/A"),
            empresa.get("descripcion", "N/A"),
            empresa.get("estado", "N/A")
        )

    console.print(table) 