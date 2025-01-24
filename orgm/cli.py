import click
import colorama
import json
import os
import subprocess
from colorama import Fore, Style
from .server.auth import login
from dotenv import load_dotenv

load_dotenv(override=True)


url = os.getenv("SERVER_URL_U")

# Inicializar colorama
colorama.init(autoreset=True)

# Variable global para almacenar el token
token = None


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def cli(ctx):
    """Bienvenido a CLI de ORGM"""
    click.echo(Style.BRIGHT + Fore.CYAN + "Bienvenido a CLI de ORGM")
    click.echo(Fore.BLUE + "----------------------------------")
    if ctx.invoked_subcommand is None:
        with open("orgm/cache/comandos.json", "r") as f:
            comandos = json.load(f)
        for comando, info in comandos.items():
            click.echo(
                Style.BRIGHT
                + Fore.YELLOW
                + f"{comando} - "
                + Style.BRIGHT
                + Fore.BLUE
                + info
            )

            # for key, value in info.items():
            #     click.echo(Fore.BLACK + f"{key}: {value}")


@click.command()
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
@click.argument("edit", nargs=1, required=False)
def update(edit):
    """Actualizar el paquete de ORGM CLI"""
    click.echo(Fore.GREEN + "Actualizando paquete de ORGM CLI")

    if edit == "-e":
        try:
            # Ejecuta el comando pip install
            subprocess.check_call(
                [
                    "uv",
                    "pip",
                    "install -e",
                    "git+ssh://git@github.com/osmargm1202/orgmcli.git",
                ]
            )
            click.echo(Fore.GREEN + "Paquete instalado correctamente.")
        except subprocess.CalledProcessError as e:
            click.echo(Fore.RED + f"Error al instalar el paquete: {e}")
    else:
        try:
            # Ejecuta el comando pip install
            subprocess.check_call(
                ["pip", "install", "git+ssh://git@github.com/osmargm1202/orgmcli.git"]
            )
            click.echo(Fore.GREEN + "Paquete instalado correctamente.")
        except subprocess.CalledProcessError as e:
            click.echo(Fore.RED + f"Error al instalar el paquete: {e}")


cli.add_command(login)
cli.add_command(update)


if __name__ == "__main__":
    cli()
