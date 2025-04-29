# -*- coding: utf-8 -*-
import os
import subprocess
import requests
import platform
from rich.console import Console

# Crear consola para salida con Rich
console = Console()

def print_comandos() -> None:
    """Imprimir lista de comandos disponibles desde un archivo markdown"""
    # Obtener la ruta al archivo comandos.md relativo a este archivo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    orgm_dir = os.path.dirname(script_dir)  # Subir un nivel a orgm/
    comandos_path = os.path.join(orgm_dir, "comandos.md")
    try:
        with open(comandos_path, "r", encoding="utf-8") as f:
            comandos = f.read()
        console.print(comandos)
    except FileNotFoundError:
        console.print(f"[bold red]Error: Archivo comandos.md no encontrado en {comandos_path}[/bold red]")

def help_command() -> None:
    """Muestra la ayuda con la lista de comandos disponibles"""
    print_comandos()

def check_urls() -> None:
    """Verifica rápidamente la accesibilidad de URLs clave definidas en variables de entorno."""
    endpoints = {
        "POSTGREST_URL": os.getenv("POSTGREST_URL"),
        "API_URL": os.getenv("API_URL"),
    }

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

def update() -> None:
    """Actualizar el paquete de ORGM CLI"""
    console.print("Actualizando paquete de ORGM CLI")

    # Detect platform and delegate to update.bat on Windows
    if platform.system() == "Windows":
        # Asumimos que update.bat está en el mismo directorio que orgm.py
        # La estructura exacta podría necesitar ajuste
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Sube a orgm/
        bat_path = os.path.join(script_dir, "update.bat")
        try:
            console.print("Sistema Windows detectado. Ejecutando update.bat...")
            subprocess.check_call([bat_path], shell=True)
        except subprocess.CalledProcessError as e:
            console.print(f"Error al ejecutar update.bat: {e}")
        except FileNotFoundError:
             console.print(f"[bold red]Error: update.bat no encontrado en {bat_path}[/bold red]")
        return

    try:
        # Obtener la rama específica del entorno si está configurada
        branch = os.getenv(
            "GIT_BRANCH", "master"
        )  # Default a 'master' si no está especificada
        git_url_base = os.getenv('GIT_URL')
        if not git_url_base:
            console.print("[bold red]Error: GIT_URL no está definida en las variables de entorno.[/bold red]")
            return
            
        git_url = f"{git_url_base}@{branch}"

        # Primero desinstalar el paquete
        console.print("Desinstalando versión actual...")
        subprocess.check_call(
            [
                "uv",
                "tool",
                "uninstall",
                "orgm",
            ]
        )

        # Luego instalar la nueva versión
        console.print(f"Instalando nueva versión desde la rama {branch}...")
        subprocess.check_call(
            [
                "uv",
                "tool",
                "install",
                "--force",
                f"git+{git_url}",
            ]
        )
        console.print(f"Paquete instalado correctamente desde la rama {branch}.")
    except subprocess.CalledProcessError as e:
        console.print(f"Error al actualizar el paquete: {e}")

def install() -> None:
    """Instalar el paquete de ORGM CLI"""
    console.print("Instalando paquete de ORGM CLI")

    try:
        # Obtener la rama específica del entorno si está configurada
        branch = os.getenv(
            "GIT_BRANCH", "master"
        )  # Default a 'master' si no está especificada
        git_url_base = os.getenv('GIT_URL')
        if not git_url_base:
            console.print("[bold red]Error: GIT_URL no está definida en las variables de entorno.[/bold red]")
            return

        git_url = f"{git_url_base}@{branch}"

        console.print(f"Instalando desde la rama {branch}...")
        subprocess.check_call(
            [
                "uv",
                "tool",
                "install",
                "--force",
                f"git+{git_url}",
            ]
        )
        console.print(f"Paquete instalado correctamente desde la rama {branch}.")
    except subprocess.CalledProcessError as e:
        console.print(f"Error al instalar el paquete: {e}") 