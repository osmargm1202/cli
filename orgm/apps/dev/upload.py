import subprocess
from rich.console import Console
import re  # Importar re para expresiones regulares
from pathlib import Path  # Importar Path para manejar archivos

console = Console()


def _increment_version():
    """Lee pyproject.toml, incrementa la versión patch y escribe el archivo."""
    pyproject_path = Path("pyproject.toml")
    try:
        content = pyproject_path.read_text()
        version_match = re.search(
            r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content, re.MULTILINE
        )
        if not version_match:
            console.print(
                "[bold red]Error: No se pudo encontrar la línea de versión en pyproject.toml[/bold red]"
            )
            return False

        major, minor, patch = map(int, version_match.groups())
        new_patch = patch + 1
        current_version = f"{major}.{minor}.{patch}"
        new_version = f"{major}.{minor}.{new_patch}"

        console.print(
            f"Actualizando versión de {current_version} a {new_version} en {pyproject_path}..."
        )

        new_content = re.sub(
            r'^version\s*=\s*".*?"',
            f'version = "{new_version}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )

        pyproject_path.write_text(new_content)
        console.print(
            f"[green]Versión actualizada a {new_version} en {pyproject_path}[/green]"
        )
        return True
    except FileNotFoundError:
        console.print(
            f"[bold red]Error: No se encontró el archivo {pyproject_path}[/bold red]"
        )
        return False
    except Exception as e:
        console.print(f"[bold red]Error al actualizar la versión: {e}[/bold red]")
        return False


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

    # Incrementar versión solo si todo lo anterior tuvo éxito
    console.print("\nIntentando incrementar la versión del paquete...")
    if _increment_version():
        console.print("[bold green]Versión incrementada con éxito.[/bold green]")
    else:
        console.print(
            "[bold yellow]No se pudo incrementar la versión automáticamente.[/bold yellow]"
        )
