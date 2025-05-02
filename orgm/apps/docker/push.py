import os
from orgm.apps.docker.local_env import load_local_env, require_vars
from orgm.apps.docker.cmd import _docker_cmd
from rich.console import Console

console = Console()

def push():
    """Envía la imagen Docker al registry configurado."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_IMAGE_TAG", "DOCKER_USER", "DOCKER_URL"])

    tag = os.getenv("DOCKER_IMAGE_TAG")
    image = f"{os.getenv('DOCKER_URL')}/{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{tag}"

    console.print(f"[bold green]Pushing imagen:[/bold green] {image}")
    _docker_cmd(["docker", "push", image])
