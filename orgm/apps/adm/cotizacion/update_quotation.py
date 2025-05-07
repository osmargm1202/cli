from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import Optional
from orgm.apps.adm.cotizacion.form_quotation import formulario_cotizacion
from orgm.apps.adm.cotizacion.get_quotation import obtener_cotizacion

console = Console()


def actualizar_cotizacion(id_cotizacion: int, datos: dict) -> bool:
    """
    Actualiza una cotización existente.

    Args:
        id_cotizacion (int): ID de la cotización a actualizar.
        datos (dict): Nuevos datos para la cotización.

    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        # Remover id si está en los datos para evitar conflictos
        if "id" in datos:
            del datos["id"]

        response = requests.patch(
            f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}",
            json=datos,
            headers=headers,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return False
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return False


def definir_y_actualizar_cotizacion(
    id_cotizacion: int, cotizacion: Optional[dict] = None
) -> dict:
    """Modificar una cotización existente"""
    cot = obtener_cotizacion(id_cotizacion)
    if not cot:
        console.print(
            f"[bold red]No se encontró la cotización con ID {id_cotizacion}[/bold red]"
        )
        return
    datos = formulario_cotizacion(cot)
    if datos:
        act = actualizar_cotizacion(id_cotizacion, datos)
        if act:
            console.print("[bold green]Cotización actualizada[/bold green]")
