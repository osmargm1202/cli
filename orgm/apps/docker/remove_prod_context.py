import os
from orgm.apps.docker.local_env import load_local_env, require_vars
from orgm.apps.docker.cmd import _docker_cmd
from rich.console import Console

console = Console()

def remove_prod_context():
    """Elimina el contexto Docker 'prod'."""
    load_local_env()

    console.print("[bold green]Eliminando contexto prod...[/bold green]")
    _docker_cmd(["docker", "context", "rm", "prod"])
