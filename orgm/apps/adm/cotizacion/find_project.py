from typing import Optional
from orgm.apps.adm.db import Proyecto
from orgm.apps.adm.proyecto.find_project import buscar_proyectos
from orgm.stuff.spinner import spinner
from typing import List
import questionary


def seleccionar_proyecto_por_nombre(termino: str) -> Optional[int]:
    """Busca proyectos por nombre y permite al usuario seleccionar uno."""
    with spinner(f"Buscando proyectos por '{termino}'..."):
        proyectos: List[Proyecto] = buscar_proyectos(termino)
    if not proyectos:
        print("[yellow]No se encontraron proyectos[/yellow]")
        return None

    # Manejar tanto diccionarios como objetos (aunque buscar_proyectos devuelve Proyecto)
    opciones = []
    for p in proyectos:
        if isinstance(p, Proyecto):  # Verificar si es instancia de Proyecto
            id_proyecto = p.id
            nombre_proyecto = p.nombre_proyecto
            opciones.append(f"{id_proyecto}: {nombre_proyecto}")
        elif isinstance(p, dict):  # Fallback por si acaso
            id_proyecto = p.get("id", "")
            nombre_proyecto = p.get("nombre_proyecto", "")
            opciones.append(f"{id_proyecto}: {nombre_proyecto}")
        # Ignorar otros tipos si los hubiera

    if not opciones:
        print("[yellow]No se encontraron proyectos válidos[/yellow]")
        return None

    opciones.append("Buscar de nuevo")
    opciones.append("Cancelar")

    while True:
        sel = questionary.select("Seleccione un proyecto:", choices=opciones).ask()

        if sel == "Cancelar":
            return None
        elif sel == "Buscar de nuevo":
            nuevo_termino = questionary.text("Nuevo término de búsqueda:").ask()
            if not nuevo_termino:
                return None  # Cancelar si no ingresa nuevo término
            with spinner(f"Buscando proyectos por '{nuevo_termino}'..."):
                proyectos = buscar_proyectos(nuevo_termino)
            if not proyectos:
                print("[yellow]No se encontraron proyectos[/yellow]")
                # Podríamos preguntar si quiere intentar de nuevo o cancelar
                if not questionary.confirm(
                    "¿Intentar buscar de nuevo?", default=True
                ).ask():
                    return None
                continue  # Volver a pedir término
            # Actualizar opciones si se encontraron proyectos
            opciones = [
                f"{p.id}: {p.nombre_proyecto}"
                for p in proyectos
                if isinstance(p, Proyecto)
            ]
            opciones.append("Buscar de nuevo")
            opciones.append("Cancelar")
            continue  # Mostrar nueva lista
        else:
            # Seleccionó un proyecto
            try:
                return int(sel.split(":")[0])
            except (ValueError, IndexError):
                print("[red]Selección inválida[/red]")
                # Volver a mostrar la lista actual
