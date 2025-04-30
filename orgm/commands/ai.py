# -*- coding: utf-8 -*-
import os
import requests
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import typer
from rich.console import Console
import questionary

# Importaciones locales del proyecto
from orgm.apis.ai import generate_text
from orgm.apis.header import get_headers_json
# Importar el editor JSON
from orgm.commands.editar import edit_json_file

# Crear consola para salida con Rich
console = Console()

# --- Función auxiliar para obtener modelos de OpenAI ---

def _get_openai_models() -> List[str]:
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
        console.print("[bold green]Respuesta IA:[/bold green] ", end="")
        for char in str(resultado):
            console.print(char, end="")
        console.print()

def ai_configs() -> None:
    """Lista las configuraciones disponibles en el servicio de IA"""
    API_URL = os.getenv("API_URL")
    if not API_URL:
        console.print("[bold red]Error: API_URL no está definida en las variables de entorno.[/bold red]")
        return

    # Usar la función importada para obtener los headers
    headers = get_headers_json()

    try:
        response = requests.get(f"{API_URL}/configs", headers=headers, timeout=10)
        response.raise_for_status()

        configs = response.json()
        console.print("[bold green]Configuraciones disponibles:[/bold green]")
        # Asumiendo que 'configs' es una lista de nombres o un dict
        if isinstance(configs, list):
            for config_name in sorted(configs): # Ordenar alfabéticamente
                 console.print(f"  - {config_name}")
        elif isinstance(configs, dict):
             # Si es un dict, podríamos querer listar las claves
             for config_name in sorted(configs.keys()):
                 console.print(f"  - {config_name}")
        else:
             console.print(f"  Respuesta inesperada: {configs}")

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al comunicarse con el servicio: {e}[/bold red]")
    except json.JSONDecodeError:
        console.print("[bold red]Error: La respuesta del servicio no es JSON válido.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error al procesar la respuesta: {e}[/bold red]")

def ai_config_upload() -> None: # Cambiado a None, la lógica de retorno bool ya no aplica directamente aquí
    """Lista y permite seleccionar un archivo de config local para subirlo al servicio de IA."""
    
    # Definir directorio de destino y asegurarse de que exista
    target_dir = Path(__file__).parent.parent / "temp" / "ai"
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        console.print(f"[bold red]Error al acceder/crear el directorio {target_dir}: {e}[/bold red]")
        return

    # Listar archivos JSON en el directorio
    json_files = sorted(list(target_dir.glob("*.json")))

    if not json_files:
        console.print(f"[yellow]No se encontraron archivos de configuración (.json) en {target_dir}.[/yellow]")
        console.print("Puedes crear uno usando: orgm ai create")
        return

    # Permitir seleccionar un archivo
    try:
        selected_path_str = questionary.select(
            "Selecciona el archivo de configuración a subir:",
            choices=[file.name for file in json_files] # Mostrar solo nombres de archivo
        ).ask()

        if selected_path_str is None: # Usuario canceló (Ctrl+C)
            console.print("[yellow]Selección cancelada.[/yellow]")
            return
            
    except Exception as e:
        console.print(f"[red]Error durante la selección interactiva: {e}[/red]")
        return
        
    # Construir la ruta completa y extraer el nombre de la configuración
    config_file_path = target_dir / selected_path_str
    config_name = config_file_path.stem # Nombre del archivo sin extensión

    # --- Lógica de subida original adaptada ---
    API_URL = os.getenv("API_URL")
    if not API_URL:
        console.print("[bold red]Error: API_URL no está definida en las variables de entorno.[/bold red]")
        return # Cambiado de return False

    headers = get_headers_json()

    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        if not isinstance(config_data, dict):
             console.print(f"[bold red]Error: El archivo '{config_file_path.name}' no contiene un objeto JSON válido (diccionario).[/bold red]")
             return # Cambiado de return False

        console.print(f"Subiendo configuración '{config_name}' desde '{config_file_path.name}'...")
        response = requests.post(
            f"{API_URL}/configs/{config_name}",
            json=config_data,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()

        console.print(f"[bold green]Configuración '{config_name}' subida correctamente.[/bold green]")
        # Podríamos llamar a ai_configs() aquí si quisiéramos verificar siempre
        # console.print("\nVerificando lista de configuraciones actualizada...")
        # ai_configs()
        # return True # Ya no necesario

    except json.JSONDecodeError:
        console.print(f"[bold red]Error: El archivo '{config_file_path.name}' no contiene JSON válido.[/bold red]")
        # return False
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al comunicarse con el servicio: {e}[/bold red]")
        try:
            error_data = response.json()
            console.print(f"  Detalles: {error_data.get('detail', 'No disponible')}")
        except:
            pass 
        # return False
    except Exception as e:
        console.print(f"[bold red]Error inesperado al procesar la solicitud: {e}[/bold red]")
        # return False
    # --- Fin lógica de subida adaptada ---

def ai_config_create() -> None:
    """Crea una nueva configuración de IA interactivamente."""
    
    config_name = typer.prompt("Nombre para la nueva configuración (ej. mi_config)")
    if not config_name:
        console.print("[bold red]El nombre de la configuración no puede estar vacío.[/bold red]")
        return
        
    # Obtener modelos de OpenAI
    available_models = _get_openai_models()
    
    selected_model = None
    if available_models:
        try:
            # Usar questionary para seleccionar el modelo
            selected_model = questionary.select(
                "Selecciona el modelo de IA a utilizar:",
                choices=available_models
            ).ask()
            
            if selected_model is None: # El usuario presionó Ctrl+C
                 console.print("[yellow]Selección de modelo cancelada.[/yellow]")
                 return
                 
        except Exception as e:
             console.print(f"[red]Error durante la selección interactiva: {e}. Usando valor predeterminado.[/red]")
             selected_model = "gpt-3.5-turbo" # Fallback
    else:
        console.print("\nNo se pudo obtener la lista de modelos de OpenAI.")
        selected_model = typer.prompt("Introduce manually el nombre del modelo", default="gpt-3.5-turbo")

    # Crear estructura JSON de ejemplo con el modelo seleccionado y el nuevo formato
    default_config = {
        "model": selected_model,
        "messages": [
            {
                "role": "system", # Usar 'system' para la instrucción inicial
                "content": "Eres un ingeniero ." # Añadir espacio al final si es necesario
            }
        ],
        "temperature": 0.7,
        "reasoning": {"effort": "medium"}, # Añadir campo reasoning
        "max_output_tokens": 10000, # Cambiar nombre y valor de max_tokens
        "frequency_penalty": 0.0 # Añadir frequency_penalty
        # Eliminar "system_prompt" y "user_prompt_template"
    }
    
    # Convertir a JSON string formateado
    initial_json_content = json.dumps(default_config, indent=4)
    
    # --- Cambio de ruta y creación de directorio ---
    # Definir directorio de destino
    target_dir = Path(__file__).parent.parent / "temp" / "ai"
    # Asegurar que el directorio exista
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        console.print(f"[bold red]Error al crear el directorio {target_dir}: {e}[/bold red]")
        return
        
    # Definir ruta del archivo JSON dentro del directorio
    config_file_path = target_dir / f"{config_name}.json"
    # --- Fin cambio de ruta --- 
    
    console.print(f"\nSe generará un archivo de configuración JSON en: [cyan]{config_file_path}[/cyan]")
    console.print("Puedes editar los parámetros antes de subir la configuración.")
    
    # Abrir el editor JSON y capturar el mensaje de salida
    exit_message = edit_json_file(str(config_file_path), initial_content=initial_json_content)
    
    # Procesar según el mensaje de salida del editor
    if exit_message == "Guardado":
        console.print(f"Archivo de configuración [cyan]{config_file_path.name}[/cyan] guardado localmente en {target_dir}.")
        # Preguntar si se quiere subir la configuración editada, default=False
        if typer.confirm(f"\n¿Deseas subir la configuración '{config_name}' desde '{config_file_path.name}' al servidor?", default=False):
            console.print("Intentando subir la configuración...")
            # Llamar a la función de subida
            ai_config_upload()
            
            console.print("\n[green]Subida exitosa.[/green] Verificando lista de configuraciones actualizada...")
            ai_configs() # Mostrar lista actualizada solo si la subida fue exitosa
        else:
            console.print(f"Subida cancelada por el usuario. El archivo local [cyan]{config_file_path.name}[/cyan] se conserva en {target_dir}.")

    elif exit_message == "Cancelado":
        console.print("[yellow]Edición cancelada. No se subirá la configuración.[/yellow]")
        console.print(f"Archivo local [cyan]{config_file_path.name}[/cyan] conservado en {target_dir} (puede tener contenido no guardado).")
            
    else: # Incluye None (error al iniciar editor) u otros mensajes inesperados
        console.print("[red]El editor se cerró inesperadamente o con un error. No se subirá la configuración.[/red]")
        console.print(f"Archivo local [cyan]{config_file_path.name}[/cyan] conservado en {target_dir}.")

def ai_config_edit() -> None:
    """Edita una configuración de IA existente desde el directorio temp."""
    
    # Definir directorio de destino y asegurarse de que exista
    target_dir = Path(__file__).parent.parent / "temp" / "ai"
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        console.print(f"[bold red]Error al acceder/crear el directorio {target_dir}: {e}[/bold red]")
        return

    # Listar archivos JSON en el directorio
    json_files = sorted(list(target_dir.glob("*.json")))

    if not json_files:
        console.print(f"[yellow]No se encontraron archivos de configuración (.json) en {target_dir}.[/yellow]")
        console.print("Puedes crear uno usando: orgm ai create")
        return

    # Permitir seleccionar un archivo
    try:
        selected_path = questionary.select(
            "Selecciona el archivo de configuración a editar:",
            choices=[file.name for file in json_files] # Mostrar solo nombres de archivo
        ).ask()

        if selected_path is None: # Usuario canceló (Ctrl+C)
            console.print("[yellow]Selección cancelada.[/yellow]")
            return
            
    except Exception as e:
        console.print(f"[red]Error durante la selección interactiva: {e}[/red]")
        return
        
    # Construir la ruta completa y extraer el nombre de la configuración
    config_file_path = target_dir / selected_path
    config_name = config_file_path.stem # Nombre del archivo sin extensión

    console.print(f"\nEditando configuración '{config_name}' desde [cyan]{config_file_path}[/cyan]...")

    # Abrir el editor JSON (sin contenido inicial, carga desde archivo)
    exit_message = edit_json_file(str(config_file_path))

    
    # Procesar según el mensaje de salida del editor
    if exit_message == "Guardado":
        console.print(f"Archivo de configuración [cyan]{config_file_path.name}[/cyan] guardado localmente en {target_dir}.")
        # Preguntar si se quiere subir la configuración editada, default=False
        if typer.confirm(f"\n¿Deseas subir la configuración actualizada '{config_name}' al servidor?", default=False):
            console.print("Intentando subir la configuración...")
            # Llamar a la función de subida
            ai_config_upload()
            
            console.print("\n[green]Subida exitosa.[/green] Verificando lista de configuraciones actualizada...")
            ai_configs() # Mostrar lista actualizada solo si la subida fue exitosa
        else:
            console.print(f"Subida cancelada por el usuario. El archivo local [cyan]{config_file_path.name}[/cyan] se conserva.")

    elif exit_message == "Cancelado":
        console.print("[yellow]Edición cancelada. Los cambios (si los hubo) no fueron guardados.[/yellow]")
        console.print(f"El archivo local [cyan]{config_file_path.name}[/cyan] se conserva sin modificar.")
            
    else: # Incluye None (error al iniciar editor) u otros mensajes inesperados
        console.print("[red]El editor se cerró inesperadamente o con un error. No se subió ninguna configuración.[/red]")
        console.print(f"El archivo local [cyan]{config_file_path.name}[/cyan] se conserva.") 