import os
import questionary
from orgm.qstyle import custom_style_fancy
def seleccionar_carpeta():
    """
    Solicita al usuario seleccionar una carpeta mediante questionary
    
    Returns:
        str: Ruta de la carpeta seleccionada
    """
    ruta = questionary.path(
        "Por favor seleccione la carpeta:",
        only_directories=True,
        default=os.getcwd(),
        style=custom_style_fancy,
    ).ask()

    return ruta.strip().strip('"').strip("'")


if __name__ == "__main__":
    print(seleccionar_carpeta())
