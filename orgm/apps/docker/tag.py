import os
from orgm.apps.docker.local_env import load_local_env, require_vars
from orgm.apps.docker.cmd import _docker_cmd
from rich.console import Console

console = Console()



def tag():
    """Etiqueta la imagen con la etiqueta latest en el registry."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_IMAGE_TAG", "DOCKER_USER", "DOCKER_URL"])

    current = f"{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{os.getenv('DOCKER_IMAGE_TAG')}"
    target = f"{os.getenv('DOCKER_URL')}/{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:latest"

    console.print(f"[bold green]Etiquetando imagen:[/bold green] {current} → {target}")
    _docker_cmd(["docker", "tag", current, target])