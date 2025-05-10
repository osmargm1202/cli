from rich.table import Table
from rich.console import Console
import questionary

from orgm.apps.adm.db import Cotizacion
from orgm.apps.adm.cotizacion.get_quotation import obtener_cotizacion
from orgm.apps.adm.cotizacion.quotation_by_client import cotizaciones_por_cliente
from orgm.apps.adm.cotizacion.quotation_by_project import cotizaciones_por_proyecto


console = Console()


def mostrar_cotizaciones(cotizaciones):
    """Muestra una tabla con las cotizaciones"""
    if not cotizaciones:
        print("[yellow]No se encontraron cotizaciones[/yellow]")
        return

    table = Table(title="Cotizaciones")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Cliente", style="green")
    table.add_column("Proyecto", style="green")
    table.add_column("Descripción", style="white", overflow="fold")
    table.add_column("Subtotal", style="magenta")
    table.add_column("ITBIS", style="magenta")
    table.add_column("Indirectos", style="magenta")
    table.add_column("Total", style="yellow")

    for c in cotizaciones:
        total = f"{c['moneda']} {c.get('total', 0):,.2f}" if c.get("total") else "N/A"
        subtotal = f"{c['moneda']} {c.get('subtotal', 0):,.2f}"
        itbis = f"{c.get('itbism', 0):,.2f}"
        indirectos = f"{c.get('indirectos', 0):,.2f}"
        table.add_row(
            str(c["id"]),
            f"{c['cliente']['id']} - {c['cliente']['nombre']}"
            if "cliente" in c
            else str(c["id_cliente"]),
            f"{c['proyecto']['id']} - {c['proyecto']['nombre_proyecto']}"
            if "proyecto" in c
            else str(c["id_proyecto"]),
            (
                c.get("descripcion", "")[:60]
                + (
                    "..."
                    if c.get("descripcion") and len(c.get("descripcion")) > 60
                    else ""
                )
            ),
            subtotal,
            itbis,
            indirectos,
            total,
        )

    console.print(table)


def mostrar_cotizaciones_por_cliente(id_cliente: int):
    cotis = cotizaciones_por_cliente(id_cliente, 10)
    if not cotis:
        print("[yellow]No hay cotizaciones para este cliente[/yellow]")
        return
    mostrar_cotizaciones(cotis)
    # verificar si hay más de 10
    if len(cotis) == 10:
        # Hacer una consulta para contar total?
        mas = questionary.confirm("¿Mostrar más cotizaciones?", default=False).ask()
        if mas:
            cotis_all = cotizaciones_por_cliente(id_cliente, None)
            mostrar_cotizaciones(cotis_all)


def mostrar_cotizaciones_por_proyecto(id_proyecto: int):
    """Obtiene y muestra las cotizaciones para un ID de proyecto específico."""
    cotis = cotizaciones_por_proyecto(id_proyecto, 10)
    if not cotis:
        print("[yellow]No hay cotizaciones para este proyecto[/yellow]")
        return
    mostrar_cotizaciones(cotis)
    # verificar si hay más de 10
    if len(cotis) == 10:
        # Hacer una consulta para contar total? Mejor obtener todas si confirma
        mas = questionary.confirm("¿Mostrar más cotizaciones?", default=False).ask()
        if mas:
            cotis_all = cotizaciones_por_proyecto(id_proyecto, None)  # Obtener todas
            mostrar_cotizaciones(cotis_all)


def mostrar_cotizacion_detalle(cotizacion):
    """Muestra los datos completos de una cotización (modelo o dict)"""
    # Convert model to dict if needed
    if isinstance(cotizacion, Cotizacion):
        data = cotizacion.model_dump()
    else:
        data = cotizacion

    table = Table(title=f"Cotización ID: {data.get('id')}")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="green")

    for k, v in data.items():
        if k == 'id_cliente':
            table.add_row(str(k), f"{v} - {data['cliente']['nombre']}")
        elif k == 'id_proyecto':
            table.add_row(str(k), f"{v} - {data['proyecto']['nombre_proyecto']}")
        elif k == 'id_servicio':
            table.add_row(str(k), f"{v} - {data['servicio']['nombre']} - {data['servicio']['descripcion']}")
        elif k in ['cliente', 'proyecto', 'servicio']:
            continue
        else:
            table.add_row(str(k), str(v))

    console.print(table)


def mostrar_datalle_cotizacion(id_cotizacion: int):
    """Ver detalles de una cotización"""
    cot = obtener_cotizacion(id_cotizacion)
    if not cot:
        print(
            f"[bold red]No se encontró la cotización con ID {id_cotizacion}[/bold red]"
        )
        return
    mostrar_cotizacion_detalle(cot)
