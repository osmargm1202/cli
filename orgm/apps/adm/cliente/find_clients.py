from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List, Optional
from orgm.apps.adm.db import Cliente
from orgm.apps.adm.cliente.get_clients import mostrar_tabla_clientes
from orgm.stuff.spinner import spinner

console = Console()


def buscar_clientes(search_term=None) -> Optional[List[Cliente]]:
    """
    Returns the clients that match the search term
    """
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Cliente

    if not POSTGREST_URL:
        console.print(
            "[bold red]No se ha configurado la variable de entorno POSTGREST_URL[/bold red]"
        )
        return None

    search_term = search_term or ""
    try:
        response = requests.get(
            f"{POSTGREST_URL}/cliente?nombre=ilike.*{search_term}*",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        clientes_data = response.json()
        clientes = [Cliente.model_validate(cliente) for cliente in clientes_data]
        return clientes
    except Exception as e:
        console.print(f"[bold red]Error al buscar clientes: {e}[/bold red]")
        return None


def buscar(termino: str):
    """Comando para buscar clientes."""
    with spinner(f"Buscando clientes por '{termino}'..."):
        resultados = buscar_clientes(termino)
    mostrar_tabla_clientes(resultados)
