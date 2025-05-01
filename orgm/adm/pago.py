import requests
import os
from orgm.apis.header import get_headers_json
from typing import Dict, List, Optional, Union
from rich.console import Console

console = Console()

def registrar_pago(
    id_cliente: int, 
    moneda: str, 
    monto: float, 
    fecha: str, 
    comprobante: str = ""
) -> Optional[Dict]:
    """
    Registra un nuevo pago en la base de datos.
    
    Args:
        id_cliente: ID del cliente al que pertenece el pago
        moneda: Moneda del pago (ej. RD$, USD)
        monto: Monto del pago
        fecha: Fecha del pago (formato YYYY-MM-DD)
        comprobante: Número de comprobante o referencia (opcional)
        
    Returns:
        Dict con los datos del pago registrado o None si hay error
    """
    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
        )
        return None
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    # Añadir header adicional para PostgREST
    headers["Prefer"] = "return=representation"
    
    # Datos del pago a registrar
    pago_data = {
        "id": obtener_id_maximo(),
        "id_cliente": id_cliente,
        "moneda": moneda,
        "monto": monto,
        "fecha": fecha,
        "comprobante": comprobante
    }
    
    try:
        response = requests.post(
            f"{POSTGREST_URL}/pagorecibido",
            json=pago_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()[0] if response.json() else None
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error HTTP al registrar pago: {e}[/bold red]")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error de conexión al registrar pago: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado al registrar pago: {e}[/bold red]")
        return None


def obtener_pagos(id_cliente: Optional[int] = None) -> List[Dict]:
    """
    Obtiene todos los pagos o los pagos de un cliente específico.
    
    Args:
        id_cliente: ID del cliente para filtrar los pagos (opcional)
        
    Returns:
        List[Dict]: Lista de pagos.
    """
    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
        )
        return []
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    
    try:
        url = f"{POSTGREST_URL}/pagorecibido"
        if id_cliente:
            url += f"?id_cliente=eq.{id_cliente}"
            
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error HTTP al obtener pagos: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error de conexión al obtener pagos: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado al obtener pagos: {e}[/bold red]")
        return []


def obtener_id_maximo() -> int:
    """
    Obtiene el ID máximo de la tabla pagorecibido.
    
    Returns:
        int: ID máximo.
    """

    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
        )
        return 0
    
    headers = get_headers_json()
    response = requests.get(f"{POSTGREST_URL}/pagorecibido?select=id", headers=headers)
    response.raise_for_status()
    pagos = response.json()
    return max(pago['id'] for pago in pagos) + 1 if pagos else 1

def asignar_pago_a_cotizacion(
    id_pago: int, 
    id_cotizacion: int, 
    monto: float
) -> Optional[Dict]:
    """
    Asigna un pago a una cotización específica.
    
    Args:
        id_pago: ID del pago a asignar
        id_cotizacion: ID de la cotización
        monto: Monto a asignar a esta cotización
        
    Returns:
        Dict con los datos de la asignación o None si hay error
    """
    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
        )
        return None
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    # Añadir header adicional para PostgREST
    headers["Prefer"] = "return=representation"
    
    # Datos de la asignación
    asignacion_data = {
        "id_pago": id_pago,
        "id_cotizacion": id_cotizacion,
        "monto": monto
    }
    
    try:
        response = requests.post(
            f"{POSTGREST_URL}/asignacionpago",
            json=asignacion_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()[0] if response.json() else None
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error HTTP al asignar pago: {e}[/bold red]")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error de conexión al asignar pago: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado al asignar pago: {e}[/bold red]")
        return None


def obtener_asignaciones_pago(id_cotizacion: Optional[int] = None) -> List[Dict]:
    """
    Obtiene todas las asignaciones de pago o las asignaciones de una cotización específica.
    
    Args:
        id_cotizacion: ID de la cotización para filtrar (opcional)
        
    Returns:
        List[Dict]: Lista de asignaciones de pago.
    """
    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
        )
        return []
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    
    try:
        url = f"{POSTGREST_URL}/asignacionpago"
        if id_cotizacion:
            url += f"?id_cotizacion=eq.{id_cotizacion}"
            
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error HTTP al obtener asignaciones: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error de conexión al obtener asignaciones: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado al obtener asignaciones: {e}[/bold red]")
        return [] 


if __name__ == "__main__":
    # Ejemplo de uso\
    id = obtener_id_maximo()
    # id_cliente = 3
    # moneda = "RD$"
    # monto = 140000.00
    # fecha = "2025-01-27"
    # comprobante = "1234567890"

    # registrar_pago(id_cliente, moneda, monto, fecha, comprobante)
    # pagos = obtener_pagos(id_cliente)
    # print(pagos)

