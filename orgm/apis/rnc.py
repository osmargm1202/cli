import requests
import os
from orgm.apis.header import get_headers_json

def buscar_rnc_cliente(busqueda: str, activo: bool = True):
    RNC_URL = os.getenv("RNC_URL")
    """Busca clientes por nombre o RNC en la API."""
    if not RNC_URL:
        print("Error: La URL de la API RNC no está configurada en las variables de entorno.")
        return None

    headers = get_headers_json()
    url = f"{RNC_URL}/buscar"
    payload = {"busqueda": busqueda, "activo": activo}

    try:
        response = requests.get(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status() # Lanza excepción para códigos de error HTTP
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API RNC: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al buscar RNC: {e}")
        return None

