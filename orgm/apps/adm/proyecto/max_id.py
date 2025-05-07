from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console

console = Console()


def obtener_id_maximo() -> int:
    """
    Obtiene el ID máximo de la tabla proyecto.

    Returns:
        int: ID máximo + 1 (siguiente ID disponible).
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        response = requests.get(
            f"{POSTGREST_URL}/proyecto?select=id", headers=headers, timeout=10
        )
        response.raise_for_status()
        proyectos = response.json()
        return max(proyecto["id"] for proyecto in proyectos) + 1 if proyectos else 1
    except Exception as e:
        console.print(
            f"[bold red]Error al obtener ID máximo de proyectos: {e}[/bold red]"
        )
        return 1
