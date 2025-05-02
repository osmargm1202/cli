import os
from orgm.apps.docker.local_env import load_local_env, require_vars
from orgm.apps.docker.cmd import _docker_cmd
from rich.console import Console

console = Console()

def save():
    """Guarda la imagen Docker en un archivo tar."""
    load_local_env()

    require_vars(
        [
            "DOCKER_IMAGE_NAME",
            "DOCKER_IMAGE_TAG",
            "DOCKER_SAVE_FILE",
            "DOCKER_FOLDER_SAVE",
            "DOCKER_USER",
        ]
    )

    tag = os.getenv("DOCKER_IMAGE_TAG")
    image = f"{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{tag}"
    save_path = os.path.join(os.getenv("DOCKER_FOLDER_SAVE"), os.getenv("DOCKER_SAVE_FILE"))

    console.print(f"[bold green]Guardando imagen en:[/bold green] {save_path}")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    _docker_cmd(["docker", "save", "-o", save_path, image])