from typing import List
from orgm.apps.adm.db import Ubicacion
from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from orgm.stuff.spinner import spinner
from orgm.apps.adm.proyecto.locations import obtener_ubicaciones

import questionary
from typing import Optional


console = Console()


def buscar_ubicaciones(termino: str) -> List[Ubicacion]:
    """Busca ubicaciones por provincia, distrito o distrito municipal"""
    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Ubicacion

    try:
        response = requests.get(
            f"{POSTGREST_URL}/ubicacion?or=(provincia.ilike.*{termino}*,distrito.ilike.*{termino}*,distritomunicipal.ilike.*{termino}*)",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        ubicaciones_data = response.json()
        ubicaciones = [
            Ubicacion.model_validate(ubicacion) for ubicacion in ubicaciones_data
        ]
        return ubicaciones
    except Exception as e:
        console.print(f"[bold red]Error al buscar ubicaciones: {e}[/bold red]")
        return []


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
