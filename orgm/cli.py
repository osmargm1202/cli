import click
import json
import os
import subprocess
from .server.auth import login
from dotenv import load_dotenv

load_dotenv(override=True)


url = os.getenv("SERVER_URL_U")

# Variable global para almacenar el token
token = None


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def cli(ctx):
    """Bienvenido a CLI de ORGM"""
    click.echo("Bienvenido a CLI de ORGM")
    click.echo("----------------------------------")
    if ctx.invoked_subcommand is None:
        with open("orgm/cache/comandos.json", "r") as f:
            comandos = json.load(f)
        for comando, info in comandos.items():
            click.echo(f"{comando} - {info}")

            # for key, value in info.items():
            #     click.echo(Fore.BLACK + f"{key}: {value}")


@click.command()
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
@click.argument("edit", nargs=1, required=False)
def update(edit):
    """Actualizar el paquete de ORGM CLI"""
    click.echo("Actualizando paquete de ORGM CLI")

    if edit == "-e":
        try:
            # Ejecuta el comando pip install
            subprocess.check_call(
                [
                    "uv",
                    "tool",
                    "install -e",
                    "git+https://github.com/osmargm1202/cli.git",
                ]
            )
            click.echo("Paquete instalado correctamente.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Error al instalar el paquete: {e}")
    else:
        try:
            subprocess.check_call(
                [
                    "uv",
                    "tool",
                    "install",
                    "git+https://github.com/osmargm1202/cli.git",
                ]
            )
            click.echo("Paquete instalado correctamente.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Error al instalar el paquete: {e}")


cli.add_command(login)
cli.add_command(update)

if __name__ == "__main__":
    cli()
