from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List, Optional
from orgm.stuff.spinner import spinner
import requests

console = Console()


def cotizaciones_por_proyecto(
    id_proyecto: int, limite: Optional[int] = None
) -> List[dict]:
    """
    Obtiene las cotizaciones relacionadas con un proyecto específico.

    Args:
        id_proyecto (int): ID del proyecto.
        limite (Optional[int]): Cantidad máxima de cotizaciones a retornar.

    Returns:
        List[dict]: Lista de cotizaciones del proyecto.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    try:
        select_query = "select=*,cliente(id,nombre),proyecto(id,nombre_proyecto)"
        url = f"{POSTGREST_URL}/cotizacion?id_proyecto=eq.{id_proyecto}&{select_query}"

        # Añadir límite si se especifica
        if limite:
            url += f"&limit={limite}"
        # Ordenar por fecha de creación descendente
        url += "&order=fecha.desc"

        with spinner(f"Obteniendo cotizaciones del proyecto {id_proyecto}..."):
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
