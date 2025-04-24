# -*- coding: utf-8 -*-
import click
import json
import os
import subprocess
from dotenv import load_dotenv
from rich import print
from orgm.stuff.variables import edit_env_variables
from orgm.adm.clientes import obtener_clientes, obtener_cliente, buscar_clientes
from orgm.adm.firma import firmar_pdf, seleccionar_y_firmar_pdf

load_dotenv(override=True)


# Variable global para almacenar el token
token = None


def print_comandos():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # print(script_dir)
    # Build path relative to script location
    comandos_path = os.path.join(script_dir, "comandos.md")
    with open(comandos_path, "r", encoding="utf-8") as f:
        comandos = f.read()
    print(comandos)


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
    print("Actualizando paquete de ORGM CLI")

    try:
        # Obtener la rama específica del entorno si está configurada
        branch = os.getenv('GIT_BRANCH', 'master')  # Default a 'main' si no está especificada
        git_url = f"{os.getenv('GIT_URL')}@{branch}"
        
        subprocess.check_call(
            [
                "uv",
                "tool", 
                "install",
                "--force",
                f"git+{git_url}",
            ]
        )
        print(f"Paquete instalado correctamente desde la rama {branch}.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar el paquete: {e}")


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
@click.pass_context
def env(ctx):
    """Administrar variables de entorno"""
    if ctx.invoked_subcommand is None:
        print("Uso: orgm env [edit|file]")


@env.command("edit")
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def env_edit():
    """Editar variables de entorno en una interfaz TUI"""
    print("Abriendo editor de variables de entorno...")
    edit_env_variables()


@env.command("file")
@click.argument("archivo", type=click.Path(exists=True))
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def env_file(archivo):
    """Leer un archivo y guardarlo como .env"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"[bold green]Archivo '{archivo}' guardado como .env[/bold green]")
    except Exception as e:
        print(f"[bold red]Error al procesar el archivo: {e}[/bold red]")


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
@click.pass_context
def cliente(ctx):
    """Administrar clientes"""
    if ctx.invoked_subcommand is None:
        print("[bold green]Listando todos los clientes...[/bold green]")
        try:
            from orgm.questionary.clientes import listar_clientes, buscar_y_mostrar_clientes
            clientes_list = obtener_clientes()
            listar_clientes(clientes_list)
            
            # Preguntar si quiere buscar un cliente específico
            import questionary
            if questionary.confirm("¿Desea buscar un cliente específico?").ask():
                buscar_y_mostrar_clientes()
        except Exception as e:
            print(f"[bold red]Error al listar clientes: {e}[/bold red]")


@cliente.command("nuevo")
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def clientes_nuevo():
    """Crear un nuevo cliente"""
    try:
        from orgm.questionary.clientes import nuevo_cliente
        nuevo_cliente()
    except Exception as e:
        print(f"[bold red]Error al crear nuevo cliente: {e}[/bold red]")


@cliente.command("buscar")
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def clientes_buscar():
    """Buscar clientes por nombre, nombre comercial o número"""
    try:
        from orgm.questionary.clientes import buscar_y_mostrar_clientes
        buscar_y_mostrar_clientes()
    except Exception as e:
        print(f"[bold red]Error al buscar clientes: {e}[/bold red]")


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
        print(f"[bold red]Error al mostrar cliente: {e}[/bold red]")


@cliente.command("editar")
@click.argument("id_cliente", type=int)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def clientes_editar(id_cliente):
    """Editar un cliente existente"""
    try:
        from orgm.questionary.clientes import editar_cliente
        editar_cliente(id_cliente)
    except Exception as e:
        print(f"[bold red]Error al editar cliente: {e}[/bold red]")


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
@click.pass_context
def pdf(ctx):
    """Operaciones con archivos PDF"""
    if ctx.invoked_subcommand is None:
        click.echo("Uso: orgm pdf [firmar]")


@pdf.command("firmar-ruta-archivo")
@click.argument("archivo_pdf", type=click.Path(exists=True))
@click.option("--x", "-x", "x_pos", type=int, required=True, help="Posición X donde colocar la firma")
@click.option("--y", "-y", "y_pos", type=int, required=True, help="Posición Y donde colocar la firma")
@click.option("--ancho", "-a", type=int, required=True, help="Ancho de la firma")
@click.option("--salida", "-s", type=str, help="Nombre del archivo de salida")
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def pdf_firmar(archivo_pdf, x_pos, y_pos, ancho, salida):
    """Firma un archivo PDF"""
    try:
        resultado = firmar_pdf(archivo_pdf, x_pos, y_pos, ancho, salida)
        if resultado:
            print(f"[bold green]Archivo firmado: {resultado}[/bold green]")
    except Exception as e:
        print(f"[bold red]Error al firmar el PDF: {e}[/bold red]")


@pdf.command("firmar")
@click.option("--x", "-x", "x_pos", type=int, default=100, help="Posición X donde colocar la firma (default: 100)")
@click.option("--y", "-y", "y_pos", type=int, default=100, help="Posición Y donde colocar la firma (default: 100)")
@click.option("--ancho", "-a", type=int, default=200, help="Ancho de la firma (default: 200)")
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def pdf_firmar_interactivo(x_pos, y_pos, ancho):
    """Firma un archivo PDF de forma interactiva utilizando un selector de archivos"""
    try:
        resultado = seleccionar_y_firmar_pdf(x_pos, y_pos, ancho)
        if resultado:
            print(f"[bold green]Archivo firmado: {resultado}[/bold green]")
    except Exception as e:
        print(f"[bold red]Error al firmar el PDF: {e}[/bold red]")


# Agregar los comandos al grupo CLI
cli.add_command(update)
cli.add_command(help)
cli.add_command(env)
cli.add_command(cliente)
cli.add_command(pdf)


if __name__ == "__main__":
    cli()
