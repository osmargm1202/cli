from typing import List
from orgm.apps.adm.db import Proyecto
from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from rich.table import Table

console = Console()


def obtener_proyectos() -> List[Proyecto]:
    """Obtiene todos los proyectos desde PostgREST"""
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Proyecto

    try:
        response = requests.get(
            f"{POSTGREST_URL}/proyecto", headers=headers, timeout=10
        )
        response.raise_for_status()

        proyectos_data = response.json()
        proyectos = [Proyecto.model_validate(proyecto) for proyecto in proyectos_data]
        return proyectos
    except Exception as e:
        console.print(f"[bold red]Error al obtener proyectos: {e}[/bold red]")
        return []


def mostrar_proyectos(proyectos):
    """Muestra una tabla con los proyectos"""
    if not proyectos:
        print("[yellow]No se encontraron proyectos[/yellow]")
        return

    table = Table(title="Proyectos")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Nombre", style="green")
    table.add_column("Ubicación", style="yellow")
    table.add_column("Descripción", style="white")

    for p in proyectos:
        # Limitar la longitud de la descripción para una mejor visualización
        descripcion = (
            p.descripcion[:100] + "..." if len(p.descripcion) > 100 else p.descripcion
        )
        table.add_row(str(p.id), p.nombre_proyecto, p.ubicacion, descripcion)

    console.print(table)


def listar_proyectos():
    """Lista todos los proyectos"""
    proyectos = obtener_proyectos()
    mostrar_proyectos(proyectos)
