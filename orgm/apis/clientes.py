import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum  # Usar Enum en lugar de Literal
import questionary
import requests
import typer
from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.table import Table
from orgm.adm.clientes import (
    obtener_clientes,
    obtener_cliente,
    crear_cliente,
    actualizar_cliente,
    buscar_clientes,
)
from orgm.stuff.spinner import spinner
from orgm.apis.header import get_headers_json
from orgm.apis.rnc import buscar_rnc_cliente # Importar la función de búsqueda RNC

console = Console()

# Definir enum para tipo de factura
class TipoFactura(str, Enum):
    NCFC = "NCFC"
    NCF = "NCF"

# Cargar variables de entorno en cada función que las necesite, no a nivel de módulo

def get_postgrest_url():
    """Obtiene la URL de PostgREST y verifica que esté definida."""
    # Cargar variables de entorno
    load_dotenv(override=True)
    
    # URL de PostgREST
    postgrest_url = os.getenv("POSTGREST_URL")
    
    # Verificar si está definida sin terminar el programa
    if not postgrest_url:
        console.print(
            "[bold yellow]Advertencia: POSTGREST_URL no está definida en las variables de entorno.[/bold yellow]"
        )
    
    return postgrest_url

# Obtener headers de forma centralizada, solo cuando se necesiten
def get_headers():
    """Obtiene los headers para las solicitudes a PostgREST."""
    headers = get_headers_json()
    
    # Verificar si se obtuvieron las credenciales (opcional)
    if "CF-Access-Client-Id" not in headers:
        console.print(
            "[bold yellow]Advertencia: Credenciales de Cloudflare Access no encontradas o no configuradas.[/bold yellow]"
        )
        console.print(
            "[bold yellow]Las consultas a PostgREST no incluirán autenticación de Cloudflare Access.[/bold yellow]"
        )
    
    return headers

# El resto del archivo queda igual... 