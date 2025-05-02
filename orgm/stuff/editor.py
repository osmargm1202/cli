
import os
import json
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Button, TextArea, Static, Footer
from textual.containers import Container, VerticalScroll, Horizontal
from textual.binding import Binding
from rich.console import Console
from rich.syntax import Syntax

console = Console()

# --- Editor para .env --- 

class EnvEditor(App):
    """Editor de variables de entorno con Textual."""

    BINDINGS = [
        Binding(key="ctrl+s", action="save", description="Guardar"),
        Binding(key="ctrl+q", action="quit", description="Salir sin guardar"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }
    
    #title {
        dock: top;
        width: 100%;
        text-align: center;
        background: $accent;
        color: $text;
        padding: 1;
        margin-bottom: 1;
        text-style: bold;
    }

    TextArea {
        height: 1fr;
        width: 1fr;
        border: round $accent;
        margin: 1 0;
    }
    
    Footer {
         dock: bottom;
    }
    """

    def __init__(self, file_path: str = ".env", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = Path(file_path).resolve()
        self.original_content = ""

    def compose(self) -> ComposeResult:
        yield Static(f"Editando: {self.file_path.name} (Ctrl+S Guardar, Ctrl+Q Salir)", id="title")
        
        content = self._load_content()
        self.original_content = content # Guardar contenido original
        
        # Usar Rich Syntax para resaltar .env si es posible
        text_area = TextArea(content, id="editor", language="dotenv", theme="vscode_dark")
        yield text_area
        yield Footer()
        
    def _load_content(self) -> str:
        """Carga el contenido inicial para el editor."""
        content = ""       
        # Prioridad: 1. Archivo existente, 2. ormg/.env.example, 3. .env.example, 4. Default
        orgm_env_example_path = Path(__file__).parent.parent / ".env.example"
        local_env_example_path = self.file_path.parent / ".env.example"

        if self.file_path.exists():
            try:
                content = self.file_path.read_text(encoding='utf-8')
                console.print(f"Cargado desde: [cyan]{self.file_path}[/cyan]")
            except Exception as e:
                content = f"# Error al leer {self.file_path.name}: {e}"
        elif orgm_env_example_path.exists():
            try:
                content = orgm_env_example_path.read_text(encoding='utf-8')
                content = f"# Contenido inicial desde {orgm_env_example_path.name}\n{content}"                
                console.print(f"Usando plantilla desde: [cyan]{orgm_env_example_path}[/cyan]")
                # No creamos .env automáticamente aquí, solo cargamos el ejemplo
            except Exception as e:
                content = f"# Error al leer {orgm_env_example_path.name}: {e}"
        elif local_env_example_path.exists():
             try:
                content = local_env_example_path.read_text(encoding='utf-8')
                content = f"# Contenido inicial desde {local_env_example_path.name}\n{content}"
                console.print(f"Usando plantilla desde: [cyan]{local_env_example_path}[/cyan]")
             except Exception as e:
                 content = f"# Error al leer {local_env_example_path.name}: {e}"
        else:
            content = """# Archivo de variables de entorno (.env)
# Formato: VARIABLE=valor
# Ejemplo:
# API_KEY=abc123xyz
# DATABASE_URL=postgres://user:pass@host:port/db
"""
            console.print("Usando plantilla predeterminada para .env")
            
        return content

    def action_save(self) -> None:
        """Guardar el contenido actual en el archivo."""
        text_area = self.query_one(TextArea)
        content = text_area.text
        try:
            self.file_path.write_text(content, encoding='utf-8')
            console.print(f"Archivo [cyan]{self.file_path.name}[/cyan] guardado.")
            self.exit(message="Guardado")
        except Exception as e:
            self.bell()
            console.print(f"[bold red]Error al guardar {self.file_path.name}:[/bold red] {e}")
            # Podríamos mostrar un diálogo de error aquí en lugar de salir

    def action_quit(self) -> None:
        """Salir sin guardar."""
        text_area = self.query_one(TextArea)
        if text_area.text != self.original_content:
             # Podríamos añadir una confirmación aquí si hay cambios sin guardar
             console.print("Saliendo sin guardar cambios.")
             pass
        self.exit(message="Cancelado")
