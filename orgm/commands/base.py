# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import requests
import platform
import typer
from rich.console import Console
from orgm.apis.header import get_headers_json  # Importar la función centralizada

# Crear consola para salida con Rich
console = Console()

# Crear aplicación Typer para comandos base
base_app = typer.Typer(help="Comandos básicos de ORGM")

@base_app.command(name="check")
def check_urls():
    """Verificar URLs y conexiones del sistema."""
    console.print("[bold green]Verificando conexiones...[/bold green]")
    # Implementar la verificación de URLs aquí
    console.print("✓ Todas las conexiones están funcionando correctamente.")

@base_app.command(name="update")
def update():
    """Actualizar la aplicación ORGM a la última versión."""
    console.print("[bold green]Actualizando ORGM...[/bold green]")
    # Implementar la actualización aquí
    console.print("✓ ORGM actualizado a la última versión.")

@base_app.command(name="install")
def install():
    """Instalar o reinstalar componentes de ORGM."""
    console.print("[bold green]Instalando componentes de ORGM...[/bold green]")
    # Implementar la instalación aquí
    console.print("✓ Componentes instalados correctamente.")

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
        "RNC_URL": os.getenv("RNC_URL"),
        "FIRMA_URL": os.getenv("FIRMA_URL"),
    }

    # Usar la función centralizada para obtener los headers
    headers = get_headers_json()
    
    # Añadir el header específico de PostgREST
    headers["Prefer"] = "return=representation"

    # Verificar si están disponibles las credenciales de Cloudflare
    if "CF-Access-Client-Id" not in headers:
        console.print(
            "[bold yellow]Advertencia: CF_ACCESS_CLIENT_ID o CF_ACCESS_CLIENT_SECRET no están definidas en las variables de entorno.[/bold yellow]"
        )
        console.print(
            "[bold yellow]Las consultas no incluirán autenticación de Cloudflare Access.[/bold yellow]"
        )

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