import os
import requests
import json
from rich.console import Console
from orgm.apis.header import get_headers_json

console = Console()

def ai_configs_list() -> None:
    """Lista las configuraciones disponibles en el servicio de IA"""
    API_URL = os.getenv("API_URL")
    if not API_URL:
        console.print("[bold red]Error: API_URL no está definida en las variables de entorno.[/bold red]")
        return

    # Usar la función importada para obtener los headers
    headers = get_headers_json()

    try:
        response = requests.get(f"{API_URL}/configs", headers=headers, timeout=10)
        response.raise_for_status()

        configs = response.json()
        console.print("[bold green]Configuraciones disponibles:[/bold green]")
        # Asumiendo que 'configs' es una lista de nombres o un dict
        if isinstance(configs, list):
            for config_name in sorted(configs): # Ordenar alfabéticamente
                 console.print(f"  - {config_name}")
        elif isinstance(configs, dict):
             # Si es un dict, podríamos querer listar las claves
             for config_name in sorted(configs.keys()):
                 console.print(f"  - {config_name}")
        else:
             console.print(f"  Respuesta inesperada: {configs}")

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al comunicarse con el servicio: {e}[/bold red]")
    except json.JSONDecodeError:
        console.print("[bold red]Error: La respuesta del servicio no es JSON válido.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error al procesar la respuesta: {e}[/bold red]")