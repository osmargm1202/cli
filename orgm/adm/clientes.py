# -*- coding: utf-8 -*-
import os
import requests
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from orgm.adm.db import Cliente

console = Console()
load_dotenv(override=True)

# Obtener la URL de PostgREST desde las variables de entorno
POSTGREST_URL = os.getenv("POSTGREST_URL")
if not POSTGREST_URL:
    console.print("[bold red]Error: POSTGREST_URL no está definida en las variables de entorno[/bold red]")

# Configuración de los headers para PostgREST
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Prefer": "return=representation"
}

def obtener_clientes() -> List[Cliente]:
    """Obtiene todos los clientes desde PostgREST"""
    try:
        response = requests.get(f"{POSTGREST_URL}/cliente", headers=headers)
        response.raise_for_status()
        
        clientes_data = response.json()
        clientes = [Cliente.parse_obj(cliente) for cliente in clientes_data]
        return clientes
    except Exception as e:
        console.print(f"[bold red]Error al obtener clientes: {e}[/bold red]")
        return []

def obtener_cliente(id_cliente: int) -> Optional[Cliente]:
    """Obtiene un cliente por su ID"""
    try:
        response = requests.get(f"{POSTGREST_URL}/cliente?id=eq.{id_cliente}", headers=headers)
        response.raise_for_status()
        
        clientes_data = response.json()
        if not clientes_data:
            console.print(f"[yellow]No se encontró el cliente con ID {id_cliente}[/yellow]")
            return None
            
        cliente = Cliente.parse_obj(clientes_data[0])
        return cliente
    except Exception as e:
        console.print(f"[bold red]Error al obtener cliente {id_cliente}: {e}[/bold red]")
        return None

def crear_cliente(cliente_data: Dict) -> Optional[Cliente]:
    """Crea un nuevo cliente"""
    try:
        # Validar datos mínimos requeridos
        if not cliente_data.get("nombre"):
            console.print("[bold red]Error: El nombre del cliente es obligatorio[/bold red]")
            return None
            
        response = requests.post(
            f"{POSTGREST_URL}/cliente",
            headers=headers,
            json=cliente_data
        )
        response.raise_for_status()
        
        nuevo_cliente = Cliente.parse_obj(response.json()[0])
        console.print(f"[bold green]Cliente creado correctamente con ID: {nuevo_cliente.id}[/bold green]")
        return nuevo_cliente
    except Exception as e:
        console.print(f"[bold red]Error al crear cliente: {e}[/bold red]")
        return None

def actualizar_cliente(id_cliente: int, cliente_data: Dict) -> Optional[Cliente]:
    """Actualiza un cliente existente"""
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
            json=cliente_data
        )
        response.raise_for_status()
        
        cliente_actualizado = Cliente.parse_obj(response.json()[0])
        console.print(f"[bold green]Cliente actualizado correctamente: {cliente_actualizado.nombre}[/bold green]")
        return cliente_actualizado
    except Exception as e:
        console.print(f"[bold red]Error al actualizar cliente {id_cliente}: {e}[/bold red]")
        return None

def eliminar_cliente(id_cliente: int) -> bool:
    """Elimina un cliente existente"""
    try:
        # Verificar que el cliente existe
        cliente_existente = obtener_cliente(id_cliente)
        if not cliente_existente:
            return False
            
        response = requests.delete(
            f"{POSTGREST_URL}/cliente?id=eq.{id_cliente}",
            headers=headers
        )
        response.raise_for_status()
        
        console.print(f"[bold green]Cliente eliminado correctamente: ID {id_cliente}[/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]Error al eliminar cliente {id_cliente}: {e}[/bold red]")
        return False

def buscar_clientes(termino: str) -> List[Cliente]:
    """Busca clientes por nombre o número"""
    try:
        # Usamos el operador ILIKE de PostgreSQL para búsqueda case-insensitive
        response = requests.get(
            f"{POSTGREST_URL}/cliente?or=(nombre.ilike.*{termino}*,nombre_comercial.ilike.*{termino}*,numero.ilike.*{termino}*)",
            headers=headers
        )
        response.raise_for_status()
        
        clientes_data = response.json()
        clientes = [Cliente.parse_obj(cliente) for cliente in clientes_data]
        return clientes
    except Exception as e:
        console.print(f"[bold red]Error al buscar clientes: {e}[/bold red]")
        return [] 