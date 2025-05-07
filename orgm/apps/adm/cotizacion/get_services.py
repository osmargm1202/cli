from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List

console = Console()


def obtener_servicios() -> List[dict]:
    """
    Obtiene la lista de servicios desde PostgREST.

    Returns:
        List[dict]: Lista de servicios en formato dict.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        response = requests.get(
            f"{POSTGREST_URL}/servicio", headers=headers, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al obtener servicios: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []
