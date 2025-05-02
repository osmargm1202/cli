from pathlib import Path
from rich.console import Console

console = Console()

def mostrar_ayuda():
    """Muestra el contenido del archivo comandos.md"""
    try:
        # Obtener la ruta del script actual
        script_dir = Path(__file__).parent.parent.parent
        comandos_path = script_dir / "comandos.md"

        
        # Leer y mostrar el archivo
        with open(comandos_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        console.print(contenido)
    except Exception as e:
        console.print(f"[bold red]Error al mostrar la ayuda: {e}[/bold red]")


if __name__ == "__main__":
    mostrar_ayuda() 