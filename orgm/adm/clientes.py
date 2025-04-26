# -*- coding: utf-8 -*-
import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
from rich.console import Console
from orgm.adm.db import Cliente




console = Console()
load_dotenv(override=True)

# Inicializar estas variables a nivel de módulo
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


def obtener_clientes() -> List[Cliente]:
    """Obtiene todos los clientes desde PostgREST"""
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
    try:
        # Validar datos mínimos requeridos
        if not cliente_data.get("nombre"):
            console.print(
                "[bold red]Error: El nombre del cliente es obligatorio[/bold red]"
            )
            return None

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



def buscar_clientes(search_term=None):
    """
    Returns the clients that match the search term
    """
    env_url = os.environ.get("POSTGREST_URL")
    if not env_url:
        console.print(
            "[bold red]No se ha configurado la variable de entorno POSTGREST_URL[/bold red]"
        )
        return None

    search_term = search_term or ""
    try:
        response = requests.get(
            f"{env_url}/cliente?nombre=ilike.*{search_term}*",
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
