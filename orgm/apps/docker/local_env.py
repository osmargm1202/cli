
from dotenv import load_dotenv
import os
import typer
from rich.console import Console
from typing import List

console = Console()


def load_local_env() -> None:
    """Carga el fichero `.env` del directorio actual (si existe)."""
    dotenv_path = os.path.join(os.getcwd(), ".env")
    if os.path.isfile(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        console.print("[bold red]Error: .env file not found en el directorio actual[/bold red]")
        raise typer.Exit(1)

def require_vars(varnames: List[str]):
    """Verifica que todas las variables de entorno indicadas estén definidas."""

    missing = [v for v in varnames if not os.getenv(v)]
    if missing:
        vars_str = ", ".join(missing)
        console.print(
            f"[bold red]Error: Variables de entorno faltantes:[/bold red] {vars_str}"
        )
        raise typer.Exit(1)