import os
from orgm.apps.docker.local_env import load_local_env, require_vars
from orgm.apps.docker.cmd import _docker_cmd
from rich.console import Console
import typer
console = Console()

def deploy():
    """Despliega la aplicación en el contexto 'prod' usando docker compose."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_USER", "DOCKER_URL"])

    image = f"{os.getenv('DOCKER_URL')}/{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:latest"

    console.print("[bold green]Desplegando en contexto prod...[/bold green]")

    # Extra: asegurarse de que el contexto existe intentando crear si falla
    try:
        _docker_cmd(["docker", "context", "inspect", "prod"])
    except typer.Exit:
        console.print("[yellow]Contexto 'prod' no existe. Creándolo...[/yellow]")
        ctx_user = os.getenv("DOCKER_HOST_USER")
        ctx_ip = os.getenv("DOCKER_HOST_IP")
        if ctx_user and ctx_ip:
            host_str = f"ssh://{ctx_user}@{ctx_ip}"
            _docker_cmd(["docker", "context", "create", "prod", "--docker", f"host={host_str}"])
        else:
            raise typer.Exit("No se pudo crear contexto 'prod'. Falta DOCKER_HOST_USER o DOCKER_HOST_IP")

    _docker_cmd(["docker", "--context", "prod", "pull", image])
    _docker_cmd(["docker", "--context", "prod", "compose", "up", "-d", "--remove-orphans"])