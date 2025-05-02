import asyncio
from typing import Optional
from pathlib import Path
from rich.console import Console
from orgm.stuff.editor import EnvEditor

console = Console()

def env_edit(env_file_path: Optional[str] = None) -> bool:
    """Abre el editor Textual para el archivo .env."""
    target_path = env_file_path or str(Path.cwd() / ".env")
    try:
        app = EnvEditor(file_path=target_path)
        # Ejecutar la app Textual dentro de asyncio.run()
        # Usamos run_async() dentro de asyncio.run
        # Nota: app.run() síncrono usualmente maneja el bucle, pero run_async
        # es explícitamente para ejecutar la corutina de la app.
        asyncio.run(app.run_async())
        
        # app.run() y run_async() devuelven None.
        # Para saber si se guardó, necesitaríamos que App.exit() devuelva algo
        # o que la app comunique el resultado de otra forma.
        # Asumimos éxito si no lanza excepción por ahora.
        return True
    except Exception as e:
        # Revisamos si el error es por el bucle (indicando un posible doble bucle)
        if "Cannot run the event loop while another loop is running" in str(e):
             console.print("[bold yellow]Advertencia:[/bold yellow] Parece que ya hay un bucle de eventos activo.")
             console.print("Intentando ejecutar de forma síncrona simple...")
             try:
                 # Intento alternativo si asyncio.run falla por bucle existente
                 app_sync = EnvEditor(file_path=target_path)
                 app_sync.run() # Probar el run síncrono normal
                 return True # Asumir éxito si run() no lanza excepción
             except Exception as inner_e:
                 console.print(f"[bold red]Error (intento síncrono):[/bold red] {inner_e}")
                 return False
        else:
            console.print(f"[bold red]Error al iniciar el editor de .env:[/bold red] {e}")
            return False