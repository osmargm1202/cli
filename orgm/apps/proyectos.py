import typer
import questionary
from typing import Dict, Optional
from rich.console import Console
from rich.table import Table
from rich import print
from orgm.adm.proyectos import (
    obtener_proyectos,
    obtener_proyecto,
    crear_proyecto,
    actualizar_proyecto,
    eliminar_proyecto,
    buscar_proyectos,
    obtener_ubicaciones,
    buscar_ubicaciones,
)
from orgm.adm.db import Proyecto
from orgm.stuff.spinner import spinner

console = Console()

# Crear la aplicación Typer para proyectos
app = typer.Typer(help="Gestión de proyectos")


def mostrar_proyectos(proyectos):
    """Muestra una tabla con los proyectos"""
    if not proyectos:
        print("[yellow]No se encontraron proyectos[/yellow]")
        return

    table = Table(title="Proyectos")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Nombre", style="green")
    table.add_column("Ubicación", style="yellow")
    table.add_column("Descripción", style="white")

    for p in proyectos:
        # Limitar la longitud de la descripción para una mejor visualización
        descripcion = (
            p.descripcion[:100] + "..." if len(p.descripcion) > 100 else p.descripcion
        )
        table.add_row(str(p.id), p.nombre_proyecto, p.ubicacion, descripcion)

    console.print(table)


def seleccionar_ubicacion() -> Optional[str]:
    """Permite al usuario buscar y seleccionar una ubicación"""
    # Primera pregunta: ¿cómo quiere buscar la ubicación?
    metodo_busqueda = questionary.select(
        "¿Cómo desea seleccionar la ubicación?",
        choices=["Buscar por nombre", "Ver todas las ubicaciones", "Cancelar"],
    ).ask()

    if metodo_busqueda == "Cancelar":
        return None

    ubicaciones = []
    if metodo_busqueda == "Buscar por nombre":
        termino = questionary.text(
            "Ingrese término de búsqueda (provincia, distrito o municipio):"
        ).ask()
        if not termino:
            print("[yellow]Búsqueda cancelada[/yellow]")
            return None
        with spinner(f"Buscando ubicaciones por '{termino}'..."):
            ubicaciones = buscar_ubicaciones(termino)
    elif metodo_busqueda == "Ver todas las ubicaciones":
        with spinner("Obteniendo todas las ubicaciones..."):
            ubicaciones = obtener_ubicaciones()
    else:
        return None

    if not ubicaciones:
        print("[yellow]No se encontraron ubicaciones[/yellow]")
        return None

    # Crear las opciones para el selector
    opciones = [
        f"{u.id}: {u.provincia}, {u.distrito}, {u.distritomunicipal}"
        for u in ubicaciones
    ]
    opciones.append("Cancelar")

    seleccion = questionary.select("Seleccione una ubicación:", choices=opciones).ask()

    if seleccion == "Cancelar":
        return None

    # Extraer el ID seleccionado
    id_ubicacion = seleccion.split(":")[0].strip()
    ubicacion = next((u for u in ubicaciones if str(u.id) == id_ubicacion), None)

    if not ubicacion:
        return None

    # Devolver una cadena formateada con la ubicación
    return f"{ubicacion.provincia}, {ubicacion.distrito}, {ubicacion.distritomunicipal}"


def formulario_proyecto(proyecto=None) -> Dict:
    """Formulario para crear o actualizar un proyecto"""
    # Si proyecto es None, estamos creando uno nuevo
    # Si no, estamos actualizando uno existente
    es_nuevo = proyecto is None
    titulo = (
        "Crear nuevo proyecto"
        if es_nuevo
        else f"Actualizar proyecto: {proyecto.nombre_proyecto}"
    )

    print(f"[bold blue]{titulo}[/bold blue]")

    # Valores por defecto
    defaults = {
        "nombre_proyecto": "",
        "ubicacion": "",
        "descripcion": "",
    }

    if not es_nuevo:
        defaults["nombre_proyecto"] = proyecto.nombre_proyecto
        defaults["ubicacion"] = proyecto.ubicacion
        defaults["descripcion"] = proyecto.descripcion

    # Recopilar datos
    data = {}

    nombre = questionary.text(
        "Nombre del proyecto:", default=defaults["nombre_proyecto"]
    ).ask()

    if nombre is None:  # El usuario canceló
        return {}

    data["nombre_proyecto"] = nombre

    # Preguntar si quiere cambiar la ubicación
    cambiar_ubicacion = (
        es_nuevo
        or questionary.confirm(
            "¿Desea cambiar la ubicación del proyecto?", default=False
        ).ask()
    )

    if cambiar_ubicacion:
        ubicacion = seleccionar_ubicacion()
        if ubicacion:
            data["ubicacion"] = ubicacion
    elif not es_nuevo:
        # Mantener la ubicación existente
        data["ubicacion"] = defaults["ubicacion"]

    # Descripción - puede quedar vacía y se generará automáticamente
    generar_descripcion = questionary.confirm(
        "¿Desea generar automáticamente la descripción del proyecto?",
        default=not defaults["descripcion"],
    ).ask()

    if not generar_descripcion:
        descripcion = questionary.text(
            "Descripción del proyecto:", default=defaults["descripcion"]
        ).ask()

        if descripcion is not None:  # El usuario no canceló
            data["descripcion"] = descripcion
    else:
        # Dejar vacío para que se genere automáticamente
        data["descripcion"] = ""

    return data


# Comando principal para el menú interactivo
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Gestión de proyectos"""
    if ctx.invoked_subcommand is None:
        menu_principal()


def menu_principal():
    """Menú principal para la gestión de proyectos"""
    while True:
        accion = questionary.select(
            "¿Qué desea hacer?",
            choices=[
                "Ver todos los proyectos",
                "Buscar proyectos",
                "Crear nuevo proyecto",
                "Modificar proyecto existente",
                "Eliminar proyecto",
                "Ver detalles de un proyecto",
                "Volver al menú principal",
            ],
        ).ask()

        if accion == "Volver al menú principal":
            # Intentar volver al menú principal de orgm si existe
            return "exit"

        if accion == "Ver todos los proyectos":
            with spinner("Listando proyectos..."):
                proyectos = obtener_proyectos()
            mostrar_proyectos(proyectos)

        elif accion == "Buscar proyectos":
            termino = questionary.text("Término de búsqueda:").ask()
            if termino:
                with spinner(f"Buscando proyectos por '{termino}'..."):
                    proyectos = buscar_proyectos(termino)
                mostrar_proyectos(proyectos)
                if proyectos:
                    opciones = [f"{p.id}: {p.nombre_proyecto}" for p in proyectos] + ["Cancelar"]
                    sel = questionary.select("¿Qué proyecto desea ver?", choices=opciones).ask()
                    if sel != "Cancelar":
                        pid = int(sel.split(":" )[0])
                        with spinner(f"Obteniendo detalles del proyecto {pid}..."):
                            proyecto_sel = obtener_proyecto(pid)
                        if proyecto_sel:
                            mostrar_proyecto_detalle(proyecto_sel)
                            if questionary.confirm("¿Desea editar este proyecto?", default=False).ask():
                                datos = formulario_proyecto(proyecto_sel)
                                if datos:
                                    with spinner(f"Actualizando proyecto {pid}..."):
                                        proyecto_actualizado = actualizar_proyecto(pid, datos)
                                    if proyecto_actualizado:
                                        print("[bold green]Proyecto actualizado correctamente[/bold green]")

        elif accion == "Crear nuevo proyecto":
            datos = formulario_proyecto()
            if datos:
                with spinner("Creando proyecto..."):
                    nuevo_proyecto = crear_proyecto(datos)
                if nuevo_proyecto:
                    print(
                        f"[bold green]Proyecto creado: {nuevo_proyecto.nombre_proyecto}[/bold green]"
                    )

        elif accion == "Modificar proyecto existente":
            # Primero seleccionar el proyecto
            id_proyecto = questionary.text(
                "ID del proyecto a modificar (o buscar por nombre):"
            ).ask()

            if not id_proyecto:
                continue

            # Verificar si es un ID o un término de búsqueda
            proyecto_a_editar = None
            try:
                id_num = int(id_proyecto)
                with spinner(f"Obteniendo proyecto {id_num}..."):
                    proyecto_a_editar = obtener_proyecto(id_num)
            except ValueError:
                # Es un término de búsqueda
                with spinner(f"Buscando proyectos por '{id_proyecto}'..."):
                    proyectos = buscar_proyectos(id_proyecto)
                mostrar_proyectos(proyectos)

                if not proyectos:
                    continue

                # Permitir seleccionar de la lista
                opciones = [f"{p.id}: {p.nombre_proyecto}" for p in proyectos]
                opciones.append("Cancelar")

                seleccion = questionary.select(
                    "Seleccione un proyecto para editar:", choices=opciones
                ).ask()

                if seleccion == "Cancelar":
                    continue

                id_seleccionado = int(seleccion.split(":")[0].strip())
                with spinner(f"Obteniendo proyecto {id_seleccionado}..."):
                    proyecto_a_editar = obtener_proyecto(id_seleccionado)

            if not proyecto_a_editar:
                print("[bold red]No se encontró el proyecto[/bold red]")
                continue

            # Editar el proyecto
            datos = formulario_proyecto(proyecto_a_editar)
            if datos:
                with spinner(f"Actualizando proyecto {proyecto_a_editar.id}..."):
                    proyecto_actualizado = actualizar_proyecto(proyecto_a_editar.id, datos)
                if proyecto_actualizado:
                    print(
                        f"[bold green]Proyecto actualizado: {proyecto_actualizado.nombre_proyecto}[/bold green]"
                    )

        elif accion == "Eliminar proyecto":
            # Primero seleccionar el proyecto
            id_proyecto = questionary.text(
                "ID del proyecto a eliminar (o buscar por nombre):"
            ).ask()

            if not id_proyecto:
                continue

            # Verificar si es un ID o un término de búsqueda
            proyecto_a_eliminar = None
            try:
                id_num = int(id_proyecto)
                with spinner(f"Verificando proyecto {id_num}..."):
                    proyecto_a_eliminar = obtener_proyecto(id_num)
                if proyecto_a_eliminar:
                    print(
                        f"Proyecto: {proyecto_a_eliminar.id} - {proyecto_a_eliminar.nombre_proyecto}"
                    )
            except ValueError:
                # Es un término de búsqueda
                with spinner(f"Buscando proyectos por '{id_proyecto}'..."):
                    proyectos = buscar_proyectos(id_proyecto)
                mostrar_proyectos(proyectos)

                if not proyectos:
                    continue

                # Permitir seleccionar de la lista
                opciones = [f"{p.id}: {p.nombre_proyecto}" for p in proyectos]
                opciones.append("Cancelar")

                seleccion = questionary.select(
                    "Seleccione un proyecto para eliminar:", choices=opciones
                ).ask()

                if seleccion == "Cancelar":
                    continue

                id_seleccionado = int(seleccion.split(":")[0].strip())
                with spinner(f"Verificando proyecto {id_seleccionado}..."):
                    proyecto_a_eliminar = obtener_proyecto(id_seleccionado)

            if not proyecto_a_eliminar:
                print("[bold red]No se encontró el proyecto[/bold red]")
                continue

            # Confirmar eliminación
            confirmar = questionary.confirm(
                f"¿Está seguro de eliminar el proyecto '{proyecto_a_eliminar.nombre_proyecto}'?",
                default=False,
            ).ask()

            if confirmar:
                with spinner(f"Eliminando proyecto {proyecto_a_eliminar.id}..."):
                    if eliminar_proyecto(proyecto_a_eliminar.id):
                        print("[bold green]Proyecto eliminado correctamente[/bold green]")

        elif accion == "Ver detalles de un proyecto":
            id_text = questionary.text("ID del proyecto a ver (o búsqueda):").ask()
            if not id_text:
                continue
            try:
                id_num = int(id_text)
                with spinner(f"Obteniendo detalles del proyecto {id_num}..."):
                    proyecto_obj = obtener_proyecto(id_num)
            except ValueError:
                print("[bold red]ID inválido.[/bold red]")
                continue
            if proyecto_obj:
                mostrar_proyecto_detalle(proyecto_obj)


@app.command("list")
def listar_proyectos():
    """Listar todos los proyectos"""
    with spinner("Listando proyectos..."):
        proyectos = obtener_proyectos()
    mostrar_proyectos(proyectos)


@app.command("find")
def cmd_buscar_proyectos(termino: str):
    """Buscar proyectos por término"""
    with spinner(f"Buscando proyectos por '{termino}'..."):
        proyectos = buscar_proyectos(termino)
    mostrar_proyectos(proyectos)


@app.command("create")
def cmd_crear_proyecto():
    """Crear un nuevo proyecto"""
    datos = formulario_proyecto()
    if datos:
        with spinner("Creando proyecto..."):
            nuevo_proyecto = crear_proyecto(datos)
        if nuevo_proyecto:
            print(
                f"[bold green]Proyecto creado: {nuevo_proyecto.nombre_proyecto}[/bold green]"
            )


@app.command("edit")
def cmd_modificar_proyecto(id_proyecto: int):
    """Modificar un proyecto existente"""
    with spinner(f"Obteniendo proyecto {id_proyecto}..."):
        proyecto_a_editar = obtener_proyecto(id_proyecto)
    if not proyecto_a_editar:
        print(f"[bold red]No se encontró el proyecto con ID {id_proyecto}[/bold red]")
        return

    datos = formulario_proyecto(proyecto_a_editar)
    if datos:
        with spinner(f"Actualizando proyecto {id_proyecto}..."):
            proyecto_actualizado = actualizar_proyecto(id_proyecto, datos)
        if proyecto_actualizado:
            print(
                f"[bold green]Proyecto actualizado: {proyecto_actualizado.nombre_proyecto}[/bold green]"
            )


@app.command("delete")
def cmd_eliminar_proyecto(id_proyecto: int):
    """Eliminar un proyecto existente"""
    with spinner(f"Verificando proyecto {id_proyecto}..."):
        proyecto_a_eliminar = obtener_proyecto(id_proyecto)
    if not proyecto_a_eliminar:
        print(f"[bold red]No se encontró el proyecto con ID {id_proyecto}[/bold red]")
        return

    # Confirmar eliminación
    confirmar = typer.confirm(
        f"¿Está seguro de eliminar el proyecto '{proyecto_a_eliminar.nombre_proyecto}'?",
        default=False,
    )

    if confirmar:
        with spinner(f"Eliminando proyecto {id_proyecto}..."):
            if eliminar_proyecto(id_proyecto):
                print("[bold green]Proyecto eliminado correctamente[/bold green]")


def mostrar_proyecto_detalle(proyecto: Proyecto):
    """Muestra los datos completos de un proyecto"""
    table = Table(title=f"Proyecto: {proyecto.nombre_proyecto} (ID: {proyecto.id})")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="green")

    for campo in proyecto.__fields__.keys():
        valor = getattr(proyecto, campo)
        table.add_row(campo, str(valor))

    console.print(table)


@app.command("show")
def cmd_ver_proyecto(id_proyecto: int):
    """Ver los datos de un proyecto por su ID"""
    with spinner(f"Obteniendo detalles del proyecto {id_proyecto}..."):
        proyecto_obj = obtener_proyecto(id_proyecto)
    if not proyecto_obj:
        print(f"[bold red]No se encontró el proyecto con ID {id_proyecto}[/bold red]")
        return
    mostrar_proyecto_detalle(proyecto_obj)


# Reemplazar la exportación del grupo click por la app de typer
proyecto = app

if __name__ == "__main__":
    app()
