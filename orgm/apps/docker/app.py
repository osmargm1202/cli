
import typer


from orgm.apps.docker.menu import menu
from orgm.apps.docker.build import build
from orgm.apps.docker.build import build_no_cache
from orgm.apps.docker.save import save
from orgm.apps.docker.push import push
from orgm.apps.docker.tag import tag
from orgm.apps.docker.create_prod_context import create_prod_context
from orgm.apps.docker.deploy import deploy
from orgm.apps.docker.remove_prod_context import remove_prod_context
from orgm.apps.docker.login import login

app = typer.Typer(help="Comandos de Configuración de ORGM")


app.command(name="build")(build)
app.command(name="build-no-cache")(build_no_cache)
app.command(name="save")(save)
app.command(name="push")(push)
app.command(name="tag")(tag)
app.command(name="create-prod-context")(create_prod_context)
app.command(name="deploy")(deploy)
app.command(name="remove-prod-context")(remove_prod_context)
app.command(name="login")(login)



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