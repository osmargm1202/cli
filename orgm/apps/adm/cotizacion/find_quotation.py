from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List
from orgm.apps.adm.cotizacion.find_client import seleccionar_cliente_por_nombre
from orgm.apps.adm.cotizacion.quotation_by_client import (
    mostrat_cotizaciones_por_cliente,
)
from orgm.apps.adm.cotizacion.find_project import seleccionar_proyecto_por_nombre
from orgm.apps.adm.cotizacion.quotation_by_project import (
    mostrar_cotizaciones_por_proyecto,
)


console = Console()


def buscar_cotizaciones(termino: str) -> List[dict]:
    """
    Busca cotizaciones que coincidan con el término de búsqueda.

    Args:
        termino (str): Término de búsqueda.

    Returns:
        List[dict]: Lista de cotizaciones que coinciden con la búsqueda.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        # Buscar en varios campos
        query = f"?or=(numero.ilike.*{termino}*,descripcion.ilike.*{termino}*)"
        response = requests.get(f"{POSTGREST_URL}/cotizacion{query}", headers=headers)
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


def obtener_cotizaciones_por_cliente(termino: str) -> List[dict]:
    cliente_id = seleccionar_cliente_por_nombre(termino)
    if cliente_id:
        mostrat_cotizaciones_por_cliente(cliente_id)


def obtener_cotizaciones_por_proyecto(termino: str) -> List[dict]:
    proyecto_id = seleccionar_proyecto_por_nombre(termino)
    if proyecto_id:
        mostrar_cotizaciones_por_proyecto(proyecto_id)
