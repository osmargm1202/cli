import typer

from orgm.apps.dev.upload import upload

from orgm.apps.dev.menu import menu
from orgm.apps.dev.install_desktop import crear_desktop_entry
from orgm.apps.dev.install_desktop_windows import crear_acceso_directo_windows

app = typer.Typer(help="Comandos de Configuración de ORGM")


app.command(name="upload")(upload)
app.command(name="shortcut")(crear_desktop_entry)
app.command(name="shortcut_windows")(crear_acceso_directo_windows)

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
