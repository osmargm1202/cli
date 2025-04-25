import click
import questionary
from typing import Dict, Optional
from rich.console import Console
from rich.table import Table
from rich import print
from orgm.adm.cotizaciones import (
    obtener_cotizaciones,
    obtener_cotizacion,
    crear_cotizacion,
    actualizar_cotizacion,
    eliminar_cotizacion,
    buscar_cotizaciones,
)
from orgm.adm.servicios import obtener_servicios
from orgm.stuff.ai import generate_project_description
from orgm.stuff.spinner import spinner
import os, requests
from orgm.adm.clientes import buscar_clientes
from orgm.adm.cotizaciones import cotizaciones_por_cliente

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
        total = f"{c['moneda']} {c.get('total',0):,.2f}" if c.get('total') else "N/A"
        subtotal = f"{c['moneda']} {c.get('subtotal',0):,.2f}"
        itbis = f"{c.get('itbism',0):,.2f}"
        indirectos = f"{c.get('indirectos',0):,.2f}"
        table.add_row(
            str(c["id"]),
            f"{c['cliente']['id']} - {c['cliente']['nombre']}" if 'cliente' in c else str(c['id_cliente']),
            f"{c['proyecto']['id']} - {c['proyecto']['nombre_proyecto']}" if 'proyecto' in c else str(c['id_proyecto']),
            (c.get('descripcion','')[:60] + ('...' if c.get('descripcion') and len(c.get('descripcion'))>60 else '')),
            subtotal,
            itbis,
            indirectos,
            total,
        )

    console.print(table)


def _seleccionar_servicio(id_default: Optional[int] = None) -> int:
    servicios = obtener_servicios()
    opciones = [f"{s.id}: {s.nombre}" for s in servicios]
    if not opciones:
        return id_default or 0
    if id_default:
        opciones_default = next((o for o in opciones if o.startswith(str(id_default))), opciones[0])
    else:
        opciones_default = opciones[0]
    opciones.append("Cancelar")
    sel = questionary.select("Seleccione servicio:", choices=opciones, default=opciones_default).ask()
    if sel == "Cancelar":
        return id_default or 0
    return int(sel.split(":")[0])


# Último cliente usado
_ultimo_cliente_id: Optional[int] = None


def _preguntar_cliente() -> Optional[int]:
    global _ultimo_cliente_id
    default_val = str(_ultimo_cliente_id) if _ultimo_cliente_id else ""
    cid_str = questionary.text("ID del cliente:", default=default_val).ask()
    if not cid_str:
        return None
    try:
        cid = int(cid_str)
    except ValueError:
        print("[bold red]ID inválido[/bold red]")
        return None

    # Mostrar últimas 10 cotizaciones de este cliente
    cotis = [c for c in obtener_cotizaciones() if c["id_cliente"] == cid]
    cotis.sort(key=lambda x: x.get('fecha', ''), reverse=True)
    mostrar_cotizaciones(cotis[:10])
    if len(cotis) > 10 and questionary.confirm("¿Mostrar más cotizaciones?", default=False).ask():
        mostrar_cotizaciones(cotis)

    _ultimo_cliente_id = cid
    return cid


# --- tasa de cambio helper ---
def _obtener_tasa(moneda_desde: str, moneda_hasta: str = "DOP") -> float:
    api_url = os.getenv("API_URL")
    if not api_url:
        return 1.0
    payload = {"desde": moneda_desde, "a": moneda_hasta, "cantidad": 1}
    try:
        with spinner("Obteniendo tasa de cambio..."):
            resp = requests.post(f"{api_url}/divisa", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return float(data.get("resultado", 1))
    except Exception as e:
        console.print(f"[bold yellow]No se pudo obtener tasa, usando 1: {e}[/bold yellow]")
        return 1.0


def formulario_cotizacion(cotizacion=None) -> Dict:
    """Formulario para crear o actualizar una cotización"""
    es_nuevo = cotizacion is None

    defaults = {
        "id_cliente": cotizacion.id_cliente if cotizacion else "",
        "id_proyecto": cotizacion.id_proyecto if cotizacion else "",
        "id_servicio": cotizacion.id_servicio if cotizacion else "",
        "moneda": cotizacion.moneda if cotizacion else "RD$",
        "descripcion": cotizacion.descripcion if cotizacion else "",
        "estado": cotizacion.estado if cotizacion else "GENERADA",
        "total": cotizacion.total if cotizacion else 0.0,
    }

    cid = _preguntar_cliente() if es_nuevo else defaults["id_cliente"]
    if cid is None:
        return {}
    datos = {}
    datos["id_cliente"] = cid
    datos["id_servicio"] = _seleccionar_servicio(defaults["id_servicio"])
    datos["moneda"] = questionary.select(
        "Moneda:", choices=["RD$", "USD$", "EUR€"], default=defaults["moneda"]
    ).ask()

    # Fecha
    datos["fecha"] = questionary.text("Fecha (YYYY-MM-DD):", default=getattr(cotizacion, "fecha", "")).ask()

    # Tasa de cambio
    metodo_tasa = questionary.select(
        "¿Cómo desea obtener la tasa de cambio?",
        choices=["API", "Manual"],
        default="API",
    ).ask()
    if metodo_tasa == "API":
        datos["tasa_moneda"] = _obtener_tasa(datos["moneda"].replace("$", ""))
    else:
        tasa_str = questionary.text("Tasa de cambio:", default=str(getattr(cotizacion, "tasa_moneda", 1.0))).ask()
        try:
            datos["tasa_moneda"] = float(tasa_str)
        except ValueError:
            datos["tasa_moneda"] = 1.0

    metodo_desc = questionary.select(
        "¿Cómo desea establecer la descripción?",
        choices=["Manual", "Automática"],
        default="Manual" if defaults["descripcion"] else "Automática",
    ).ask()
    if metodo_desc == "Manual":
        datos["descripcion"] = questionary.text(
            "Descripción de la cotización:", default=defaults["descripcion"]
        ).ask()
    else:
        prompt = questionary.text("Prompt para generar descripción:").ask()
        if prompt:
            desc = generate_project_description(prompt)
            datos["descripcion"] = desc or ""
        else:
            datos["descripcion"] = defaults["descripcion"]

    datos["estado"] = questionary.select(
        "Estado:", choices=["GENERADA", "ENVIADA", "ACEPTADA", "RECHAZADA"], default=defaults["estado"]
    ).ask()

    datos["tiempo_entrega"] = questionary.text("Tiempo de entrega:", default=getattr(cotizacion, "tiempo_entrega", "3")).ask()
    datos["avance"] = questionary.text("Porcentaje de avance:", default=getattr(cotizacion, "avance", "60")).ask()
    datos["validez"] = int(questionary.text("Días de validez:", default=str(getattr(cotizacion, "validez", 30))).ask())
    datos["idioma"] = questionary.select(
        "Idioma:", choices=["ES", "EN"], default=getattr(cotizacion, "idioma", "ES")
    ).ask()

    # descuento porcentaje
    desc_p = questionary.text("Descuento (%):", default=str(getattr(cotizacion, "descuentop", 0))).ask()
    try:
        datos["descuentop"] = float(desc_p)
    except ValueError:
        datos["descuentop"] = 0.0

    return datos


@click.group(invoke_without_command=True)
@click.pass_context
def cotizacion(ctx):
    """Gestión de cotizaciones"""
    if ctx.invoked_subcommand is None:
        menu_principal()


def menu_principal():
    while True:
        accion = questionary.select(
            "¿Qué desea hacer?",
            choices=[
                "Ver todas las cotizaciones",
                "Buscar cotizaciones",
                "Crear nueva cotización",
                "Modificar cotización existente",
                "Eliminar cotización",
                "Volver al menú principal",
            ],
        ).ask()

        if accion == "Volver al menú principal":
            break

        if accion == "Ver todas las cotizaciones":
            cotizaciones = obtener_cotizaciones()
            mostrar_cotizaciones(cotizaciones)
        elif accion == "Buscar cotizaciones":
            termino = questionary.text("Nombre del cliente a buscar:").ask()
            if termino:
                cliente_id = _seleccionar_cliente_por_nombre(termino)
                if cliente_id:
                    _mostrar_cotis_cliente(cliente_id)
        elif accion == "Crear nueva cotización":
            datos = formulario_cotizacion()
            if datos:
                nueva = crear_cotizacion(datos)
                if nueva:
                    print(f"[bold green]Cotización creada: ID {nueva.id}[/bold green]")
        elif accion == "Modificar cotización existente":
            id_text = questionary.text("ID de la cotización a modificar:").ask()
            if not id_text:
                continue
            try:
                id_num = int(id_text)
            except ValueError:
                print("[bold red]ID inválido[/bold red]")
                continue
            cot = obtener_cotizacion(id_num)
            if not cot:
                print("[bold red]No se encontró la cotización[/bold red]")
                continue
            datos = formulario_cotizacion(cot)
            if datos:
                act = actualizar_cotizacion(id_num, datos)
                if act:
                    print("[bold green]Cotización actualizada correctamente[/bold green]")
        elif accion == "Eliminar cotización":
            id_text = questionary.text("ID de la cotización a eliminar:").ask()
            if not id_text:
                continue
            try:
                id_num = int(id_text)
            except ValueError:
                print("[bold red]ID inválido[/bold red]")
                continue
            cot = obtener_cotizacion(id_num)
            if not cot:
                print("[bold red]No se encontró la cotización[/bold red]")
                continue
            if questionary.confirm("¿Eliminar cotización?", default=False).ask():
                if eliminar_cotizacion(id_num):
                    print("[bold green]Cotización eliminada[/bold green]")


# Subcommand wrappers

@cotizacion.command("listar")
def cmd_listar_cotizaciones():
    cotizaciones = obtener_cotizaciones()
    mostrar_cotizaciones(cotizaciones)


@cotizacion.command("buscar")
@click.argument("termino")
def cmd_buscar_cotizaciones(termino):
    cliente_id = _seleccionar_cliente_por_nombre(termino)
    if cliente_id:
        _mostrar_cotis_cliente(cliente_id)


@cotizacion.command("crear")
def cmd_crear_cotizacion():
    datos = formulario_cotizacion()
    if datos:
        nueva = crear_cotizacion(datos)
        if nueva:
            print(f"[bold green]Cotización creada: ID {nueva.id}[/bold green]")


@cotizacion.command("modificar")
@click.argument("id_cotizacion", type=int)
def cmd_modificar_cotizacion(id_cotizacion):
    cot = obtener_cotizacion(id_cotizacion)
    if not cot:
        print(f"[bold red]No se encontró la cotización con ID {id_cotizacion}[/bold red]")
        return
    datos = formulario_cotizacion(cot)
    if datos:
        act = actualizar_cotizacion(id_cotizacion, datos)
        if act:
            print("[bold green]Cotización actualizada[/bold green]")


@cotizacion.command("eliminar")
@click.argument("id_cotizacion", type=int)
def cmd_eliminar_cotizacion(id_cotizacion):
    cot = obtener_cotizacion(id_cotizacion)
    if not cot:
        print(f"[bold red]No se encontró la cotización con ID {id_cotizacion}[/bold red]")
        return
    if questionary.confirm("¿Eliminar cotización?", default=False).ask():
        if eliminar_cotizacion(id_cotizacion):
            print("[bold green]Cotización eliminada[/bold green]")


# --- helper para seleccionar cliente ---
def _seleccionar_cliente_por_nombre(termino: str) -> Optional[int]:
    clientes = buscar_clientes(termino)
    if not clientes:
        print("[yellow]No se encontraron clientes[/yellow]")
        return None
    opciones = [f"{c.id}: {c.nombre}" for c in clientes]
    opciones.append("Cancelar")
    sel = questionary.select("Seleccione un cliente:", choices=opciones).ask()
    if sel == "Cancelar":
        return None
    return int(sel.split(":")[0])


def _mostrar_cotis_cliente(id_cliente: int):
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


if __name__ == "__main__":
    cotizacion() 