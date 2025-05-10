# -*- coding: utf-8 -*-
# Main ORGM CLI application
import sys
import typer
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
import os
import questionary
from pyfiglet import Figlet  # Importar Figlet
from click_repl import register_repl
from click_repl import repl as start_repl
from orgm.apps.conf.app import app as conf_app
from orgm.apps.ai.app import app as ai_app
from orgm.apps.dev.app import app as dev_app
from orgm.apps.docker.app import app as docker_app
from orgm.apps.utils.rnc.app import app as rnc_app
from orgm.apps.adm.cliente.app import app as cliente_app
from orgm.apps.adm.proyecto.app import app as proyecto_app
from orgm.apps.adm.cotizacion.app import app as cotizacion_app
from orgm.menu import menu_principal
from orgm.apps.utils.docs.app import app as docs_app
from orgm.apps.utils.carpetas.app import app as carpeta_app

console = Console()


# Clase principal que maneja la aplicación CLI
class OrgmCLI:
    def __init__(self):
        # Crear la aplicación Typer
        self.app = typer.Typer(
            context_settings={"help_option_names": ["-h", "--help"]},
            no_args_is_help=False,  # Evita la ayuda predeterminada de Typer sin argumentos
            add_completion=True,  # Opcional: deshabilitar la autocompletación si no se usa
        )
        # Añadir todos los módulos usando add_typer

        self.app.add_typer(conf_app, name="conf")
        self.app.add_typer(ai_app, name="ai")
        self.app.add_typer(dev_app, name="dev")
        self.app.add_typer(docker_app, name="docker")
        self.app.add_typer(rnc_app, name="rnc")
        self.app.add_typer(cliente_app, name="cliente")
        self.app.add_typer(proyecto_app, name="proyecto")
        self.app.add_typer(cotizacion_app, name="cotizacion")
        self.app.add_typer(docs_app, name="documento")
        self.app.add_typer(carpeta_app, name="carpeta")
        # --- Comando de menú ---
        @self.app.command(name="menu", help="Muestra el menú interactivo principal.")
        def menu_command(ctx_menu: typer.Context): # ctx_menu es el contexto de este comando 'menu'
            """Muestra el menú interactivo y ejecuta la selección."""
            comando_seleccionado = menu_principal()

            if comando_seleccionado == "exit":
                console.print("[bold yellow]Saliendo...[/bold yellow]")
                sys.exit(0) # Termina la aplicación
            elif comando_seleccionado: # Es una cadena de comando válida
                args_originales = sys.argv.copy()
                try:
                    # sys.argv[0] es el nombre del script/programa.
                    # El comando y sus argumentos vienen después.
                    sys.argv = [sys.argv[0]] + comando_seleccionado.split()
                    
                    # Re-invocar la aplicación principal para procesar el nuevo comando.
                    # Esto asegura que Typer/Click maneje el comando como si
                    # hubiera sido ingresado directamente en la línea de comandos o REPL.
                    self.app()
                    
                    # Importante: Si self.app() procesa un comando que no sale
                    # (por ej. 'client list'), la ejecución volverá aquí.
                    # Si 'orgm menu' fue el comando original, queremos que el programa
                    # termine después de que el comando del menú se haya ejecutado.
                    # Sin embargo, la llamada cli.app() en main() ya maneja la finalización.
                    # Si 'menu' se llamó desde el REPL, queremos que vuelva al REPL.
                    # No llamar a sys.exit() aquí permite ese comportamiento dual.
                    # El flujo normal hará que el programa termine si 'orgm menu' fue el comando inicial,
                    # o volverá al REPL si 'menu' fue invocado desde el REPL.

                except SystemExit:
                    # Si el comando invocado (e.g., 'exit' de otro subcomando o el propio 'exit')
                    # llama a sys.exit(), lo propagamos para permitir que la app termine.
                    raise
                except Exception as e:
                    console.print(f"[bold red]Error al ejecutar '{comando_seleccionado}' desde el menú: {e}[/bold red]")
                    # Después de un error, restauramos argv y dejamos que el flujo continúe.
                    # Si estamos en el REPL, volverá al prompt. Si fue 'orgm menu', terminará.
                finally:
                    sys.argv = args_originales # Es crucial restaurar sys.argv
            # Si comando_seleccionado es None (no debería ocurrir con el menu.py actual),
            # simplemente no se hace nada, y el comando 'menu' termina.

        # --- Comandos explícitos para salir del REPL ---
        @self.app.command(name="exit", help="Salir del shell REPL.")
        def exit_command():
            """Comando para salir del REPL."""
            console.print("[bold yellow]Saliendo...[/bold yellow]")
            sys.exit(0)

        # @self.app.command(name="quit", help="Salir del shell REPL.")
        # def quit_command():
        #     """Comando alternativo para salir del REPL."""
        #     exit_command() # Reutiliza la lógica de exit
        # # ----------------------------------------------

        # Registrar el REPL
        register_repl(self.app)

        self.configurar_callback()
        self.cargar_variables_entorno()

    def configurar_callback(self) -> None:
        """Configura el callback principal para iniciar el REPL si no hay subcomando."""

        @self.app.callback(invoke_without_command=True)
        def main_callback(ctx: typer.Context):
            """
            Si no se invoca ningún subcomando, inicia el shell REPL interactivo.
            """
            if ctx.invoked_subcommand is None:
                # Iniciar el REPL directamente
                try:
                    # Mostrar mensaje de inicio
                    console.print(
                        "[bold blue]¡Bienvenido al shell interactivo de ORGM![/bold blue]"
                    )
                    console.print(
                        "[dim]Use 'exit' o Ctrl+D para salir. 'conf help' para ver comandos disponibles.[/dim]"
                    )

                    # Configurar el prompt personalizado y llamar al REPL
                    start_repl(
                        ctx,
                        prompt_kwargs={
                            "message": "orgm> ",
                            "enable_history_search": True,
                            # "mouse_support": True,
                            # "enable_open_in_editor": True,
                        },
                    )

                    # Cuando el REPL termina (por 'exit' o EOF), salimos
                    console.print(
                        "[bold blue]Saliendo de la Terminal ORGM...[/bold blue]"
                    )
                    sys.exit(0)
                except (EOFError, KeyboardInterrupt):
                    # Manejar salida por Ctrl+C si ocurre antes de que el REPL lo capture
                    console.print("\n[bold yellow]Saliendo del REPL...[/bold yellow]")
                    sys.exit(0)
                except Exception as e:
                    console.print(
                        f"[bold red]Error durante la sesión REPL: {e}[/bold red]"
                    )
                    sys.exit(1)
            # Si se invoca un subcomando (ej: orgm conf env-edit),
            # Typer/Click lo manejará automáticamente después de que esta función retorne.
            # No es necesario hacer nada más aquí para ese caso.

    def cargar_variables_entorno(self) -> None:
        """Cargar variables de entorno desde un archivo .env"""
        # Find .env file relative to the main script or project root
        # This assumes orgm.py is in the 'orgm' directory
        project_root = Path(__file__).parent.parent
        # Definir la ruta del archivo .env según el sistema operativo

        orgm_env = os.path.join(os.path.expanduser("~"), ".orgm", ".env")
        dotenv_path = project_root / ".env" / orgm_env
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=True)
        else:
            # Try loading from current working directory as fallback
            load_dotenv(override=True)
            if not Path(".env").exists():
                # No .env found, run env edit command
                console.print(
                    "[yellow]No se encontró archivo .env. Ejecutando 'orgm conf env-edit' o en su defecto 'orgm env-file [DIRECTORIO]'...[/yellow]"
                )
                args_originales = sys.argv.copy()
                try:
                    argumentos = questionary.text(
                        "Ingrese el comando para ejecutar: ", default="conf env-edit"
                    ).ask()
                    if argumentos == "":
                        argumentos = "conf help"
                    sys.argv = [sys.argv[0]] + argumentos.split()
                    self.app()
                except Exception as e:
                    console.print(
                        f"[bold red]Error al ejecutar comando {argumentos}: {e}[/bold red]"
                    )
                sys.argv = args_originales


# Inicializar y ejecutar la CLI
def main():
    # --- Mostrar título con pyfiglet ---
    f = Figlet(
        font="ghost"
    )  # Puedes probar otras fuentes como 'standard', 'big', 'digital'
    ascii_art = f.renderText("ORGM")
    console.print(f"[bold blue]{ascii_art}[/bold blue]", justify="center")
    console.print()  # Añadir una línea en blanco después del título
    # ---------------------------------

    # Crear instancia de la CLI
    cli = OrgmCLI()
    # Ejecutar la aplicación Typer y manejar interrupciones de usuario
    try:
        # La llamada a cli.app() ahora:
        # 1. Si hay argumentos (ej. orgm conf), ejecuta el comando.
        # 2. Si NO hay argumentos, main_callback es llamado, detecta
        #    invoked_subcommand is None, y llama a start_repl(ctx).
        cli.app()
    except (KeyboardInterrupt, EOFError):
        # Esta excepción podría ser capturada por el REPL o aquí si ocurre fuera.
        # El manejo dentro del REPL es más específico.
        # Mantenemos esto como un respaldo general si algo sale mal antes de entrar al REPL.
        console.print("[bold yellow]Saliendo...[/bold yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
