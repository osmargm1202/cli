from rich.console import Console
from rich.table import Table
from orgm.apps.utils.rnc.api import buscar_empresa_en_dgii

console = Console()


def mostrar_busqueda(busqueda: str, activo: bool = True):
    """
    Realiza la búsqueda de una empresa utilizando la API existente
    y muestra los resultados en una tabla.
    """
    console.print(f"Buscando '{busqueda}' (Activo: {activo})...")
    resultado = buscar_empresa_en_dgii(busqueda, activo)

    if resultado is None:
        console.print("[bold red]Error al buscar la empresa.[/bold red]")
        return

    if not resultado:
        console.print("[yellow]No se encontraron empresas con ese criterio.[/yellow]")
        return

    # Crear tabla para mostrar resultados
    table = Table(
        title="Resultados de Búsqueda RNC",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("RNC/Cédula", style="dim", width=15)
    table.add_column("Nombre Comercial")
    table.add_column("Razón Social")
    table.add_column("Actividad")
    table.add_column("Estado", justify="right")

    for empresa in resultado:
        table.add_row(
            str(empresa.get("rnc", "N/A")),
            empresa.get("nombre", "N/A"),
            empresa.get("razon", "N/A"),
            empresa.get("descripcion", "N/A"),
            empresa.get("estado", "N/A"),
        )

    console.print(table)
