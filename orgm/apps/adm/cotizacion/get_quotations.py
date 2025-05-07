from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List
from orgm.apps.adm.cotizacion.show_quotations import mostrar_cotizaciones

console = Console()


def obtener_cotizaciones() -> List[dict]:
    """
    Obtiene todas las cotizaciones.

    Returns:
        List[dict]: Lista de cotizaciones.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        # Consulta con selección de campos específicos de cliente y proyecto
        query = "?select=*,cliente(id,nombre),proyecto(id,nombre_proyecto)"
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


def listar_cotizaciones():
    """Lista todas las cotizaciones disponibles."""
    cotis = obtener_cotizaciones()
    mostrar_cotizaciones(cotis)
