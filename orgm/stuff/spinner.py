from contextlib import contextmanager
from rich.console import Console

console = Console()


@contextmanager
def spinner(message: str = "Cargando..."):
    """
    Context manager para mostrar un spinner mientras se ejecuta
    una operación que puede tardar.

    Uso:
        with spinner("Obteniendo datos..."):
            resultado = hacer_algo()
    """
    with console.status(f"[cyan]{message}", spinner="dots"):
        yield
