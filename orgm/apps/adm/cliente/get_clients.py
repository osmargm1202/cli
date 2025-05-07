from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import List
from orgm.apps.adm.db import Cliente
from rich.table import Table
from rich import box
from datetime import datetime
from orgm.stuff.spinner import spinner

console = Console()


def obtener_clientes() -> List[Cliente]:
    """Obtiene todos los clientes desde PostgREST"""
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Cliente

    try:
        response = requests.get(f"{POSTGREST_URL}/cliente", headers=headers, timeout=10)
        response.raise_for_status()

        clientes_data = response.json()
        clientes = [Cliente.model_validate(cliente) for cliente in clientes_data]
        return clientes
    except Exception as e:
        console.print(f"[bold red]Error al obtener clientes: {e}[/bold red]")
        return []


def mostrar_tabla_clientes(clientes: List) -> None:
    """
    Muestra una tabla con los clientes.

    Args:
        clientes (List): Lista de objetos Cliente para mostrar.
    """
    if not clientes:
        console.print("[bold yellow]No se encontraron clientes.[/bold yellow]")
        return

    # Crear tabla
    tabla = Table(
        title="[bold blue]Lista de Clientes[/bold blue]",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold cyan",
    )

    # Añadir columnas - Usar los nombres de campo del modelo Cliente
    tabla.add_column("ID", justify="right", style="dim")
    tabla.add_column("Nombre", style="green")
    tabla.add_column("Número/NIF", style="blue")  # Asumiendo que 'numero' es NIF/CIF
    tabla.add_column("Email", style="yellow")  # Asumiendo que es 'correo'
    tabla.add_column("Teléfono", style="magenta")
    tabla.add_column("Última Actualización", style="cyan")  # Cambiado de Fecha Alta

    # Añadir filas
    for cliente in clientes:
        # Formatear fecha
        fecha_actualizacion = getattr(cliente, "fecha_actualizacion", None)
        fecha_formateada = ""
        if fecha_actualizacion:
            try:
                # Pydantic puede devolver datetime o str, manejar ambos
                if isinstance(fecha_actualizacion, str):
                    fecha_obj = datetime.fromisoformat(
                        fecha_actualizacion.replace("Z", "+00:00")
                    )
                elif isinstance(fecha_actualizacion, datetime):
                    fecha_obj = fecha_actualizacion
                else:
                    fecha_obj = None

                if fecha_obj:
                    fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
            except (ValueError, TypeError):
                fecha_formateada = str(
                    fecha_actualizacion
                )  # Mostrar como string si falla el formato

        tabla.add_row(
            str(getattr(cliente, "id", "")),
            getattr(cliente, "nombre", ""),
            getattr(cliente, "numero", ""),  # Usar 'numero' para NIF/CIF
            getattr(cliente, "correo", ""),  # Usar 'correo' para Email
            getattr(cliente, "telefono", ""),
            fecha_formateada,  # Usar fecha formateada
        )

    # Mostrar tabla
    console.print(tabla)


def listar():
    """Comando para listar todos los clientes."""
    with spinner("Listando clientes..."):
        lista_clientes = obtener_clientes()
    mostrar_tabla_clientes(lista_clientes)
