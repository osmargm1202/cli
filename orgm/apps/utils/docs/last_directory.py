

import os
from rich.console import Console

console = Console()

def guardar_ultimo_directorio(directorio: str) -> bool:
    """
    Guarda el último directorio utilizado en un archivo de texto.
    
    Args:
        directorio: Ruta del directorio a guardar
        
    Returns:
        bool: True si se guardó correctamente, False en caso de error
    """
    try:
        ruta_config = os.path.join(os.path.expanduser("~"), ".orgm")
        if not os.path.exists(ruta_config):
            os.makedirs(ruta_config)
            
        ruta_archivo = os.path.join(ruta_config, "last_directory.txt")
        
        with open(ruta_archivo, "w") as f:
            f.write(directorio)

        directorio = os.path.normpath(directorio)
            
        console.print(f"Directorio guardado: {directorio}", style="bold green")
        return True
        
    except Exception as e:
        console.print(f"Error al guardar el directorio: {e}", style="bold red")
        return False

def obtener_ultimo_directorio() -> str:
    """
    Obtiene el último directorio guardado del archivo de texto.
    
    Returns:
        str: Ruta del último directorio utilizado o directorio actual si no existe
    """
    try:
        ruta_archivo = os.path.join(os.path.expanduser("~"), ".orgm", "last_directory.txt")
        
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, "r") as f:
                directorio = f.read().strip()
                if os.path.exists(directorio):
                    return directorio
                    
        return os.getcwd()
        
    except Exception as e:
        console.print(f"Error al leer el directorio: {e}", style="bold red")
        return os.getcwd()
