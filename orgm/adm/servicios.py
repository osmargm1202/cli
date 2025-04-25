# -*- coding: utf-8 -*-
"""Funciones para acceder a datos de la tabla *servicio* en PostgREST."""

import os
import requests
from typing import List, Optional
from dotenv import load_dotenv
from rich.console import Console
from orgm.adm.db import Servicios
from orgm.stuff.spinner import spinner

console = Console()
load_dotenv(override=True)

POSTGREST_URL = os.getenv("POSTGREST_URL")
if not POSTGREST_URL:
    console.print(
        "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno[/bold red]"
    )

CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

headers = {"Content-Type": "application/json", "Accept": "application/json"}
if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
    headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
    headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET


def obtener_servicios() -> List[Servicios]:
    try:
        with spinner("Obteniendo servicios..."):
            resp = requests.get(f"{POSTGREST_URL}/servicio", headers=headers)
        resp.raise_for_status()
        return [Servicios.parse_obj(s) for s in resp.json()]
    except Exception as e:
        console.print(f"[bold red]Error al obtener servicios: {e}[/bold red]")
        return []


def obtener_servicio(id_servicio: int) -> Optional[Servicios]:
    try:
        resp = requests.get(f"{POSTGREST_URL}/servicio?id=eq.{id_servicio}", headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        return Servicios.parse_obj(data[0])
    except Exception as e:
        console.print(f"[bold red]Error al obtener servicio {id_servicio}: {e}[/bold red]")
        return None 