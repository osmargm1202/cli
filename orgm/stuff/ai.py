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


def generate_text(text: str, config_name: str) -> Optional[str]:
    """Llama al endpoint de IA para generar un contenido basado en el parámetro *text* y la configuración *config_name*.

    Args:
        text: Texto de entrada que describe el contexto o prompt.
        config_name: Nombre de la configuración del modelo / plantilla que la API debe aplicar.

    Returns:
        Cadena con el resultado enviado por la API o ``None`` si ocurre un error.
    """
    if not API_URL:
        console.print(
            "[bold yellow]No se puede generar descripción: URL de API no configurada[/bold yellow]"
        )
        return None

    request_data = {"text": text, "config_name": config_name}

    try:
        with spinner("Obteniendo respuesta IA..."):
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

        # Algunos servicios devuelven la respuesta en 'result', otros en 'data' u otro campo.
        return data["response"]

    except requests.exceptions.RequestException as e:
        console.print(
            f"[bold red]Error al comunicarse con el servicio de IA: {e}[/bold red]"
        )
        return None
    except Exception as e:
        console.print(f"[bold red]Error al procesar respuesta IA: {e}[/bold red]")
        return None


def generate_project_description(project_name: str) -> Optional[str]:
    """Conveniencia: genera descripción electromecánica para un proyecto.

    Mantiene la firma anterior para no romper código existente
    (por ejemplo, *orgm/adm/proyectos.py*).
    """
    return generate_text(project_name, "descripcion_electromecanica")
