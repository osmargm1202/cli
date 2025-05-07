from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List, Optional

console = Console()


def cotizaciones_por_cliente(
    id_cliente: int, limite: Optional[int] = None
) -> List[dict]:
    """
    Obtiene las cotizaciones de un cliente específico.

    Args:
        id_cliente (int): ID del cliente.
        limite (Optional[int]): Límite de resultados a devolver.

    Returns:
        List[dict]: Lista de cotizaciones del cliente.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        # Construir la URL con el ID del cliente
        select_query = "select=*,cliente(id,nombre),proyecto(id,nombre_proyecto)"
        url = f"{POSTGREST_URL}/cotizacion?id_cliente=eq.{id_cliente}&{select_query}"

        # Agregar límite si se especifica
        if limite is not None:
            url += f"&limit={limite}"

        # Ordenar por fecha de creación descendente
        url += "&order=fecha.desc"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []
