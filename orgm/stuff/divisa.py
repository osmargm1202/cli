import os
import requests
from dotenv import load_dotenv

load_dotenv()

POSTGREST_URL = os.getenv("POSTGREST_URL")
POSTGREST_URL = "http://10.0.0.13:3011"

def obtener_tasa_divisa(desde: str, a: str, cantidad: float) -> float:
    """Obtiene la tasa de cambio entre dos divisas"""
    response = requests.post(
        f"{POSTGREST_URL}/divisa", json={"desde": desde, "a": a, "cantidad": cantidad}
    )
    print("Divisa response:", response.json())
    return response.json().get("resultado", 1)

if __name__ == "__main__":
    print(obtener_tasa_divisa("USD", "DOP", 1))
