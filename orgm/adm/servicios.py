# -*- coding: utf-8 -*-
"""Funciones para acceder a datos de la tabla *servicio* en PostgREST."""

import os
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
from rich.console import Console
from orgm.adm.db import Servicios

console = Console()

# Load environment variables
load_dotenv(override=True)

# Get the PostgREST URL from environment variables
POSTGREST_URL = os.getenv("POSTGREST_URL")

# Get Cloudflare Access credentials
CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

if not POSTGREST_URL:
    console.print(
        "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
    )
    exit(1)

if not all([CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET]):
    console.print(
        "[bold yellow]Advertencia: CF_ACCESS_CLIENT_ID o CF_ACCESS_CLIENT_SECRET no están definidas en las variables de entorno.[/bold yellow]"
    )
    console.print(
        "[bold yellow]Las consultas a PostgREST no incluirán autenticación de Cloudflare Access.[/bold yellow]"
    )

# Configure headers for PostgREST API
headers = {"Content-Type": "application/json", "Accept": "application/json"}

# Add Cloudflare Access headers if available
if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
    headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
    headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET


def obtener_servicios() -> List[Dict]:
    """
    Obtiene la lista de servicios desde PostgREST.

    Returns:
        List[Dict]: Lista de servicios en formato dict.
    """
    try:
        response = requests.get(f"{POSTGREST_URL}/servicio", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al obtener servicios: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []


def obtener_servicio(servicio_id: int) -> Optional[Dict]:
    """
    Obtiene los detalles de un servicio específico.

    Args:
        servicio_id (int): ID del servicio a obtener.

    Returns:
        Optional[Dict]: Detalles del servicio o None si no se encuentra.
    """
    try:
        response = requests.get(
            f"{POSTGREST_URL}/servicio?id=eq.{servicio_id}", headers=headers, timeout=10
        )
        response.raise_for_status()
        servicios = response.json()
        return servicios[0] if servicios else None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al obtener servicio: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None


def crear_servicio(
    concepto: str, descripcion: str, tiempo: float, coste: float
) -> Optional[Dict]:
    """
    Crea un nuevo servicio en PostgREST.

    Args:
        concepto (str): Concepto del servicio.
        descripcion (str): Descripción detallada del servicio.
        tiempo (float): Tiempo estimado para el servicio (en horas).
        coste (float): Coste del servicio.

    Returns:
        Optional[Dict]: Servicio creado o None si hay un error.
    """
    datos_servicio = {
        "concepto": concepto,
        "descripcion": descripcion,
        "tiempo": tiempo,
        "coste": coste,
    }

    try:
        response = requests.post(
            f"{POSTGREST_URL}/servicio",
            json=datos_servicio,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()[0] if response.json() else None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al crear servicio: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None


def actualizar_servicio(
    servicio_id: int,
    concepto: Optional[str] = None,
    descripcion: Optional[str] = None,
    tiempo: Optional[float] = None,
    coste: Optional[float] = None,
) -> bool:
    """
    Actualiza un servicio existente en PostgREST.

    Args:
        servicio_id (int): ID del servicio a actualizar.
        concepto (Optional[str], optional): Nuevo concepto. Defaults to None.
        descripcion (Optional[str], optional): Nueva descripción. Defaults to None.
        tiempo (Optional[float], optional): Nuevo tiempo estimado. Defaults to None.
        coste (Optional[float], optional): Nuevo coste. Defaults to None.

    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.
    """
    # Crear un diccionario con los datos a actualizar
    datos_actualizacion = {}
    if concepto is not None:
        datos_actualizacion["concepto"] = concepto
    if descripcion is not None:
        datos_actualizacion["descripcion"] = descripcion
    if tiempo is not None:
        datos_actualizacion["tiempo"] = tiempo
    if coste is not None:
        datos_actualizacion["coste"] = coste

    # Si no hay datos para actualizar, retornar True
    if not datos_actualizacion:
        return True

    try:
        response = requests.patch(
            f"{POSTGREST_URL}/servicio?id=eq.{servicio_id}",
            json=datos_actualizacion,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al actualizar servicio: {e}[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return False


def eliminar_servicio(servicio_id: int) -> bool:
    """
    Elimina un servicio de PostgREST.

    Args:
        servicio_id (int): ID del servicio a eliminar.

    Returns:
        bool: True si la eliminación fue exitosa, False en caso contrario.
    """
    try:
        response = requests.delete(
            f"{POSTGREST_URL}/servicio?id=eq.{servicio_id}", headers=headers, timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al eliminar servicio: {e}[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return False


def buscar_servicios(termino: str) -> List[Dict]:
    """
    Busca servicios que coincidan con el término proporcionado.

    Args:
        termino (str): Término de búsqueda.

    Returns:
        List[Dict]: Lista de servicios coincidentes.
    """
    try:
        # Construir una consulta SQL para búsqueda en texto
        response = requests.get(
            f"{POSTGREST_URL}/servicio?or=(concepto.ilike.*{termino}*,descripcion.ilike.*{termino}*)",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al buscar servicios: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return [] 