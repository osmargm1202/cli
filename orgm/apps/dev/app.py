
import typer

from orgm.apps.dev.upload import upload

from orgm.apps.dev.menu import menu

app = typer.Typer(help="Comandos de Configuración de ORGM")


app.command(name="upload")(upload)



@app.callback(invoke_without_command=True)
def ai_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con la IA. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de IA
        
        menu()

if __name__ == "__main__":
    app()