from orgm.apps.adm.cotizacion.get_quotations import obtener_cotizaciones
from orgm.apps.adm.cotizacion.show_quotations import mostrar_cotizaciones
from typing import Optional
import questionary


def _preguntar_cliente() -> Optional[int]:
    global _ultimo_cliente_id
    default_val = str(_ultimo_cliente_id) if _ultimo_cliente_id else ""
    cid_str = questionary.text("ID del cliente:", default=default_val).ask()
    if not cid_str:
        return None
    try:
        cid = int(cid_str)
    except ValueError:
        print("[bold red]ID inválido[/bold red]")
        return None

    # Mostrar últimas 10 cotizaciones de este cliente
    cotis = [c for c in obtener_cotizaciones() if c["id_cliente"] == cid]
    cotis.sort(key=lambda x: x.get("fecha", ""), reverse=True)
    mostrar_cotizaciones(cotis[:10])
    if (
        len(cotis) > 10
        and questionary.confirm("¿Mostrar más cotizaciones?", default=False).ask()
    ):
        mostrar_cotizaciones(cotis)

    _ultimo_cliente_id = cid
    return cid
