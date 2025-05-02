


def obtener_tasa_divisa(desde: str, a: str, cantidad: float) -> float | None:
    import os
    import requests

    API_URL = os.getenv("API_URL")
    """Obtiene la tasa de cambio entre dos divisas"""
    if not API_URL:
        print("Error: La URL de PostgREST no está configurada en las variables de entorno.")
        return None
        
    try:
        response = requests.post(
            f"{API_URL}/divisa", json={"desde": desde, "a": a, "cantidad": cantidad}, timeout=10
        )
        response.raise_for_status()
        # Quitado: print("Divisa response:", response.json())
        return response.json().get("resultado") # Devuelve None si 'resultado' no existe
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de divisas: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al obtener tasa de divisa: {e}")
        return None
    


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    API_URL = "http://10.0.0.13:3011" 
    print(obtener_tasa_divisa("USD", "RD$", 1))
