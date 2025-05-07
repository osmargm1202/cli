from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List
from orgm.apps.adm.db import Ubicacion


console = Console()


def obtener_ubicaciones() -> List[Ubicacion]:
    """Obtiene todas las ubicaciones disponibles"""
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Ubicacion

    try:
        response = requests.get(
            f"{POSTGREST_URL}/ubicacion", headers=headers, timeout=10
        )
        response.raise_for_status()

        ubicaciones_data = response.json()
        ubicaciones = [
            Ubicacion.model_validate(ubicacion) for ubicacion in ubicaciones_data
        ]
        return ubicaciones
    except Exception as e:
        console.print(f"[bold red]Error al obtener ubicaciones: {e}[/bold red]")
        return []
