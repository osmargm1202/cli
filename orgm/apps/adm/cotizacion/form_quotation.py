from orgm.apps.adm.cotizacion.ask_client import _preguntar_cliente
from orgm.apps.adm.cotizacion.select_service import seleccionar_servicio
from orgm.apps.utils.divisa import obtener_tasa_divisa
from orgm.apps.ai.generate import generate_text
from orgm.stuff.spinner import spinner
import questionary


def formulario_cotizacion(cotizacion=None) -> dict:
    """Formulario para crear o actualizar una cotización"""
    es_nuevo = cotizacion is None

    # Verificar si cotizacion es un diccionario o un objeto y obtener valores por defecto
    defaults = {}
    if cotizacion:
        if isinstance(cotizacion, dict):
            # Si es un diccionario, usar .get()
            defaults = {
                "id_cliente": cotizacion.get("id_cliente", ""),
                "id_proyecto": cotizacion.get("id_proyecto", ""),
                "id_servicio": cotizacion.get("id_servicio", ""),
                "moneda": cotizacion.get("moneda", "RD$"),
                "descripcion": cotizacion.get("descripcion", ""),
                "estado": cotizacion.get("estado", "GENERADA"),
                "total": cotizacion.get("total", 0.0),
                "fecha": cotizacion.get("fecha", ""),
                "tasa_moneda": cotizacion.get("tasa_moneda", 1.0),
                "tiempo_entrega": cotizacion.get("tiempo_entrega", "3"),
                "avance": cotizacion.get("avance", "60"),
                "validez": cotizacion.get("validez", 30),
                "idioma": cotizacion.get("idioma", "ES"),
                "descuentop": cotizacion.get("descuentop", 0),
            }
        else:
            # Si es un objeto, usar getattr()
            defaults = {
                "id_cliente": getattr(cotizacion, "id_cliente", ""),
                "id_proyecto": getattr(cotizacion, "id_proyecto", ""),
                "id_servicio": getattr(cotizacion, "id_servicio", ""),
                "moneda": getattr(cotizacion, "moneda", "RD$"),
                "descripcion": getattr(cotizacion, "descripcion", ""),
                "estado": getattr(cotizacion, "estado", "GENERADA"),
                "total": getattr(cotizacion, "total", 0.0),
                "fecha": getattr(cotizacion, "fecha", ""),
                "tasa_moneda": getattr(cotizacion, "tasa_moneda", 1.0),
                "tiempo_entrega": getattr(cotizacion, "tiempo_entrega", "3"),
                "avance": getattr(cotizacion, "avance", "60"),
                "validez": getattr(cotizacion, "validez", 30),
                "idioma": getattr(cotizacion, "idioma", "ES"),
                "descuentop": getattr(cotizacion, "descuentop", 0),
            }
    else:
        # Valores predeterminados para nueva cotización
        defaults = {
            "id_cliente": "",
            "id_proyecto": "",
            "id_servicio": "",
            "moneda": "RD$",
            "descripcion": "",
            "estado": "GENERADA",
            "total": 0.0,
            "fecha": "",
            "tasa_moneda": 1.0,
            "tiempo_entrega": "3",
            "avance": "60",
            "validez": 30,
            "idioma": "ES",
            "descuentop": 0,
        }

    cid = _preguntar_cliente() if es_nuevo else defaults["id_cliente"]
    if cid is None:
        return {}
    datos = {}
    datos["id_cliente"] = cid
    datos["id_servicio"] = seleccionar_servicio(defaults["id_servicio"])
    datos["moneda"] = questionary.select(
        "Moneda:", choices=["RD$", "USD$", "EUR€"], default=defaults["moneda"]
    ).ask()

    # Fecha
    datos["fecha"] = questionary.text(
        "Fecha (YYYY-MM-DD):", default=defaults["fecha"]
    ).ask()

    # Tasa de cambio
    metodo_tasa = questionary.select(
        "¿Cómo desea obtener la tasa de cambio?",
        choices=["API", "Manual"],
        default="API",
    ).ask()
    if metodo_tasa == "API":
        with spinner("Obteniendo tasa de cambio USD->RD$..."):
            tasa = obtener_tasa_divisa("USD", "DOP", 10)
        datos["tasa_moneda"] = tasa or 1.0
    else:
        tasa_str = questionary.text(
            "Tasa de cambio:", default=str(defaults["tasa_moneda"])
        ).ask()
        try:
            datos["tasa_moneda"] = float(tasa_str)
        except ValueError:
            datos["tasa_moneda"] = 1.0

    metodo_desc = questionary.select(
        "¿Cómo desea establecer la descripción?",
        choices=["Manual", "Automática"],
        default="Manual" if defaults["descripcion"] else "Automática",
    ).ask()
    if metodo_desc == "Manual":
        datos["descripcion"] = questionary.text(
            "Descripción de la cotización:", default=defaults["descripcion"]
        ).ask()
    else:
        prompt = questionary.text("Prompt para generar descripción:").ask()
        if prompt:
            with spinner("Generando descripción con IA..."):
                desc = generate_text(prompt, "descripcion_electromecanica")
            datos["descripcion"] = desc or ""
        else:
            datos["descripcion"] = defaults["descripcion"]

    datos["estado"] = questionary.select(
        "Estado:",
        choices=["GENERADA", "ENVIADA", "ACEPTADA", "RECHAZADA"],
        default=defaults["estado"],
    ).ask()

    datos["tiempo_entrega"] = questionary.text(
        "Tiempo de entrega:", default=defaults["tiempo_entrega"]
    ).ask()
    datos["avance"] = questionary.text(
        "Porcentaje de avance:", default=defaults["avance"]
    ).ask()
    datos["validez"] = int(
        questionary.text("Días de validez:", default=str(defaults["validez"])).ask()
    )
    datos["idioma"] = questionary.select(
        "Idioma:", choices=["ES", "EN"], default=defaults["idioma"]
    ).ask()

    # descuento porcentaje
    desc_p = questionary.text(
        "Descuento (%):", default=str(defaults["descuentop"])
    ).ask()
    try:
        datos["descuentop"] = float(desc_p)
    except ValueError:
        datos["descuentop"] = 0.0

    return datos
