import os
import requests
import json
from typing import List
from rich.console import Console

console = Console()

def ai_models_list() -> List[str]:
    """Obtiene la lista de modelos disponibles desde la API de OpenAI."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        console.print("[bold yellow]Advertencia: OPENAI_API_KEY no está definida. No se pueden listar modelos de OpenAI.[/bold yellow]")
        return []

    api_url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {openai_api_key}"}

    model_ids = []
    try:
        console.print("Obteniendo lista de modelos de OpenAI...")
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Filtrar y ordenar modelos (ej: incluir gpt, o1, o4)
        model_ids = sorted([
            model["id"] for model in data.get("data", [])
            if model.get("id", "").startswith(("gpt-", "o1-", "o4-"))
        ])
        
        if not model_ids:
             console.print("[yellow]No se encontraron modelos GPT/O* en la respuesta de la API.[/yellow]")
        
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al contactar la API de OpenAI: {e}[/bold red]")
    except json.JSONDecodeError:
        console.print("[bold red]Error: La respuesta de la API de OpenAI no es JSON válido.[/bold red]")
    except Exception as e:
         console.print(f"[bold red]Error inesperado al obtener modelos: {e}[/bold red]")
         
    return model_ids