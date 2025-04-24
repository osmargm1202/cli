import click
import json
import os
import subprocess
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from orgm.stuff.variables import edit_env_variables
from orgm.adm.clientes import obtener_clientes, obtener_cliente, buscar_clientes
console = Console()


load_dotenv(override=True)


url = os.getenv("SERVER_URL_U")

# Variable global para almacenar el token
token = None


def print_comandos():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(script_dir)
    # Build path relative to script location
    comandos_path = os.path.join(script_dir, "comandos.md")
    with open(comandos_path, "r") as f:
        comandos = f.read()
    console.print(comandos)


class CustomGroup(click.Group):
    def get_help(self, ctx):
        print_comandos()
        return ""


@click.group(invoke_without_command=True, cls=CustomGroup)
@click.version_option()
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print_comandos()
    else:
        print_comandos()

@click.command()
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def help():
    print_comandos()


@click.command()
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
# @click.pass_context  # Pasa el contexto del comando al callback de la función
def update():
    """Actualizar el paquete de ORGM CLI"""
    console.print("Actualizando paquete de ORGM CLI")

    try:
        subprocess.check_call(
            [
                "uv",
                "tool",
                "install",
                "--force",
                f"git+{os.getenv('GIT_URL')}",
            ]
        )
        console.print("Paquete instalado correctamente.")
    except subprocess.CalledProcessError as e:
        console.print(f"Error al instalar el paquete: {e}")


@click.command()
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def env():
    """Editar variables de entorno en una interfaz TUI"""
    console.print("Abriendo editor de variables de entorno...")
    edit_env_variables()


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
@click.pass_context
def cliente(ctx):
    """Administrar clientes"""
    if ctx.invoked_subcommand is None:
        console.print("[bold green]Listando todos los clientes...[/bold green]")
        try:
            from orgm.questionary.clientes import listar_clientes, buscar_y_mostrar_clientes
            clientes_list = obtener_clientes()
            listar_clientes(clientes_list)
            
            # Preguntar si quiere buscar un cliente específico
            import questionary
            if questionary.confirm("¿Desea buscar un cliente específico?").ask():
                buscar_y_mostrar_clientes()
        except Exception as e:
            console.print(f"[bold red]Error al listar clientes: {e}[/bold red]")


@cliente.command("nuevo")
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def clientes_nuevo():
    """Crear un nuevo cliente"""
    try:
        from orgm.questionary.clientes import nuevo_cliente
        nuevo_cliente()
    except Exception as e:
        console.print(f"[bold red]Error al crear nuevo cliente: {e}[/bold red]")


@cliente.command("buscar")
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def clientes_buscar():
    """Buscar clientes por nombre, nombre comercial o número"""
    try:
        from orgm.questionary.clientes import buscar_y_mostrar_clientes
        buscar_y_mostrar_clientes()
    except Exception as e:
        console.print(f"[bold red]Error al buscar clientes: {e}[/bold red]")


@cliente.command("ver")
@click.argument("id_cliente", type=int)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def clientes_ver(id_cliente):
    """Ver detalles de un cliente específico"""
    try:
        from orgm.questionary.clientes import mostrar_cliente
        cliente = obtener_cliente(id_cliente)
        if cliente:
            mostrar_cliente(cliente)
            
            # Preguntar si quiere editar el cliente
            import questionary
            if questionary.confirm("¿Desea editar este cliente?").ask():
                from orgm.questionary.clientes import editar_cliente
                editar_cliente(id_cliente)
    except Exception as e:
        console.print(f"[bold red]Error al mostrar cliente: {e}[/bold red]")


@cliente.command("editar")
@click.argument("id_cliente", type=int)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def clientes_editar(id_cliente):
    """Editar un cliente existente"""
    try:
        from orgm.questionary.clientes import editar_cliente
        editar_cliente(id_cliente)
    except Exception as e:
        console.print(f"[bold red]Error al editar cliente: {e}[/bold red]")


# Agregar los comandos al grupo CLI
cli.add_command(update)
cli.add_command(help)
cli.add_command(env)
cli.add_command(cliente)


if __name__ == "__main__":
    cli()
