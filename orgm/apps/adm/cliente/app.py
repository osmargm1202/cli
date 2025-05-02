import typer
from typing import List
from rich.console import Console

# Importar la función que define los argumentos y la lógica
from orgm.apps.adm.cliente.get_clients import listar
from orgm.apps.adm.cliente.get_client import mostrar
from orgm.apps.adm.cliente.find_clients import buscar
from orgm.apps.adm.cliente.new_client import crear
from orgm.apps.adm.cliente.edit_client import actualizar
from orgm.apps.adm.cliente.mostrar_export import exportar
# Crear consola para salida con Rich    
console = Console()

# Crear aplicación Typer para comandos de IA
app = typer.Typer(help="Comandos para interactuar con datos de clientes")

# Registrar ai_prompt directamente con el nombre 'prompt'
# El docstring de ai_prompt se usará como ayuda
app.command(name="list")(listar)
app.command(name="show")(mostrar)
app.command(name="find")(buscar)
app.command(name="create")(crear)
app.command(name="edit")(actualizar)
app.command(name="export")(exportar)

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