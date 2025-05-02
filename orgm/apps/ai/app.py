import typer
from typing import List
from rich.console import Console

# Importar la función que define los argumentos y la lógica
from orgm.apps.ai.prompt import ai_prompt
from orgm.apps.ai.configs_list import ai_configs_list
from orgm.apps.ai.modelos import ai_models_list
from orgm.apps.ai.config_create import ai_config_create
from orgm.apps.ai.config_edit import ai_config_edit
from orgm.apps.ai.config_upload import ai_config_upload
from orgm.apps.ai.generate import generate_text
# Crear consola para salida con Rich
console = Console()

# Crear aplicación Typer para comandos de IA
app = typer.Typer(help="Comandos para interactuar con servicios de IA")

# Registrar ai_prompt directamente con el nombre 'prompt'
# El docstring de ai_prompt se usará como ayuda
app.command(name="prompt")(ai_prompt)
app.command(name="configs")(ai_configs_list)
app.command(name="models")(ai_models_list)
app.command(name="create")(ai_config_create)    
app.command(name="edit")(ai_config_edit)
app.command(name="upload")(ai_config_upload)
app.command(name="generate")(generate_text)


@app.callback(invoke_without_command=True)
def ai_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con la IA. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de IA
        from orgm.apps.ai.menu import menu
        menu()

if __name__ == "__main__":
    app()