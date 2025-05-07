from typing import Optional
import questionary
from orgm.apps.adm.cliente.find_clients import buscar_clientes
from orgm.stuff.spinner import spinner


def seleccionar_cliente_por_nombre(termino: str) -> Optional[int]:
    with spinner(f"Buscando clientes por '{termino}'..."):
        clientes = buscar_clientes(termino)
    if not clientes:
        print("[yellow]No se encontraron clientes[/yellow]")
        return None

    # Manejar tanto diccionarios como objetos
    opciones = []
    for c in clientes:
        if isinstance(c, dict):
            # Si es un diccionario, usar .get()
            id_cliente = c.get("id", "")
            nombre_cliente = c.get("nombre", "")
        else:
            # Si es un objeto, usar getattr()
            id_cliente = getattr(c, "id", "")
            nombre_cliente = getattr(c, "nombre", "")

        opciones.append(f"{id_cliente}: {nombre_cliente}")

    opciones.append("Cancelar")
    sel = questionary.select("Seleccione un cliente:", choices=opciones).ask()
    if sel == "Cancelar":
        return None

    return int(sel.split(":")[0])
