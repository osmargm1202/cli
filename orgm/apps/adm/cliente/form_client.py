from rich.console import Console
from typing import Optional, Dict
from orgm.apps.utils.rnc.api import buscar_empresa_en_dgii
import questionary
from orgm.apps.adm.cliente.tipos import TipoFactura
from orgm.stuff.spinner import spinner

console = Console()


def formulario_cliente(cliente=None) -> Optional[Dict]:
    """
    Muestra un formulario interactivo para crear o modificar un cliente.

    Args:
        cliente: Datos del cliente existente para modificar. None si es nuevo.

    Returns:
        Optional[Dict]: Diccionario con los datos del cliente o None si se cancela.
    """
    nombre_seleccionado = None
    numero_seleccionado = None

    if cliente is None:  # Crear nuevo cliente
        buscar_api = questionary.confirm(
            "¿Buscar cliente por RNC/Nombre en la API antes de crear?"
        ).ask()
        if buscar_api:
            while True:  # Bucle de búsqueda
                termino_busqueda = questionary.text(
                    "Ingrese término de búsqueda (Nombre o RNC):"
                ).ask()
                if not termino_busqueda:
                    print(
                        "[yellow]Búsqueda cancelada. Ingresando datos manualmente.[/yellow]"
                    )
                    break  # Salir del bucle y proceder manualmente

                with spinner(f"Buscando '{termino_busqueda}' en la API RNC..."):
                    resultados_api = buscar_empresa_en_dgii(termino_busqueda)

                if not resultados_api:
                    print("[yellow]No se encontraron resultados.[/yellow]")
                    reintentar = questionary.select(
                        "¿Qué desea hacer?",
                        choices=["Buscar de nuevo", "Continuar manualmente"],
                    ).ask()
                    if reintentar == "Continuar manualmente":
                        break
                    # Si elige "Buscar de nuevo", el bucle continúa
                else:
                    # Formatear resultados para questionary
                    opciones = []
                    for res in resultados_api:
                        # Asegurarse de que las claves existen y formatear
                        rnc = res.get("rnc", "N/A")
                        razon = res.get("razon", "N/A")
                        opciones.append(f"{rnc} - {razon}")

                    opciones.extend(["Buscar de nuevo", "Continuar manualmente"])

                    seleccion = questionary.select(
                        "Seleccione el cliente deseado:", choices=opciones
                    ).ask()

                    if seleccion == "Continuar manualmente":
                        break
                    elif seleccion == "Buscar de nuevo":
                        continue  # Volver a pedir término de búsqueda
                    else:
                        # Extraer RNC y Razón Social de la selección
                        try:
                            numero_seleccionado = seleccion.split(" - ")[0]
                            nombre_seleccionado = seleccion.split(" - ")[1]
                            print(
                                f"[green]Cliente seleccionado:[/green] {nombre_seleccionado} (RNC: {numero_seleccionado})"
                            )
                            break  # Salir del bucle con los datos seleccionados
                        except IndexError:
                            print(
                                "[red]Error al procesar la selección. Intentando de nuevo.[/red]"
                            )
                            continue  # Algo salió mal, volver a buscar

    # Valores por defecto (usar los seleccionados si existen)
    defaults = {}
    if cliente:  # Modificar cliente existente
        try:
            defaults = cliente.model_dump()
        except AttributeError:
            defaults = {}  # Fallback
    else:  # Crear nuevo cliente
        defaults = {
            "nombre": nombre_seleccionado or "",
            "numero": numero_seleccionado or "",
            "nombre_comercial": "",
            "correo": "",
            "direccion": "",
            "ciudad": "",
            "provincia": "",
            "telefono": "",
            "representante": "",
            "telefono_representante": "",
            "extension_representante": "",
            "celular_representante": "",
            "correo_representante": "",
            "tipo_factura": TipoFactura.NCFC,  # Usar Enum
        }

    # --- Formulario principal ---
    nombre = questionary.text(
        "Nombre del cliente:", default=defaults.get("nombre", "")
    ).ask()
    if not nombre:
        return None  # Cancelar si no hay nombre
    # ... resto de las preguntas del formulario ...

    nombre_comercial = questionary.text(
        "Nombre comercial:", default=defaults.get("nombre_comercial", "")
    ).ask()

    numero = questionary.text(
        "Número/NIF del cliente:", default=defaults.get("numero", "")
    ).ask()
    if not numero:
        return None  # Cancelar si no hay número

    correo = questionary.text(
        "Correo electrónico:", default=defaults.get("correo", "")
    ).ask()
    direccion = questionary.text(
        "Dirección:", default=defaults.get("direccion", "")
    ).ask()
    ciudad = questionary.text("Ciudad:", default=defaults.get("ciudad", "")).ask()
    provincia = questionary.text(
        "Provincia:", default=defaults.get("provincia", "")
    ).ask()
    telefono = questionary.text("Teléfono:", default=defaults.get("telefono", "")).ask()
    representante = questionary.text(
        "Nombre del representante:", default=defaults.get("representante", "")
    ).ask()
    telefono_representante = questionary.text(
        "Teléfono del representante:",
        default=defaults.get("telefono_representante", ""),
    ).ask()
    extension_representante = questionary.text(
        "Extensión del representante:",
        default=defaults.get("extension_representante", ""),
    ).ask()
    celular_representante = questionary.text(
        "Celular del representante:",
        default=defaults.get("celular_representante", ""),
    ).ask()
    correo_representante = questionary.text(
        "Correo del representante:",
        default=defaults.get("correo_representante", ""),
    ).ask()

    # Usar el Enum para el tipo de factura
    tipo_factura_str = questionary.select(
        "Tipo de factura:",
        choices=[e.value for e in TipoFactura],
        default=defaults.get("tipo_factura", TipoFactura.NCFC).value,
    ).ask()
    tipo_factura = (
        TipoFactura(tipo_factura_str) if tipo_factura_str else TipoFactura.NCFC
    )

    # Devolver un diccionario con los datos, usando None para campos vacíos opcionales
    return {
        "nombre": nombre,
        "nombre_comercial": nombre_comercial if nombre_comercial else None,
        "numero": numero,
        "correo": correo if correo else None,
        "direccion": direccion if direccion else None,
        "ciudad": ciudad if ciudad else None,
        "provincia": provincia if provincia else None,
        "telefono": telefono if telefono else None,
        "representante": representante if representante else None,
        "telefono_representante": telefono_representante
        if telefono_representante
        else None,
        "extension_representante": extension_representante
        if extension_representante
        else None,
        "celular_representante": celular_representante
        if celular_representante
        else None,
        "correo_representante": correo_representante if correo_representante else None,
        "tipo_factura": tipo_factura.value,  # Enviar el valor string a la API
    }
