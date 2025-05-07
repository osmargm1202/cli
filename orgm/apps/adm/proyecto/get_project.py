from typing import Optional
from orgm.apps.adm.db import Proyecto
from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from rich.table import Table

console = Console()


def obtener_proyecto(id_proyecto: int) -> Optional[Proyecto]:
    """Obtiene un proyecto por su ID"""
    # Asegurar que las variables estén inicializadas

    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Proyecto

    try:
        response = requests.get(
            f"{POSTGREST_URL}/proyecto?id=eq.{id_proyecto}", headers=headers, timeout=10
        )
        response.raise_for_status()

        proyectos_data = response.json()
        if not proyectos_data:
            console.print(
                f"[yellow]No se encontró el proyecto con ID {id_proyecto}[/yellow]"
            )
            return None

        proyecto = Proyecto.parse_obj(proyectos_data[0])
        return proyecto
    except Exception as e:
        console.print(
            f"[bold red]Error al obtener proyecto {id_proyecto}: {e}[/bold red]"
        )
        return None


def mostrar_proyecto_detalle(proyecto: Proyecto):
    """Muestra los datos completos de un proyecto"""
    table = Table(title=f"Proyecto: {proyecto.nombre_proyecto} (ID: {proyecto.id})")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="green")

    for campo in proyecto.__fields__.keys():
        valor = getattr(proyecto, campo)
        table.add_row(campo, str(valor))

    console.print(table)


def obtener_y_mostrar_proyecto(id_proyecto: int):
    """Obtiene y muestra los detalles de un proyecto por su ID"""
    proyecto = obtener_proyecto(id_proyecto)
    if proyecto:
        mostrar_proyecto_detalle(proyecto)
