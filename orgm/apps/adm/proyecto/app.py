import typer
from typing import List
from rich.console import Console

# Importar la función que define los argumentos y la lógica
from orgm.apps.adm.proyecto.get_projects import listar_proyectos
from orgm.apps.adm.proyecto.get_project import obtener_y_mostrar_proyecto
from orgm.apps.adm.proyecto.find_project import buscar_y_mostrar_proyectos
from orgm.apps.adm.proyecto.create_project import definir_y_crear_proyecto
from orgm.apps.adm.proyecto.update_project import definir_y_actualizar_proyecto
from orgm.apps.adm.proyecto.gui import iniciar_gui
# Crear consola para salida con Rich    
console = Console()

# Crear aplicación Typer para comandos de IA
app = typer.Typer(help="Comandos para interactuar con datos de clientes")

# Registrar ai_prompt directamente con el nombre 'prompt'
# El docstring de ai_prompt se usará como ayuda
app.command(name="list")(listar_proyectos)
app.command(name="show")(obtener_y_mostrar_proyecto)
app.command(name="find")(buscar_y_mostrar_proyectos)
app.command(name="create")(definir_y_crear_proyecto)
app.command(name="edit")(definir_y_actualizar_proyecto)
app.command(name="gui")(iniciar_gui)

@app.callback(invoke_without_command=True)
def ai_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con la IA. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de IA
        from orgm.apps.adm.proyecto.menu import menu
        menu()

if __name__ == "__main__":
    app()