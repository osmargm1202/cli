from orgm.apps.adm.cotizacion.max_id import obtener_id_maximo
from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import Optional
from orgm.apps.adm.cotizacion.form_quotation import formulario_cotizacion

console = Console()


def crear_cotizacion(datos: dict) -> Optional[dict]:
    """
    Crea una nueva cotización.

    Args:
        datos (dict): Datos de la cotización a crear.

    Returns:
        Optional[dict]: Cotización creada o None si falla.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests
    from datetime import datetime

    try:
        # Asegurar que tenga fecha de creación
        if "fecha_creacion" not in datos:
            datos["fecha_creacion"] = datetime.now().isoformat()

        # Asignar ID si no está definido
        if "id" not in datos:
            datos["id"] = obtener_id_maximo()

        response = requests.post(
            f"{POSTGREST_URL}/cotizacion", json=datos, headers=headers
        )
        response.raise_for_status()
        return response.json()[0] if response.json() else None
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None


def definir_y_crear_cotizacion(cotizacion: Optional[dict] = None) -> dict:
    """Crear una nueva cotización"""
    datos = formulario_cotizacion()
    if datos:
        nueva = crear_cotizacion(datos)
        if nueva:
            # Obtener el ID usando getattr para objetos o get para diccionarios
            nueva_id = (
                getattr(nueva, "id", None)
                if not isinstance(nueva, dict)
                else nueva.get("id", None)
            )
            console.print(f"[bold green]Cotización creada: ID {nueva_id}[/bold green]")
    else:
        console.print("[bold red]No se pudo crear la cotización[/bold red]")
    return nueva
