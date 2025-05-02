import subprocess
from rich.console import Console

console = Console()

def upload() -> None:
    """Construye y sube el paquete ORGM CLI a PyPI."""
    console.print("Iniciando el proceso de construcción y subida del paquete...")
    
    commands = [
        ["uv", "pip", "install", "--upgrade", "pip"],
        ["uv", "pip", "install", "--upgrade", "build"],
        ["uv", "pip", "install", "--upgrade", "twine"],
        ["rm", "-rf", "dist/*"],
        ["uv", "run", "-m", "build"],
        # El comando twine upload necesita manejar el globbing. 
        # Usamos shell=True con precaución o manejamos el globbing en Python.
    # Por simplicidad aquí, y dado que el path es fijo, se usa shell=True.
        # Considerar alternativas más seguras si el path fuera dinámico.
        ["uv", "run", "twine", "upload", "dist/*"] 
    ]

    for cmd in commands:
        console.print(f"[cyan]Ejecutando: {' '.join(cmd) if isinstance(cmd, list) else cmd}[/cyan]")
        try:
            # Usamos check=True para que lance una excepción si el comando falla
            # Usamos shell=True solo para el comando que necesita expansión de glob (*)
            use_shell = isinstance(cmd, str)
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, shell=use_shell)
            console.print(result.stdout)
            if result.stderr:
                 console.print(f"[yellow]Stderr:[/yellow]\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Error al ejecutar el comando: {' '.join(e.cmd) if isinstance(e.cmd, list) else e.cmd}[/bold red]")
            console.print(f"[red]Código de salida:[/red] {e.returncode}")
            console.print(f"[red]Salida:[/red]\n{e.stdout}")
            console.print(f"[red]Error:[/red]\n{e.stderr}")
            # Detener el script si un comando falla
            return None
        except FileNotFoundError as e:
             console.print(f"[bold red]Error: Comando no encontrado - {e}. Asegúrate de que 'uv' y 'twine' estén instalados y en el PATH.[/bold red]")
             return None

    console.print("[bold green]Proceso de construcción y subida completado.[/bold green]")
