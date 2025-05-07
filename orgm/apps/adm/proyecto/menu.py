from rich.console import Console
import questionary
import sys
from orgm.apps.adm.proyecto.get_projects import obtener_proyectos, mostrar_proyectos
from orgm.apps.adm.proyecto.get_project import (
    obtener_proyecto,
    mostrar_proyecto_detalle,
)
from orgm.apps.adm.proyecto.form_project import formulario_proyecto
from orgm.apps.adm.proyecto.find_project import buscar_proyectos
from orgm.apps.adm.proyecto.update_project import actualizar_proyecto
from orgm.apps.adm.proyecto.create_project import crear_proyecto
from orgm.apps.adm.proyecto.gui import iniciar_gui
from orgm.qstyle import custom_style_fancy
from orgm.stuff.spinner import spinner

console = Console()


def menu():
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
                "Iniciar GUI",
                "Salir",
            ],
            style=custom_style_fancy,
        ).ask()

        if accion == "Salir":
            sys.exit()

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
                    opciones = [f"{p.id}: {p.nombre_proyecto}" for p in proyectos] + [
                        "Cancelar"
                    ]
                    sel = questionary.select(
                        "¿Qué proyecto desea ver?", choices=opciones
                    ).ask()
                    if sel != "Cancelar":
                        pid = int(sel.split(":")[0])
                        with spinner(f"Obteniendo detalles del proyecto {pid}..."):
                            proyecto_sel = obtener_proyecto(pid)
                        if proyecto_sel:
                            mostrar_proyecto_detalle(proyecto_sel)
                            if questionary.confirm(
                                "¿Desea editar este proyecto?", default=False
                            ).ask():
                                datos = formulario_proyecto(proyecto_sel)
                                if datos:
                                    with spinner(f"Actualizando proyecto {pid}..."):
                                        proyecto_actualizado = actualizar_proyecto(
                                            pid, datos
                                        )
                                    if proyecto_actualizado:
                                        print(
                                            "[bold green]Proyecto actualizado correctamente[/bold green]"
                                        )

        elif accion == "Crear nuevo proyecto":
            datos = formulario_proyecto()
            if datos:
                with spinner("Creando proyecto..."):
                    nuevo_proyecto = crear_proyecto(datos)
                if nuevo_proyecto:
                    console.print(
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
                    proyecto_actualizado = actualizar_proyecto(
                        proyecto_a_editar.id, datos
                    )
                if proyecto_actualizado:
                    print(
                        f"[bold green]Proyecto actualizado: {proyecto_actualizado.nombre_proyecto}[/bold green]"
                    )

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

        elif accion == "Iniciar GUI":
            iniciar_gui()
