import multiprocessing

# Configurar multiprocessing para usar 'spawn' en lugar de 'fork'
multiprocessing.set_start_method("spawn", force=True)

from nicegui import ui
from typing import List, Optional
from functools import partial
from orgm.apps.adm.cliente.find_clients import buscar_clientes
from orgm.apps.adm.cliente.get_client import obtener_cliente
from orgm.apps.adm.cliente.edit_client import actualizar_cliente
from orgm.apps.adm.cliente.new_client import crear_cliente
from orgm.apps.adm.db import Cliente
from orgm.apps.adm.cliente.tipos import TipoFactura

# Intentar importar el módulo de colores, si falla usar los valores predefinidos
try:
    from orgm.stuff.gui_color import *
except ImportError:
    # Definición de colores como respaldo
    # Colores principales
    FONDO_PRINCIPAL = "#121212"  # Gris oscuro casi negro
    FONDO_SECUNDARIO = "#1E1E1E"  # Gris oscuro para contraste
    FONDO_TARJETA = "#2D2D2D"  # Gris para tarjetas

    # Colores de acentos
    AZUL_PRIMARIO = "#2563EB"  # Azul para botones principales
    TEXTO_PRINCIPAL = "#FFFFFF"  # Blanco para texto principal

    # Configuración de tema
    TEMA_OSCURO = True  # Indicador de tema oscuro


class ClienteGUI:
    def __init__(self):
        self.clientes_encontrados: List[Cliente] = []
        self.cliente_seleccionado: Optional[Cliente] = None
        self.barra_busqueda = None
        self.seccion_detalles = None
        self.campos_cliente = {}
        self.label_seleccionado = None
        self.boton_editar = None
        self.contenedor_resultados = None  # Contenedor para las tarjetas
        self.tarjeta_seleccionada_actual = None  # Para resaltar la tarjeta

    def crear_interfaz(self):
        # Establecer tema oscuro
        ui.dark_mode().enable() if TEMA_OSCURO else ui.dark_mode().disable()

        # Establecer fondo principal
        ui.page_title("Gestión de Clientes")
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
                ui.label("Gestión de Clientes").classes("text-h4 text-center").style(
                    f"color: {TEXTO_PRINCIPAL}"
                )

            # Sección de búsqueda y acciones
            with (
                ui.card().classes("w-full").style(f"background-color: {FONDO_TARJETA}")
            ):
                with ui.row().classes("w-full items-center"):
                    self.barra_busqueda = (
                        ui.input(label="Buscar cliente", placeholder="Nombre o ID...")
                        .classes("flex-grow")
                        .style(f"color: {TEXTO_PRINCIPAL}")
                    )
                    self.barra_busqueda.on("keydown.enter", self.buscar_clientes)
                    ui.button("Buscar", on_click=self.buscar_clientes).classes(
                        "bg-blue-600"
                    )

                with ui.row().classes("w-full justify-between items-center mt-4"):
                    self.label_seleccionado = (
                        ui.label("Ningún cliente seleccionado")
                        .classes("text-body1")
                        .style(f"color: {TEXTO_PRINCIPAL}")
                    )
                    with ui.row().classes("gap-2"):
                        self.boton_editar = ui.button(
                            "Editar Cliente", on_click=self.mostrar_form_editar_cliente
                        ).classes("bg-blue-600")
                        self.boton_editar.disable()
                        ui.button(
                            "Nuevo Cliente", on_click=self.mostrar_form_nuevo_cliente
                        ).classes("bg-blue-600")

            # Contenedor para los resultados (tarjetas)
            ui.label("Resultados de búsqueda").classes("text-h5 mt-4").style(
                f"color: {TEXTO_PRINCIPAL}"
            )
            self.contenedor_resultados = ui.column().classes("w-full gap-2")

            # Sección de detalles/formulario del cliente (inicialmente oculta)
            self.seccion_detalles = (
                ui.card()
                .classes("w-full mt-4")
                .style(f"background-color: {FONDO_TARJETA}")
            )
            self.seccion_detalles.visible = False

    async def buscar_clientes(self):
        termino = self.barra_busqueda.value
        self.seccion_detalles.visible = False
        self.label_seleccionado.set_text("Ningún cliente seleccionado")
        self.boton_editar.disable()
        self.cliente_seleccionado = None
        self.tarjeta_seleccionada_actual = None

        spinner = ui.spinner(color="blue")
        try:
            cliente_id = int(termino)
            cliente = obtener_cliente(cliente_id)
            self.clientes_encontrados = [cliente] if cliente else []
        except ValueError:
            self.clientes_encontrados = buscar_clientes(termino) or []
        finally:
            spinner.delete()

        self.actualizar_lista_clientes()

    def actualizar_lista_clientes(self):
        self.contenedor_resultados.clear()

        with self.contenedor_resultados:
            if not self.clientes_encontrados:
                ui.label("No se encontraron clientes.").classes(
                    "text-center text-gray-500"
                )
                return

            for cliente in self.clientes_encontrados:
                card_style = f"background-color: {FONDO_SECUNDARIO}; cursor: pointer; border: 1px solid gray;"
                hover_style = f"background-color: {AZUL_PRIMARIO};"

                # Crear tarjeta y asignar eventos usando la instancia 'tarjeta'
                with ui.card().classes("w-full p-2 hover:shadow-lg") as tarjeta:
                    tarjeta.style(card_style)
                    # Usar la instancia 'tarjeta' en las lambdas
                    tarjeta.on(
                        "mouseover", lambda t=tarjeta, hs=hover_style: t.style(hs)
                    )
                    tarjeta.on("mouseout", lambda t=tarjeta, cs=card_style: t.style(cs))
                    tarjeta.on(
                        "click",
                        partial(
                            self.seleccionar_cliente_desde_tarjeta, cliente.id, tarjeta
                        ),
                    )

                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.column():
                            ui.label(f"{cliente.nombre}").classes(
                                "text-lg font-semibold"
                            ).style(f"color: {TEXTO_PRINCIPAL}")
                            ui.label(
                                f"ID: {cliente.id} | NIF: {cliente.numero}"
                            ).classes("text-sm").style(f"color: {TEXTO_PRINCIPAL}")
                        ui.label(f"Tel: {cliente.telefono or 'N/A'}").classes(
                            "text-sm"
                        ).style(f"color: {TEXTO_PRINCIPAL}")

    async def seleccionar_cliente_desde_tarjeta(
        self, cliente_id: int, tarjeta_seleccionada
    ):
        # Opcional: Lógica para resaltar/desresaltar tarjetas
        # if self.tarjeta_seleccionada_actual and self.tarjeta_seleccionada_actual != tarjeta_seleccionada:
        #     self.tarjeta_seleccionada_actual.style(f'background-color: {FONDO_SECUNDARIO}; cursor: pointer; border: 1px solid gray;')
        # tarjeta_seleccionada.style(f'background-color: {AZUL_PRIMARIO}; border: 2px solid white;')
        # self.tarjeta_seleccionada_actual = tarjeta_seleccionada

        await self.cargar_cliente(cliente_id)

    async def cargar_cliente(self, cliente_id: int):
        spinner = ui.spinner(color="blue")
        self.cliente_seleccionado = obtener_cliente(cliente_id)
        spinner.delete()

        if self.cliente_seleccionado:
            self.label_seleccionado.set_text(
                f"Cliente seleccionado: {self.cliente_seleccionado.nombre}"
            )
            self.boton_editar.enable()
            ui.notify(
                f'Cliente "{self.cliente_seleccionado.nombre}" seleccionado',
                color="info",
            )
            self.seccion_detalles.visible = False
        else:
            ui.notify("No se pudo cargar el cliente", color="negative")
            self.label_seleccionado.set_text("Error al cargar cliente")
            self.boton_editar.disable()

    def mostrar_form_editar_cliente(self):
        if not self.cliente_seleccionado:
            ui.notify("Debe seleccionar un cliente primero", color="warning")
            return

        self.seccion_detalles.clear()
        self.seccion_detalles.visible = True

        with self.seccion_detalles:
            ui.label(f"Editar Cliente: {self.cliente_seleccionado.nombre}").classes(
                "text-h5"
            ).style(f"color: {TEXTO_PRINCIPAL}")
            self._crear_campos_formulario(editar=True)
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button(
                    "Cancelar",
                    on_click=lambda: self.seccion_detalles.set_visibility(False),
                ).classes("bg-red-500")
                ui.button(
                    "Guardar Cambios", on_click=self.guardar_cambios_cliente
                ).classes("bg-blue-600")

    def mostrar_form_nuevo_cliente(self):
        self.seccion_detalles.clear()
        self.seccion_detalles.visible = True
        self.cliente_seleccionado = None
        self.label_seleccionado.set_text("Creando nuevo cliente...")
        self.boton_editar.disable()

        with self.seccion_detalles:
            ui.label("Nuevo Cliente").classes("text-h5").style(
                f"color: {TEXTO_PRINCIPAL}"
            )
            self._crear_campos_formulario(editar=False)
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button(
                    "Cancelar",
                    on_click=lambda: self.seccion_detalles.set_visibility(False),
                ).classes("bg-red-500")
                ui.button("Crear Cliente", on_click=self.crear_nuevo_cliente).classes(
                    "bg-blue-600"
                )

    def _crear_campos_formulario(self, editar: bool):
        data = self.cliente_seleccionado if editar else None

        with ui.row().classes("w-full items-center"):
            self.campos_cliente["nombre"] = ui.input(
                label="Nombre *", value=getattr(data, "nombre", "")
            ).classes("w-1/2")
            self.campos_cliente["numero"] = ui.input(
                label="Número/NIF *", value=getattr(data, "numero", "")
            ).classes("w-1/2")

        with ui.row().classes("w-full items-center"):
            self.campos_cliente["nombre_comercial"] = ui.input(
                label="Nombre Comercial",
                value=getattr(data, "nombre_comercial", "") or "",
            ).classes("w-1/2")
            self.campos_cliente["correo"] = ui.input(
                label="Correo", value=getattr(data, "correo", "") or ""
            ).classes("w-1/2")

        with ui.row().classes("w-full items-center"):
            self.campos_cliente["telefono"] = ui.input(
                label="Teléfono", value=getattr(data, "telefono", "") or ""
            ).classes("w-1/2")
            self.campos_cliente["direccion"] = ui.input(
                label="Dirección", value=getattr(data, "direccion", "") or ""
            ).classes("w-1/2")

        with ui.row().classes("w-full items-center"):
            self.campos_cliente["ciudad"] = ui.input(
                label="Ciudad", value=getattr(data, "ciudad", "") or ""
            ).classes("w-1/2")
            self.campos_cliente["provincia"] = ui.input(
                label="Provincia", value=getattr(data, "provincia", "") or ""
            ).classes("w-1/2")

        ui.label("Datos del Representante").classes("text-h6 mt-4").style(
            f"color: {TEXTO_PRINCIPAL}"
        )
        with ui.row().classes("w-full items-center"):
            self.campos_cliente["representante"] = ui.input(
                label="Nombre Representante",
                value=getattr(data, "representante", "") or "",
            ).classes("w-1/2")
            self.campos_cliente["telefono_representante"] = ui.input(
                label="Teléfono Representante",
                value=getattr(data, "telefono_representante", "") or "",
            ).classes("w-1/2")

        with ui.row().classes("w-full items-center"):
            self.campos_cliente["extension_representante"] = ui.input(
                label="Extensión",
                value=getattr(data, "extension_representante", "") or "",
            ).classes("w-1/3")
            self.campos_cliente["celular_representante"] = ui.input(
                label="Celular", value=getattr(data, "celular_representante", "") or ""
            ).classes("w-1/3")
            self.campos_cliente["correo_representante"] = ui.input(
                label="Correo", value=getattr(data, "correo_representante", "") or ""
            ).classes("w-1/3")

        ui.label("Configuración de Factura").classes("text-h6 mt-4").style(
            f"color: {TEXTO_PRINCIPAL}"
        )
        self.campos_cliente["tipo_factura"] = ui.select(
            label="Tipo de Factura",
            options=[e.value for e in TipoFactura],
            value=getattr(data, "tipo_factura", TipoFactura.NCFC.value),
        ).classes("w-full")

    async def guardar_cambios_cliente(self):
        datos_actualizacion = {}
        for campo, elemento in self.campos_cliente.items():
            valor = elemento.value
            if (
                isinstance(valor, str)
                and not valor.strip()
                and campo not in ["nombre", "numero"]
            ):
                datos_actualizacion[campo] = None
            elif valor or valor == 0:
                datos_actualizacion[campo] = valor
            else:
                datos_actualizacion[campo] = None

        if not datos_actualizacion.get("nombre") or not datos_actualizacion.get(
            "numero"
        ):
            ui.notify("Nombre y Número/NIF son campos obligatorios", color="negative")
            return

        spinner = ui.spinner(color="blue")
        cliente_actualizado = actualizar_cliente(
            self.cliente_seleccionado.id, datos_actualizacion
        )
        spinner.delete()

        if cliente_actualizado:
            ui.notify("Cliente actualizado correctamente", color="positive")
            self.cliente_seleccionado = cliente_actualizado
            await self.buscar_clientes()
            self.seccion_detalles.visible = False
            self.label_seleccionado.set_text(
                f"Cliente seleccionado: {self.cliente_seleccionado.nombre}"
            )
            self.boton_editar.enable()
        else:
            ui.notify("Error al actualizar el cliente", color="negative")

    async def crear_nuevo_cliente(self):
        datos_cliente = {}
        for campo, elemento in self.campos_cliente.items():
            valor = elemento.value
            if (
                isinstance(valor, str)
                and not valor.strip()
                and campo not in ["nombre", "numero"]
            ):
                datos_cliente[campo] = None
            elif valor or valor == 0:
                datos_cliente[campo] = valor
            else:
                datos_cliente[campo] = None

        if not datos_cliente.get("nombre") or not datos_cliente.get("numero"):
            ui.notify("Nombre y Número/NIF son campos obligatorios", color="negative")
            return

        spinner = ui.spinner(color="blue")
        nuevo_cliente = crear_cliente(datos_cliente)
        spinner.delete()

        if nuevo_cliente:
            ui.notify(
                f"Cliente creado correctamente con ID: {nuevo_cliente.id}",
                color="positive",
            )
            self.barra_busqueda.set_value(str(nuevo_cliente.id))
            await self.buscar_clientes()
            self.seccion_detalles.visible = False
        else:
            ui.notify("Error al crear el cliente", color="negative")


def iniciar_gui():
    app = ClienteGUI()
    app.crear_interfaz()

    ui.run(
        title="Gestión de Clientes", reload=False, show=True, host="0.0.0.0", port=3000
    )


if __name__ in {"__main__", "__mp_main__"}:
    iniciar_gui()
