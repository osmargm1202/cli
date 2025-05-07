from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import Optional

console = Console()


def obtener_servicio(id_servicio: int) -> Optional[dict]:
    """
    Obtiene un servicio específico por su ID.

    Args:
        id_servicio (int): ID del servicio a buscar.

    Returns:
        Optional[dict]: Datos del servicio o None si no se encuentra.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        response = requests.get(
            f"{POSTGREST_URL}/servicio?id=eq.{id_servicio}", headers=headers, timeout=10
        )
        response.raise_for_status()
        servicios = response.json()
        return servicios[0] if servicios else None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al obtener servicio: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None
