# -*- coding: utf-8 -*-
"""
Comandos relacionados con operaciones Docker para ORGM CLI.

Este módulo traslada la lógica del script `build.sh` a Python utilizando `click` para la
línea de comandos y `questionary` para la interacción cuando se ejecuta el comando
principal `orgm docker` sin subcomandos.

Se respetan fielmente las operaciones originales:
• build (con y sin caché)
• save
• push
• tag
• create-prod-context
• deploy
• remove-prod-context
Además se añade el subcomando `login` que ejecuta `docker login` con las variables de
entorno `DOCKER_HUB_URL` y `DOCKER_HUB_USER`, solicitando la contraseña de forma
interactiva.

Todas las operaciones consumen el fichero `.env` presente en el directorio desde el cual
se invoque el comando, de forma equivalente al script original.
"""

import os
import subprocess
from typing import List, Optional

import click
import questionary
from dotenv import load_dotenv
from rich.console import Console

console = Console()


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def load_local_env() -> None:
    """Carga el fichero `.env` del directorio actual (si existe)."""
    dotenv_path = os.path.join(os.getcwd(), ".env")
    if os.path.isfile(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        console.print("[bold red]Error: .env file not found en el directorio actual[/bold red]")
        raise click.ClickException("Falta archivo .env")


def require_vars(varnames: List[str]):
    """Verifica que todas las variables de entorno indicadas estén definidas."""

    missing = [v for v in varnames if not os.getenv(v)]
    if missing:
        vars_str = ", ".join(missing)
        console.print(
            f"[bold red]Error: Variables de entorno faltantes:[/bold red] {vars_str}"
        )
        raise click.ClickException("Variables de entorno faltantes")


# ---------------------------------------------------------------------------
# Comandos individuales
# ---------------------------------------------------------------------------

def _docker_cmd(cmd: List[str], *, input_text: Optional[str] = None):
    """Ejecuta un comando docker mostrando la salida.

    Si *input_text* se proporciona, se envía al stdin del comando (por ejemplo para
    `docker login --password-stdin`).
    """
    console.print(f"[bold cyan]$ {' '.join(cmd)}[/bold cyan]")

    try:
        subprocess.run(
            cmd,
            check=True,
            text=True,
            input=input_text,
        )
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"Error al ejecutar docker: {exc}") from exc


@click.group(invoke_without_command=True)
@click.pass_context
def docker(ctx):
    """Grupo de comandos para la gestión de imágenes Docker."""

    # Si se invoca sin subcomando, mostrar menú interactivo.
    if ctx.invoked_subcommand is None:
        choices = [
            ("build", "build"),
            ("build (sin cache)", "build_no_cache"),
            ("save", "save"),
            ("push", "push"),
            ("tag", "tag"),
            ("create prod context", "create_prod_context"),
            ("deploy", "deploy"),
            ("remove prod context", "remove_prod_context"),
            ("login", "login"),
        ]
        selected = questionary.checkbox(
            "Selecciona las operaciones a ejecutar:",
            choices=[c[0] for c in choices],
        ).ask()


        if not selected:
            console.print("[yellow]No se seleccionaron operaciones.[/yellow]")
            return

        # Map from displayed name to internal id
        mapping = {display: internal for display, internal in choices}
        for choice_name in selected:
            op = mapping[choice_name]
            ctx.invoke(globals()[op])  # invoca la función click correspondiente


# ---------------------------------------------------------------------------
# Subcomandos
# ---------------------------------------------------------------------------

@docker.command()
def build():
    """Construye la imagen Docker usando cache."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_IMAGE_TAG", "DOCKER_USER"])

    tag = os.getenv("DOCKER_IMAGE_TAG")
    image = f"{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{tag}"

    console.print(f"[bold green]Construyendo imagen:[/bold green] {image}")
    _docker_cmd(["docker", "build", "-t", image, "."])


@docker.command("build-nocache")
def build_no_cache():
    """Construye la imagen Docker sin utilizar la cache."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_IMAGE_TAG", "DOCKER_USER"])

    tag = os.getenv("DOCKER_IMAGE_TAG")
    image = f"{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{tag}"

    console.print(f"[bold green]Construyendo imagen sin cache:[/bold green] {image}")
    _docker_cmd(["docker", "build", "--no-cache", "-t", image, "."])


@docker.command()
def save():
    """Guarda la imagen Docker en un archivo tar."""
    load_local_env()

    require_vars(
        [
            "DOCKER_IMAGE_NAME",
            "DOCKER_IMAGE_TAG",
            "DOCKER_SAVE_FILE",
            "DOCKER_FOLDER_SAVE",
            "DOCKER_USER",
        ]
    )

    tag = os.getenv("DOCKER_IMAGE_TAG")
    image = f"{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{tag}"
    save_path = os.path.join(os.getenv("DOCKER_FOLDER_SAVE"), os.getenv("DOCKER_SAVE_FILE"))

    console.print(f"[bold green]Guardando imagen en:[/bold green] {save_path}")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    _docker_cmd(["docker", "save", "-o", save_path, image])


@docker.command()
def push():
    """Envía la imagen Docker al registry configurado."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_IMAGE_TAG", "DOCKER_USER", "DOCKER_URL"])

    tag = os.getenv("DOCKER_IMAGE_TAG")
    image = f"{os.getenv('DOCKER_URL')}/{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{tag}"

    console.print(f"[bold green]Pushing imagen:[/bold green] {image}")
    _docker_cmd(["docker", "push", image])


@docker.command()
def tag():
    """Etiqueta la imagen con la etiqueta latest en el registry."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_IMAGE_TAG", "DOCKER_USER", "DOCKER_URL"])

    current = f"{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:{os.getenv('DOCKER_IMAGE_TAG')}"
    target = f"{os.getenv('DOCKER_URL')}/{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:latest"

    console.print(f"[bold green]Etiquetando imagen:[/bold green] {current} → {target}")
    _docker_cmd(["docker", "tag", current, target])


@docker.command()
def create_prod_context():
    """Crea un contexto Docker denominado 'prod'."""
    load_local_env()

    require_vars(["DOCKER_HOST_USER", "DOCKER_HOST_IP"])

    host_str = f"ssh://{os.getenv('DOCKER_HOST_USER')}@{os.getenv('DOCKER_HOST_IP')}"

    console.print(f"[bold green]Creando contexto prod:[/bold green] {host_str}")
    _docker_cmd(["docker", "context", "create", "prod", "--docker", f"host={host_str}"])


@docker.command()
def deploy():
    """Despliega la aplicación en el contexto 'prod' usando docker compose."""
    load_local_env()

    require_vars(["DOCKER_IMAGE_NAME", "DOCKER_USER", "DOCKER_URL"])

    image = f"{os.getenv('DOCKER_URL')}/{os.getenv('DOCKER_USER')}/{os.getenv('DOCKER_IMAGE_NAME')}:latest"

    console.print("[bold green]Desplegando en contexto prod...[/bold green]")

    # Extra: asegurarse de que el contexto existe intentando crear si falla
    try:
        _docker_cmd(["docker", "context", "inspect", "prod"])
    except click.ClickException:
        console.print("[yellow]Contexto 'prod' no existe. Creándolo...[/yellow]")
        ctx_user = os.getenv("DOCKER_HOST_USER")
        ctx_ip = os.getenv("DOCKER_HOST_IP")
        if ctx_user and ctx_ip:
            host_str = f"ssh://{ctx_user}@{ctx_ip}"
            _docker_cmd(["docker", "context", "create", "prod", "--docker", f"host={host_str}"])
        else:
            raise click.ClickException("No se pudo crear contexto 'prod'. Falta DOCKER_HOST_USER o DOCKER_HOST_IP")

    _docker_cmd(["docker", "--context", "prod", "pull", image])
    _docker_cmd(["docker", "--context", "prod", "compose", "up", "-d", "--remove-orphans"])


@docker.command()
def remove_prod_context():
    """Elimina el contexto Docker 'prod'."""
    load_local_env()

    console.print("[bold green]Eliminando contexto prod...[/bold green]")
    _docker_cmd(["docker", "context", "rm", "prod"])


@docker.command()
def login():
    """Inicia sesión en Docker Hub usando variables de entorno y contraseña solicitada."""
    load_local_env()

    require_vars(["DOCKER_HUB_URL", "DOCKER_HUB_USER"])

    docker_hub_url = os.getenv("DOCKER_HUB_URL")
    docker_hub_user = os.getenv("DOCKER_HUB_USER")

    password = questionary.password("Introduce la contraseña de Docker Hub:").ask()
    if not password:
        raise click.ClickException("Se requiere una contraseña para continuar.")

    console.print(f"[bold green]Iniciando sesión en {docker_hub_url}...[/bold green]")
    _docker_cmd(["docker", "login", docker_hub_url, "-u", docker_hub_user, "--password-stdin"], input_text=password) 