import typer
from rich.console import Console
from rich import print
from orgm.adm.proyectos import (
    obtener_proyectos,
    obtener_proyecto,
    crear_proyecto,
    actualizar_proyecto,
    eliminar_proyecto,
    buscar_proyectos,
)
from orgm.stuff.spinner import spinner

console = Console()

# Crear la aplicación Typer para proyectos
app = typer.Typer(help="Gestión de proyectos")


# Comando principal para el menú interactivo
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Gestión de proyectos"""
    if ctx.invoked_subcommand is None:
        menu_principal()


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
