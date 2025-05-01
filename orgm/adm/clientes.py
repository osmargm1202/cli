# -*- coding: utf-8 -*-
from typing import Dict, List, Optional
from rich.console import Console
from orgm.adm.db import Cliente  # Importación a nivel de módulo para que otros módulos puedan acceder

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
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    # Añadir header adicional para PostgREST
    headers["Prefer"] = "return=representation"


def obtener_id_maximo() -> int:
    """
    Obtiene el ID máximo de la tabla cliente.
    
    Returns:
        int: ID máximo + 1 (siguiente ID disponible).
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    
    try:
        response = requests.get(f"{POSTGREST_URL}/cliente?select=id", headers=headers, timeout=10)
        response.raise_for_status()
        clientes = response.json()
        return max(cliente['id'] for cliente in clientes) + 1 if clientes else 1
    except Exception as e:
        console.print(f"[bold red]Error al obtener ID máximo de clientes: {e}[/bold red]")
        return 1


def obtener_clientes() -> List[Cliente]:
    """Obtiene todos los clientes desde PostgREST"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Cliente
    
    try:
        response = requests.get(f"{POSTGREST_URL}/cliente", headers=headers, timeout=10)
        response.raise_for_status()

        clientes_data = response.json()
        clientes = [Cliente.model_validate(cliente) for cliente in clientes_data]
        return clientes
    except Exception as e:
        console.print(f"[bold red]Error al obtener clientes: {e}[/bold red]")
        return []


def obtener_cliente(id_cliente: int) -> Optional[Cliente]:
    """Obtiene un cliente por su ID"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Cliente
    
    try:
        response = requests.get(
            f"{POSTGREST_URL}/cliente?id=eq.{id_cliente}", headers=headers, timeout=10
        )
        response.raise_for_status()

        clientes_data = response.json()
        if not clientes_data:
            console.print(
                f"[yellow]No se encontró el cliente con ID {id_cliente}[/yellow]"
            )
            return None

        cliente = Cliente.model_validate(clientes_data[0])
        return cliente
    except Exception as e:
        console.print(
            f"[bold red]Error al obtener cliente {id_cliente}: {e}[/bold red]"
        )
        return None


def crear_cliente(cliente_data: Dict) -> Optional[Cliente]:
    """Crea un nuevo cliente"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Cliente
    
    try:
        # Validar datos mínimos requeridos
        if not cliente_data.get("nombre"):
            console.print(
                "[bold red]Error: El nombre del cliente es obligatorio[/bold red]"
            )
            return None
            
        # Asignar ID si no está definido
        if "id" not in cliente_data:
            cliente_data["id"] = obtener_id_maximo()

        response = requests.post(
            f"{POSTGREST_URL}/cliente", headers=headers, json=cliente_data, timeout=10
        )
        response.raise_for_status()

        nuevo_cliente = Cliente.model_validate(response.json()[0])
        console.print(
            f"[bold green]Cliente creado correctamente con ID: {nuevo_cliente.id}[/bold green]"
        )
        return nuevo_cliente
    except Exception as e:
        console.print(f"[bold red]Error al crear cliente: {e}[/bold red]")
        return None


def actualizar_cliente(id_cliente: int, cliente_data: Dict) -> Optional[Cliente]:
    """Actualiza un cliente existente"""
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import requests
    from orgm.adm.db import Cliente
    
    try:
        # Verificar que el cliente existe
        cliente_existente = obtener_cliente(id_cliente)
        if not cliente_existente:
            return None

        update_headers = headers.copy()
        update_headers["Prefer"] = "return=representation"

        response = requests.patch(
            f"{POSTGREST_URL}/cliente?id=eq.{id_cliente}",
            headers=update_headers,
            json=cliente_data,
            timeout=10
        )
        response.raise_for_status()

        cliente_actualizado = Cliente.model_validate(response.json()[0])
        console.print(
            f"[bold green]Cliente actualizado correctamente: {cliente_actualizado.nombre}[/bold green]"
        )
        return cliente_actualizado
    except Exception as e:
        console.print(
            f"[bold red]Error al actualizar cliente {id_cliente}: {e}[/bold red]"
        )
        return None


def buscar_clientes(search_term=None) -> Optional[List[Cliente]]:
    """
    Returns the clients that match the search term
    """
    # Asegurar que las variables estén inicializadas
    if headers is None:
        initialize()
    
    import os
    import requests
    from orgm.adm.db import Cliente
    
    if not POSTGREST_URL:
        console.print(
            "[bold red]No se ha configurado la variable de entorno POSTGREST_URL[/bold red]"
        )
        return None

    search_term = search_term or ""
    try:
        response = requests.get(
            f"{POSTGREST_URL}/cliente?nombre=ilike.*{search_term}*",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        clientes_data = response.json()
        clientes = [Cliente.model_validate(cliente) for cliente in clientes_data]
        return clientes
    except Exception as e:
        console.print(f"[bold red]Error al buscar clientes: {e}[/bold red]")
        return None


def crear_cliente_ejemplo() -> Optional[Cliente]:
    """Crea un cliente de ejemplo para pruebas"""
    cliente_data = {
        "nombre": "Cliente de Prueba",
        "email": "cliente@ejemplo.com",
        "telefono": "+34 600 123 456",
        "direccion": "Calle Ejemplo 123, Ciudad Ejemplo",
        "notas": "Cliente creado para pruebas del sistema"
    }
    
    return crear_cliente(cliente_data)
