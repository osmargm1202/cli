# -*- coding: utf-8 -*-
import questionary
import subprocess
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

# Importar la funcionalidad existente
from orgm.apis.rnc import buscar_rnc_cliente

# Crear consola para salida con Rich
console = Console()

# Crear la aplicación Typer
rnc_app = typer.Typer(help="Buscar empresas por RNC o nombre")

@rnc_app.callback(invoke_without_command=True)
def find_company(
    ctx: typer.Context,
    consulta: Optional[str] = typer.Argument(None, help="RNC o nombre de la empresa a buscar"),
    activo: bool = typer.Option(True, "--activo/--inactivo", help="Buscar solo empresas activas o suspendidas")
):
    """
    Busca empresas por RNC o nombre.
    Si se ejecuta sin argumentos, muestra un menú interactivo.
    """
    # Si no se proporciona consulta, mostrar menú interactivo
    if consulta is None and ctx.invoked_subcommand is None:
        rnc_menu()
        return
    
    # Si hay una consulta, realizar la búsqueda
    if consulta:
        realizar_busqueda(consulta, activo)

def realizar_busqueda(busqueda: str, activo: bool = True):
    """
    Realiza la búsqueda de una empresa utilizando la API existente
    y muestra los resultados en una tabla.
    """
    console.print(f"Buscando '{busqueda}' (Activo: {activo})...")
    resultado = buscar_rnc_cliente(busqueda, activo)

    if resultado is None:
        console.print("[bold red]Error al buscar la empresa.[/bold red]")
        return

    if not resultado:
        console.print("[yellow]No se encontraron empresas con ese criterio.[/yellow]")
        return

    # Crear tabla para mostrar resultados
    table = Table(title="Resultados de Búsqueda RNC", show_header=True, header_style="bold magenta")
    table.add_column("RNC/Cédula", style="dim", width=15)
    table.add_column("Nombre Comercial")
    table.add_column("Razón Social")
    table.add_column("Actividad")
    table.add_column("Estado", justify="right")

    for empresa in resultado:
        table.add_row(
            str(empresa.get("rnc", "N/A")),
            empresa.get("nombre", "N/A"),
            empresa.get("razon", "N/A"),
            empresa.get("descripcion", "N/A"),
            empresa.get("estado", "N/A")
        )

    console.print(table)

def buscar_empresa():
    """
    Función para buscar empresas por RNC o nombre interactivamente.
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

        try:
            # Determinar el estado para la búsqueda
            activo = True  # Por defecto, buscar activas
            if estado == "Inactivas":
                activo = False
            elif estado == "Todas (sin filtro)":
                activo = None  # Indicar que no hay filtro de estado
            
            # Realizar la búsqueda usando la función existente
            realizar_busqueda(nombre_empresa, activo)
            
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
                
        except Exception as e:
            console.print(f"[bold red]Error al ejecutar la búsqueda: {e}[/bold red]")
            return "error"
            
    except Exception as e:
        console.print(f"[bold red]Error en el módulo de búsqueda: {e}[/bold red]")
        return "error"

def rnc_menu():
    """
    Menú interactivo para el módulo de RNC.
    Permite realizar búsquedas de empresas.
    """
    opciones = [
        "Buscar empresas por RNC o nombre",
        "Volver al menú principal"
    ]
    
    seleccion = questionary.select(
        "Seleccione una opción:",
        choices=opciones,
        use_indicator=True,
        use_shortcuts=True
    ).ask()
    
    if seleccion is None or seleccion == "Volver al menú principal":
        return "exit"
    
    if "Buscar" in seleccion:
        return buscar_empresa()
    
    return "exit"

if __name__ == "__main__":
    # Para pruebas
    resultado = rnc_menu()
    console.print(f"Resultado: {resultado}")
                    
