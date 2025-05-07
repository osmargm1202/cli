from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import Optional
from orgm.apps.adm.db import Cliente
from rich.table import Table
from rich import box
from datetime import datetime
import typer
from orgm.stuff.spinner import spinner
from orgm.apps.adm.cliente.export_client import formatear_cliente_json

console = Console()


def obtener_cliente(id_cliente: int) -> Optional[Cliente]:
    """Obtiene un cliente por su ID"""
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Cliente

    try:
        response = requests.get(
            f"{POSTGREST_URL}/cliente?id=eq.{id_cliente}", headers=headers, timeout=10
        )
        response.raise_for_status()

        clientes_data = response.json()
        if not clientes_data:
            console.print(
                f"[yellow]No se encontró el cliente con ID {id_cliente}[/yellow]"
            )
            return None

        cliente = Cliente.model_validate(clientes_data[0])
        return cliente
    except Exception as e:
        console.print(
            f"[bold red]Error al obtener cliente {id_cliente}: {e}[/bold red]"
        )
        return None


def mostrar_detalle_cliente(cliente) -> None:
    """
    Muestra los detalles completos de un cliente.

    Args:
        cliente: Objeto Cliente con los datos.
    """
    if not cliente:
        console.print("[bold yellow]No se encontró el cliente.[/bold yellow]")
        return

    # Crear tabla de detalles
    tabla = Table(
        title=f"[bold blue]Detalles del Cliente: {getattr(cliente, 'nombre', '')}[/bold blue]",  # Usar getattr
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold cyan",
    )

    # Configurar columnas
    tabla.add_column("Campo", style="green")
    tabla.add_column("Valor", style="yellow")

    # Mapeo de campos y sus nombres para mostrar
    campos = [
        ("ID", "id"),
        ("Nombre", "nombre"),
        ("Nombre Comercial", "nombre_comercial"),
        ("Número/NIF", "numero"),
        ("Correo", "correo"),
        ("Dirección", "direccion"),
        ("Ciudad", "ciudad"),
        ("Provincia", "provincia"),
        ("Teléfono", "telefono"),
        ("Representante", "representante"),
        ("Teléfono Representante", "telefono_representante"),
        ("Extensión Representante", "extension_representante"),
        ("Celular Representante", "celular_representante"),
        ("Correo Representante", "correo_representante"),
        ("Tipo de Factura", "tipo_factura"),
        ("Última Actualización", "fecha_actualizacion"),
    ]

    # Añadir filas con los datos
    for etiqueta, campo in campos:
        valor = getattr(cliente, campo, "")  # Usar getattr
        if campo == "fecha_actualizacion" and valor:
            try:
                # Pydantic puede devolver datetime o str, manejar ambos
                if isinstance(valor, str):
                    fecha_obj = datetime.fromisoformat(valor.replace("Z", "+00:00"))
                elif isinstance(valor, datetime):
                    fecha_obj = valor
                else:
                    fecha_obj = None

                if fecha_obj:
                    valor = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
            except (ValueError, TypeError):
                valor = str(valor)  # Mostrar como string si falla el formato
        tabla.add_row(etiqueta, str(valor))

    # Mostrar tabla
    console.print(tabla)


def mostrar(
    id: int,
    formato_json: bool = typer.Option(False, "--json", help="Mostrar en formato JSON"),
):
    """Comando para mostrar detalles de un cliente."""
    with spinner(f"Obteniendo detalles del cliente {id}..."):
        cliente_obj = obtener_cliente(id)

    if not cliente_obj:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    if formato_json:
        contenido = formatear_cliente_json(cliente_obj)
        console.print(contenido)
    else:
        mostrar_detalle_cliente(cliente_obj)
