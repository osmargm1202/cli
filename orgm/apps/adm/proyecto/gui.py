# Configurar multiprocessing para usar 'spawn' en lugar de 'fork'
# Es importante si la GUI se ejecuta en diferentes entornos (ej. macOS/Windows)
# Comentado si no causa problemas en tu entorno Linux específico.
# try:
#     multiprocessing.set_start_method('spawn', force=True)
# except RuntimeError:
#     pass # Ignorar si ya está configurado o no se puede cambiar

from nicegui import ui
from typing import List, Optional
from functools import partial
from orgm.apps.adm.proyecto.find_project import buscar_proyectos
from orgm.apps.adm.proyecto.get_project import obtener_proyecto
from orgm.apps.adm.proyecto.update_project import actualizar_proyecto
from orgm.apps.adm.proyecto.create_project import crear_proyecto
from orgm.apps.adm.db import Proyecto  # Importar modelo Proyecto

# Intentar importar el módulo de colores, si falla usar los valores predefinidos
try:
    from orgm.stuff.gui_color import *
except ImportError:
    # Definición de colores como respaldo
    FONDO_PRINCIPAL = "#121212"
    FONDO_SECUNDARIO = "#1E1E1E"
    FONDO_TARJETA = "#2D2D2D"
    AZUL_PRIMARIO = "#2563EB"
    TEXTO_PRINCIPAL = "#FFFFFF"
    TEMA_OSCURO = True


class ProyectoGUI:
    def __init__(self):
        self.proyectos_encontrados: List[Proyecto] = []
        self.proyecto_seleccionado: Optional[Proyecto] = None
        self.barra_busqueda = None
        self.seccion_detalles = None
        self.campos_proyecto = {}
        self.label_seleccionado = None
        self.boton_editar = None
        self.contenedor_resultados = None
        self.tarjeta_seleccionada_actual = None

    def crear_interfaz(self):
        # Establecer tema oscuro
        ui.dark_mode().enable() if TEMA_OSCURO else ui.dark_mode().disable()

        # Establecer fondo principal
        ui.page_title("Gestión de Proyectos")
        ui.colors(primary=AZUL_PRIMARIO)

        # Crear contenedor principal
        with (
            ui.column()
            .classes("w-full h-full p-4 gap-4")
            .style(f"background-color: {FONDO_PRINCIPAL}")
        ):
            # Cabecera
            with (
                ui.card()
                .classes("w-full")
                .style(f"background-color: {FONDO_SECUNDARIO}")
            ):
                ui.label("Gestión de Proyectos").classes("text-h4 text-center").style(
                    f"color: {TEXTO_PRINCIPAL}"
                )

            # Sección de búsqueda y acciones
            with (
                ui.card().classes("w-full").style(f"background-color: {FONDO_TARJETA}")
            ):
                with ui.row().classes("w-full items-center"):
                    self.barra_busqueda = (
                        ui.input(
                            label="Buscar proyecto",
                            placeholder="Nombre, descripción, ubicación o ID...",
                        )
                        .classes("flex-grow")
                        .style(f"color: {TEXTO_PRINCIPAL}")
                    )
                    self.barra_busqueda.on("keydown.enter", self.buscar_proyectos_gui)
                    ui.button("Buscar", on_click=self.buscar_proyectos_gui).classes(
                        "bg-blue-600"
                    )

                with ui.row().classes("w-full justify-between items-center mt-4"):
                    self.label_seleccionado = (
                        ui.label("Ningún proyecto seleccionado")
                        .classes("text-body1")
                        .style(f"color: {TEXTO_PRINCIPAL}")
                    )
                    with ui.row().classes("gap-2"):
                        self.boton_editar = ui.button(
                            "Editar Proyecto",
                            on_click=self.mostrar_form_editar_proyecto,
                        ).classes("bg-blue-600")
                        self.boton_editar.disable()
                        ui.button(
                            "Nuevo Proyecto", on_click=self.mostrar_form_nuevo_proyecto
                        ).classes("bg-blue-600")

            # Contenedor para los resultados (tarjetas)
            ui.label("Resultados de búsqueda").classes("text-h5 mt-4").style(
                f"color: {TEXTO_PRINCIPAL}"
            )
            self.contenedor_resultados = ui.column().classes("w-full gap-2")

            # Sección de detalles/formulario del proyecto (inicialmente oculta)
            self.seccion_detalles = (
                ui.card()
                .classes("w-full mt-4")
                .style(f"background-color: {FONDO_TARJETA}")
            )
            self.seccion_detalles.visible = False

    async def buscar_proyectos_gui(
        self,
    ):  # Renombrado para evitar conflicto con la importación
        termino = self.barra_busqueda.value
        self.seccion_detalles.visible = False
        self.label_seleccionado.set_text("Ningún proyecto seleccionado")
        self.boton_editar.disable()
        self.proyecto_seleccionado = None
        self.tarjeta_seleccionada_actual = None

        spinner = ui.spinner(color="blue")
        try:
            # Intentar buscar por ID primero
            try:
                proyecto_id = int(termino)
                proyecto = obtener_proyecto(proyecto_id)
                self.proyectos_encontrados = [proyecto] if proyecto else []
            except ValueError:
                # Si no es un ID, buscar por término
                self.proyectos_encontrados = buscar_proyectos(termino) or []
        finally:
            spinner.delete()

        self.actualizar_lista_proyectos()

    def actualizar_lista_proyectos(self):
        self.contenedor_resultados.clear()

        with self.contenedor_resultados:
            if not self.proyectos_encontrados:
                ui.label("No se encontraron proyectos.").classes(
                    "text-center text-gray-500"
                )
                return

            for proyecto in self.proyectos_encontrados:
                card_style = f"background-color: {FONDO_SECUNDARIO}; cursor: pointer; border: 1px solid gray;"
                hover_style = f"background-color: {AZUL_PRIMARIO};"

                # Crear tarjeta y asignar eventos
                with ui.card().classes("w-full p-2 hover:shadow-lg") as tarjeta:
                    tarjeta.style(card_style)
                    tarjeta.on(
                        "mouseover", lambda t=tarjeta, hs=hover_style: t.style(hs)
                    )
                    tarjeta.on(
                        "mouseout",
                        lambda t=tarjeta, cs=card_style: t.style(cs)
                        if t != self.tarjeta_seleccionada_actual
                        else None,
                    )  # No quitar hover si está seleccionada
                    tarjeta.on(
                        "click",
                        partial(
                            self.seleccionar_proyecto_desde_tarjeta,
                            proyecto.id,
                            tarjeta,
                        ),
                    )

                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.column():
                            ui.label(f"{proyecto.nombre_proyecto}").classes(
                                "text-lg font-semibold"
                            ).style(f"color: {TEXTO_PRINCIPAL}")
                            ui.label(
                                f"ID: {proyecto.id} | Ubic: {proyecto.ubicacion or 'N/A'}"
                            ).classes("text-sm").style(f"color: {TEXTO_PRINCIPAL}")
                        ui.label(
                            f"Desc: {proyecto.descripcion[:50] + '...' if proyecto.descripcion and len(proyecto.descripcion) > 50 else (proyecto.descripcion or 'N/A')}"
                        ).classes("text-sm").style(f"color: {TEXTO_PRINCIPAL}")

    async def seleccionar_proyecto_desde_tarjeta(
        self, proyecto_id: int, tarjeta_seleccionada
    ):
        # Resaltar tarjeta seleccionada y desresaltar la anterior
        if (
            self.tarjeta_seleccionada_actual
            and self.tarjeta_seleccionada_actual != tarjeta_seleccionada
        ):
            self.tarjeta_seleccionada_actual.style(
                f"background-color: {FONDO_SECUNDARIO}; cursor: pointer; border: 1px solid gray;"
            )
        tarjeta_seleccionada.style(
            f"background-color: {AZUL_PRIMARIO}; border: 2px solid white;"
        )
        self.tarjeta_seleccionada_actual = tarjeta_seleccionada

        await self.cargar_proyecto(proyecto_id)

    async def cargar_proyecto(self, proyecto_id: int):
        spinner = ui.spinner(color="blue")
        self.proyecto_seleccionado = obtener_proyecto(proyecto_id)
        spinner.delete()

        if self.proyecto_seleccionado:
            self.label_seleccionado.set_text(
                f"Proyecto seleccionado: {self.proyecto_seleccionado.nombre_proyecto}"
            )
            self.boton_editar.enable()
            ui.notify(
                f'Proyecto "{self.proyecto_seleccionado.nombre_proyecto}" seleccionado',
                color="info",
            )
            self.seccion_detalles.visible = False  # Ocultar formulario al seleccionar
        else:
            ui.notify("No se pudo cargar el proyecto", color="negative")
            self.label_seleccionado.set_text("Error al cargar proyecto")
            self.boton_editar.disable()

    def mostrar_form_editar_proyecto(self):
        if not self.proyecto_seleccionado:
            ui.notify("Debe seleccionar un proyecto primero", color="warning")
            return

        self.seccion_detalles.clear()
        self.seccion_detalles.visible = True

        with self.seccion_detalles:
            ui.label(
                f"Editar Proyecto: {self.proyecto_seleccionado.nombre_proyecto}"
            ).classes("text-h5").style(f"color: {TEXTO_PRINCIPAL}")
            self._crear_campos_formulario(editar=True)
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button(
                    "Cancelar",
                    on_click=lambda: self.seccion_detalles.set_visibility(False),
                ).classes("bg-red-500")
                ui.button(
                    "Guardar Cambios", on_click=self.guardar_cambios_proyecto
                ).classes("bg-blue-600")

    def mostrar_form_nuevo_proyecto(self):
        self.seccion_detalles.clear()
        self.seccion_detalles.visible = True
        self.proyecto_seleccionado = None  # Deseleccionar al crear nuevo
        self.label_seleccionado.set_text("Creando nuevo proyecto...")
        self.boton_editar.disable()
        if self.tarjeta_seleccionada_actual:
            self.tarjeta_seleccionada_actual.style(
                f"background-color: {FONDO_SECUNDARIO}; cursor: pointer; border: 1px solid gray;"
            )
            self.tarjeta_seleccionada_actual = None

        with self.seccion_detalles:
            ui.label("Nuevo Proyecto").classes("text-h5").style(
                f"color: {TEXTO_PRINCIPAL}"
            )
            self._crear_campos_formulario(editar=False)
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button(
                    "Cancelar",
                    on_click=lambda: self.seccion_detalles.set_visibility(False),
                ).classes("bg-red-500")
                ui.button("Crear Proyecto", on_click=self.crear_nuevo_proyecto).classes(
                    "bg-blue-600"
                )

    def _crear_campos_formulario(self, editar: bool):
        data = self.proyecto_seleccionado if editar else None

        with ui.row().classes("w-full items-center gap-4"):
            self.campos_proyecto["nombre_proyecto"] = ui.input(
                label="Nombre Proyecto *", value=getattr(data, "nombre_proyecto", "")
            ).classes("flex-grow")
            self.campos_proyecto["ubicacion"] = ui.input(
                label="Ubicación", value=getattr(data, "ubicacion", "") or ""
            ).classes("flex-grow")

        self.campos_proyecto["descripcion"] = ui.textarea(
            label="Descripción", value=getattr(data, "descripcion", "") or ""
        ).classes("w-full mt-4")

        # Añadir nota sobre la generación automática de descripción si está vacía
        if not editar:
            ui.label(
                "Nota: Si la descripción se deja vacía, se intentará generar una automáticamente."
            ).classes("text-xs text-gray-400 mt-1")

    async def guardar_cambios_proyecto(self):
        datos_actualizacion = {}
        for campo, elemento in self.campos_proyecto.items():
            valor = elemento.value
            # Tratar strings vacíos como None excepto para campos obligatorios
            if (
                isinstance(valor, str)
                and not valor.strip()
                and campo not in ["nombre_proyecto"]
            ):
                datos_actualizacion[campo] = None
            elif (
                valor is not None
            ):  # Permitir otros valores falsy como 0 si fuera aplicable
                datos_actualizacion[campo] = valor
            else:
                datos_actualizacion[campo] = (
                    None  # Asegurar que los campos no rellenados sean None si es necesario
                )

        if not datos_actualizacion.get("nombre_proyecto"):
            ui.notify("El Nombre del Proyecto es obligatorio", color="negative")
            return

        spinner = ui.spinner(color="blue")
        proyecto_actualizado = actualizar_proyecto(
            self.proyecto_seleccionado.id, datos_actualizacion
        )
        spinner.delete()

        if proyecto_actualizado:
            ui.notify("Proyecto actualizado correctamente", color="positive")
            self.proyecto_seleccionado = proyecto_actualizado
            # Actualizar la búsqueda para reflejar cambios si la lista actual lo contiene
            if self.proyectos_encontrados and any(
                p.id == proyecto_actualizado.id for p in self.proyectos_encontrados
            ):
                await self.buscar_proyectos_gui()  # Refresca la lista
            self.seccion_detalles.visible = False
            self.label_seleccionado.set_text(
                f"Proyecto seleccionado: {proyecto_actualizado.nombre_proyecto}"
            )
            self.boton_editar.enable()
        else:
            ui.notify("Error al actualizar el proyecto", color="negative")

    async def crear_nuevo_proyecto(self):
        datos_proyecto = {}
        for campo, elemento in self.campos_proyecto.items():
            valor = elemento.value
            if (
                isinstance(valor, str)
                and not valor.strip()
                and campo not in ["nombre_proyecto"]
            ):
                datos_proyecto[campo] = None
            elif valor is not None:
                datos_proyecto[campo] = valor
            else:
                datos_proyecto[campo] = None

        if not datos_proyecto.get("nombre_proyecto"):
            ui.notify("El Nombre del Proyecto es obligatorio", color="negative")
            return

        spinner = ui.spinner(color="blue")
        nuevo_proyecto = crear_proyecto(datos_proyecto)
        spinner.delete()

        if nuevo_proyecto:
            ui.notify(
                f"Proyecto creado correctamente con ID: {nuevo_proyecto.id}",
                color="positive",
            )
            self.barra_busqueda.set_value(
                str(nuevo_proyecto.id)
            )  # Poner ID en búsqueda
            await self.buscar_proyectos_gui()  # Buscar el nuevo proyecto
            self.seccion_detalles.visible = False
        else:
            ui.notify("Error al crear el proyecto", color="negative")


def iniciar_gui():
    # Importar inicializador de DB aquí si es necesario antes de arrancar la GUI
    # from orgm.apps.adm.db import initialize_db
    # initialize_db() # Asegúrate de que la conexión a la BD esté lista si las funciones la necesitan al cargarse

    app = ProyectoGUI()
    app.crear_interfaz()

    ui.run(
        title="Gestión de Proyectos",
        reload=False,  # Deshabilitar reload para producción o si causa problemas
        show=True,
        host="0.0.0.0",  # Escuchar en todas las interfaces
        port=3001,  # Usar puerto diferente al de cliente si se ejecutan ambos
    )


if __name__ in {"__main__", "__mp_main__"}:
    # Asegúrate de que las dependencias como la BD estén listas
    # initialize_db() # Podría ser necesario llamarlo aquí también
    iniciar_gui()
