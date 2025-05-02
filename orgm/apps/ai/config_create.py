import typer
import json
from pathlib import Path
from rich.console import Console
import questionary

console = Console()


def ai_config_create() -> None:
    """Crea una nueva configuración de IA interactivamente."""
    from orgm.apps.ai.modelos import ai_models_list
    
    config_name = typer.prompt("Nombre para la nueva configuración (ej. mi_config)")
    if not config_name:
        console.print("[bold red]El nombre de la configuración no puede estar vacío.[/bold red]")
        return
        
    # Obtener modelos de OpenAI
    available_models = ai_models_list()
    
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
    target_dir = Path(__file__).parent.parent.parent / "temp" / "ai"
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
    from orgm.apps.ai.jsonedit import json_edit
    exit_message = json_edit(str(config_file_path), initial_content=initial_json_content)
    
    # Procesar según el mensaje de salida del editor
    if exit_message == "Guardado":
        console.print(f"Archivo de configuración [cyan]{config_file_path.name}[/cyan] guardado localmente en {target_dir}.")
        # Preguntar si se quiere subir la configuración editada, default=False
        if typer.confirm(f"\n¿Deseas subir la configuración '{config_name}' desde '{config_file_path.name}' al servidor?", default=False):
            console.print("Intentando subir la configuración...")
            # Llamar a la función de subida
            from orgm.apps.ai.config_upload import ai_config_upload
            ai_config_upload()
            
            console.print("\n[green]Subida exitosa.[/green] Verificando lista de configuraciones actualizada...")
            from orgm.apps.ai.configs_select import ai_configs
            ai_configs() # Mostrar lista actualizada solo si la subida fue exitosa
        else:
            console.print(f"Subida cancelada por el usuario. El archivo local [cyan]{config_file_path.name}[/cyan] se conserva en {target_dir}.")

    elif exit_message == "Cancelado":
        console.print("[yellow]Edición cancelada. No se subirá la configuración.[/yellow]")
        console.print(f"Archivo local [cyan]{config_file_path.name}[/cyan] conservado en {target_dir} (puede tener contenido no guardado).")
            
    else: # Incluye None (error al iniciar editor) u otros mensajes inesperados
        console.print("[red]El editor se cerró inesperadamente o con un error. No se subirá la configuración.[/red]")
        console.print(f"Archivo local [cyan]{config_file_path.name}[/cyan] conservado en {target_dir}.")