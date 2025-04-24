import questionary
from rich.console import Console
from rich.table import Table
from typing import Dict, Optional
from orgm.adm.clientes import (
    obtener_clientes, 
    obtener_cliente, 
    crear_cliente, 
    actualizar_cliente, 
    eliminar_cliente, 
    buscar_clientes
)
from orgm.adm.db import Cliente

console = Console()

def mostrar_cliente(cliente: Cliente):
    """Muestra los detalles de un cliente en formato de tabla"""
    table = Table(title=f"Cliente: {cliente.nombre} (ID: {cliente.id})")
    
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="green")
    
    table.add_row("Nombre", cliente.nombre)
    table.add_row("Nombre Comercial", cliente.nombre_comercial)
    table.add_row("Número", cliente.numero)
    table.add_row("Correo", cliente.correo)
    table.add_row("Dirección", cliente.direccion)
    table.add_row("Ciudad", cliente.ciudad)
    table.add_row("Provincia", cliente.provincia)
    table.add_row("Teléfono", cliente.telefono)
    table.add_row("Representante", cliente.representante)
    table.add_row("Teléfono Representante", cliente.telefono_representante)
    table.add_row("Extensión Representante", cliente.extension_representante)
    table.add_row("Celular Representante", cliente.celular_representante)
    table.add_row("Correo Representante", cliente.correo_representante)
    table.add_row("Tipo Factura", cliente.tipo_factura)
    
    console.print(table)

def listar_clientes(clientes):
    """Muestra una lista de clientes en formato de tabla"""
    if not clientes:
        console.print("[yellow]No se encontraron clientes[/yellow]")
        return
    
    table = Table(title=f"Lista de Clientes ({len(clientes)} encontrados)")
    
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="green")
    table.add_column("Nombre Comercial", style="green")
    table.add_column("Teléfono", style="green")
    table.add_column("Ciudad", style="green")
    
    for cliente in clientes:
        table.add_row(
            str(cliente.id),
            cliente.nombre,
            cliente.nombre_comercial,
            cliente.telefono,
            cliente.ciudad
        )
    
    console.print(table)

def solicitar_datos_cliente(cliente: Optional[Cliente] = None) -> Dict:
    """Solicita los datos del cliente al usuario utilizando questionary"""
    cliente_data = {}
    
    # Valores predeterminados para edición
    defaults = {
        "nombre": "",
        "nombre_comercial": "",
        "numero": "",
        "correo": "",
        "direccion": "",
        "ciudad": "",
        "provincia": "",
        "telefono": "",
        "representante": "",
        "telefono_representante": "",
        "extension_representante": "",
        "celular_representante": "",
        "correo_representante": "",
        "tipo_factura": "NCFC"
    }
    
    # Si tenemos un cliente, usar sus valores como predeterminados
    if cliente:
        defaults = {
            "nombre": cliente.nombre,
            "nombre_comercial": cliente.nombre_comercial,
            "numero": cliente.numero,
            "correo": cliente.correo,
            "direccion": cliente.direccion,
            "ciudad": cliente.ciudad,
            "provincia": cliente.provincia,
            "telefono": cliente.telefono,
            "representante": cliente.representante,
            "telefono_representante": cliente.telefono_representante,
            "extension_representante": cliente.extension_representante,
            "celular_representante": cliente.celular_representante,
            "correo_representante": cliente.correo_representante,
            "tipo_factura": cliente.tipo_factura
        }
    
    # Solicitar datos con questionary
    cliente_data["nombre"] = questionary.text(
        "Nombre del cliente:", 
        default=defaults["nombre"]
    ).ask()
    
    cliente_data["nombre_comercial"] = questionary.text(
        "Nombre comercial:",
        default=defaults["nombre_comercial"]
    ).ask()
    
    cliente_data["numero"] = questionary.text(
        "Número:",
        default=defaults["numero"]
    ).ask()
    
    cliente_data["correo"] = questionary.text(
        "Correo electrónico:",
        default=defaults["correo"]
    ).ask()
    
    cliente_data["direccion"] = questionary.text(
        "Dirección:",
        default=defaults["direccion"]
    ).ask()
    
    cliente_data["ciudad"] = questionary.text(
        "Ciudad:",
        default=defaults["ciudad"]
    ).ask()
    
    cliente_data["provincia"] = questionary.text(
        "Provincia:",
        default=defaults["provincia"]
    ).ask()
    
    cliente_data["telefono"] = questionary.text(
        "Teléfono:",
        default=defaults["telefono"]
    ).ask()
    
    cliente_data["representante"] = questionary.text(
        "Representante:",
        default=defaults["representante"]
    ).ask()
    
    cliente_data["telefono_representante"] = questionary.text(
        "Teléfono del representante:",
        default=defaults["telefono_representante"]
    ).ask()
    
    cliente_data["extension_representante"] = questionary.text(
        "Extensión del representante:",
        default=defaults["extension_representante"]
    ).ask()
    
    cliente_data["celular_representante"] = questionary.text(
        "Celular del representante:",
        default=defaults["celular_representante"]
    ).ask()
    
    cliente_data["correo_representante"] = questionary.text(
        "Correo del representante:",
        default=defaults["correo_representante"]
    ).ask()
    
    tipo_factura_opciones = ["NCFC", "NCF", "NCG", "NCRE"]
    cliente_data["tipo_factura"] = questionary.select(
        "Tipo de factura:",
        choices=tipo_factura_opciones,
        default=defaults["tipo_factura"]
    ).ask()
    
    return cliente_data

def nuevo_cliente():
    """Función para crear un nuevo cliente"""
    console.print("[bold green]Creación de nuevo cliente[/bold green]")
    
    # Solicitar datos del cliente
    cliente_data = solicitar_datos_cliente()
    
    # Confirmar la creación
    if questionary.confirm("¿Desea crear este cliente?").ask():
        # Crear el cliente
        resultado = crear_cliente(cliente_data)
        if resultado:
            console.print(f"[bold green]Cliente creado con ID: {resultado.id}[/bold green]")
            mostrar_cliente(resultado)
    else:
        console.print("[yellow]Operación cancelada por el usuario[/yellow]")

def editar_cliente(id_cliente: int):
    """Función para editar un cliente existente"""
    # Obtener el cliente
    cliente = obtener_cliente(id_cliente)
    if not cliente:
        console.print(f"[bold red]No se encontró un cliente con ID {id_cliente}[/bold red]")
        return
    
    console.print(f"[bold green]Editando cliente: {cliente.nombre} (ID: {cliente.id})[/bold green]")
    
    # Mostrar cliente actual
    mostrar_cliente(cliente)
    
    # Solicitar datos actualizados
    cliente_data = solicitar_datos_cliente(cliente)
    
    # Confirmar la actualización
    if questionary.confirm("¿Desea guardar los cambios?").ask():
        # Actualizar el cliente
        resultado = actualizar_cliente(id_cliente, cliente_data)
        if resultado:
            console.print(f"[bold green]Cliente actualizado correctamente[/bold green]")
            mostrar_cliente(resultado)
    else:
        console.print("[yellow]Operación cancelada por el usuario[/yellow]")

def buscar_y_mostrar_clientes():
    """Función para buscar y mostrar clientes"""
    termino = questionary.text("Ingrese término de búsqueda (nombre, nombre comercial o número):").ask()
    
    if not termino:
        console.print("[yellow]Búsqueda cancelada[/yellow]")
        return
    
    console.print(f"[bold green]Buscando clientes con término: '{termino}'[/bold green]")
    
    # Buscar clientes
    clientes = buscar_clientes(termino)
    
    # Mostrar resultados
    listar_clientes(clientes)
    
    # Si hay resultados, permitir seleccionar uno para ver detalles
    if clientes:
        opciones = [f"{c.id} - {c.nombre}" for c in clientes]
        opciones.append("Cancelar")
        
        seleccion = questionary.select(
            "Seleccione un cliente para ver detalles:",
            choices=opciones
        ).ask()
        
        if seleccion != "Cancelar":
            id_cliente = int(seleccion.split(" - ")[0])
            cliente = next((c for c in clientes if c.id == id_cliente), None)
            if cliente:
                mostrar_cliente(cliente)
                
                # Ofrecer editar el cliente
                if questionary.confirm("¿Desea editar este cliente?").ask():
                    editar_cliente(id_cliente) 