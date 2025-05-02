import os
from typing import Optional
from rich.console import Console

# Moved console initialization to the top level as it's generally safe
# and used by multiple functions potentially.
console = Console()

# Removed module-level variables API_URL, headers, CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET
# Removed initialize() function

# Imports like requests, get_headers_json, load_dotenv are now inside functions
# or the __main__ block to avoid execution on import.

def generate_text(text: str, config_name: str) -> Optional[str]:
    """Llama al endpoint de IA para generar un contenido basado en el parámetro *text* y la configuración *config_name*.

    Args:
        text: Texto de entrada que describe el contexto o prompt.
        config_name: Nombre de la configuración del modelo / plantilla que la API debe aplicar.

    Returns:
        Cadena con el resultado enviado por la API o ``None`` si ocurre un error.
    """
    # Import necessary modules inside the function
    import requests
    from orgm.apis.header import get_headers_json

    # Get API_URL from environment variables inside the function
    API_URL = os.getenv("API_URL")

    if not API_URL:
        console.print(
            "[bold yellow]Advertencia: API_URL no está definida en las variables de entorno.[/bold yellow]"
        )
        console.print(
            "[bold yellow]La generación automática de descripciones no estará disponible.[/bold yellow]"
        )
        return None

    # Get headers using the dedicated function
    headers = get_headers_json()

    request_data = {"text": text, "config_name": config_name}

    try:
        # Make the API call
        response = requests.post(
            f"{API_URL}/ai", json=request_data, headers=headers, timeout=30
        )
        response.raise_for_status() # Raise an exception for bad status codes

        data = response.json()
        if "error" in data:
            console.print(
                f"[bold red]Error del servicio de IA: {data['error']}[/bold red]"
            )
            return None

        # Assuming the response field is 'response'
        return data.get("response") # Use .get for safety

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        console.print(
            f"[bold red]Error al comunicarse con el servicio de IA: {e}[/bold red]"
        )
        return None
    except Exception as e:
        # Handle other potential errors (like JSON decoding)
        console.print(f"[bold red]Error inesperado al procesar respuesta IA: {e}[/bold red]")
        return None