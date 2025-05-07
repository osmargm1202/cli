from typing import Dict
import questionary
from orgm.apps.adm.proyecto.find_location import seleccionar_ubicacion
from rich.console import Console

console = Console()


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
        ubicacion_seleccionada = False
        while not ubicacion_seleccionada:
            ubicacion = seleccionar_ubicacion()
            if ubicacion:
                data["ubicacion"] = ubicacion
                ubicacion_seleccionada = True
            else:
                # Si seleccionar_ubicacion devuelve None (no encontró o canceló)
                reintentar = questionary.confirm(
                    "No se seleccionó ubicación. ¿Desea intentar buscar de nuevo?",
                    default=True,
                ).ask()
                if not reintentar:
                    # Si el usuario no quiere reintentar, mantener la ubicación existente (si la hay) o dejarla vacía
                    if not es_nuevo:
                        data["ubicacion"] = defaults["ubicacion"]
                    # Si es nuevo y no reintenta, la ubicación quedará sin asignar (o podría pedirla manualmente)
                    # Por ahora, rompemos el bucle y se queda vacía o con el valor por defecto si no era nuevo
                    break
                # Si reintentar es True, el bucle continúa

    elif not es_nuevo:
        # Mantener la ubicación existente si no se quiso cambiar
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
