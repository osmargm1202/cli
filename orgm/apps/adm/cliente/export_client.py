import json
from typing import Tuple
from rich.console import Console

console = Console()


def exportar_cliente(cliente, formato: str) -> Tuple[bool, str]:
    """
    Exporta los datos de un cliente al formato especificado.

    Args:
        cliente: Objeto (preferiblemente Pydantic model) o diccionario con los datos del cliente.
        formato (str): El formato deseado (actualmente solo soporta 'json').

    Returns:
        Tuple[bool, str]: Una tupla (éxito, contenido).
                         Si éxito es True, contenido es la cadena formateada.
                         Si éxito es False, contenido es un mensaje de error.
    """
    if formato.lower() == "json":
        try:
            if hasattr(cliente, "model_dump_json"):
                # Si es un modelo Pydantic, usar su método de serialización
                # Asegurarse de que fechas y otros tipos se manejen bien
                contenido_json = cliente.model_dump_json(indent=4)
            elif isinstance(cliente, dict):
                # Si es un diccionario (como el devuelto por actualizar_cliente a veces)
                # Usar default=str para manejar tipos no serializables como datetime
                contenido_json = json.dumps(
                    cliente, indent=4, default=str, ensure_ascii=False
                )
            else:
                # Fallback genérico para otros tipos serializables
                # Intentar convertir a dict si tiene __dict__ o similar? O simplemente usar str?
                # Por seguridad, intentar volcar directamente puede ser mejor
                # Añadir default=str aquí también
                contenido_json = json.dumps(
                    cliente, indent=4, default=str, ensure_ascii=False
                )

            return True, contenido_json
        except TypeError as e:
            return False, f"Error al serializar a JSON: {e}"
        except Exception as e:
            return False, f"Error inesperado durante la exportación a JSON: {e}"
    else:
        return False, f"Formato de exportación no soportado: {formato}"


def formatear_cliente_json(cliente) -> str:
    """
    Formatea los datos de un cliente como una cadena JSON.

    Args:
        cliente: Objeto (preferiblemente Pydantic model) o diccionario con los datos del cliente.

    Returns:
        str: Cadena JSON formateada o un JSON de error si falla la serialización.
    """
    exito, contenido = exportar_cliente(cliente, "json")
    if exito:
        return contenido
    else:
        # Devolver un JSON indicando el error
        return json.dumps({"error": contenido}, indent=4, ensure_ascii=False)
