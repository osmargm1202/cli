import requests
from typing import Optional, Dict
from orgm.apps.adm.db import Proyecto
from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from orgm.apps.adm.proyecto.get_project import obtener_proyecto
from orgm.apps.ai.generate import generate_text
from orgm.apps.adm.proyecto.form_project import formulario_proyecto
from orgm.stuff.spinner import spinner

console = Console()


def actualizar_proyecto(id_proyecto: int, proyecto_data: Dict) -> Optional[Proyecto]:
    """Actualiza un proyecto existente"""
    # Asegurar que las variables estén inicializadas

    POSTGREST_URL, headers = initialize()

    try:
        # Verificar que el proyecto existe
        proyecto_existente = obtener_proyecto(id_proyecto)
        if not proyecto_existente:
            return None

        # Si la descripción está vacía, generarla automáticamente
        if "descripcion" in proyecto_data and not proyecto_data["descripcion"]:
            nombre = proyecto_data.get(
                "nombre_proyecto", proyecto_existente.nombre_proyecto
            )
            descripcion = generate_text(nombre, "descripcion_electromecanica")
            print(f"Descripción generada: {descripcion}")
            if descripcion:
                proyecto_data["descripcion"] = descripcion

        update_headers = headers.copy()
        update_headers["Prefer"] = "return=representation"

        response = requests.patch(
            f"{POSTGREST_URL}/proyecto?id=eq.{id_proyecto}",
            headers=update_headers,
            json=proyecto_data,
            timeout=10,
        )
        response.raise_for_status()

        proyecto_actualizado = Proyecto.parse_obj(response.json()[0])
        console.print(
            f"[bold green]Proyecto actualizado correctamente: [blue]{proyecto_actualizado.nombre_proyecto}[/blue][/bold green] \n"
            f"[bold green]Descripción: [blue]{proyecto_actualizado.descripcion}[/blue][/bold green] \n"
            f"[bold green]Ubicación: [blue]{proyecto_actualizado.ubicacion}[/blue][/bold green] \n"
        )
        return proyecto_actualizado
    except Exception as e:
        console.print(
            f"[bold red]Error al actualizar proyecto {id_proyecto}: {e}[/bold red]"
        )
        return None


def definir_y_actualizar_proyecto(id_proyecto: int):
    """Modificar un proyecto existente"""
    with spinner(f"Obteniendo proyecto {id_proyecto}..."):
        proyecto_a_editar = obtener_proyecto(id_proyecto)
    if not proyecto_a_editar:
        print(f"[bold red]No se encontró el proyecto con ID {id_proyecto}[/bold red]")
        return

    datos = formulario_proyecto(proyecto_a_editar)
    if datos:
        with spinner(f"Actualizando proyecto {id_proyecto}..."):
            proyecto_actualizado = actualizar_proyecto(id_proyecto, datos)
        if proyecto_actualizado:
            print(
                f"[bold green]Proyecto actualizado: {proyecto_actualizado.nombre_proyecto}[/bold green]"
            )
