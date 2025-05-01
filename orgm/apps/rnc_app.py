# -*- coding: utf-8 -*-
import questionary
import subprocess
from rich.console import Console

# Crear consola para salida con Rich
console = Console()

def buscar_empresa():
    """
    Función para buscar empresas por RNC o nombre.
    Permite filtrar por estado (activas/inactivas).
    """
    try:
        # Solicitar el nombre de la empresa
        nombre_empresa = None
        while not nombre_empresa:
            nombre_empresa = questionary.text("Nombre o RNC de la empresa a buscar:").ask()
            if nombre_empresa is None:  # Usuario presionó Ctrl+C
                return "exit"
                
        # Preguntar por el estado (activo/inactivo)
        estado = questionary.select(
            "¿Buscar empresas activas o inactivas?",
            choices=[
                "Activas",
                "Inactivas", 
                "Todas (sin filtro)"
            ]
        ).ask()
        
        if estado is None:  # Usuario presionó Ctrl+C
            return "exit"

        # Construir el comando de búsqueda
        comando_busqueda = "find-company " + nombre_empresa
        if estado == "Activas":
            comando_busqueda += " --activo"
        elif estado == "Inactivas":
            comando_busqueda += " --inactivo"
            
        try:
            # Ejecutar la búsqueda
            subprocess.run(f"orgm {comando_busqueda}", shell=True, check=True)
            
            # Preguntar si desea buscar nuevamente
            seleccion = questionary.select(
                "¿Buscar nuevamente?",
                choices=["Si", "No"],
                use_indicator=True,
                use_shortcuts=True,
                default="Si"
            ).ask()
            
            if seleccion is None or seleccion == "No":
                return "exit"
            else:
                # Volver a ejecutar la función para una nueva búsqueda
                return buscar_empresa()
                
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Error al ejecutar la búsqueda: Código {e.returncode}[/bold red]")
            return "error"
        except Exception as e:
            console.print(f"[bold red]Error al ejecutar la búsqueda: {e}[/bold red]")
            return "error"
            
    except Exception as e:
        console.print(f"[bold red]Error en el módulo de búsqueda: {e}[/bold red]")
        return "error"

def rnc_app():
    """
    Función principal para la aplicación de búsqueda de RNC.
    Se integra con el menú principal.
    """
    result = buscar_empresa()
    return result

if __name__ == "__main__":
    # Para pruebas
    resultado = rnc_app()
    console.print(f"Resultado: {resultado}")
                    
