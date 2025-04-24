# -*- coding: utf-8 -*-
import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Button, TextArea, Static
from textual.containers import Container, Horizontal
from rich.console import Console

console = Console()

class EnvEditor(App):
    """Editor de variables de entorno"""
    CSS = """
    #editor {
        height: 1fr;
        margin: 1;
    }
    
    TextArea {
        height: 100%;
        width: 100%;
        border: solid $accent;
    }
    
    #actions {
        height: auto;
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
        align: right middle;
    }
    
    Button {
        margin-right: 1;
    }
    
    #title {
        text-align: center;
        background: $accent;
        color: $text;
        padding: 1;
        margin-bottom: 1;
        text-style: bold;
    }
    """
    
    def __init__(self, env_file_path=None):
        super().__init__()
        self.env_file_path = env_file_path or os.path.join(os.getcwd(), ".env")
        
    def compose(self) -> ComposeResult:
        """Crear la interfaz de usuario"""
        yield Static("Editor de Variables de Entorno (.env)", id="title")
        
        content = ""
        env_example_path = os.path.join(os.path.dirname(self.env_file_path), ".env.example")
        orgm_env_example_path = os.path.join(os.getcwd(), "orgm", ".env.example")

        console.print(f"Intentando cargar desde: {self.env_file_path}")
        console.print(f"Intentando cargar desde: {orgm_env_example_path}")
        
        # 1. Intentar cargar desde .env si existe
        if os.path.exists(self.env_file_path):
            try:
                with open(self.env_file_path, "r") as f:
                    content = f.read()
            except Exception as e:
                content = f"# Error al leer el archivo: {str(e)}"
        # 2. Si no existe .env, intentar cargar desde ormg/.env.example
        elif os.path.exists(orgm_env_example_path):
            try:
                with open(orgm_env_example_path, "r") as f:
                    content = f.read()
                content = f"# Contenido cargado desde orgm/.env.example\n{content}"
                # Crear el archivo .env con el contenido de ormg/.env.example
                with open(self.env_file_path, "w") as f:
                    f.write(content)
                console.print(f"Archivo [bold]{self.env_file_path}[/bold] creado con variables de [bold]ormg/.env.example[/bold]")
            except Exception as e:
                content = f"# Error al leer ormg/.env.example: {str(e)}"
        # 3. Si no existe ormg/.env.example, intentar cargar desde .env.example local
        elif os.path.exists(env_example_path):
            try:
                with open(env_example_path, "r") as f:
                    content = f.read()
                content = f"# Contenido cargado desde .env.example\n{content}"
            except Exception as e:
                content = f"# Error al leer .env.example: {str(e)}"
        # 4. Si no existe ninguno, usar contenido predeterminado
        else:
            content = """   # Archivo de variables de entorno
                            # Formato: VARIABLE=valor
                            # Ejemplo:
                            # API_KEY=abc123
                            # DATABASE_URL=postgres://user:pass@localhost/dbname"""
        
        yield TextArea(content, id="editor")
        
        with Horizontal(id="actions"):
            yield Button("Guardar", id="save_button", variant="primary")
            yield Button("Cancelar", id="cancel_button", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejar eventos de los botones"""
        if event.button.id == "save_button":
            self.save_variables()
            self.exit()
        elif event.button.id == "cancel_button":
            self.exit()
    
    def save_variables(self) -> None:
        """Guardar contenido al archivo .env"""
        text_area = self.query_one(TextArea)
        content = text_area.text
        
        try:
            with open(self.env_file_path, "w") as f:
                f.write(content)
            console.print(f"Variables guardadas en [bold]{self.env_file_path}[/bold]")
        except Exception as e:
            console.print(f"[bold red]Error al guardar variables:[/bold red] {str(e)}")

def edit_env_variables():
    """Función principal para editar variables de entorno"""
    try:
        app = EnvEditor()
        app.run()
    except Exception as e:
        console.print(f"[bold red]Error al editar variables de entorno:[/bold red] {str(e)}")
        return False
    return True 