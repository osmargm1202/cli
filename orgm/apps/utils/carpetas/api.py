import requests
import json
from typing import Dict, List, Optional
from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console

console = Console()

def obtener_servicios() -> List[Dict]:
    """
    Obtiene todos los servicios disponibles desde la API de PostgREST.
    
    Returns:
        List[Dict]: Lista de servicios en formato diccionario
    """
    # Inicializar configuración de PostgREST
    postgrest_url, headers = initialize()
    
    if not postgrest_url:
        console.print("[bold red]Error: No se pudo inicializar la conexión a PostgREST[/bold red]")
        return []
    
    try:
        # Realizar solicitud GET a la tabla de servicios
        response = requests.get(
            f"{postgrest_url}/servicio?select=id,nombre",
            headers=headers
        )
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[bold red]Error al obtener servicios: {response.status_code} - {response.text}[/bold red]")
            return []
    except Exception as e:
        console.print(f"[bold red]Error en la solicitud: {str(e)}[/bold red]")
        return []


def obtener_datos_de_cotizacion(cotizacion_id: int) -> Optional[Dict]:
    """
    Obtiene el servicio asociado a una cotización específica.
    
    Args:
        cotizacion_id (int): ID de la cotización
        
    Returns:
        Optional[Dict]: Datos del servicio asociado a la cotización o None si no se encuentra
    """
    # Inicializar configuración de PostgREST
    postgrest_url, headers = initialize()
    
    if not postgrest_url:
        console.print("[bold red]Error: No se pudo inicializar la conexión a PostgREST[/bold red]")
        return None
    
    try:
        # Primero obtenemos la cotización para conseguir el id_servicio
        response_cotizacion = requests.get(
            f"{postgrest_url}/cotizacion?select=servicio(id,nombre),proyecto(id,nombre_proyecto)&id=eq.{cotizacion_id}",
            headers=headers
        )
        
        if response_cotizacion.status_code == 200:
            cotizaciones = response_cotizacion.json()
            if cotizaciones:
                return cotizaciones[0]
            else:
                console.print(f"[bold yellow]No se encontró cotización con ID {cotizacion_id}[/bold yellow]")
                return None
        else:
            console.print(f"[bold red]Error al obtener cotización: {response_cotizacion.status_code} - {response_cotizacion.text}[/bold red]")
            return None
    except Exception as e:
        console.print(f"[bold red]Error en la solicitud: {str(e)}[/bold red]")
        return None


def buscar_clientes(nombre: str) -> Optional[Dict]:
    """
    Busca un cliente por nombre.
    
    Args:
        nombre (str): Nombre del cliente a buscar
    
    Returns:
        Optional[Dict]: Datos del cliente o None si no se encuentra
    """
    # Inicializar configuración de PostgREST
    postgrest_url, headers = initialize()

    if not postgrest_url:
        console.print("[bold red]Error: No se pudo inicializar la conexión a PostgREST[/bold red]")
        return None
    
    try:
        # Realizar solicitud GET filtrando por nombre
        response = requests.get(
            f"{postgrest_url}/cliente?select=id,nombre,nombre_comercial&or=(nombre.ilike.%{nombre}%,nombre_comercial.ilike.%{nombre}%)",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[bold red]Error al obtener clientes: {response.status_code} - {response.text}[/bold red]")
            return None
    except Exception as e:
        console.print(f"[bold red]Error en la solicitud: {str(e)}[/bold red]")
        return None

def buscar_cotizaciones(cliente_id: int) -> Optional[Dict]:
    """
    Busca cotizaciones asociadas a un cliente específico.
    
    Args:
        cliente_id (int): ID del cliente a buscar
    
    Returns:
        Optional[Dict]: Datos de las cotizaciones o None si no se encuentra
    """
    # Inicializar configuración de PostgREST
    postgrest_url, headers = initialize()

    if not postgrest_url:
        console.print("[bold red]Error: No se pudo inicializar la conexión a PostgREST[/bold red]")
        return None
    
    try:
        # Realizar solicitud GET filtrando por cliente_id
        response = requests.get(
            f"{postgrest_url}/cotizacion?select=id,fecha,servicio(id,nombre),proyecto(id,nombre_proyecto)&id_cliente=eq.{cliente_id}&order=id.desc",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[bold red]Error al obtener cotizaciones: {response.status_code} - {response.text}[/bold red]")
            return None
    except Exception as e:
        console.print(f"[bold red]Error en la solicitud: {str(e)}[/bold red]")
        return None
    
if __name__ == "__main__":
    # print(obtener_servicios())
    print(obtener_datos_de_cotizacion(533))
    # print(buscar_clientes("dap"))
    # print(buscar_cotizaciones(3))