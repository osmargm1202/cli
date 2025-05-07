import os
from dotenv import load_dotenv
from orgm.stuff.header import get_headers_json
from rich.console import Console

console = Console()

# Inicializar variables como None a nivel de módulo
API_URL = None
headers = None


def initialize():
    """Inicializa las variables que anteriormente estaban a nivel de módulo"""
    global API_URL, headers



    load_dotenv(override=True)

    # Obtener URL de API
    API_URL = os.getenv("API_URL")
    if not API_URL:
        console.print(
            "[bold red]Error: API_URL no está definida en las variables de entorno[/bold red]"
        )

    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    # Añadir header adicional para API
    headers["Prefer"] = "return=representation"

    return API_URL, headers
