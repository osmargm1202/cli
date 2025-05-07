from rich.console import Console
from typing import Optional
from orgm.stuff.spinner import spinner
from orgm.apps.adm.cotizacion.get_services import obtener_servicios
import questionary

console = Console()


def seleccionar_servicio(id_default: Optional[int] = None) -> int:
    with spinner("Obteniendo lista de servicios..."):
        servicios = obtener_servicios()
    # Manejar tanto diccionarios como objetos
    opciones = []
    for s in servicios:
        if isinstance(s, dict):
            # Si es un diccionario, usar .get()
            id_servicio = s.get("id", "")
            nombre_servicio = s.get("nombre", "") or s.get("concepto", "")
        else:
            # Si es un objeto, usar getattr()
            id_servicio = getattr(s, "id", "")
            nombre_servicio = getattr(s, "nombre", "") or getattr(s, "concepto", "")

        opciones.append(f"{id_servicio}: {nombre_servicio}")

    if not opciones:
        return id_default or 0

    if id_default:
        opciones_default = next(
            (o for o in opciones if o.startswith(str(id_default))), opciones[0]
        )
    else:
        opciones_default = opciones[0]

    opciones.append("Cancelar")
    sel = questionary.select(
        "Seleccione servicio:", choices=opciones, default=opciones_default
    ).ask()
    if sel == "Cancelar":
        return id_default or 0

    return int(sel.split(":")[0])
