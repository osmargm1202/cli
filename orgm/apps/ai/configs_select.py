import os
import requests
import json
from rich.console import Console
from orgm.apis.header import get_headers_json
from typing import List, Optional

console = Console()



def ai_configs_select() -> Optional[List[str]]:
    """Obtiene la lista de configuraciones disponibles desde el servicio de IA."""
    API_URL = os.getenv("API_URL")
    if not API_URL:
        console.print("[bold red]Error: API_URL no está definida en las variables de entorno.[/bold red]", stderr=True)
        return None

    headers = get_headers_json()

    try:
        response = requests.get(f"{API_URL}/configs", headers=headers, timeout=10)
        response.raise_for_status()

        configs = response.json()
        # Asegurarse de que configs sea una lista de strings
        if isinstance(configs, list) and all(isinstance(item, str) for item in configs):
            return sorted(configs)
        elif isinstance(configs, dict): # Podría devolver un dict, extraemos las claves
             return sorted(list(configs.keys()))
        else:
            console.print(f"[bold red]Respuesta inesperada del endpoint /configs: {configs}[/bold red]", stderr=True)
            return None

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al obtener configuraciones del servicio: {e}[/bold red]", stderr=True)
        return None
    except json.JSONDecodeError:
        console.print("[bold red]Error: La respuesta del servicio /configs no es JSON válido.[/bold red]", stderr=True)
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado al obtener configuraciones: {e}[/bold red]", stderr=True)
        return None