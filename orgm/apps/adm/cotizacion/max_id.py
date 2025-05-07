from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console

console = Console()


def obtener_id_maximo() -> int:
    """
    Obtiene el ID máximo de la tabla cotizacion.

    Returns:
        int: ID máximo + 1 (siguiente ID disponible).
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        response = requests.get(
            f"{POSTGREST_URL}/cotizacion?select=id", headers=headers
        )
        response.raise_for_status()
        cotizaciones = response.json()
        return (
            max(cotizacion["id"] for cotizacion in cotizaciones) + 1
            if cotizaciones
            else 1
        )
    except Exception as e:
        console.print(
            f"[bold red]Error al obtener ID máximo de cotizaciones: {e}[/bold red]"
        )
        return 1
