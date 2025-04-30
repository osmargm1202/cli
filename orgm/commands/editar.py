# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from typing import Optional
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
        text_area = TextArea(content, id="editor", language="dotenv", theme="github-dark")
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

def edit_env_variables(env_file_path: Optional[str] = None) -> bool:
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

# --- Editor genérico JSON ---

class JsonEditor(App):
    """Editor de archivos JSON con Textual y validación."""

    BINDINGS = [
        Binding(key="ctrl+s", action="save", description="Guardar"),
        Binding(key="ctrl+q", action="quit", description="Salir sin guardar"),
        Binding(key="f5", action="validate", description="Validar JSON"),
    ]

    CSS = EnvEditor.CSS + """ 
    #actions_container {
        height: auto;
        dock: bottom;
        padding: 0 1;
        align: right middle;
    }
    Button {
        margin-left: 1;
        min-width: 10;
    }
    /* Comentario CSS corregido 
    status_bar { 
        dock: bottom;
        height: 1;
        background: $panel-darken-1;
        color: $text-muted;
        padding: 0 1;
    } */
    """

    def __init__(self, file_path: str, initial_content: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = Path(file_path).resolve()
        self.initial_content = initial_content
        self.original_content = ""
        self.validation_status = "JSON no validado" # Estado inicial

    def compose(self) -> ComposeResult:
        yield Static(f"Editando: {self.file_path.name} (F5 Validar)", id="title")
        
        content = self._load_content()
        self.original_content = content
        
        # Usar resaltado de sintaxis JSON y un tema válido
        text_area = TextArea(content, id="editor", language="json", theme="vscode_dark")
        yield text_area
        
        # Añadir contenedor horizontal para los botones
        with Horizontal(id="actions_container"):
            yield Button("Guardar", id="save_button", variant="primary")
            yield Button("Cancelar", id="cancel_button", variant="error")
        
    def _load_content(self) -> str:
        """Carga contenido: usa initial_content si se provee, si no lee el archivo."""
        if self.initial_content is not None:
            console.print(f"Usando contenido inicial proporcionado para [cyan]{self.file_path.name}[/cyan]")
            return self.initial_content
        elif self.file_path.exists():
            try:
                content = self.file_path.read_text(encoding='utf-8')
                console.print(f"Cargado desde: [cyan]{self.file_path}[/cyan]")
                return content
            except Exception as e:
                console.print(f"[bold red]Error al leer {self.file_path.name}: {e}. Usando JSON vacío.[/bold red]")
                return "{\n    \"error\": \"No se pudo cargar el archivo\"\n}"
        else:
             console.print(f"Archivo [cyan]{self.file_path.name}[/cyan] no existe. Creando JSON básico.")
             return "{\n    \"nuevo_parametro\": \"valor\"\n}"

    def _validate_json(self, content: str) -> bool:
         """Intenta validar el contenido JSON."""
         try:
             json.loads(content)
             self.validation_status = "JSON Válido"
             # Actualizar la barra de estado si existe
             # status_bar = self.query_one("#status_bar", Static)
             # status_bar.update(f"[green]{self.validation_status}[/green]")
             return True
         except json.JSONDecodeError as e:
             self.validation_status = f"JSON Inválido: {e}"
             # Actualizar la barra de estado si existe
             # status_bar = self.query_one("#status_bar", Static)
             # status_bar.update(f"[bold red]{self.validation_status}[/bold red]")
             self.bell() # Sonido de error
             return False

    def action_validate(self) -> None:
        """Acción para validar el JSON en el editor."""
        text_area = self.query_one(TextArea)
        if self._validate_json(text_area.text):
             console.print("[green]El contenido JSON es válido.[/green]")
        else:
             console.print(f"[bold red]{self.validation_status}[/bold red]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejar clics en los botones Guardar/Cancelar."""
        print(f"DEBUG: Button pressed: {event.button.id}") # DEBUG
        if event.button.id == "save_button":
            self.action_save()
        elif event.button.id == "cancel_button":
            self.action_quit()

    def action_save(self) -> None:
        """Guarda el contenido si es JSON válido."""
        print("DEBUG: action_save called") 
        text_area = self.query_one(TextArea)
        content = text_area.text
        if self._validate_json(content):
            print("DEBUG: JSON is valid") 
            try:
                self.file_path.write_text(content, encoding='utf-8')
                print(f"DEBUG: File {self.file_path.name} written successfully") 
                # console.print(f"Archivo [cyan]{self.file_path.name}[/cyan] guardado.") # Mover feedback al llamador
                print("DEBUG: Calling self.exit(message='Guardado')") 
                self.exit(message="Guardado")
            except Exception as e:
                print(f"DEBUG: Error during file write: {e}") 
                self.bell()
                console.print(f"[bold red]Error al guardar {self.file_path.name}:[/bold red] {e}")
        else:
            print("DEBUG: JSON is invalid, save aborted") 
            self.bell()
            console.print("[bold yellow]No se puede guardar: El contenido no es JSON válido...[/bold yellow]")

    def action_quit(self) -> None:
        """Salir sin guardar."""
        print("DEBUG: action_quit called") 
        text_area = self.query_one(TextArea)
        # No es necesario imprimir aquí, el llamador lo indicará
        # if text_area.text != self.original_content:
        #     console.print("Saliendo sin guardar cambios.") 
        print("DEBUG: Calling self.exit(message='Cancelado')") 
        self.exit(message="Cancelado")

def edit_json_file(file_path: str, initial_content: Optional[str] = None) -> Optional[str]:
    """Abre el editor Textual para un archivo JSON. Devuelve el mensaje de salida ('Guardado', 'Cancelado') o None."""
    target_path = str(Path(file_path).resolve()) 
    result = None # Inicializar result
    try:
        app = JsonEditor(file_path=target_path, initial_content=initial_content)
        result = app.run()
        return 'Guardado' 
    except Exception as e:
        console.print(f"[bold red]Error al iniciar el editor JSON:[/bold red] {e}")
        return None 

# --- Bloque de prueba ---
if __name__ == "__main__":
    console.print("[yellow]Probando editor .env...[/yellow]")
    # edit_env_variables("test.env") 
    # if Path("test.env").exists(): os.remove("test.env")

    console.print("\n[yellow]Probando editor JSON...[/yellow]")
    test_json_path = "test_config.json"
    initial_json = json.dumps({"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 150}, indent=4)
    
    # Probar creando un archivo con contenido inicial
    console.print(f"Editando {test_json_path} con contenido inicial...")
    edit_json_file(test_json_path, initial_content=initial_json)
    if Path(test_json_path).exists(): 
        print(f"Contenido de {test_json_path} después de editar:")
        print(Path(test_json_path).read_text())
        os.remove(test_json_path)
        
    # Probar editando un archivo existente (crearlo primero)
    test_existing_json = "{\"existing\": true}"
    Path(test_json_path).write_text(test_existing_json)
    console.print(f"\nEditando {test_json_path} existente...")
    edit_json_file(test_json_path)
    if Path(test_json_path).exists(): 
        print(f"Contenido de {test_json_path} después de editar:")
        print(Path(test_json_path).read_text())
        os.remove(test_json_path)
        
    # Probar creando un archivo que no existe
    console.print(f"\nEditando {test_json_path} (no existente)...")
    edit_json_file(test_json_path)
    if Path(test_json_path).exists(): 
        print(f"Contenido de {test_json_path} después de editar:")
        print(Path(test_json_path).read_text())
        os.remove(test_json_path) 