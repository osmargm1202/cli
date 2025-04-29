from contextlib import contextmanager
from rich.console import Console

console = Console()

# Contador global para llevar el control de cuántos spinners están activos.
_spinner_counter: int = 0


@contextmanager
def spinner(message: str = "Cargando..."):
    """
    Context manager para mostrar un spinner mientras se ejecuta una operación
    potencialmente lenta. Si ya existe un spinner activo (por ejemplo, el
    código se encuentra dentro de otro bloque `with spinner()`), se omite la
    creación de un nuevo *live display* para evitar la excepción de Rich:

        RuntimeError: Only one live display may be active at once

    Ejemplo de uso::

        with spinner("Obteniendo datos..."):
            resultado = hacer_algo_lento()
    """

    global _spinner_counter

    # Si ya hay un spinner activo, no crear uno nuevo; simplemente ejecutar el
    # bloque para evitar la anidación que provoca la excepción.
    if _spinner_counter > 0:
        _spinner_counter += 1  # Incrementamos para mantener el balance
        try:
            yield
        finally:
            _spinner_counter -= 1
        return

    # Primer (y único) spinner activo
    _spinner_counter += 1
    try:
        with console.status(f"[blue]{message}", spinner="dots"):
            yield
    finally:
        _spinner_counter -= 1
