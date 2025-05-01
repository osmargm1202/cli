# -*- coding: utf-8 -*-
# Main ORGM CLI application
import os
import sys
import typer
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from typing import List, Optional

# Importar los grupos de comandos de las aplicaciones
from orgm.apps.clientes import clientes as clientes_app
from orgm.apps.proyectos import proyecto as proyecto_app
from orgm.apps.cotizaciones import cotizacion as cotizacion_app
from orgm.apps.docker import docker as docker_app
from orgm.apps.rnc_app import rnc_app

# Importar los typer apps para los módulos
from orgm.apps.env_app import env_app, env_menu
from orgm.apps.pdf_app import pdf_app, pdf_menu
from orgm.apps.ai_app import ai_app, ai_menu
from orgm.apps.pago_app import pago_app, pago_menu

# Importar comandos básicos
from orgm.commands.base import base_app
# Importar comandos de API
from orgm.commands.api_commands import api_app

# Importar el menú principal
from orgm.commands.menu import menu_principal

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
        self.app = typer.Typer(
            context_settings={"help_option_names": ["-h", "--help"]},
            no_args_is_help=False, # Evita la ayuda predeterminada de Typer sin argumentos
            add_completion=True # Opcional: deshabilitar la autocompletación si no se usa
        )
        
        # Añadir todos los módulos usando add_typer
        self.app.add_typer(env_app, name="env")
        self.app.add_typer(pdf_app, name="pdf")
        self.app.add_typer(ai_app, name="ai")
        self.app.add_typer(pago_app, name="payment")
        self.app.add_typer(clientes_app, name="client")
        self.app.add_typer(proyecto_app, name="project")
        self.app.add_typer(cotizacion_app, name="quotation")
        self.app.add_typer(docker_app, name="docker")
        self.app.add_typer(base_app, name="base")
        self.app.add_typer(api_app, name="api")
        
        # Configurar el callback principal
        self.configurar_callback()
        
        # Cargar variables de entorno
        self.cargar_variables_entorno()

    def configurar_callback(self) -> None:
        """Configura el callback principal para mostrar el menú interactivo."""
        @self.app.callback(invoke_without_command=True)
        def main_callback(ctx: typer.Context):
            """
            Si no se invoca ningún subcomando, muestra el menú interactivo.
            """
            if ctx.invoked_subcommand is None:
                while True:
                    # Mostrar el menú interactivo
                    resultado = menu_principal()
                    if resultado is None or resultado == "exit" or resultado == "error":
                        break
                    
                    # Manejar submenús especiales
                    if resultado == "env":
                        self.ejecutar_submenu(env_menu)
                        continue
                    elif resultado == "pdf":
                        self.ejecutar_submenu(pdf_menu)
                        continue
                    elif resultado == "ai":
                        self.ejecutar_submenu(ai_menu)
                        continue
                    elif resultado == "payment":
                        self.ejecutar_submenu(pago_menu)
                        continue
                    
                    # Ejecutar el comando seleccionado en el menú
                    try:
                        # Dividir el comando en argumentos si contiene espacios
                        comando_args = resultado.split()
                        # Guardamos los argumentos originales
                        args_originales = sys.argv.copy()
                        # Configuramos los nuevos argumentos
                        sys.argv = [sys.argv[0]] + comando_args
                        # Ejecutamos el comando
                        self.app()
                        # Restauramos los argumentos originales
                        sys.argv = args_originales
                    except Exception as e:
                        console.print(f"[bold red]Error al ejecutar el comando '{resultado}': {e}[/bold red]")
                        # Pausa para que el usuario pueda leer el error
                        input("\nPresione Enter para continuar...")
    
    def ejecutar_submenu(self, submenu_func):
        """Ejecuta un submenú y maneja su resultado para la navegación."""
        try:
            resultado_submenu = submenu_func()
            if resultado_submenu is not None and resultado_submenu != "exit" and resultado_submenu != "error":
                # Si el submenú devuelve un comando, ejecutarlo
                comando_args = resultado_submenu.split()
                args_originales = sys.argv.copy()
                sys.argv = [sys.argv[0]] + comando_args
                self.app()
                sys.argv = args_originales
        except Exception as e:
            console.print(f"[bold red]Error en el submenú: {e}[/bold red]")
            # Pausa para que el usuario pueda leer el error
            input("\nPresione Enter para continuar...")

    def cargar_variables_entorno(self) -> None:
        """Cargar variables de entorno desde un archivo .env"""
        # Find .env file relative to the main script or project root
        # This assumes orgm.py is in the 'orgm' directory
        project_root = Path(__file__).parent.parent
        dotenv_path = project_root / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=True)
        else:
            # Try loading from current working directory as fallback
            load_dotenv(override=True)
            if not Path(".env").exists():
                # No .env found, run env edit command
                console.print("[yellow]No se encontró archivo .env. Ejecutando 'orgm env edit'...[/yellow]")
                args_originales = sys.argv.copy()
                sys.argv = [sys.argv[0], "env", "edit"] 
                self.app()
                sys.argv = args_originales

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