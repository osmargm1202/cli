import questionary
import os

from orgm.qstyle import custom_style_fancy

from rich.console import Console

from orgm.apps.utils.carpetas.esquemas import crear_carpeta_proyecto
from orgm.apps.utils.carpetas.api import buscar_clientes, buscar_cotizaciones

console = Console()


def menu():

    console.print("Bienvenido al menú de Carpetas", style="bold blue italic")

    
    opciones = [
        "Crear carpeta",
        "Buscar cotizaciones por cliente",
        "Salir"
    ]
    
    respuesta = questionary.select(
        "¿Qué desea hacer?",
        choices=opciones,
        style=custom_style_fancy
    ).ask()

    if respuesta == "Crear carpeta":
        cotizacion = questionary.text("Ingrese la cotización", style=custom_style_fancy).ask()
        crear_carpeta_proyecto(cotizacion)
        return menu()
    elif respuesta == "Buscar cotizaciones por cliente":
        # Solicitar nombre del cliente para búsqueda
        nombre_cliente = questionary.text(
            "Ingrese el nombre del cliente a buscar", 
            style=custom_style_fancy
        ).ask()
        
        # Buscar clientes que coincidan con el nombre
        clientes = buscar_clientes(nombre_cliente)
        
        if not clientes or len(clientes) == 0:
            console.print("No se encontraron clientes con ese nombre", style="bold red")
            return menu()
        
        # Crear lista de opciones para selección de cliente
        opciones_clientes = [
            f"{cliente['id']} - {cliente['nombre']} ({cliente['nombre_comercial'] or 'Sin nombre comercial'})" 
            for cliente in clientes
        ]
        
        # Agregar opción para volver al menú
        opciones_clientes.append("Volver al menú")
        
        # Preguntar cuál cliente desea seleccionar
        cliente_seleccionado = questionary.select(
            "Seleccione un cliente",
            choices=opciones_clientes,
            style=custom_style_fancy
        ).ask()
        
        if cliente_seleccionado == "Volver al menú":
            return menu()
        
        # Extraer el ID del cliente
        id_cliente = int(cliente_seleccionado.split(" - ")[0])
        
        # Buscar cotizaciones de ese cliente
        cotizaciones = buscar_cotizaciones(id_cliente)
        
        if not cotizaciones or len(cotizaciones) == 0:
            console.print("No se encontraron cotizaciones para este cliente", style="bold red")
            return menu()
        
        # Crear lista de opciones para selección de cotización
        opciones_cotizaciones = [
            f"{cot['id']} - {cot['servicio']['nombre']} - {cot['proyecto']['nombre_proyecto']}" 
            for cot in cotizaciones
        ]
        
        # Agregar opción para volver al menú
        opciones_cotizaciones.append("Volver al menú")
        
        # Preguntar cuál cotización desea seleccionar
        cotizacion_seleccionada = questionary.select(
            "Seleccione una cotización",
            choices=opciones_cotizaciones,
            style=custom_style_fancy
        ).ask()
        
        if cotizacion_seleccionada == "Volver al menú":
            return menu()
        
        # Extraer el ID de la cotización
        id_cotizacion = int(cotizacion_seleccionada.split(" - ")[0])
        
        # Crear carpeta con la cotización seleccionada
        crear_carpeta_proyecto(id_cotizacion)
        console.print(f"Carpeta creada exitosamente para la cotización {id_cotizacion}", style="bold green")
        
        return menu()
    else:
        return 'exit'
        
    return True

if __name__ == "__main__":
    menu()