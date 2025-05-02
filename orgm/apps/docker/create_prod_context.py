import os
from orgm.apps.docker.local_env import load_local_env, require_vars
from orgm.apps.docker.cmd import _docker_cmd
from rich.console import Console

console = Console()

def create_prod_context():
    """Crea un contexto Docker denominado 'prod'."""
    load_local_env()

    require_vars(["DOCKER_HOST_USER", "DOCKER_HOST_IP"])

    host_str = f"ssh://{os.getenv('DOCKER_HOST_USER')}@{os.getenv('DOCKER_HOST_IP')}"

    console.print(f"[bold green]Creando contexto prod:[/bold green] {host_str}")
    _docker_cmd(["docker", "context", "create", "prod", "--docker", f"host={host_str}"])