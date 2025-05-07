from rich.console import Console
import questionary
from orgm.apps.utils.rnc.find import mostrar_busqueda
from orgm.qstyle import custom_style_fancy

console = Console()


def menu():
    """
    Función para buscar empresas por RNC o nombre interactivamente.
    Permite filtrar por estado (activas/inactivas).
    """
    try:
        # Solicitar el nombre de la empresa
        nombre_empresa = None
        while not nombre_empresa:
            nombre_empresa = questionary.text(
                "Nombre o RNC de la empresa a buscar:"
            ).ask()
            if nombre_empresa is None:  # Usuario presionó Ctrl+C
                return "exit"

        # Preguntar por el estado (activo/inactivo)
        estado = questionary.select(
            "¿Buscar empresas activas o inactivas?",
            choices=["Activas", "Inactivas", "Todas (sin filtro)"],
            style=custom_style_fancy,
        ).ask()

        if estado is None:  # Usuario presionó Ctrl+C
            return "exit"

        try:
            # Determinar el estado para la búsqueda
            activo = True  # Por defecto, buscar activas
            if estado == "Inactivas":
                activo = False
            elif estado == "Todas (sin filtro)":
                activo = None  # Indicar que no hay filtro de estado

            # Realizar la búsqueda usando la función existente
            mostrar_busqueda(nombre_empresa, activo)

            # Preguntar si desea buscar nuevamente
            seleccion = questionary.select(
                "¿Buscar nuevamente?",
                choices=["Si", "No"],
                use_indicator=True,
                use_shortcuts=True,
                default="Si",
            ).ask()

            if seleccion is None or seleccion == "No":
                return "exit"
            else:
                # Volver a ejecutar la función para una nueva búsqueda
                return menu()

        except Exception as e:
            console.print(f"[bold red]Error al ejecutar la búsqueda: {e}[/bold red]")
            return "error"

    except Exception as e:
        console.print(f"[bold red]Error en el módulo de búsqueda: {e}[/bold red]")
        return "error"
