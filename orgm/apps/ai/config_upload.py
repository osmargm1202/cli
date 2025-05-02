import os
import requests
import json
from pathlib import Path
from rich.console import Console
from orgm.apis.header import get_headers_json
import questionary
console = Console()

def ai_config_upload() -> None: 
    """Lista y permite seleccionar un archivo de config local para subirlo al servicio de IA."""
    
    # Definir directorio de destino y asegurarse de que exista
    target_dir = Path(__file__).parent.parent.parent / "temp" / "ai"
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