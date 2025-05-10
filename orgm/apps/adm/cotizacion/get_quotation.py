from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import Optional

console = Console()


def obtener_cotizacion(id_cotizacion: int) -> Optional[dict]:
    """
    Obtiene una cotización específica por su ID.

    Args:
        id_cotizacion (int): ID de la cotización a buscar.

    Returns:
        Optional[dict]: Datos de la cotización o None si no se encuentra.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        query = f"?select=*,cliente(id,nombre),proyecto(id,nombre_proyecto),servicio(id,nombre,descripcion)&id=eq.{id_cotizacion}"
        response = requests.get(
            f"{POSTGREST_URL}/cotizacion{query}", headers=headers
        )
        response.raise_for_status()
        result = response.json()
        return result[0] if result else None
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None
