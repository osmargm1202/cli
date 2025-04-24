import click
import questionary
from typing import Dict, Optional, List
from rich.console import Console
from rich.table import Table
from rich import print
from orgm.adm.clientes import (
    obtener_clientes,
    obtener_cliente,
    crear_cliente,
    actualizar_cliente,
    eliminar_cliente,
    buscar_clientes,
)
from orgm.adm.db import Cliente
from orgm.stuff.spinner import spinner

console = Console()

# Helper functions similar to orgm/questionary/clientes.py


def mostrar_cliente(cliente: Cliente):
    table = Table(title=f"Cliente: {cliente.nombre} (ID: {cliente.id})")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="green")
    for campo in cliente.__fields__.keys():
        valor = getattr(cliente, campo)
        table.add_row(campo, str(valor))
    console.print(table)


def listar_clientes(clientes: List[Cliente]):
    if not clientes:
        console.print("[yellow]No se encontraron clientes[/yellow]")
        return
    table = Table(title=f"Lista de Clientes ({len(clientes)} encontrados)")
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="green")
    table.add_column("Nombre Comercial", style="green")
    table.add_column("Teléfono", style="green")
    table.add_column("Ciudad", style="green")
    for c in clientes:
        table.add_row(str(c.id), c.nombre, c.nombre_comercial, c.telefono, c.ciudad)
    console.print(table)


def solicitar_datos_cliente(cliente: Optional[Cliente] = None) -> Dict:
    defaults = {
        campo: getattr(cliente, campo) if cliente else ""
        for campo in Cliente.__fields__.keys()
    }
    datos = {}
    for campo in [
        "nombre",
        "nombre_comercial",
        "numero",
        "correo",
        "direccion",
        "ciudad",
        "provincia",
        "telefono",
        "representante",
        "telefono_representante",
        "extension_representante",
        "celular_representante",
        "correo_representante",
    ]:
        datos[campo] = questionary.text(
            campo.replace("_", " ").capitalize() + ":", default=defaults[campo]
        ).ask()
    datos["tipo_factura"] = questionary.select(
        "Tipo de factura:",
        choices=["NCFC", "NCF", "NCG", "NCRE"],
        default=defaults["tipo_factura"] or "NCFC",
    ).ask()
    return datos


# Interactive menu


@click.group(invoke_without_command=True)
@click.pass_context
def cliente(ctx):
    """Gestión de clientes"""
    if ctx.invoked_subcommand is None:
        menu_principal()


def menu_principal():
    while True:
        accion = questionary.select(
            "¿Qué desea hacer?",
            choices=[
                "Ver todos los clientes",
                "Buscar clientes",
                "Crear nuevo cliente",
                "Modificar cliente existente",
                "Eliminar cliente",
                "Volver al menú principal",
            ],
        ).ask()
        if accion == "Volver al menú principal":
            break
        elif accion == "Ver todos los clientes":
            with spinner("Obteniendo clientes..."):
                clientes = obtener_clientes()
            listar_clientes(clientes)
        elif accion == "Buscar clientes":
            termino = questionary.text("Término de búsqueda:").ask()
            if termino:
                with spinner("Buscando clientes..."):
                    clientes = buscar_clientes(termino)
                listar_clientes(clientes)
        elif accion == "Crear nuevo cliente":
            datos = solicitar_datos_cliente()
            if datos and questionary.confirm("¿Crear cliente?", default=True).ask():
                with spinner("Creando cliente..."):
                    nuevo = crear_cliente(datos)
                if nuevo:
                    print(f"[bold green]Cliente creado con ID {nuevo.id}[/bold green]")
                    mostrar_cliente(nuevo)
        elif accion == "Modificar cliente existente":
            id_text = questionary.text("ID del cliente a modificar (o búsqueda):").ask()
            if not id_text:
                continue
            try:
                id_num = int(id_text)
                cliente_obj = obtener_cliente(id_num)
            except ValueError:
                clientes = buscar_clientes(id_text)
                listar_clientes(clientes)
                if not clientes:
                    continue
                opciones = [f"{c.id}: {c.nombre}" for c in clientes] + ["Cancelar"]
                sel = questionary.select("Seleccione cliente:", choices=opciones).ask()
                if sel == "Cancelar":
                    continue
                id_num = int(sel.split(":")[0])
                cliente_obj = obtener_cliente(id_num)
            if not cliente_obj:
                print("[bold red]Cliente no encontrado[/bold red]")
                continue
            datos = solicitar_datos_cliente(cliente_obj)
            if datos and questionary.confirm("¿Guardar cambios?", default=True).ask():
                with spinner("Actualizando cliente..."):
                    actualizado = actualizar_cliente(id_num, datos)
                if actualizado:
                    print("[bold green]Cliente actualizado[/bold green]")
                    mostrar_cliente(actualizado)
        elif accion == "Eliminar cliente":
            id_text = questionary.text("ID del cliente a eliminar (o búsqueda):").ask()
            if not id_text:
                continue
            try:
                id_num = int(id_text)
            except ValueError:
                clientes = buscar_clientes(id_text)
                listar_clientes(clientes)
                if not clientes:
                    continue
                opciones = [f"{c.id}: {c.nombre}" for c in clientes] + ["Cancelar"]
                sel = questionary.select("Seleccione cliente:", choices=opciones).ask()
                if sel == "Cancelar":
                    continue
                id_num = int(sel.split(":")[0])
            if questionary.confirm("¿Eliminar cliente?", default=False).ask():
                with spinner("Eliminando cliente..."):
                    ok = eliminar_cliente(id_num)
                if ok:
                    print("[bold green]Cliente eliminado[/bold green]")


# CLI subcommands wrappers


@cliente.command("listar")
def cmd_listar():
    with spinner("Obteniendo clientes..."):
        clientes = obtener_clientes()
    listar_clientes(clientes)


@cliente.command("buscar")
@click.argument("termino")
def cmd_buscar(termino):
    with spinner("Buscando clientes..."):
        clientes = buscar_clientes(termino)
    listar_clientes(clientes)


@cliente.command("crear")
def cmd_crear():
    datos = solicitar_datos_cliente()
    if datos and questionary.confirm("¿Crear cliente?", default=True).ask():
        with spinner("Creando cliente..."):
            nuevo = crear_cliente(datos)
        if nuevo:
            mostrar_cliente(nuevo)


@cliente.command("modificar")
@click.argument("id_cliente", type=int)
def cmd_modificar(id_cliente):
    cliente_obj = obtener_cliente(id_cliente)
    if not cliente_obj:
        print("[bold red]Cliente no encontrado[/bold red]")
        return
    datos = solicitar_datos_cliente(cliente_obj)
    if datos and questionary.confirm("¿Guardar cambios?", default=True).ask():
        with spinner("Actualizando cliente..."):
            actualizado = actualizar_cliente(id_cliente, datos)
        if actualizado:
            mostrar_cliente(actualizado)


@cliente.command("eliminar")
@click.argument("id_cliente", type=int)
def cmd_eliminar(id_cliente):
    if questionary.confirm("¿Eliminar cliente?", default=False).ask():
        with spinner("Eliminando cliente..."):
            ok = eliminar_cliente(id_cliente)
        if ok:
            print("[bold green]Cliente eliminado[/bold green]")
