import typer
from rich.console import Console
import os
import questionary
from orgm.qstyle import custom_style_fancy
from orgm.apps.utils.carpetas.esquemas import crear_carpeta_proyecto

console = Console()


app = typer.Typer(help="Comandos para interactuar con carpetas")



@app.command(name="proyecto")
def crear_carpeta(): 
    cotizacion = questionary.text("Ingrese la cotización", style=custom_style_fancy).ask()
    crear_carpeta_proyecto(cotizacion)



if __name__ == "__main__":
    app()