from typing import Optional
from pathlib import Path
from rich.console import Console
from orgm.stuff.editor import EnvEditor

console = Console()

def env_edit(env_file_path: Optional[str] = None) -> bool:
    """Abre el editor Textual para el archivo .env."""
    target_path = env_file_path or str(Path.cwd() / ".env")
    try:
        app = EnvEditor(file_path=target_path)
        result = app.run()
        # El resultado puede ser "Guardado" o "Cancelado"
        return "Guardado"
    except Exception as e:
        console.print(f"[bold red]Error al iniciar el editor de .env:[/bold red] {e}")
        return False