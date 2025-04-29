# -*- coding: utf-8 -*-
import os
import requests
import json
from pathlib import Path
from typing import List
import typer
from rich.console import Console

# Importaciones locales del proyecto
from orgm.stuff.ai import generate_text

# Crear consola para salida con Rich
console = Console()

def ai_prompt(
    prompt: List[str] = typer.Argument(..., help="Texto que describe la solicitud a la IA"),
    config_name: str = typer.Option("default", "--config", "-c", help="Nombre de la configuración del modelo IA")
) -> None:
    """Genera texto usando el servicio de IA"""
    # Unir el prompt que puede venir en múltiples palabras
    prompt_text = " ".join(prompt).strip()

    if not prompt_text:
        console.print("[bold red]Debe proporcionar un texto de entrada para la IA.[/bold red]")
        return

    resultado = generate_text(prompt_text, config_name)
    if resultado:
        # Mostrar la respuesta devuelta por la IA progresivamente para simular streaming
        console.print("[bold green]Respuesta IA:[/bold green] ", end="", flush=True)
        for char in str(resultado):
            print(char, end="", flush=True)  # imprime carácter por carácter
        print()  # nueva línea al finalizar

def ai_configs() -> None:
    """Lista las configuraciones disponibles en el servicio de IA"""
    API_URL = os.getenv("API_URL")
    if not API_URL:
        console.print("[bold red]Error: API_URL no está definida en las variables de entorno.[/bold red]")
        return

    # Obtener credenciales de Cloudflare Access
    CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
    CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

    # Configuración de los headers para la API
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Agregar headers de Cloudflare Access si están disponibles
    if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
        headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
        headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET

    try:
        response = requests.get(f"{API_URL}/configs", headers=headers, timeout=10)
        response.raise_for_status()

        configs = response.json()
        console.print("[bold green]Configuraciones disponibles:[/bold green]")
        for config in configs:
            console.print(f"  - {config}")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al comunicarse con el servicio: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error al procesar la respuesta: {e}[/bold red]")

def ai_config_upload(
    config_name: str = typer.Argument(..., help="Nombre de la configuración a subir"),
    config_file: str = typer.Argument(..., help="Ruta al archivo JSON que contiene la configuración")
) -> None:
    """Carga una configuración desde un archivo JSON al servicio de IA"""
    API_URL = os.getenv("API_URL")
    if not API_URL:
        console.print("[bold red]Error: API_URL no está definida en las variables de entorno.[/bold red]")
        return

    # Verificar si el archivo existe
    config_path = Path(config_file)
    if not config_path.exists():
        console.print(f"[bold red]Error: El archivo '{config_file}' no existe[/bold red]")
        return

    # Obtener credenciales de Cloudflare Access
    CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
    CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

    # Configuración de los headers para la API
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Agregar headers de Cloudflare Access si están disponibles
    if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
        headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
        headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET

    try:
        # Cargar el archivo JSON
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        response = requests.post(
            f"{API_URL}/configs/{config_name}", 
            json=config_data, 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()

        console.print(f"[bold green]Configuración '{config_name}' subida correctamente.[/bold green]")
    except json.JSONDecodeError:
        console.print(f"[bold red]Error: El archivo '{config_file}' no contiene JSON válido.[/bold red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al comunicarse con el servicio: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error al procesar la solicitud: {e}[/bold red]") 