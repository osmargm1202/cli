from typing import Optional, Dict
from orgm.apps.adm.db import Proyecto
from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from orgm.apps.adm.proyecto.max_id import obtener_id_maximo
from orgm.apps.adm.proyecto.form_project import formulario_proyecto
from orgm.stuff.spinner import spinner

console = Console()


def crear_proyecto(proyecto_data: Dict) -> Optional[Proyecto]:
    """Crea un nuevo proyecto"""
    # Asegurar que las variables estén inicializadas

    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Proyecto
    from orgm.apps.ai.generate import generate_text

    try:
        # Validar datos mínimos requeridos
        if not proyecto_data.get("nombre_proyecto"):
            console.print(
                "[bold red]Error: El nombre del proyecto es obligatorio[/bold red]"
            )
            return None

        # Si la descripción está vacía, generarla automáticamente
        if not proyecto_data.get("descripcion"):
            descripcion = generate_text(
                proyecto_data.get("nombre_proyecto"), "descripcion_electromecanica"
            )
            if descripcion:
                proyecto_data["descripcion"] = descripcion

        # Asignar ID si no está definido
        if "id" not in proyecto_data:
            proyecto_data["id"] = obtener_id_maximo()

        response = requests.post(
            f"{POSTGREST_URL}/proyecto", headers=headers, json=proyecto_data, timeout=10
        )
        response.raise_for_status()

        nuevo_proyecto = Proyecto.parse_obj(response.json()[0])
        console.print(
            f"[bold green]Proyecto creado correctamente con ID: {nuevo_proyecto.id}[/bold green]"
        )
        return nuevo_proyecto
    except Exception as e:
        console.print(f"[bold red]Error al crear proyecto: {e}[/bold red]")
        return None


def definir_y_crear_proyecto():
    """Crear un nuevo proyecto"""
    datos = formulario_proyecto()
    if datos:
        with spinner("Creando proyecto..."):
            nuevo_proyecto = crear_proyecto(datos)
        if nuevo_proyecto:
            print(
                f"[bold green]Proyecto creado: {nuevo_proyecto.nombre_proyecto}[/bold green]"
            )
