from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console

console = Console()


def obtener_id_maximo() -> int:
    """
    Obtiene el ID máximo de la tabla cliente.

    Returns:
        int: ID máximo + 1 (siguiente ID disponible).
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests

    try:
        response = requests.get(
            f"{POSTGREST_URL}/cliente?select=id", headers=headers, timeout=10
        )
        response.raise_for_status()
        clientes = response.json()
        return max(cliente["id"] for cliente in clientes) + 1 if clientes else 1
    except Exception as e:
        console.print(
            f"[bold red]Error al obtener ID máximo de clientes: {e}[/bold red]"
        )
        return 1
