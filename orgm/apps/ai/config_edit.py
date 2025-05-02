from pathlib import Path
from typing import Optional
from rich.console import Console
import questionary
import typer
from orgm.apps.ai.jsonedit import json_edit

console = Console()

    
def ai_config_edit() -> None:
    """Edita una configuración de IA existente desde el directorio temp."""
    
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
    exit_message = json_edit(str(config_file_path))

    
    # Procesar según el mensaje de salida del editor
    if exit_message == "Guardado":
        console.print(f"Archivo de configuración [cyan]{config_file_path.name}[/cyan] guardado localmente en {target_dir}.")
        # Preguntar si se quiere subir la configuración editada, default=False
        if typer.confirm(f"\n¿Deseas subir la configuración actualizada '{config_name}' al servidor?", default=False):
            console.print("Intentando subir la configuración...")
            # Llamar a la función de subida
            from orgm.apps.ai.config_upload import ai_config_upload
            ai_config_upload()
            
            console.print("\n[green]Subida exitosa.[/green] Verificando lista de configuraciones actualizada...")
            from orgm.apps.ai.configs_select import ai_configs
            ai_configs() # Mostrar lista actualizada solo si la subida fue exitosa
        else:
            console.print(f"Subida cancelada por el usuario. El archivo local [cyan]{config_file_path.name}[/cyan] se conserva.")

    elif exit_message == "Cancelado":
        console.print("[yellow]Edición cancelada. Los cambios (si los hubo) no fueron guardados.[/yellow]")
        console.print(f"El archivo local [cyan]{config_file_path.name}[/cyan] se conserva sin modificar.")
            
    else: # Incluye None (error al iniciar editor) u otros mensajes inesperados
        console.print("[red]El editor se cerró inesperadamente o con un error. No se subió ninguna configuración.[/red]")
        console.print(f"El archivo local [cyan]{config_file_path.name}[/cyan] se conserva.") 