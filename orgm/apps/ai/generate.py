import os
from typing import Optional
from rich.console import Console
from orgm.stuff.header import get_headers_json
import requests
from orgm.stuff.initialize_api import initialize
# Moved console initialization to the top level as it's generally safe
# and used by multiple functions potentially.
console = Console()

# Removed module-level variables API_URL, headers, CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET
# Removed initialize() function

# Imports like requests, get_headers_json, load_dotenv are now inside functions
# or the __main__ block to avoid execution on import.


def generate_text(text: str, config_name: str) -> Optional[str]:
    """Llama al endpoint de IA para generar un contenido basado en el parámetro *text* y la configuración *config_name*."""

    # Get API_URL from environment variables inside the function
    API_URL, headers = initialize()

    request_data = {"text": text, "config_name": config_name}

    try:
        # Make the API call
        response = requests.post(
            f"{API_URL}/ai", json=request_data, headers=headers, timeout=30
        )
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()
        if "error" in data:
            console.print(
                f"[bold red]Error del servicio de IA: {data['error']}[/bold red]"
            )
            return None

        # Assuming the response field is 'response'
        return data.get("response")  # Use .get for safety

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        console.print(
            f"[bold red]Error al comunicarse con el servicio de IA: {e}[/bold red]"
        )
        return None
    except Exception as e:
        # Handle other potential errors (like JSON decoding)
        console.print(
            f"[bold red]Error inesperado al procesar respuesta IA: {e}[/bold red]"
        )
        return None
