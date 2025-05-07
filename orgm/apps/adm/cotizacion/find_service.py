from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List

console = Console()


def buscar_servicios(termino: str) -> List[dict]:
    """
    Busca servicios que coincidan con el término de búsqueda.

    Args:
        termino (str): Término de búsqueda.

    Returns:
        List[dict]: Lista de servicios que coinciden con la búsqueda.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        # Construir una consulta SQL para búsqueda en texto
        response = requests.get(
            f"{POSTGREST_URL}/servicio?or=(concepto.ilike.*{termino}*,descripcion.ilike.*{termino}*)",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al buscar servicios: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []
