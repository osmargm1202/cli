from typing import Optional, Any
from pathlib import Path
from rich.console import Console
from orgm.stuff.jsoneditor import JsonEditor

console = Console()

def json_edit(json_file_path: Optional[str] = None, initial_content: Optional[str] = None) -> Any:
    """Abre el editor Textual para el archivo .json.

    Args:
        json_file_path: Ruta al archivo JSON a editar. Si es None, se usa '.json' en CWD.
        initial_content: Contenido inicial para el editor, útil si el archivo no existe.

    Returns:
        "Guardado" si el usuario guardó.
        "Cancelado" si el usuario canceló.
        None si hubo un error al iniciar el editor.
    """
    target_path_str = json_file_path or str(Path.cwd() / ".json")
    try:
        app = JsonEditor(file_path=target_path_str, initial_content=initial_content)
        result = app.run()
        # El resultado puede ser "Guardado" o "Cancelado" o None si hay error interno
        return result # Retornar directamente el mensaje de salida de app.run()
    except Exception as e:
        console.print(f"[bold red]Error al iniciar el editor de .json:[/bold red] {e}")
        return None # Retornar None en caso de excepción