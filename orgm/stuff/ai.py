import os
import requests
from dotenv import load_dotenv
from rich.console import Console
from typing import Optional
from orgm.stuff.spinner import spinner

console = Console()
load_dotenv(override=True)

# Obtener la URL base de la API desde las variables de entorno
API_URL = os.getenv("API_URL")
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

# Configuración de los headers para la API
headers = {"Content-Type": "application/json", "Accept": "application/json"}

# Agregar headers de Cloudflare Access si están disponibles
if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
    headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
    headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET


if not API_URL:
    console.print(
        "[bold yellow]Advertencia: API_URL no está definida en las variables de entorno.[/bold yellow]"
    )
    console.print(
        "[bold yellow]La generación automática de descripciones no estará disponible.[/bold yellow]"
    )


def generate_project_description(project_name: str) -> Optional[str]:
    """
    Genera una descripción para un proyecto basado en su nombre
    utilizando una API externa de IA.

    Args:
        project_name: Nombre del proyecto

    Returns:
        Una descripción generada o None si hubo un error
    """
    if not API_URL:
        console.print(
            "[bold yellow]No se puede generar descripción: URL de API no configurada[/bold yellow]"
        )
        return None

    try:
        request_data = {
            "text": project_name,
            "config_name": "descripcion_electromecanica",
        }
        with spinner("Generando descripción de proyecto..."):
            response = requests.post(
                f"{API_URL}/ai", json=request_data, headers=headers, timeout=30
            )
        response.raise_for_status()

        data = response.json()
        if "error" in data:
            console.print(
                f"[bold red]Error del servicio de IA: {data['error']}[/bold red]"
            )
            return None

        if "result" in data:
            return data["result"]

        return None
    except requests.exceptions.RequestException as e:
        console.print(
            f"[bold red]Error al comunicarse con el servicio de IA: {e}[/bold red]"
        )
        return None
    except Exception as e:
        console.print(f"[bold red]Error al generar descripción: {e}[/bold red]")
        return None
