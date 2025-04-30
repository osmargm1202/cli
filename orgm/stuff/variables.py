# -*- coding: utf-8 -*-
from typing import Optional
from rich.console import Console

# Importar la función de edición desde el nuevo módulo
from orgm.commands.editar import edit_env_variables

console = Console()

# La clase EnvEditor y la función original edit_env_variables 
# han sido movidas a orgm/commands/editar.py

def editar_variables(env_file_path: Optional[str] = None) -> bool:
    """Punto de entrada para editar variables de entorno (llama a la implementación en editar.py)."""
    console.print("[dim]Iniciando editor de variables de entorno...[/dim]")
    return edit_env_variables(env_file_path)

# Mantener un bloque __main__ para posible prueba directa (aunque ahora es solo un wrapper)
if __name__ == "__main__":
    console.print("Ejecutando editor de variables desde stuff/variables.py...")
    editar_variables()
