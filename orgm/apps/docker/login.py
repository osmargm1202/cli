import os
from orgm.apps.docker.local_env import load_local_env, require_vars
from orgm.apps.docker.cmd import _docker_cmd
from rich.console import Console
import questionary
import typer

console = Console()

def login():
    """Inicia sesión en Docker Hub usando variables de entorno y contraseña solicitada."""
    require_vars(["DOCKER_HUB_URL", "DOCKER_HUB_USER"])

    docker_hub_url = os.getenv("DOCKER_HUB_URL")
    docker_hub_user = os.getenv("DOCKER_HUB_USER")

    password = questionary.password("Introduce la contraseña de Docker Hub:").ask()
    if not password:
        raise typer.Exit("Se requiere una contraseña para continuar.")

    console.print(f"[bold green]Iniciando sesión en {docker_hub_url}...[/bold green]")
    _docker_cmd(["docker", "login", docker_hub_url, "-u", docker_hub_user, "--password-stdin"], input_text=password)