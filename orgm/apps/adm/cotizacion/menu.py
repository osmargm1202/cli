from rich.console import Console
import questionary
from orgm.apps.adm.cotizacion.get_quotation import obtener_cotizacion
from orgm.apps.adm.cotizacion.get_quotations import obtener_cotizaciones
from orgm.apps.adm.cotizacion.form_quotation import formulario_cotizacion
from orgm.apps.adm.cotizacion.update_quotation import actualizar_cotizacion
from orgm.apps.adm.cotizacion.ask_client import _preguntar_cliente
from orgm.apps.adm.cotizacion.find_client import seleccionar_cliente_por_nombre
from orgm.apps.adm.cotizacion.find_project import seleccionar_proyecto_por_nombre
from orgm.apps.adm.cotizacion.create_quotation import (
    crear_cotizacion,
)
from orgm.apps.adm.cotizacion.update_quotation import actualizar_cotizacion
from orgm.apps.adm.cotizacion.show_quotations import (
    mostrar_cotizaciones_por_proyecto,
    mostrar_cotizaciones_por_cliente,
    mostrar_cotizaciones,
    mostrar_cotizacion_detalle,
)
from orgm.apps.adm.cotizacion.gui import gui as iniciar_gui
from orgm.qstyle import custom_style_fancy

console = Console()


def menu():
    """Menú interactivo para comandos de Cotizaciones."""
    while True:
        accion = questionary.select(
            "¿Qué desea hacer?",
            choices=[
                "Ver todas las cotizaciones",
                "Buscar cotizaciones (por Cliente o Proyecto)",
                "Crear nueva cotización",
                "Modificar cotización existente",
                "Ver detalles de una cotización",
                "Iniciar Gui",
                "Salir",
            ],
            style=custom_style_fancy,
        ).ask()

        if accion == "Salir":
            return "exit"

        if accion == "Ver todas las cotizaciones":
            cotizaciones = obtener_cotizaciones()
            mostrar_cotizaciones(cotizaciones)
        elif accion == "Buscar cotizaciones (por Cliente o Proyecto)":
            tipo_busqueda = questionary.select(
                "¿Buscar por Cliente o Proyecto?",
                choices=["Cliente", "Proyecto", "Cancelar"],
            ).ask()

            if tipo_busqueda == "Cliente":
                termino = questionary.text("Nombre del cliente a buscar:").ask()
                if termino:
                    cliente_id = seleccionar_cliente_por_nombre(termino)
                    if cliente_id:
                        mostrar_cotizaciones_por_cliente(cliente_id)
                        # Opción para ver/editar una cotización específica
                        id_text = questionary.text(
                            "ID de la cotización a ver/editar (dejar en blanco para continuar):"
                        ).ask()
                        if id_text:
                            try:
                                cid = int(id_text)
                                cot = obtener_cotizacion(cid)
                            except ValueError:
                                cot = None
                            if cot:
                                mostrar_cotizacion_detalle(cot)
                                if questionary.confirm(
                                    "¿Desea editar esta cotización?", default=False
                                ).ask():
                                    datos = formulario_cotizacion(cot)
                                    if datos:
                                        cot_id = (
                                            getattr(cot, "id", None)
                                            if not isinstance(cot, dict)
                                            else cot.get("id", None)
                                        )
                                        if cot_id is not None:
                                            act = actualizar_cotizacion(cot_id, datos)
                                            if act:
                                                print(
                                                    "[bold green]Cotización actualizada[/bold green]"
                                                )
                                        else:
                                            print(
                                                "[bold red]No se pudo obtener el ID de la cotización[/bold red]"
                                            )

            elif tipo_busqueda == "Proyecto":
                termino_proyecto = questionary.text(
                    "Nombre o término del proyecto a buscar:"
                ).ask()
                if termino_proyecto:
                    proyecto_id = seleccionar_proyecto_por_nombre(termino_proyecto)
                    if proyecto_id:
                        mostrar_cotizaciones_por_proyecto(proyecto_id)
                        # Opción para ver/editar una cotización específica después de mostrar
                        id_text = questionary.text(
                            "ID de la cotización a ver/editar (dejar en blanco para continuar):"
                        ).ask()
                        if id_text:
                            try:
                                cid = int(id_text)
                                # Validar que la cotización pertenece al proyecto buscado?
                                # Por ahora, se asume que el usuario introduce un ID válido de la lista mostrada
                                cot = obtener_cotizacion(cid)
                            except ValueError:
                                cot = None
                            if cot:
                                mostrar_cotizacion_detalle(cot)
                                if questionary.confirm(
                                    "¿Desea editar esta cotización?", default=False
                                ).ask():
                                    datos = formulario_cotizacion(cot)
                                    if datos:
                                        cot_id = (
                                            getattr(cot, "id", None)
                                            if not isinstance(cot, dict)
                                            else cot.get("id", None)
                                        )
                                        if cot_id is not None:
                                            act = actualizar_cotizacion(cot_id, datos)
                                            if act:
                                                print(
                                                    "[bold green]Cotización actualizada[/bold green]"
                                                )
                                        else:
                                            print(
                                                "[bold red]No se pudo obtener el ID de la cotización[/bold red]"
                                            )
                    # Si proyecto_id es None, _seleccionar_proyecto_por_nombre ya mostró mensaje

            # Si tipo_busqueda es "Cancelar", no hace nada y vuelve al menú.

        elif accion == "Crear nueva cotización":
            datos = formulario_cotizacion()
            if datos:
                nueva = crear_cotizacion(datos)
                if nueva:
                    # Obtener el ID usando getattr para objetos o get para diccionarios
                    nueva_id = (
                        getattr(nueva, "id", None)
                        if not isinstance(nueva, dict)
                        else nueva.get("id", None)
                    )
                    print(f"[bold green]Cotización creada: ID {nueva_id}[/bold green]")
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
                    print(
                        "[bold green]Cotización actualizada correctamente[/bold green]"
                    )
        elif accion == "Ver detalles de una cotización":
            id_text = questionary.text("ID de la cotización a ver:").ask()
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
            mostrar_cotizacion_detalle(cot)

        elif accion == "Iniciar Gui":
            iniciar_gui()
