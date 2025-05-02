
import typer
from orgm.apps.conf.check import check_urls
from orgm.apps.conf.env_file import env_file
from orgm.apps.conf.env_edit import env_edit
from orgm.apps.conf.ayuda import mostrar_ayuda
from orgm.apps.conf.ayuda import mostrar_ayuda
from orgm.apps.conf.menu import menu

app = typer.Typer(help="Comandos de Configuración de ORGM")

app.command(name="check")(check_urls)
app.command(name="env-file")(env_file)
app.command(name="env-edit")(env_edit)
app.command(name="ayuda")(mostrar_ayuda)
app.command(name="help")(mostrar_ayuda)


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