import typer
from rich.console import Console
import os
import questionary
from orgm.qstyle import custom_style_fancy
from orgm.apps.utils.carpetas.esquemas import crear_carpeta_proyecto
from orgm.apps.utils.carpetas.menu import menu

console = Console()


app = typer.Typer(help="Comandos para interactuar con carpetas")



@app.command(name="proyecto")
def crear_carpeta(cotizacion: int):
    if not cotizacion:
        cotizacion = questionary.text("Ingrese la cotización", style=custom_style_fancy).ask()
    crear_carpeta_proyecto(cotizacion)




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