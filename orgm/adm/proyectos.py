# -*- coding: utf-8 -*-
import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
from rich.console import Console
from orgm.adm.db import Proyecto, Ubicacion
from orgm.stuff.ai import generate_project_description
from orgm.stuff.spinner import spinner

console = Console()
load_dotenv(override=True)

# Obtener la URL de PostgREST desde las variables de entorno
POSTGREST_URL = os.getenv("POSTGREST_URL")
if not POSTGREST_URL:
    console.print(
        "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno[/bold red]"
    )

# Obtener credenciales de Cloudflare Access
CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

if not all([CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET]):
    console.print(
        "[bold yellow]Advertencia: CF_ACCESS_CLIENT_ID o CF_ACCESS_CLIENT_SECRET no están definidas en las variables de entorno.[/bold yellow]"
    )
    console.print(
        "[bold yellow]Las consultas no incluirán autenticación de Cloudflare Access.[/bold yellow]"
    )

# Configuración de los headers para PostgREST
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Prefer": "return=representation",
}

# Agregar headers de Cloudflare Access si están disponibles
if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
    headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
    headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET


def obtener_proyectos() -> List[Proyecto]:
    """Obtiene todos los proyectos desde PostgREST"""
    try:
        with spinner("Obteniendo proyectos..."):
            response = requests.get(f"{POSTGREST_URL}/proyecto", headers=headers)
        response.raise_for_status()

        proyectos_data = response.json()
        proyectos = [Proyecto.parse_obj(proyecto) for proyecto in proyectos_data]
        return proyectos
    except Exception as e:
        console.print(f"[bold red]Error al obtener proyectos: {e}[/bold red]")
        return []


def obtener_proyecto(id_proyecto: int) -> Optional[Proyecto]:
    """Obtiene un proyecto por su ID"""
    try:
        response = requests.get(
            f"{POSTGREST_URL}/proyecto?id=eq.{id_proyecto}", headers=headers
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
    try:
        # Validar datos mínimos requeridos
        if not proyecto_data.get("nombre_proyecto"):
            console.print(
                "[bold red]Error: El nombre del proyecto es obligatorio[/bold red]"
            )
            return None

        # Si la descripción está vacía, generarla automáticamente
        if not proyecto_data.get("descripcion"):
            descripcion = generate_project_description(
                proyecto_data.get("nombre_proyecto")
            )
            if descripcion:
                proyecto_data["descripcion"] = descripcion

        response = requests.post(
            f"{POSTGREST_URL}/proyecto", headers=headers, json=proyecto_data
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
            if descripcion:
                proyecto_data["descripcion"] = descripcion

        update_headers = headers.copy()
        update_headers["Prefer"] = "return=representation"

        response = requests.patch(
            f"{POSTGREST_URL}/proyecto?id=eq.{id_proyecto}",
            headers=update_headers,
            json=proyecto_data,
        )
        response.raise_for_status()

        proyecto_actualizado = Proyecto.parse_obj(response.json()[0])
        console.print(
            f"[bold green]Proyecto actualizado correctamente: {proyecto_actualizado.nombre_proyecto}[/bold green]"
        )
        return proyecto_actualizado
    except Exception as e:
        console.print(
            f"[bold red]Error al actualizar proyecto {id_proyecto}: {e}[/bold red]"
        )
        return None


def eliminar_proyecto(id_proyecto: int) -> bool:
    """Elimina un proyecto existente"""
    try:
        # Verificar que el proyecto existe
        proyecto_existente = obtener_proyecto(id_proyecto)
        if not proyecto_existente:
            return False

        response = requests.delete(
            f"{POSTGREST_URL}/proyecto?id=eq.{id_proyecto}", headers=headers
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
    try:
        # Usamos el operador ILIKE de PostgreSQL para búsqueda case-insensitive
        response = requests.get(
            f"{POSTGREST_URL}/proyecto?or=(nombre_proyecto.ilike.*{termino}*,descripcion.ilike.*{termino}*,ubicacion.ilike.*{termino}*)",
            headers=headers,
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
    try:
        response = requests.get(f"{POSTGREST_URL}/ubicacion", headers=headers)
        response.raise_for_status()

        ubicaciones_data = response.json()
        ubicaciones = [Ubicacion.parse_obj(ubicacion) for ubicacion in ubicaciones_data]
        return ubicaciones
    except Exception as e:
        console.print(f"[bold red]Error al obtener ubicaciones: {e}[/bold red]")
        return []


def buscar_ubicaciones(termino: str) -> List[Ubicacion]:
    """Busca ubicaciones por provincia, distrito o distrito municipal"""
    try:
        response = requests.get(
            f"{POSTGREST_URL}/ubicacion?or=(provincia.ilike.*{termino}*,distrito.ilike.*{termino}*,distritomunicipal.ilike.*{termino}*)",
            headers=headers,
        )
        response.raise_for_status()

        ubicaciones_data = response.json()
        ubicaciones = [Ubicacion.parse_obj(ubicacion) for ubicacion in ubicaciones_data]
        return ubicaciones
    except Exception as e:
        console.print(f"[bold red]Error al buscar ubicaciones: {e}[/bold red]")
        return []
