import requests
from dotenv import load_dotenv
import os
load_dotenv()

POSTGREST_URL = os.getenv("POSTGREST_URL")
# POSTGREST_URL = "http://10.0.0.13:3006"
# POSTGREST_URL = "https://sql.orgmapp.com"

CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

headers = {"Accept": "application/json"}

if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
    headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
    headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET

def get_cliente(id_cliente: int) -> dict:
    """
    Obtiene un cliente específico desde PostgREST
    
    Args:
        id_cliente: ID del cliente a consultar
        
    Returns:
        dict: Datos del cliente o diccionario vacío si no se encuentra
    """
    try:
        response = requests.get(
            f"{POSTGREST_URL}/cliente?id=eq.{id_cliente}",
            headers=headers
        )
        response.raise_for_status()
        clientes = response.json()
        return clientes[0] if clientes else {}
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener cliente: {e}")
        return {}

def buscar_clientes(termino: str) -> list:
    """
    Busca clientes que coincidan con el término en PostgREST
    
    Args:
        termino: Término de búsqueda
        
    Returns:
        list: Lista de clientes que coinciden con la búsqueda
    """
    try:
        response = requests.get(
            f"{POSTGREST_URL}/cliente?nombre=ilike.*{termino}*",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al buscar clientes: {e}")
        return []


if __name__ == "__main__":
    print(POSTGREST_URL)
    print(get_cliente(55))
    print(buscar_clientes("orgm"))
