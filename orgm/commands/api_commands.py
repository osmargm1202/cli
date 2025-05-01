# -*- coding: utf-8 -*-
# api_commands.py
import typer
import sys
from typing import List
from rich.console import Console

# Importar comandos específicos de API
from orgm.commands.rnc import buscar_empresa_command
from orgm.commands.divisa import tasa_divisa_command
from orgm.apps.rnc_app import rnc_app

# Crear consola para salida con Rich
console = Console()

# Crear aplicación Typer para comandos de API
api_app = typer.Typer(help="Comandos para acceder a APIs externas")

@api_app.command(name="find-company")
def find_company_command(
    busqueda_parts: List[str] = typer.Argument(None, help="Término de búsqueda para la empresa (nombre o RNC), puede contener espacios."),
    activo: bool = typer.Option(True, "--activo/--inactivo", help="Buscar solo empresas activas o suspendidas")
):
    """Busca información de una empresa por su nombre o RNC."""
    # Si no se pasaron argumentos, usar la interfaz interactiva
    if not busqueda_parts:
        return rnc_app()
    else:
        # Si se pasaron argumentos, usar la función original
        buscar_empresa_command(busqueda_parts, activo)

@api_app.command(name="currency-rate")
def currency_rate_command():
    """Consulta tasas de cambio de divisas actuales."""
    tasa_divisa_command() 