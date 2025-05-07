import os
from dotenv import load_dotenv
from orgm.stuff.header import get_headers_json
from rich.console import Console

console = Console()

# Inicializar variables como None a nivel de módulo
POSTGREST_URL = None
headers = None


def initialize():
    """Inicializa las variables que anteriormente estaban a nivel de módulo"""
    global POSTGREST_URL, headers



    load_dotenv(override=True)

    # Obtener URL de PostgREST
    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno[/bold red]"
        )

    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    # Añadir header adicional para PostgREST
    headers["Prefer"] = "return=representation"

    return POSTGREST_URL, headers
