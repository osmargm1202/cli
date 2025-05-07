import requests
from typing import List
from orgm.apps.adm.db import Proyecto
from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from orgm.apps.adm.proyecto.get_projects import mostrar_proyectos


console = Console()


def buscar_proyectos(termino: str) -> List[Proyecto]:
    """Busca proyectos por nombre"""
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    try:
        # Usamos el operador ILIKE de PostgreSQL para búsqueda case-insensitive
        response = requests.get(
            f"{POSTGREST_URL}/proyecto?or=(nombre_proyecto.ilike.*{termino}*,descripcion.ilike.*{termino}*,ubicacion.ilike.*{termino}*)",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        proyectos_data = response.json()
        proyectos = [Proyecto.model_validate(proyecto) for proyecto in proyectos_data]
        return proyectos
    except Exception as e:
        console.print(f"[bold red]Error al buscar proyectos: {e}[/bold red]")
        return []


def buscar_y_mostrar_proyectos(termino: str):
    """Busca y muestra proyectos por nombre"""
    proyectos = buscar_proyectos(termino)
    if proyectos:
        mostrar_proyectos(proyectos)
    else:
        console.print("[yellow]No se encontraron proyectos[/yellow]")
