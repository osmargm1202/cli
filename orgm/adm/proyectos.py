# -*- coding: utf-8 -*-
from typing import Dict, List, Optional
from rich.console import Console
from orgm.adm.db import Proyecto, Ubicacion  # Importación a nivel de módulo para que otros módulos puedan acceder
from orgm.apps.ai.generate import generate_text

console = Console()

# Inicializar variables como None a nivel de módulo
POSTGREST_URL = None
headers = None

def initialize():
    """Inicializa las variables que anteriormente estaban a nivel de módulo"""
    global POSTGREST_URL, headers
    
    import os
    from dotenv import load_dotenv
    from orgm.apis.header import get_headers_json
    
    load_dotenv(override=True)
    
    # Obtener URL de PostgREST
    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno[/bold red]"
        )
        return False
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    
    # Verificar si se obtuvieron las credenciales (opcional)
    if "CF-Access-Client-Id" not in headers:
        console.print(
            "[bold yellow]Advertencia: Credenciales de Cloudflare Access no encontradas o no configuradas.[/bold yellow]"
        )
        console.print(
            "[bold yellow]Las consultas no incluirán autenticación de Cloudflare Access.[/bold yellow]"
        )
    
    return True


def obtener_id_maximo() -> int:
    """
    Obtiene el ID máximo de la tabla proyecto.
    
    Returns:
        int: ID máximo + 1 (siguiente ID disponible).
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        response = requests.get(f"{POSTGREST_URL}/proyecto?select=id", headers=headers, timeout=10)
        response.raise_for_status()
        proyectos = response.json()
        return max(proyecto['id'] for proyecto in proyectos) + 1 if proyectos else 1
    except Exception as e:
        console.print(f"[bold red]Error al obtener ID máximo de proyectos: {e}[/bold red]")
        return 1


def obtener_proyectos() -> List[Proyecto]:
    """Obtiene todos los proyectos desde PostgREST"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Proyecto
    
    try:
        response = requests.get(f"{POSTGREST_URL}/proyecto", headers=headers, timeout=10)
        response.raise_for_status()

        proyectos_data = response.json()
        proyectos = [Proyecto.model_validate(proyecto) for proyecto in proyectos_data]
        return proyectos
    except Exception as e:
        console.print(f"[bold red]Error al obtener proyectos: {e}[/bold red]")
        return []


def obtener_proyecto(id_proyecto: int) -> Optional[Proyecto]:
    """Obtiene un proyecto por su ID"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Proyecto
    
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


def crear_proyecto(proyecto_data: Dict) -> Optional[Proyecto]:
    """Crea un nuevo proyecto"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Proyecto
    from orgm.apis.ai import generate_project_description
    
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
                proyecto_data.get("nombre_proyecto"),
                "descripcion_electromecanica"
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


def actualizar_proyecto(id_proyecto: int, proyecto_data: Dict) -> Optional[Proyecto]:
    """Actualiza un proyecto existente"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Proyecto
    from orgm.apis.ai import generate_project_description
    
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
            descripcion = generate_project_description(nombre)
            print(f"Descripción generada: {descripcion}")
            if descripcion:
                proyecto_data["descripcion"] = descripcion

        update_headers = headers.copy()
        update_headers["Prefer"] = "return=representation"

        response = requests.patch(
            f"{POSTGREST_URL}/proyecto?id=eq.{id_proyecto}",
            headers=update_headers,
            json=proyecto_data,
            timeout=10
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


def eliminar_proyecto(id_proyecto: int) -> bool:
    """Elimina un proyecto existente"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        # Verificar que el proyecto existe
        proyecto_existente = obtener_proyecto(id_proyecto)
        if not proyecto_existente:
            return False

        response = requests.delete(
            f"{POSTGREST_URL}/proyecto?id=eq.{id_proyecto}", headers=headers, timeout=10
        )
        response.raise_for_status()

        console.print(
            f"[bold green]Proyecto eliminado correctamente: ID {id_proyecto}[/bold green]"
        )
        return True
    except Exception as e:
        console.print(
            f"[bold red]Error al eliminar proyecto {id_proyecto}: {e}[/bold red]"
        )
        return False


def buscar_proyectos(termino: str) -> List[Proyecto]:
    """Busca proyectos por nombre"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Proyecto
    
    try:
        # Usamos el operador ILIKE de PostgreSQL para búsqueda case-insensitive
        response = requests.get(
            f"{POSTGREST_URL}/proyecto?or=(nombre_proyecto.ilike.*{termino}*,descripcion.ilike.*{termino}*,ubicacion.ilike.*{termino}*)",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        proyectos_data = response.json()
        proyectos = [Proyecto.parse_obj(proyecto) for proyecto in proyectos_data]
        return proyectos
    except Exception as e:
        console.print(f"[bold red]Error al buscar proyectos: {e}[/bold red]")
        return []


def obtener_ubicaciones() -> List[Ubicacion]:
    """Obtiene todas las ubicaciones disponibles"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Ubicacion
    
    try:
        response = requests.get(f"{POSTGREST_URL}/ubicacion", headers=headers, timeout=10)
        response.raise_for_status()

        ubicaciones_data = response.json()
        ubicaciones = [Ubicacion.parse_obj(ubicacion) for ubicacion in ubicaciones_data]
        return ubicaciones
    except Exception as e:
        console.print(f"[bold red]Error al obtener ubicaciones: {e}[/bold red]")
        return []


def buscar_ubicaciones(termino: str) -> List[Ubicacion]:
    """Busca ubicaciones por provincia, distrito o distrito municipal"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Ubicacion
    
    try:
        response = requests.get(
            f"{POSTGREST_URL}/ubicacion?or=(provincia.ilike.*{termino}*,distrito.ilike.*{termino}*,distritomunicipal.ilike.*{termino}*)",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        ubicaciones_data = response.json()
        ubicaciones = [Ubicacion.parse_obj(ubicacion) for ubicacion in ubicaciones_data]
        return ubicaciones
    except Exception as e:
        console.print(f"[bold red]Error al buscar ubicaciones: {e}[/bold red]")
        return []


def crear_proyecto_ejemplo() -> Optional[Proyecto]:
    """Crea un proyecto de ejemplo para pruebas"""
    proyecto_data = {
        "nombre_proyecto": "Proyecto de Prueba",
        "descripcion": "Este es un proyecto creado automáticamente para pruebas",
        "ubicacion": "Madrid",
        "estado": "PLANIFICACION",
        "fecha_inicio": None,
        "fecha_fin_estimada": None
    }
    
    return crear_proyecto(proyecto_data)
