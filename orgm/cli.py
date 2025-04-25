# -*- coding: utf-8 -*-
import click
import os
import subprocess
import requests
from dotenv import load_dotenv
from rich import print
from orgm.stuff.variables import edit_env_variables
from orgm.adm.firma import firmar_pdf, seleccionar_y_firmar_pdf
from orgm.apps.clientes import cliente
from orgm.apps.proyectos import proyecto
from orgm.apps.cotizaciones import cotizacion
from rich.console import Console

load_dotenv(override=True)

console = Console()

# Variable global para almacenar el token
token = None


# Comprobación de endpoints
def check_urls():
    """Verifica rápidamente la accesibilidad de URLs clave definidas en variables de entorno."""
    endpoints = {
        "POSTGREST_URL": os.getenv("POSTGREST_URL"),
        "API_URL": os.getenv("API_URL"),
    }

    # Obtener credenciales de Cloudflare Access
    CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
    CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

    if not all([CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET]):
        console.print(
            "[bold yellow]Advertencia: CF_ACCESS_CLIENT_ID o CF_ACCESS_CLIENT_SECRET no están definidas en las variables de entorno.[/bold yellow]"
        )
        console.print(
            "[bold yellow]Las consultas no incluirán autenticación de Cloudflare Access.[/bold yellow]"
        )
    # Configuración de los headers para PostgREST
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Prefer": "return=representation",
    }

    # Agregar headers de Cloudflare Access si están disponibles
    if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
        headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
        headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET

    for name, url in endpoints.items():
        if not url:
            print(f"[yellow]{name} no configurada[/yellow]")
            continue
        try:
            resp = requests.get(url, headers=headers, timeout=1)
            if resp.status_code < 400:
                print(f"[bold green]{name} OK[/bold green] → {url}")
            else:
                print(f"[bold red]{name} ERROR {resp.status_code}[/bold red] → {url}")
        except Exception as e:
            print(f"[bold red]{name} inaccesible:[/bold red] {e} → {url}")


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
        check_urls()


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
        branch = os.getenv(
            "GIT_BRANCH", "master"
        )  # Default a 'main' si no está especificada
        git_url = f"{os.getenv('GIT_URL')}@{branch}"

        # Primero desinstalar el paquete
        print("Desinstalando versión actual...")
        subprocess.check_call(
            [
                "uv",
                "tool",
                "uninstall",
                "orgm",
            ]
        )

        # Luego instalar la nueva versión
        print(f"Instalando nueva versión desde la rama {branch}...")
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
        print(f"Error al actualizar el paquete: {e}")


@click.command()
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def install():
    """Instalar el paquete de ORGM CLI"""
    print("Instalando paquete de ORGM CLI")

    try:
        # Obtener la rama específica del entorno si está configurada
        branch = os.getenv(
            "GIT_BRANCH", "master"
        )  # Default a 'master' si no está especificada
        git_url = f"{os.getenv('GIT_URL')}@{branch}"

        print(f"Instalando desde la rama {branch}...")
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
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()

        with open(".env", "w", encoding="utf-8") as f:
            f.write(contenido)

        print(f"[bold green]Archivo '{archivo}' guardado como .env[/bold green]")
    except Exception as e:
        print(f"[bold red]Error al procesar el archivo: {e}[/bold red]")


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
@click.pass_context
def pdf(ctx):
    """Operaciones con archivos PDF"""
    if ctx.invoked_subcommand is None:
        click.echo("Uso: orgm pdf [firmar]")


@pdf.command("firmar-ruta-archivo")
@click.argument("archivo_pdf", type=click.Path(exists=True))
@click.option(
    "--x",
    "-x",
    "x_pos",
    type=int,
    required=True,
    help="Posición X donde colocar la firma",
)
@click.option(
    "--y",
    "-y",
    "y_pos",
    type=int,
    required=True,
    help="Posición Y donde colocar la firma",
)
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
@click.option(
    "--x",
    "-x",
    "x_pos",
    type=int,
    default=100,
    help="Posición X donde colocar la firma (default: 100)",
)
@click.option(
    "--y",
    "-y",
    "y_pos",
    type=int,
    default=100,
    help="Posición Y donde colocar la firma (default: 100)",
)
@click.option(
    "--ancho", "-a", type=int, default=200, help="Ancho de la firma (default: 200)"
)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def pdf_firmar_interactivo(x_pos, y_pos, ancho):
    """Firma un archivo PDF de forma interactiva utilizando un selector de archivos"""
    try:
        resultado = seleccionar_y_firmar_pdf(x_pos, y_pos, ancho)
        if resultado:
            print(f"[bold green]Archivo firmado: {resultado}[/bold green]")
    except Exception as e:
        print(f"[bold red]Error al firmar el PDF: {e}[/bold red]")


# Agregar el comando AI
@click.command("ai")
@click.option(
    "--config",
    "-c",
    "config_name",
    default="default",
    help="Nombre de la configuración del modelo IA (default: 'default')",
)
@click.argument("prompt", nargs=-1, required=True)
@click.help_option("-h", "--help", help="Muestra la ayuda del comando")
def ai_command(config_name, prompt):
    """Genera texto usando el servicio de IA.

    PROMPT: Texto que describe la solicitud a la IA.
    """
    from orgm.stuff.ai import generate_text

    # Unir el prompt que puede venir en múltiples palabras
    prompt_text = " ".join(prompt).strip()

    if not prompt_text:
        print("[bold red]Debe proporcionar un texto de entrada para la IA.[/bold red]")
        return

    resultado = generate_text(prompt_text, config_name)
    if resultado:
        # Mostrar la respuesta devuelta por la IA progresivamente para simular streaming
        from time import sleep
        print("[bold green]Respuesta IA:[/bold green] ", end="", flush=True)
        for char in str(resultado):
            print(char, end="", flush=True)  # imprime carácter por carácter
            sleep(0.01)  # pequeño retraso para el efecto de aparición
        print()  # nueva línea al finalizar


# Agregar los comandos al grupo CLI
cli.add_command(update)
cli.add_command(install)
cli.add_command(help)
cli.add_command(env)
cli.add_command(cliente)
cli.add_command(proyecto)
cli.add_command(pdf)
cli.add_command(ai_command)
cli.add_command(cotizacion)


if __name__ == "__main__":
    cli()
