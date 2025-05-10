import typer
from rich.console import Console

# Importar la función que define los argumentos y la lógica
from orgm.apps.adm.cotizacion.get_quotations import listar_cotizaciones
from orgm.apps.adm.cotizacion.gui import gui

# Crear consola para salida con Rich
console = Console()

# Crear aplicación Typer para comandos de IA
app = typer.Typer(help="Comandos para interactuar con datos de cotizaciones")

# Registrar ai_prompt directamente con el nombre 'prompt'
# El docstring de ai_prompt se usará como ayuda
# app.command(name="list")(listar_cotizaciones)
# app.command(name="show")(mostrar_cotizacion_detalle)
# app.command(name="find")(buscar_cotizaciones_por_cliente)
# app.command(name="create")(crear_cotizacion)
# app.command(name="edit")(actualizar_cotizacion)
# app.command(name="gui")(gui)


@app.callback(invoke_without_command=True)
def ai_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con la IA. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de Cotizaciones
        from orgm.apps.adm.cotizacion.menu import menu

        menu()


if __name__ == "__main__":
    app()
