
from typing import List, Optional
import subprocess
import typer
from rich.console import Console

console = Console()


def _docker_cmd(cmd: List[str], *, input_text: Optional[str] = None):
    """Ejecuta un comando docker mostrando la salida.

    Si *input_text* se proporciona, se envía al stdin del comando (por ejemplo para
    `docker login --password-stdin`).
    """
    console.print(f"[bold cyan]$ {' '.join(cmd)}[/bold cyan]")

    try:
        subprocess.run(
            cmd,
            check=True,
            text=True,
            input=input_text,
        )
    except subprocess.CalledProcessError as exc:
        raise typer.Exit(f"Error al ejecutar docker: {exc}")