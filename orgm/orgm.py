import sys
import typer
from rich.console import Console
from dotenv import load_dotenv
from pathlib import Path
import os # Added for potential path debugging if needed, but Path should suffice


# Import placeholder modules (keep for now)
# from orgm.apps.clientes import clientes # Eliminar placeholder
# from orgm.apps.proyectos import proyecto # Eliminar placeholder
# from orgm.apps.cotizaciones import cotizacion # Eliminar placeholder
# from orgm.apps.docker import docker as docker_cmd # Eliminar placeholder

# Importar los grupos de comandos de las aplicaciones
from orgm.apps.clientes import clientes as clientes_app
from orgm.apps.proyectos import proyecto as proyecto_app
from orgm.apps.cotizaciones import cotizacion as cotizacion_app
from orgm.apps.docker import docker as docker_app

# Import command functions from new modules
from orgm.commands.base import check_urls, update, install
from orgm.commands.env import env_edit, env_file
from orgm.commands.pdf import pdf_firmar, pdf_firmar_interactivo
from orgm.commands.ai import ai_prompt, ai_configs, ai_config_upload, ai_config_create, ai_config_edit

# Nuevos comandos API
from orgm.commands.rnc import buscar_empresa_command
from orgm.commands.divisa import tasa_divisa_command

# Importar el menú principal
from orgm.commands.menu import menu_principal

# También importamos los submenús
from orgm.apps.env_app import env_menu
from orgm.apps.pdf_app import pdf_menu
from orgm.apps.ai_app import ai_menu

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
        # El mensaje de ayuda se maneja mediante el callback ahora
        self.app = typer.Typer(
            # help="ORGM CLI - Herramienta de gestión organizacional", # Eliminado help de aquí
            context_settings={"help_option_names": ["-h", "--help"]},
            no_args_is_help=False, # Evita la ayuda predeterminada de Typer sin argumentos
            add_completion=False # Opcional: deshabilitar la autocompletación si no se usa
        )
        
        self.env_app = typer.Typer(help="Administrar variables de entorno")
        self.pdf_app = typer.Typer(help="Operaciones con archivos PDF")
        self.ai_app = typer.Typer(help="Operaciones relacionadas con la IA")
        # No necesitamos typer apps para clientes, proyectos, etc., ya que son grupos de click
        
        # Configurar subcomandos
        self.app.add_typer(self.env_app, name="env")
        self.app.add_typer(self.pdf_app, name="pdf")
        self.app.add_typer(self.ai_app, name="ai")
        # Añadir los grupos de comandos de las aplicaciones usando add_typer
        self.app.add_typer(clientes_app, name="client")
        self.app.add_typer(proyecto_app, name="project")
        self.app.add_typer(cotizacion_app, name="quotation")
        self.app.add_typer(docker_app, name="docker")
        
        # Configurar comandos individuales (los que quedan en el nivel superior)
        self.configurar_comandos_principales() # Renombrar para claridad
        self.configurar_callback() # Llamar al nuevo método para configurar el callback
        
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
                 # Optional: Warn if no .env found
                 # console.print("[yellow]Advertencia: No se encontró archivo .env[/yellow]")
                 pass 

    def configurar_comandos_principales(self) -> None:
        """Configurar los comandos principales de la aplicación (no los grupos)"""
        # Comandos principales - Use imported functions
        self.app.command(name="check")(check_urls)
        self.app.command(name="update")(update)
        self.app.command(name="install")(install)
        
        # Comandos API
        self.app.command(name="find-company")(buscar_empresa_command)
        self.app.command(name="currency-rate")(tasa_divisa_command)
        
        # Comandos de env - Use imported functions
        self.env_app.command(name="edit")(env_edit)
        self.env_app.command(name="file")(env_file)
        
        # Comandos de PDF - Use imported functions
        self.pdf_app.command(name="sign-file")(pdf_firmar)
        self.pdf_app.command(name="sign")(pdf_firmar_interactivo)
        
        # Comandos de AI - Use imported functions
        self.ai_app.command(name="prompt")(ai_prompt)
        self.ai_app.command(name="configs")(ai_configs)
        self.ai_app.command(name="upload")(ai_config_upload)
        self.ai_app.command(name="create")(ai_config_create)
        self.ai_app.command(name="edit")(ai_config_edit)

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