import json
import requests
import click
from dotenv import load_dotenv

import os

global url
global token

load_dotenv(override=True)

# url = os.getenv("URL")
url = os.getenv("URL2")


def get_token():
    try:
        with open("orgm/cache/token.json", "r") as f:
            token_data = json.load(f)
            token = token_data.get("access_token")
        return token
    except FileNotFoundError:
        click.echo("Error: Debe autenticarse primero usando el comando 'auth'."
        )
        return


def cambiar_clave():
    """Cambia la clave de acceso del usuario."""
    global token

    try:
        token = get_token()
        if token:
            new_password = click.prompt(
                "Ingresa tu nueva contraseña", hide_input=True, confirmation_prompt=True
            )

            response = requests.post(
                url=f"{url}/cambio-clave",
                headers={"Authorization": f"Bearer {token}"},
                json={"password": new_password},
            )

            if response.status_code == 200:
                click.echo("Contraseña cambiada exitosamente.")
            else:
                click.echo(
                    f"Error al cambiar la contraseña: {response.status_code} - {response.text}"
                )
        else:
            click.echo("Error: No se encontró un token de acceso.")
    except requests.RequestException as e:
        click.echo(f"Error al conectar con el servidor: {e}")


@click.command()
@click.help_option("-h", "--help", help="Muestra este mensaje de ayuda.")
@click.option(
    "-c",
    "--correo",
    prompt=True,
    help="Correo electronico sin @or-gm.com para autenticación",
)
@click.option(
    "-p",
    "--password",
    prompt=True,
    hide_input=True,
    # confirmation_prompt=True,
    help="Contraseña para autenticación",
)
# @click.argument("username")
# @click.argument("password")
def login(correo, password):
    """Autentica al usuario y obtiene un token de acceso"""
    global token

    correo = correo + "@or-gm.com"

    try:
        response = requests.post(
            url=f"{url}/auth",
            json={"correo": correo, "password": password},
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            conteo = response.json().get("conteo")
            if token:
                with open("orgm/cache/token.json", "w") as f:
                    json.dump({"access_token": token}, f)
                click.echo("Autenticación exitosa. Token guardado.")
                if conteo == 0:
                    click.echo("Ingresaste por primera vez.")
                    cambiar_clave()

            else:
                click.echo("Error: No se recibió un token.")
        else:
            click.echo(
                f"Error de autenticación: {response.status_code} - {response.text}"
            )

    except requests.RequestException as e:
        click.echo(f"Error al conectar con el servidor: {e}")
