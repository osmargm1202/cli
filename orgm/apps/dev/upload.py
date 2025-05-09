import subprocess
from rich.console import Console
import re  # Importar re para expresiones regulares
from pathlib import Path  # Importar Path para manejar archivos

console = Console()


def upload() -> None:
    """Construye y sube el paquete ORGM CLI a PyPI, luego incrementa la versión."""
    console.print("Iniciando el proceso de construcción y subida del paquete...")

    commands = [
        ["uv", "pip", "install", "--upgrade", "pip"],
        ["uv", "pip", "install", "--upgrade", "build"],
        ["uv", "pip", "install", "--upgrade", "twine"],
        # ["rm", "-rf", "dist/*"],
        ["uv", "run", "-m", "build"],
        # El comando twine upload necesita manejar el globbing.
        # Usamos shell=True con precaución o manejamos el globbing en Python.
        # Por simplicidad aquí, y dado que el path es fijo, se usa shell=True.
        # Considerar alternativas más seguras si el path fuera dinámico.
        ["uv", "run", "twine", "upload", "dist/*"],
    ]

    for cmd in commands:
        cmd_str = " ".join(cmd)
        console.print(f"[cyan]Ejecutando: {cmd_str}[/cyan]")
        try:
            # Para twine upload dist/*, necesitamos que el shell expanda el *
            # O podríamos usar pathlib.glob en Python para encontrar los archivos
            # Vamos a intentar ejecutar twine directamente, asumiendo que dist/* es interpretado correctamente
            # o que solo hay un archivo esperado. Si falla, podríamos necesitar shell=True
            # o manejar el globbing explícitamente.
            use_shell = cmd[0] == "twine"  # Usar shell solo para twine upload

            # Ejecutar proceso
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=use_shell,
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                console.print(
                    f"[bold red]Error al ejecutar el comando: {cmd_str}[/bold red]"
                )
                console.print(f"[red]Código de salida:[/red] {process.returncode}")
                if stdout:
                    console.print(f"[yellow]Salida:[/yellow]\n{stdout}")
                if stderr:
                    console.print(f"[red]Error:[/red]\n{stderr}")
                return  # Detener si un comando falla
            else:
                if stdout:
                    console.print(stdout)
                if stderr:
                    console.print(
                        f"[yellow]Stderr:[/yellow]\n{stderr}"
                    )  # Mostrar stderr aunque el comando tenga éxito

        except FileNotFoundError as e:
            console.print(
                f"[bold red]Error: Comando no encontrado - {e}. Asegúrate de que '{cmd[0]}' esté instalado y en el PATH.[/bold red]"
            )
            return
        except Exception as e:  # Captura genérica para otros posibles errores
            console.print(
                f"[bold red]Error inesperado al ejecutar {' '.join(cmd)}: {e}[/bold red]"
            )
            return

    console.print("[bold blue]Proceso de construcción y subida completado.[/bold blue]")

