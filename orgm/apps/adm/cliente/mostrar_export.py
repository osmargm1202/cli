from orgm.apps.adm.cliente.get_client import obtener_cliente
from orgm.apps.adm.cliente.export_client import exportar_cliente
from orgm.stuff.spinner import spinner
from rich.console import Console
import typer

console = Console()


def exportar(
    id: int,
    clipboard: bool = typer.Option(
        False, "--clipboard", help="Copiar al portapapeles en lugar de mostrar"
    ),
):
    """Comando para exportar un cliente a JSON."""
    with spinner(f"Obteniendo datos del cliente {id} para exportar..."):
        cliente = obtener_cliente(id)

    if not cliente:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    exito, contenido = exportar_cliente(cliente, "json")

    if exito:
        if clipboard:
            try:
                import pyperclip

                pyperclip.copy(contenido)
                console.print(
                    "[bold green]Cliente exportado a JSON y copiado al portapapeles.[/bold green]"
                )
            except ImportError:
                console.print(
                    "[bold yellow]La funcionalidad de portapapeles requiere la librería 'pyperclip'.[/bold yellow]"
                )
                console.print(
                    "[bold yellow]Instálala con: pip install pyperclip[/bold yellow]"
                )
                console.print("\nContenido JSON:")
                console.print(contenido)
            except Exception as e:
                console.print(
                    f"[bold red]Error al copiar al portapapeles: {e}[/bold red]"
                )
                console.print("\nContenido JSON:")
                console.print(contenido)
        else:
            console.print(contenido)
    else:
        console.print(f"[bold red]Error al exportar cliente: {contenido}[/bold red]")
