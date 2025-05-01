# -*- coding: utf-8 -*-
# NUEVO ARCHIVO: orgm/adm/cotizaciones.py
# Funciones para acceder a PostgREST relacionadas con las cotizaciones

from typing import Dict, List, Optional, Union
from rich.console import Console
from orgm.adm.db import Cotizacion  # Importación a nivel de módulo para que otros módulos puedan acceder

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
    # Añadir header adicional para PostgREST
    headers["Prefer"] = "return=representation"
    
    return True


def obtener_id_maximo() -> int:
    """
    Obtiene el ID máximo de la tabla cotizacion.
    
    Returns:
        int: ID máximo + 1 (siguiente ID disponible).
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        response = requests.get(f"{POSTGREST_URL}/cotizacion?select=id", headers=headers)
        response.raise_for_status()
        cotizaciones = response.json()
        return max(cotizacion['id'] for cotizacion in cotizaciones) + 1 if cotizaciones else 1
    except Exception as e:
        console.print(f"[bold red]Error al obtener ID máximo de cotizaciones: {e}[/bold red]")
        return 1


def obtener_cotizaciones() -> List[Dict]:
    """
    Obtiene todas las cotizaciones.
    
    Returns:
        List[Dict]: Lista de cotizaciones.
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        response = requests.get(f"{POSTGREST_URL}/cotizacion", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []


def obtener_cotizacion(id_cotizacion: int) -> Optional[Dict]:
    """
    Obtiene una cotización específica por su ID.
    
    Args:
        id_cotizacion (int): ID de la cotización a buscar.
        
    Returns:
        Optional[Dict]: Datos de la cotización o None si no se encuentra.
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        response = requests.get(
            f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}", headers=headers
        )
        response.raise_for_status()
        result = response.json()
        return result[0] if result else None
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None


def crear_cotizacion(datos: Dict) -> Optional[Dict]:
    """
    Crea una nueva cotización.
    
    Args:
        datos (Dict): Datos de la cotización a crear.
        
    Returns:
        Optional[Dict]: Cotización creada o None si falla.
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from datetime import datetime
    
    try:
        # Asegurar que tenga fecha de creación
        if "fecha_creacion" not in datos:
            datos["fecha_creacion"] = datetime.now().isoformat()
            
        # Asignar ID si no está definido
        if "id" not in datos:
            datos["id"] = obtener_id_maximo()
            
        response = requests.post(f"{POSTGREST_URL}/cotizacion", json=datos, headers=headers)
        response.raise_for_status()
        return response.json()[0] if response.json() else None
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None


def actualizar_cotizacion(id_cotizacion: int, datos: Dict) -> bool:
    """
    Actualiza una cotización existente.
    
    Args:
        id_cotizacion (int): ID de la cotización a actualizar.
        datos (Dict): Nuevos datos para la cotización.
        
    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        # Remover id si está en los datos para evitar conflictos
        if "id" in datos:
            del datos["id"]
            
        response = requests.patch(
            f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}", 
            json=datos, 
            headers=headers
        )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return False
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return False


def eliminar_cotizacion(id_cotizacion: int) -> bool:
    """
    Elimina una cotización.
    
    Args:
        id_cotizacion (int): ID de la cotización a eliminar.
        
    Returns:
        bool: True si la eliminación fue exitosa, False en caso contrario.
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        response = requests.delete(
            f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}", 
            headers=headers
        )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return False
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return False


def buscar_cotizaciones(termino: str) -> List[Dict]:
    """
    Busca cotizaciones que coincidan con el término de búsqueda.
    
    Args:
        termino (str): Término de búsqueda.
        
    Returns:
        List[Dict]: Lista de cotizaciones que coinciden con la búsqueda.
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        # Buscar en varios campos
        query = f"?or=(numero.ilike.*{termino}*,descripcion.ilike.*{termino}*)"
        response = requests.get(f"{POSTGREST_URL}/cotizacion{query}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []


def cotizaciones_por_cliente(id_cliente: int, limite: Optional[int] = None) -> List[Dict]:
    """
    Obtiene las cotizaciones de un cliente específico.
    
    Args:
        id_cliente (int): ID del cliente.
        limite (Optional[int]): Límite de resultados a devolver.
        
    Returns:
        List[Dict]: Lista de cotizaciones del cliente.
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        # Construir la URL con el ID del cliente
        url = f"{POSTGREST_URL}/cotizacion?id_cliente=eq.{id_cliente}"
        
        # Agregar límite si se especifica
        if limite is not None:
            url += f"&limit={limite}"
            
        # Ordenar por fecha de creación descendente
        url += "&order=fecha.desc"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []


def mostrar_tabla_cotizaciones(cotizaciones: List[Dict]) -> None:
    """
    Muestra una tabla con las cotizaciones.
    
    Args:
        cotizaciones (List[Dict]): Lista de cotizaciones para mostrar.
    """
    from datetime import datetime
    from rich.table import Table
    
    if not cotizaciones:
        console.print("[bold yellow]No se encontraron cotizaciones.[/bold yellow]")
        return
        
    tabla = Table(title="Cotizaciones", show_header=True)
    tabla.add_column("ID", style="dim")
    tabla.add_column("Número", style="green")
    tabla.add_column("Cliente", style="blue")
    tabla.add_column("Estado", style="magenta")
    tabla.add_column("Fecha", style="cyan")
    tabla.add_column("Total", style="yellow", justify="right")
    
    for cot in cotizaciones:
        # Formatear fecha
        fecha = cot.get("fecha_creacion", "")
        if fecha:
            try:
                fecha_obj = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
                fecha_form = fecha_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                fecha_form = fecha
        else:
            fecha_form = ""
            
        # Formatear total
        total = cot.get("total", 0)
        total_form = f"{total:,.2f} €" if total is not None else ""
        
        tabla.add_row(
            str(cot.get("id", "")),
            cot.get("numero", ""),
            cot.get("cliente_nombre", ""),
            cot.get("estado", ""),
            fecha_form,
            total_form
        )
    
    console.print(tabla)


def crear_cotizacion_ejemplo(id_cliente=1):
    """Crea una cotización de ejemplo para pruebas"""
    from datetime import datetime
    
    cotizacion_data = {
        "cliente_id": id_cliente,
        "numero": f"COT-{datetime.now().strftime('%Y%m%d-%H%M')}",
        "descripcion": "Cotización de prueba creada automáticamente",
        "total": 1500.50,
        "estado": "PENDIENTE",
        "fecha_creacion": datetime.now().isoformat()
    }
    
    return crear_cotizacion(cotizacion_data)
