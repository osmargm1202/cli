import sys
import typer
from rich.console import Console
from dotenv import load_dotenv
from pathlib import Path


# Import placeholder modules (keep for now)
from orgm.apps.clientes import clientes
from orgm.apps.proyectos import proyecto
from orgm.apps.cotizaciones import cotizacion
from orgm.apps.docker_cli import docker as docker_cmd

# Import command functions from new modules
from orgm.commands.base import check_urls, update, install
from orgm.commands.env import env_edit, env_file
from orgm.commands.pdf import pdf_firmar, pdf_firmar_interactivo
from orgm.commands.ai import ai_prompt, ai_configs, ai_config_upload
# Nuevos comandos API
from orgm.commands.rnc import buscar_empresa_command
from orgm.commands.divisa import tasa_divisa_command

# Crear consola para salida con Rich
console = Console()

# Clase personalizada para manejar la salida de los comandos
class SalirException(Exception):
    """Excepción personalizada para salir del programa."""
    pass

# Clase principal que maneja la aplicación CLI
class OrgmCLI:
    def __init__(self):
        # Crear la aplicación Typer, especificando explícitamente las opciones de ayuda
        self.app = typer.Typer(
            help="ORGM CLI - Herramienta de gestión organizacional",
            context_settings={"help_option_names": ["-h", "--help"]}
        )
        
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

    def configurar_comandos(self) -> None:
        """Configurar todos los comandos de la aplicación"""
        # Comandos principales - Use imported functions
        self.app.command(name="check")(check_urls)
        self.app.command(name="update")(update)
        self.app.command(name="install")(install)
        
        # Comandos API
        self.app.command(name="buscar-empresa")(buscar_empresa_command)
        self.app.command(name="divisa")(tasa_divisa_command)
        
        # Comandos de env - Use imported functions
        self.env_app.command(name="edit")(env_edit)
        self.env_app.command(name="file")(env_file)
        
        # Comandos de PDF - Use imported functions
        self.pdf_app.command(name="firmar-archivo")(pdf_firmar)
        self.pdf_app.command(name="firmar")(pdf_firmar_interactivo)
        
        # Comandos de AI - Use imported functions
        self.ai_app.command(name="prompt")(ai_prompt)
        self.ai_app.command(name="configs")(ai_configs)
        self.ai_app.command(name="config-upload")(ai_config_upload)

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