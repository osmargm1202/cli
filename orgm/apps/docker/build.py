
from orgm.apps.docker.cmd import _docker_cmd
from orgm.apps.docker.local_env import load_local_env, require_vars
import os
from rich.console import Console


console = Console()


def build():
    """Construye la imagen Docker usando cache."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_IMAGE_TAG", "DOCKER_USER"])

    tag = os.getenv("DOCKER_IMAGE_TAG")
    image = f"{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{tag}"

    console.print(f"[bold green]Construyendo imagen:[/bold green] {image}")
    _docker_cmd(["docker", "build", "-t", image, "."])


def build_no_cache():
    """Construye la imagen Docker sin usar cache."""
    load_local_env()
    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_IMAGE_TAG", "DOCKER_USER"])

    tag = os.getenv("DOCKER_IMAGE_TAG")
    image = f"{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{tag}"

    console.print(f"[bold green]Construyendo imagen:[/bold green] {image}")
    _docker_cmd(["docker", "build", "--no-cache", "-t", image, "."])