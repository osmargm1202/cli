# -*- coding: utf-8 -*-
"""Funciones para acceder a datos de la tabla *servicio* en PostgREST."""

from typing import Dict, List, Optional
from rich.console import Console
from orgm.adm.db import Servicios  # Importación a nivel de módulo para que otros módulos puedan acceder

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
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
        )
        return False
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    # Añadir header adicional para PostgREST
    headers["Prefer"] = "return=representation"
    
    return True


def obtener_servicios() -> List[Dict]:
    """
    Obtiene la lista de servicios desde PostgREST.

    Returns:
        List[Dict]: Lista de servicios en formato dict.
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
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
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
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
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    datos_servicio = {
        "id": obtener_id_maximo_servicios(),
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


def obtener_id_maximo_servicios() -> int:
    """
    Obtiene el ID máximo de la tabla servicio.

    Returns:
        int: ID máximo.
    """
    if headers is None:
        initialize()

    import requests

    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
        )
        return 0
    
    response = requests.get(f"{POSTGREST_URL}/servicio?select=id", headers=headers)
    response.raise_for_status()
    servicios = response.json()
    return max(servicio['id'] for servicio in servicios) + 1 if servicios else 1

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
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
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
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
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
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
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