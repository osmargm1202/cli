import typer
from rich.console import Console


from orgm.apps.adm.cliente.gui import iniciar_gui as gui

# Crear consola para salida con Rich
console = Console()

# Crear aplicación Typer para comandos de IA
app = typer.Typer(help="Comandos para interactuar con datos de clientes")

# Registrar ai_prompt directamente con el nombre 'prompt'
# El docstring de ai_prompt se usará como ayuda

app.command(name="gui")(gui)


@app.callback(invoke_without_command=True)
def ai_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con la IA. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de IA
        from orgm.apps.adm.cliente.menu import menu

        menu()


if __name__ == "__main__":
    app()
