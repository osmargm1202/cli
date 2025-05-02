# -*- coding: utf-8 -*-
import os
import requests
import typer
from rich.console import Console
from orgm.apis.header import get_headers_json  # Importar la función centralizada


console = Console()


def check_urls() -> None:
    """Verifica rápidamente la accesibilidad de URLs clave definidas en variables de entorno."""
    endpoints = {
        "POSTGREST_URL": os.getenv("POSTGREST_URL"),
        "API_URL": os.getenv("API_URL"),
        "RNC_URL": os.getenv("RNC_URL"),
        "FIRMA_URL": os.getenv("FIRMA_URL"),
    }

    # Usar la función centralizada para obtener los headers
    headers = get_headers_json()
    headers["Prefer"] = "return=representation"

    for name, url in endpoints.items():
        if not url:
            console.print(f"[yellow]{name} no configurada[/yellow]")
            continue
        try:
            resp = requests.get(url, headers=headers, timeout=1)
            if resp.status_code < 400:
                console.print(f"[bold green]{name} OK[/bold green] → {url}")
            else:
                console.print(f"[bold red]{name} ERROR {resp.status_code}[/bold red] → {url}")
        except Exception as e:
            console.print(f"[bold red]{name} inaccesible:[/bold red] {e} → {url}")