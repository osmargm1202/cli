# -*- coding: utf-8 -*-
import typer
from typing import List, Optional
from datetime import datetime
import questionary
from rich.console import Console
from rich.table import Table
from orgm.adm.pago import registrar_pago, obtener_pagos, asignar_pago_a_cotizacion
from orgm.adm.clientes import obtener_clientes, obtener_cliente
from orgm.adm.cotizaciones import cotizaciones_por_cliente, obtener_cotizacion
from orgm.stuff.spinner import spinner

console = Console()

def pago_registrar_command(
    id_cliente: int = typer.Argument(..., help="ID del cliente asociado al pago"),
    monto: float = typer.Argument(..., help="Monto del pago"),
    moneda: str = typer.Option("RD$", help="Moneda del pago (ej. RD$, USD)"),
    fecha: str = typer.Option(None, help="Fecha del pago en formato YYYY-MM-DD (por defecto hoy)"),
    comprobante: str = typer.Option("", help="Número de comprobante o referencia")
):
    """Registra un nuevo pago en el sistema."""
    # Si no se proporciona fecha, usar la fecha actual
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d")
    
    # Verificar que el cliente existe
    with spinner(f"Verificando cliente ID {id_cliente}..."):
        cliente = obtener_cliente(id_cliente)
    
    if not cliente:
        console.print(f"[bold red]Error: No se encontró un cliente con ID {id_cliente}[/bold red]")
        raise typer.Exit(code=1)
    
    # Mostrar confirmación
    console.print(f"Registrando pago para [bold]{cliente.get('nombre', f'Cliente {id_cliente}')}[/bold]")
    console.print(f"Monto: [bold]{monto} {moneda}[/bold]")
    console.print(f"Fecha: [bold]{fecha}[/bold]")
    if comprobante:
        console.print(f"Comprobante: [bold]{comprobante}[/bold]")
    
    # Registrar el pago
    with spinner("Registrando pago..."):
        resultado = registrar_pago(id_cliente, moneda, monto, fecha, comprobante)
    
    if resultado:
        console.print(f"[bold green]✓ Pago registrado correctamente con ID {resultado.get('id')}[/bold green]")
    else:
        console.print("[bold red]✗ Error al registrar el pago[/bold red]")
        raise typer.Exit(code=1)
    
    # Preguntar si desea asignar el pago a alguna cotización
    asignar = typer.confirm("¿Desea asignar este pago a una cotización?", default=False)
    if asignar:
        # Obtener cotizaciones del cliente
        with spinner(f"Obteniendo cotizaciones del cliente {id_cliente}..."):
            cotizaciones = cotizaciones_por_cliente(id_cliente)
        
        if not cotizaciones:
            console.print("[yellow]El cliente no tiene cotizaciones disponibles para asignar el pago.[/yellow]")
            return
        
        # Preparar lista de opciones
        opciones = []
        for cot in cotizaciones:
            opciones.append({
                "name": f"ID: {cot.get('id')} - {cot.get('descripcion', 'Sin descripción')[:30]}... - Total: {cot.get('total')} {cot.get('moneda', 'RD$')}",
                "value": str(cot.get('id'))
            })
        
        # Preguntar al usuario qué cotización
        id_cotizacion = questionary.select(
            "Seleccione la cotización a la que desea asignar el pago:",
            choices=[opcion["name"] for opcion in opciones]
        ).ask()
        
        if id_cotizacion:
            # Obtener el ID de la cotización seleccionada
            id_cot = next(opcion["value"] for opcion in opciones if opcion["name"] == id_cotizacion)
            
            # Preguntar monto a asignar (por defecto todo)
            monto_asignar = typer.prompt(
                f"Monto a asignar a la cotización ID {id_cot}", 
                default=str(monto),
                type=float
            )
            
            # Asignar el pago
            with spinner("Asignando pago..."):
                asignacion = asignar_pago_a_cotizacion(resultado.get('id'), int(id_cot), monto_asignar)
            
            if asignacion:
                console.print(f"[bold green]✓ Pago asignado correctamente a la cotización ID {id_cot}[/bold green]")
            else:
                console.print("[bold red]✗ Error al asignar el pago[/bold red]")


def pago_listar_command(
    id_cliente: Optional[int] = typer.Option(None, help="Filtrar por ID de cliente")
):
    """Lista los pagos registrados en el sistema."""
    with spinner("Obteniendo pagos..."):
        pagos = obtener_pagos(id_cliente)
    
    if not pagos:
        console.print("[yellow]No se encontraron pagos.[/yellow]")
        return
    
    # Crear tabla para mostrar resultados
    tabla = Table(title="Pagos Registrados", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim")
    tabla.add_column("Cliente")
    tabla.add_column("Monto", justify="right")
    tabla.add_column("Moneda")
    tabla.add_column("Fecha")
    tabla.add_column("Comprobante")
    
    # Obtener información de clientes
    clientes = {c.get('id'): c.get('nombre') for c in obtener_clientes()}
    
    for pago in pagos:
        tabla.add_row(
            str(pago.get("id", "N/A")),
            clientes.get(pago.get("id_cliente"), f"Cliente {pago.get('id_cliente')}"),
            f"{pago.get('monto', 0):,.2f}",
            pago.get("moneda", "RD$"),
            pago.get("fecha", "N/A"),
            pago.get("comprobante", "")
        )
    
    console.print(tabla)


def pago_asignar_command(
    id_pago: int = typer.Argument(..., help="ID del pago a asignar"),
    id_cotizacion: int = typer.Argument(..., help="ID de la cotización"),
    monto: float = typer.Argument(..., help="Monto a asignar a esta cotización")
):
    """Asigna un pago existente a una cotización específica."""
    # Verificar que la cotización existe
    with spinner(f"Verificando cotización ID {id_cotizacion}..."):
        cotizacion = obtener_cotizacion(id_cotizacion)
    
    if not cotizacion:
        console.print(f"[bold red]Error: No se encontró una cotización con ID {id_cotizacion}[/bold red]")
        raise typer.Exit(code=1)
    
    # Verificar que el pago existe
    with spinner(f"Verificando pago ID {id_pago}..."):
        pago = next((p for p in obtener_pagos() if p.get('id') == id_pago), None)
    
    if not pago:
        console.print(f"[bold red]Error: No se encontró un pago con ID {id_pago}[/bold red]")
        raise typer.Exit(code=1)
    
    # Asignar el pago
    with spinner("Asignando pago..."):
        resultado = asignar_pago_a_cotizacion(id_pago, id_cotizacion, monto)
    
    if resultado:
        console.print(f"[bold green]✓ Pago ID {id_pago} asignado correctamente a la cotización ID {id_cotizacion}[/bold green]")
    else:
        console.print("[bold red]✗ Error al asignar el pago[/bold red]")
        raise typer.Exit(code=1)


def pago_menu_interactivo():
    """Función para manejo interactivo de pagos (se implementará en el menú)"""
    # Esta función será implementada más adelante para el menú interactivo
    pass 