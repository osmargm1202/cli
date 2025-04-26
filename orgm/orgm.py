# -*- coding: utf-8 -*-
import os
import subprocess
import requests
import json
import platform
import sys
from typing import List, Optional, Any, Dict
from pathlib import Path

import typer
from rich.console import Console
from dotenv import load_dotenv
import questionary

# Importaciones de otros módulos (se mantendrán igual)
from orgm.stuff.variables import edit_env_variables
from orgm.adm.firma import firmar_pdf, seleccionar_y_firmar_pdf
from orgm.apps.clientes import clientes
from orgm.apps.proyectos import proyecto
from orgm.apps.cotizaciones import cotizacion
from orgm.stuff.docker_cli import docker as docker_cmd
from orgm.stuff.ai import generate_text

# Crear consola para salida con Rich
console = Console()

# Clase personalizada para manejar la salida de los comandos
class SalirException(Exception):
    """Excepción personalizada para salir del programa."""
    pass

# Clase principal que maneja la aplicación CLI
class OrgmCLI:
    def __init__(self):
        # Crear la aplicación Typer
        self.app = typer.Typer(help="ORGM CLI - Herramienta de gestión organizacional")
        self.env_app = typer.Typer(help="Administrar variables de entorno")
        self.pdf_app = typer.Typer(help="Operaciones con archivos PDF")
        self.ai_app = typer.Typer(help="Operaciones relacionadas con la IA")
        
        # Configurar subcomandos
        self.app.add_typer(self.env_app, name="env")
        self.app.add_typer(self.pdf_app, name="pdf")
        self.app.add_typer(self.ai_app, name="ai")
        
        # Configurar comandos individuales
        self.configurar_comandos()
        
        
        # Cargar variables de entorno
        self.cargar_variables_entorno()

    def cargar_variables_entorno(self) -> None:
        """Cargar variables de entorno desde un archivo .env"""
        load_dotenv(override=True)
    
    def configurar_comandos(self) -> None:
        """Configurar todos los comandos de la aplicación"""
        # Comandos principales
        self.app.command(name="help")(self.help_command)
        self.app.command(name="check")(self.check_urls)
        self.app.command(name="update")(self.update)
        self.app.command(name="install")(self.install)
        
        # Comandos de env
        self.env_app.command(name="edit")(self.env_edit)
        self.env_app.command(name="file")(self.env_file)
        
        # Comandos de PDF
        self.pdf_app.command(name="firmar-archivo")(self.pdf_firmar)
        self.pdf_app.command(name="firmar")(self.pdf_firmar_interactivo)
        
        # Comandos de AI
        self.ai_app.command(name="prompt")(self.ai_prompt)
        self.ai_app.command(name="configs")(self.ai_configs)
        self.ai_app.command(name="config-upload")(self.ai_config_upload)
    
    def print_comandos(self) -> None:
        """Imprimir lista de comandos disponibles desde un archivo markdown"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        comandos_path = os.path.join(script_dir, "comandos.md")
        try:
            with open(comandos_path, "r", encoding="utf-8") as f:
                comandos = f.read()
            console.print(comandos)
        except FileNotFoundError:
            console.print("[bold red]Error: Archivo comandos.md no encontrado[/bold red]")
    
    def help_command(self) -> None:
        """Muestra la ayuda con la lista de comandos disponibles"""
        self.print_comandos()

    def check_urls(self) -> None:
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

    def update(self) -> None:
        """Actualizar el paquete de ORGM CLI"""
        console.print("Actualizando paquete de ORGM CLI")

        # Detect platform and delegate to update.bat on Windows
        if platform.system() == "Windows":
            bat_path = os.path.join(os.path.dirname(__file__), "update.bat")
            try:
                console.print("Sistema Windows detectado. Ejecutando update.bat...")
                subprocess.check_call([bat_path], shell=True)
            except subprocess.CalledProcessError as e:
                console.print(f"Error al ejecutar update.bat: {e}")
            return

        try:
            # Obtener la rama específica del entorno si está configurada
            branch = os.getenv(
                "GIT_BRANCH", "master"
            )  # Default a 'main' si no está especificada
            git_url = f"{os.getenv('GIT_URL')}@{branch}"

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

    def install(self) -> None:
        """Instalar el paquete de ORGM CLI"""
        console.print("Instalando paquete de ORGM CLI")

        try:
            # Obtener la rama específica del entorno si está configurada
            branch = os.getenv(
                "GIT_BRANCH", "master"
            )  # Default a 'master' si no está especificada
            git_url = f"{os.getenv('GIT_URL')}@{branch}"

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

    def env_edit(self) -> None:
        """Editar variables de entorno en una interfaz TUI"""
        console.print("Abriendo editor de variables de entorno...")
        edit_env_variables()

    def env_file(self, archivo: str = typer.Argument(..., help="Ruta al archivo a cargar")) -> None:
        """Leer un archivo y guardarlo como .env"""
        try:
            archivo_path = Path(archivo)
            if not archivo_path.exists():
                console.print(f"[bold red]Error: El archivo '{archivo}' no existe[/bold red]")
                return
                
            with open(archivo_path, "r", encoding="utf-8") as f:
                contenido = f.read()

            with open(".env", "w", encoding="utf-8") as f:
                f.write(contenido)

            console.print(f"[bold green]Archivo '{archivo}' guardado como .env[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error al procesar el archivo: {e}[/bold red]")

    def pdf_firmar(
        self, 
        archivo_pdf: str = typer.Argument(..., help="Ruta al archivo PDF a firmar"), 
        x_pos: int = typer.Option(..., "--x", "-x", help="Posición X donde colocar la firma"),
        y_pos: int = typer.Option(..., "--y", "-y", help="Posición Y donde colocar la firma"),
        ancho: int = typer.Option(..., "--ancho", "-a", help="Ancho de la firma"),
        salida: Optional[str] = typer.Option(None, "--salida", "-s", help="Nombre del archivo de salida")
    ) -> None:
        """Firma un archivo PDF"""
        try:
            archivo_path = Path(archivo_pdf)
            if not archivo_path.exists():
                console.print(f"[bold red]Error: El archivo '{archivo_pdf}' no existe[/bold red]")
                return
                
            resultado = firmar_pdf(archivo_pdf, x_pos, y_pos, ancho, salida)
            if resultado:
                console.print(f"[bold green]Archivo firmado: {resultado}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error al firmar el PDF: {e}[/bold red]")

    def pdf_firmar_interactivo(
        self,
        x_pos: int = typer.Option(100, "--x", "-x", help="Posición X donde colocar la firma (default: 100)"),
        y_pos: int = typer.Option(100, "--y", "-y", help="Posición Y donde colocar la firma (default: 100)"),
        ancho: int = typer.Option(200, "--ancho", "-a", help="Ancho de la firma (default: 200)")
    ) -> None:
        """Firma un archivo PDF de forma interactiva utilizando un selector de archivos"""
        try:
            resultado = seleccionar_y_firmar_pdf(x_pos, y_pos, ancho)
            if resultado:
                console.print(f"[bold green]Archivo firmado: {resultado}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error al firmar el PDF: {e}[/bold red]")

    def ai_prompt(
        self,
        prompt: List[str] = typer.Argument(..., help="Texto que describe la solicitud a la IA"),
        config_name: str = typer.Option("default", "--config", "-c", help="Nombre de la configuración del modelo IA")
    ) -> None:
        """Genera texto usando el servicio de IA"""
        # Unir el prompt que puede venir en múltiples palabras
        prompt_text = " ".join(prompt).strip()

        if not prompt_text:
            console.print("[bold red]Debe proporcionar un texto de entrada para la IA.[/bold red]")
            return

        resultado = generate_text(prompt_text, config_name)
        if resultado:
            # Mostrar la respuesta devuelta por la IA progresivamente para simular streaming
            from time import sleep
            console.print("[bold green]Respuesta IA:[/bold green] ", end="", flush=True)
            for char in str(resultado):
                print(char, end="", flush=True)  # imprime carácter por carácter
                sleep(0.01)  # pequeño retraso para el efecto de aparición
            print()  # nueva línea al finalizar

    def ai_configs(self) -> None:
        """Lista las configuraciones disponibles en el servicio de IA"""
        API_URL = os.getenv("API_URL")
        if not API_URL:
            console.print("[bold red]Error: API_URL no está definida en las variables de entorno.[/bold red]")
            return

        # Obtener credenciales de Cloudflare Access
        CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
        CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

        # Configuración de los headers para la API
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Agregar headers de Cloudflare Access si están disponibles
        if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
            headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
            headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET

        try:
            response = requests.get(f"{API_URL}/configs", headers=headers, timeout=10)
            response.raise_for_status()
            
            configs = response.json()
            console.print("[bold green]Configuraciones disponibles:[/bold green]")
            for config in configs:
                console.print(f"  - {config}")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Error al comunicarse con el servicio: {e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Error al procesar la respuesta: {e}[/bold red]")

    def ai_config_upload(
        self,
        config_name: str = typer.Argument(..., help="Nombre de la configuración a subir"),
        config_file: str = typer.Argument(..., help="Ruta al archivo JSON que contiene la configuración")
    ) -> None:
        """Carga una configuración desde un archivo JSON al servicio de IA"""
        API_URL = os.getenv("API_URL")
        if not API_URL:
            console.print("[bold red]Error: API_URL no está definida en las variables de entorno.[/bold red]")
            return

        # Verificar si el archivo existe
        config_path = Path(config_file)
        if not config_path.exists():
            console.print(f"[bold red]Error: El archivo '{config_file}' no existe[/bold red]")
            return

        # Obtener credenciales de Cloudflare Access
        CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
        CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

        # Configuración de los headers para la API
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Agregar headers de Cloudflare Access si están disponibles
        if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
            headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
            headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET

        try:
            # Cargar el archivo JSON
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            response = requests.post(
                f"{API_URL}/configs/{config_name}", 
                json=config_data, 
                headers=headers, 
                timeout=10
            )
            response.raise_for_status()
            
            console.print(f"[bold green]Configuración '{config_name}' subida correctamente.[/bold green]")
        except json.JSONDecodeError:
            console.print(f"[bold red]Error: El archivo '{config_file}' no contiene JSON válido.[/bold red]")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Error al comunicarse con el servicio: {e}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]Error al procesar la solicitud: {e}[/bold red]")

# Inicializar y ejecutar la CLI
def main():
    # Crear instancia de la CLI
    cli = OrgmCLI()
    # Ejecutar la aplicación Typer y manejar interrupciones de usuario
    try:
        cli.app()
    except (KeyboardInterrupt, EOFError):
        console.print("[bold yellow]Saliendo...[/bold yellow]")
        sys.exit(0)

if __name__ == "__main__":
    main() 