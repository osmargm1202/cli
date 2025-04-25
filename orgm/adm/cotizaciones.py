# -*- coding: utf-8 -*-
# NUEVO ARCHIVO: orgm/adm/cotizaciones.py
# Funciones para acceder a PostgREST relacionadas con las cotizaciones

import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
from rich.console import Console
from orgm.adm.db import Cotizacion
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


def obtener_cotizaciones(embed: bool = True):
    """Obtiene todas las cotizaciones.

    Si *embed* es ``True`` se solicitan los nombres de cliente, proyecto y servicio
    embebidos mediante PostgREST para evitar consultas adicionales.
    """
    try:
        select_clause = (
            "*,cliente(id,nombre),proyecto(id,nombre_proyecto),servicio(id,nombre)"
            if embed
            else "*"
        )
        url = f"{POSTGREST_URL}/cotizacion?select={select_clause}"
        with spinner("Obteniendo cotizaciones..."):
            response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()  # lista de dicts con datos embebidos
    except Exception as e:
        console.print(f"[bold red]Error al obtener cotizaciones: {e}[/bold red]")
        return []


def obtener_cotizacion(id_cotizacion: int) -> Optional[Cotizacion]:
    """Obtiene una cotización por su ID"""
    try:
        response = requests.get(
            f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}", headers=headers
        )
        response.raise_for_status()

        datos = response.json()
        if not datos:
            console.print(
                f"[yellow]No se encontró la cotización con ID {id_cotizacion}[/yellow]"
            )
            return None

        return Cotizacion.model_validate(datos[0])
    except Exception as e:
        console.print(
            f"[bold red]Error al obtener cotización {id_cotizacion}: {e}[/bold red]"
        )
        return None


def crear_cotizacion(cotizacion_data: Dict) -> Optional[Cotizacion]:
    """Crea una nueva cotización"""
    try:
        # Validar campos obligatorios mínimos
        for campo in ("id_cliente", "id_proyecto", "id_servicio"):
            if not cotizacion_data.get(campo):
                console.print(
                    f"[bold red]Error: El campo '{campo}' es obligatorio[/bold red]"
                )
                return None

        response = requests.post(
            f"{POSTGREST_URL}/cotizacion", headers=headers, json=cotizacion_data
        )
        response.raise_for_status()

        nueva = Cotizacion.model_validate(response.json()[0])
        console.print(
            f"[bold green]Cotización creada correctamente con ID: {nueva.id}[/bold green]"
        )
        return nueva
    except Exception as e:
        console.print(f"[bold red]Error al crear cotización: {e}[/bold red]")
        return None


def actualizar_cotizacion(id_cotizacion: int, cotizacion_data: Dict) -> Optional[Cotizacion]:
    """Actualiza una cotización existente"""
    try:
        # Verificar existencia
        existente = obtener_cotizacion(id_cotizacion)
        if not existente:
            return None

        update_headers = headers.copy()
        update_headers["Prefer"] = "return=representation"

        response = requests.patch(
            f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}",
            headers=update_headers,
            json=cotizacion_data,
        )
        response.raise_for_status()

        act = Cotizacion.model_validate(response.json()[0])
        console.print(
            f"[bold green]Cotización actualizada correctamente: ID {act.id}[/bold green]"
        )
        return act
    except Exception as e:
        console.print(
            f"[bold red]Error al actualizar cotización {id_cotizacion}: {e}[/bold red]"
        )
        return None


def eliminar_cotizacion(id_cotizacion: int) -> bool:
    """Elimina una cotización existente"""
    try:
        # Verificar existencia
        if not obtener_cotizacion(id_cotizacion):
            return False

        response = requests.delete(
            f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}", headers=headers
        )
        response.raise_for_status()

        console.print(
            f"[bold green]Cotización eliminada correctamente: ID {id_cotizacion}[/bold green]"
        )
        return True
    except Exception as e:
        console.print(
            f"[bold red]Error al eliminar cotización {id_cotizacion}: {e}[/bold red]"
        )
        return False


def buscar_cotizaciones(termino: str, embed: bool = True):
    """Busca cotizaciones filtrando por descripción, proyecto o cliente.

    Devuelve lista de dict con datos embebidos si *embed* es True.
    """
    try:
        select_clause = (
            "*,cliente(id,nombre),proyecto(id,nombre_proyecto),servicio(id,nombre)"
            if embed
            else "*"
        )
        url = (
            f"{POSTGREST_URL}/cotizacion?select={select_clause}&or=(descripcion.ilike.*{termino}*,cliente.nombre.ilike.*{termino}*,proyecto.nombre_proyecto.ilike.*{termino}*)"
            if embed
            else f"{POSTGREST_URL}/cotizacion?or=(descripcion.ilike.*{termino}*)"
        )
        with spinner("Buscando cotizaciones..."):
            resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json() if embed else [Cotizacion.model_validate(c) for c in resp.json()]
    except Exception as e:
        console.print(f"[bold red]Error al buscar cotizaciones: {e}[/bold red]")
        return []


# Nueva utilidad: obtener cotizaciones por cliente
def cotizaciones_por_cliente(id_cliente: int, limit: int = 10, embed: bool = True):
    """Devuelve cotizaciones de un cliente dado ordenadas por fecha descendente.

    Si *limit* es ``None`` se devuelven todas. Usa *embed* para incluir nombres.
    """
    try:
        select_clause = (
            "*,cliente(id,nombre),proyecto(id,nombre_proyecto),servicio(id,nombre)"
            if embed
            else "*"
        )
        url = f"{POSTGREST_URL}/cotizacion?select={select_clause}&id_cliente=eq.{id_cliente}&order=fecha.desc"
        if limit:
            url += f"&limit={limit}"
        with spinner("Obteniendo cotizaciones del cliente..."):
            resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json() if embed else [Cotizacion.model_validate(c) for c in resp.json()]
    except Exception as e:
        console.print(f"[bold red]Error al obtener cotizaciones del cliente: {e}[/bold red]")
        return []


if __name__ == "__main__":
    print(buscar_cotizaciones("memoria"))
