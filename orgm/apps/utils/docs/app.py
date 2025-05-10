import typer
from rich.console import Console


console = Console()

from orgm.apps.utils.docs.menu import menu


app = typer.Typer(help="Comandos para interactuar con documentos")


@app.callback(invoke_without_command=True)
def docs_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con documentos. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de documentos
        menu()
        


if __name__ == "__main__":
    app()
