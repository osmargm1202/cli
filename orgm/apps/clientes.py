import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import questionary
import requests
import click
from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.table import Table
from orgm.adm.clientes import (
    obtener_clientes,
    obtener_cliente,
    crear_cliente,
    actualizar_cliente,
    buscar_clientes,
)

console = Console()

# Cargar variables de entorno
load_dotenv(override=True)

# URL de PostgREST
POSTGREST_URL = os.getenv("POSTGREST_URL")

# Credenciales de Cloudflare Access
CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

if not POSTGREST_URL:
    console.print(
        "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno.[/bold red]"
    )
    sys.exit(1)

# Configurar cabeceras para la API de PostgREST
headers = {"Content-Type": "application/json", "Accept": "application/json"}

# Añadir cabeceras de Cloudflare Access si están disponibles
if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
    headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
    headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET
else:
    console.print(
        "[bold yellow]Advertencia: CF_ACCESS_CLIENT_ID o CF_ACCESS_CLIENT_SECRET no están definidas.[/bold yellow]"
    )
    console.print(
        "[bold yellow]Las consultas a PostgREST no incluirán autenticación de Cloudflare Access.[/bold yellow]"
    )


def mostrar_tabla_clientes(clientes: List) -> None:
    """
    Muestra una tabla con los clientes.

    Args:
        clientes (List): Lista de objetos Cliente para mostrar.
    """
    if not clientes:
        console.print("[bold yellow]No se encontraron clientes.[/bold yellow]")
        return

    # Crear tabla
    tabla = Table(
        title="[bold blue]Lista de Clientes[/bold blue]",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold cyan",
    )

    # Añadir columnas - Usar los nombres de campo del modelo Cliente
    tabla.add_column("ID", justify="right", style="dim")
    tabla.add_column("Nombre", style="green")
    tabla.add_column("Número/NIF", style="blue") # Asumiendo que 'numero' es NIF/CIF
    tabla.add_column("Email", style="yellow") # Asumiendo que es 'correo'
    tabla.add_column("Teléfono", style="magenta")
    tabla.add_column("Última Actualización", style="cyan") # Cambiado de Fecha Alta

    # Añadir filas
    for cliente in clientes:
        # Formatear fecha
        fecha_actualizacion = getattr(cliente, "fecha_actualizacion", None)
        fecha_formateada = ""
        if fecha_actualizacion:
            try:
                # Pydantic puede devolver datetime o str, manejar ambos
                if isinstance(fecha_actualizacion, str):
                     fecha_obj = datetime.fromisoformat(fecha_actualizacion.replace("Z", "+00:00"))
                elif isinstance(fecha_actualizacion, datetime):
                     fecha_obj = fecha_actualizacion
                else:
                     fecha_obj = None
                
                if fecha_obj:
                     fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
            except (ValueError, TypeError):
                fecha_formateada = str(fecha_actualizacion) # Mostrar como string si falla el formato
        
        tabla.add_row(
            str(getattr(cliente, "id", "")),
            getattr(cliente, "nombre", ""),
            getattr(cliente, "numero", ""), # Usar 'numero' para NIF/CIF
            getattr(cliente, "correo", ""), # Usar 'correo' para Email
            getattr(cliente, "telefono", ""),
            fecha_formateada, # Usar fecha formateada
        )

    # Mostrar tabla
    console.print(tabla)

def mostrar_detalle_cliente(cliente) -> None:
    """
    Muestra los detalles completos de un cliente.

    Args:
        cliente: Objeto Cliente con los datos.
    """
    if not cliente:
        console.print("[bold yellow]No se encontró el cliente.[/bold yellow]")
        return

    # Crear tabla de detalles
    tabla = Table(
        title=f"[bold blue]Detalles del Cliente: {getattr(cliente, 'nombre', '')}[/bold blue]", # Usar getattr
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold cyan",
    )

    # Configurar columnas
    tabla.add_column("Campo", style="green")
    tabla.add_column("Valor", style="yellow")

    # Mapeo de campos y sus nombres para mostrar
    campos = [
        ("ID", "id"),
        ("Nombre", "nombre"),
        ("Nombre Comercial", "nombre_comercial"),
        ("Número/NIF", "numero"),
        ("Correo", "correo"),
        ("Dirección", "direccion"),
        ("Ciudad", "ciudad"),
        ("Provincia", "provincia"),
        ("Teléfono", "telefono"),
        ("Representante", "representante"),
        ("Teléfono Representante", "telefono_representante"),
        ("Extensión Representante", "extension_representante"),
        ("Celular Representante", "celular_representante"),
        ("Correo Representante", "correo_representante"),
        ("Tipo de Factura", "tipo_factura"),
        ("Última Actualización", "fecha_actualizacion")
    ]

    # Añadir filas con los datos
    for etiqueta, campo in campos:
        valor = getattr(cliente, campo, "") # Usar getattr
        if campo == "fecha_actualizacion" and valor:
            try:
                 # Pydantic puede devolver datetime o str, manejar ambos
                if isinstance(valor, str):
                     fecha_obj = datetime.fromisoformat(valor.replace("Z", "+00:00"))
                elif isinstance(valor, datetime):
                     fecha_obj = valor
                else:
                     fecha_obj = None
                
                if fecha_obj:
                     valor = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
            except (ValueError, TypeError):
                valor = str(valor) # Mostrar como string si falla el formato
        tabla.add_row(etiqueta, str(valor))

    # Mostrar tabla
    console.print(tabla)

def formulario_cliente(cliente=None) -> Optional[Dict]:
    """
    Muestra un formulario interactivo para crear o modificar un cliente.

    Args:
        cliente: Datos del cliente existente para modificar (puede ser un objeto Cliente). None si es nuevo.

    Returns:
        Optional[Dict]: Diccionario con los datos del cliente o None si se cancela.
    """
    # Valores por defecto
    if cliente:
        # Asumimos que cliente es un objeto Pydantic y usamos model_dump()
        # Si es un dict, esto fallará, pero el traceback indica que es un objeto
        try:
            defaults = cliente.model_dump()
        except AttributeError:
             # Fallback si no tiene model_dump (quizás es un dict ya?)
             # O manejar el error de forma más específica
             console.print("[bold red]Error: El objeto cliente no tiene el método model_dump().[/bold red]")
             # Si cliente ya *es* un dict, esta línea funcionaría, pero el error dice que no es subscriptable.
             # Si es otro tipo de objeto, necesitaríamos saber cómo convertirlo a dict.
             # Por ahora, asumimos que es Pydantic o similar con model_dump().
             defaults = {} # O devolver None, o lanzar excepción
    else:
        defaults = {
            "nombre": "",
            "numero": "",
            "nombre_comercial": "",
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
            "tipo_factura": "NCFC",
        }
    
    # Usamos .get() en el diccionario defaults para manejar claves faltantes si model_dump no las incluyó
    nombre = questionary.text(
        "Nombre del cliente:", default=defaults.get("nombre", "")
    ).ask()
    if not nombre:
        return None

    numero = questionary.text(
        "Número/NIF del cliente:", default=defaults.get("numero", "")
    ).ask()
    if not numero:
        return None

    nombre_comercial = questionary.text(
        "Nombre comercial:", default=defaults.get("nombre_comercial", "")
    ).ask()
    # Permitir nombre comercial vacío si el usuario lo desea
    # if not nombre_comercial:
    #     return None

    # Campos opcionales
    correo = questionary.text(
        "Correo electrónico:", default=defaults.get("correo", "")
    ).ask()

    direccion = questionary.text(
        "Dirección:", default=defaults.get("direccion", "")
    ).ask()

    ciudad = questionary.text("Ciudad:", default=defaults.get("ciudad", "")).ask()

    provincia = questionary.text(
        "Provincia:", default=defaults.get("provincia", "")
    ).ask()

    telefono = questionary.text("Teléfono:", default=defaults.get("telefono", "")).ask()

    representante = questionary.text(
        "Nombre del representante:", default=defaults.get("representante", "")
    ).ask()

    telefono_representante = questionary.text(
        "Teléfono del representante:",
        default=defaults.get("telefono_representante", ""),
    ).ask()

    extension_representante = questionary.text(
        "Extensión del representante:",
        default=defaults.get("extension_representante", ""),
    ).ask()

    celular_representante = questionary.text(
        "Celular del representante:",
        default=defaults.get("celular_representante", ""),
    ).ask()

    correo_representante = questionary.text(
        "Correo del representante:",
        default=defaults.get("correo_representante", ""),
    ).ask()

    tipo_factura = questionary.select(
        "Tipo de factura:",
        choices=["NCFC", "NCF"],
        default=defaults.get("tipo_factura", "NCFC"),
    ).ask()

    # Devolver un diccionario limpio con los datos ingresados
    return {
        "nombre": nombre,
        "numero": numero,
        "nombre_comercial": nombre_comercial if nombre_comercial is not None else "", # Asegurar string
        "correo": correo if correo is not None else "",
        "direccion": direccion if direccion is not None else "",
        "ciudad": ciudad if ciudad is not None else "",
        "provincia": provincia if provincia is not None else "",
        "telefono": telefono if telefono is not None else "",
        "representante": representante if representante is not None else "",
        "telefono_representante": telefono_representante if telefono_representante is not None else "",
        "extension_representante": extension_representante if extension_representante is not None else "",
        "celular_representante": celular_representante if celular_representante is not None else "",
        "correo_representante": correo_representante if correo_representante is not None else "",
        "tipo_factura": tipo_factura if tipo_factura is not None else "NCFC" # Asegurar un valor
    }

def eliminar_cliente(id: int) -> bool:
    """
    Elimina un cliente específico mediante una solicitud DELETE a PostgREST.

    Args:
        id (int): El ID del cliente a eliminar.

    Returns:
        bool: True si la eliminación fue exitosa, False en caso contrario.
    """
    url = f"{POSTGREST_URL}/clientes?id=eq.{id}"
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        # PostgREST devuelve 204 No Content si la eliminación es exitosa
        return response.status_code == 204
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error al eliminar cliente {id}: {e}[/bold red]")
        return False

def exportar_cliente(cliente, formato: str) -> Tuple[bool, str]:
    """
    Exporta los datos de un cliente al formato especificado.

    Args:
        cliente: Objeto (preferiblemente Pydantic model) o diccionario con los datos del cliente.
        formato (str): El formato deseado (actualmente solo soporta 'json').

    Returns:
        Tuple[bool, str]: Una tupla (éxito, contenido).
                         Si éxito es True, contenido es la cadena formateada.
                         Si éxito es False, contenido es un mensaje de error.
    """
    if formato.lower() == "json":
        try:
            if hasattr(cliente, "model_dump_json"):
                # Si es un modelo Pydantic, usar su método de serialización
                # Asegurarse de que fechas y otros tipos se manejen bien
                contenido_json = cliente.model_dump_json(indent=4)
            elif isinstance(cliente, dict):
                # Si es un diccionario (como el devuelto por actualizar_cliente a veces)
                # Usar default=str para manejar tipos no serializables como datetime
                contenido_json = json.dumps(
                    cliente, indent=4, default=str, ensure_ascii=False
                )
            else:
                # Fallback genérico para otros tipos serializables
                 # Intentar convertir a dict si tiene __dict__ o similar? O simplemente usar str?
                 # Por seguridad, intentar volcar directamente puede ser mejor
                 # Añadir default=str aquí también
                 contenido_json = json.dumps(cliente, indent=4, default=str, ensure_ascii=False)

            return True, contenido_json
        except TypeError as e:
            return False, f"Error al serializar a JSON: {e}"
        except Exception as e:
            return False, f"Error inesperado durante la exportación a JSON: {e}"
    else:
        return False, f"Formato de exportación no soportado: {formato}"

def formatear_cliente_json(cliente) -> str:
    """
    Formatea los datos de un cliente como una cadena JSON.

    Args:
        cliente: Objeto (preferiblemente Pydantic model) o diccionario con los datos del cliente.

    Returns:
        str: Cadena JSON formateada o un JSON de error si falla la serialización.
    """
    exito, contenido = exportar_cliente(cliente, "json")
    if exito:
        return contenido
    else:
        # Devolver un JSON indicando el error
        return json.dumps({"error": contenido}, indent=4, ensure_ascii=False)

def menu_clientes():
    # Mostrar menú principal
    while True:
        accion = questionary.select(
            "¿Qué desea hacer?",
            choices=[
                "Listar todos los clientes",
                "Buscar clientes",
                "Crear nuevo cliente",
                "Modificar cliente",
                "Ver detalles de cliente",
                "Salir",
            ],
        ).ask()

        if accion == "Salir":
            break
        elif accion == "Listar todos los clientes":
            clientes_list = obtener_clientes()
            mostrar_tabla_clientes(clientes_list)
        elif accion == "Buscar clientes":
            termino = questionary.text("Ingrese término de búsqueda:").ask()
            if termino:
                clientes_list = buscar_clientes(termino)
                mostrar_tabla_clientes(clientes_list)
        elif accion == "Crear nuevo cliente":
            datos = formulario_cliente()
            if datos:
                # Asumiendo que crear_cliente espera un diccionario
                nuevo_cliente_obj = crear_cliente(**datos) # Desempaquetar diccionario
                if nuevo_cliente_obj:
                    # Asumir que crear_cliente devuelve un objeto Cliente o dict
                    nombre_cliente = getattr(nuevo_cliente_obj, 'nombre', nuevo_cliente_obj.get('nombre', 'N/A'))
                    console.print(f"[bold green]Cliente creado: {nombre_cliente}[/bold green]")
                    # mostrar_tabla_clientes espera una lista de objetos
                    mostrar_tabla_clientes([nuevo_cliente_obj])
                else:
                     console.print("[bold red]No se pudo crear el cliente.[/bold red]")

        elif accion == "Modificar cliente":
            id_cliente_str = questionary.text("ID del cliente a modificar:").ask()
            if id_cliente_str:
                try:
                    id_cliente = int(id_cliente_str)
                    # obtener_cliente devuelve un objeto Cliente
                    cliente_obj = obtener_cliente(id_cliente)
                    if cliente_obj:
                        # Pasar el objeto Cliente a formulario_cliente
                        datos_actualizados = formulario_cliente(cliente_obj)
                        if datos_actualizados:
                            cliente_actualizado = actualizar_cliente(id_cliente, datos_actualizados)
                            if cliente_actualizado:
                                nombre_actualizado = getattr(cliente_actualizado, "nombre", "N/A")
                                console.print(f"[bold green]Cliente actualizado: {nombre_actualizado}[/bold green]")
                                mostrar_tabla_clientes([cliente_actualizado])
                            else:
                                console.print("[bold red]No se pudo actualizar el cliente (la API no devolvió datos).[/bold red]")
                        else:
                            console.print("[yellow]Modificación cancelada.[/yellow]")
                    else:
                        console.print(f"[bold red]Cliente con ID {id_cliente} no encontrado[/bold red]")
                except ValueError:
                    console.print("[bold red]ID inválido, debe ser un número.[/bold red]")
                except Exception as e:
                     console.print(f"[bold red]Error inesperado al modificar cliente: {e}[/bold red]")
                     import traceback
                     traceback.print_exc() # Para depuración

        elif accion == "Ver detalles de cliente":
            id_cliente_str = questionary.text("ID del cliente:").ask()
            if id_cliente_str:
                try:
                    id_cliente = int(id_cliente_str)
                    cliente_obj = obtener_cliente(id_cliente)
                    if cliente_obj:
                        mostrar_detalle_cliente(cliente_obj)
                    else:
                        console.print(f"[bold red]Cliente con ID {id_cliente} no encontrado[/bold red]")
                except ValueError:
                    console.print("[bold red]ID inválido, debe ser un número.[/bold red]")


# Comando principal
@click.group(invoke_without_command=True, help="Gestión de clientes")
@click.pass_context
def clientes(ctx):
    """Gestión de clientes"""
    if ctx.invoked_subcommand is None:
        menu_clientes()


@clientes.command(help="Listar todos los clientes")
def listar():
    """Comando para listar todos los clientes."""
    # obtener_clientes devuelve una lista de objetos Cliente
    lista_clientes = obtener_clientes()
    mostrar_tabla_clientes(lista_clientes)


@clientes.command(help="Mostrar detalles de un cliente")
@click.argument("id", type=int)
@click.option("--json", "formato_json", is_flag=True, help="Mostrar en formato JSON")
def mostrar(id: int, formato_json: bool):
    """Comando para mostrar detalles de un cliente."""
    # obtener_cliente devuelve un objeto Cliente
    cliente_obj = obtener_cliente(id)

    if not cliente_obj:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    if formato_json:
        # formatear_cliente_json espera un objeto o dict
        contenido = formatear_cliente_json(cliente_obj)
        console.print(contenido)
    else:
        # mostrar_detalle_cliente espera un objeto Cliente
        mostrar_detalle_cliente(cliente_obj)


@clientes.command(help="Buscar clientes")
@click.argument("termino")
def buscar(termino: str):
    """Comando para buscar clientes."""
    # buscar_clientes devuelve una lista de objetos Cliente
    resultados = buscar_clientes(termino)
    mostrar_tabla_clientes(resultados)


@clientes.command(help="Crear un nuevo cliente")
@click.option("--nombre", required=True, help="Nombre del cliente")
# Cambiado 'nif' a 'numero' para coincidir con el formulario y modelo
@click.option("--numero", required=True, help="Número/NIF del cliente") 
@click.option("--email", help="Email del cliente") # Hacer opcional como en el formulario
@click.option("--telefono", help="Teléfono del cliente") # Hacer opcional como en el formulario
# Añadir otros campos del formulario como opciones opcionales
@click.option("--nombre-comercial", help="Nombre comercial del cliente")
@click.option("--direccion", help="Dirección del cliente")
@click.option("--ciudad", help="Ciudad del cliente")
@click.option("--provincia", help="Provincia del cliente")
@click.option("--representante", help="Nombre del representante")
@click.option("--telefono-representante", help="Teléfono del representante")
@click.option("--extension-representante", help="Extensión del representante")
@click.option("--celular-representante", help="Celular del representante")
@click.option("--correo-representante", help="Correo del representante")
@click.option("--tipo-factura", type=click.Choice(['NCFC', 'NCF']), default='NCFC', help="Tipo de factura")
def crear(nombre: str, numero: str, **kwargs): # Usar kwargs para los opcionales
    """Comando para crear un nuevo cliente."""
    # Crear diccionario de datos del cliente
    datos_cliente = {
        "nombre": nombre,
        "numero": numero,
        "correo": kwargs.get("email"),
        "telefono": kwargs.get("telefono"),
        "nombre_comercial": kwargs.get("nombre_comercial"),
        "direccion": kwargs.get("direccion"),
        "ciudad": kwargs.get("ciudad"),
        "provincia": kwargs.get("provincia"),
        "representante": kwargs.get("representante"),
        "telefono_representante": kwargs.get("telefono_representante"),
        "extension_representante": kwargs.get("extension_representante"),
        "celular_representante": kwargs.get("celular_representante"),
        "correo_representante": kwargs.get("correo_representante"),
        "tipo_factura": kwargs.get("tipo_factura", "NCFC"),
    }
    # Filtrar valores None para no enviarlos si no se proporcionaron
    datos_cliente = {k: v for k, v in datos_cliente.items() if v is not None}

    # crear_cliente espera un diccionario
    cliente_obj = crear_cliente(**datos_cliente) # Desempaquetar

    if cliente_obj:
        id_cliente = getattr(cliente_obj, 'id', cliente_obj.get('id', 'N/A'))
        console.print(f"[bold green]Cliente creado con éxito. ID: {id_cliente}[/bold green]")
        mostrar_tabla_clientes([cliente_obj]) # Mostrar el nuevo cliente
    else:
        console.print("[bold red]Error al crear el cliente.[/bold red]")


@clientes.command(help="Actualizar un cliente existente")
@click.argument("id", type=int)
# Usar los nombres de campo correctos y permitir actualizar más campos
@click.option("--nombre", help="Nuevo nombre del cliente")
@click.option("--numero", help="Nuevo Número/NIF del cliente")
@click.option("--nombre-comercial", help="Nuevo nombre comercial")
@click.option("--correo", help="Nuevo email del cliente")
@click.option("--direccion", help="Nueva dirección")
@click.option("--ciudad", help="Nueva ciudad")
@click.option("--provincia", help="Nueva provincia")
@click.option("--telefono", help="Nuevo teléfono del cliente")
@click.option("--representante", help="Nuevo nombre del representante")
@click.option("--telefono-representante", help="Nuevo teléfono del representante")
@click.option("--extension-representante", help="Nueva extensión del representante")
@click.option("--celular-representante", help="Nuevo celular del representante")
@click.option("--correo-representante", help="Nuevo correo del representante")
@click.option("--tipo-factura", type=click.Choice(['NCFC', 'NCF']), help="Nuevo tipo de factura")
def actualizar(id: int, **kwargs):
    """Comando para actualizar un cliente existente."""
    # Verificar que el cliente existe
    cliente_existente = obtener_cliente(id)
    if not cliente_existente:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    # Crear diccionario solo con los datos que se quieren actualizar (no None)
    datos_actualizacion = {k: v for k, v in kwargs.items() if v is not None}

    if not datos_actualizacion:
        console.print("[yellow]No se especificaron campos para actualizar.[/yellow]")
        return

    # actualizar_cliente espera ID y diccionario de datos
    cliente_actualizado_dict = actualizar_cliente(id, datos_actualizacion)

    if cliente_actualizado_dict:
        console.print(f"[bold green]Cliente actualizado con éxito.[/bold green]")
        # Mostrar cliente actualizado obteniéndolo de nuevo
        cliente_obj = obtener_cliente(id)
        if cliente_obj:
            mostrar_tabla_clientes([cliente_obj])
        else:
            console.print("[yellow]No se pudo recuperar el cliente actualizado para mostrarlo.[/yellow]")

    else:
        console.print("[bold red]Error al actualizar el cliente (la API no devolvió datos).[/bold red]")


@clientes.command(help="Eliminar un cliente")
@click.argument("id", type=int)
@click.option(
    "--confirmar", is_flag=True, help="Confirmar eliminación sin preguntar"
)
def eliminar(id: int, confirmar: bool):
    """Comando para eliminar un cliente."""
    # Verificar que el cliente existe (devuelve objeto Cliente)
    cliente = obtener_cliente(id)
    if not cliente:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    # Confirmar eliminación
    if not confirmar:
        nombre_cliente = getattr(cliente, 'nombre', f"ID {id}") # Usar nombre si está disponible
        console.print(
            f"[bold yellow]¿Está seguro de eliminar el cliente {nombre_cliente} (ID: {id})?[/bold yellow]"
        )
        confirmacion = click.confirm("¿Confirmar eliminación?", default=False)
        if not confirmacion:
            console.print("[yellow]Operación cancelada.[/yellow]")
            return

    # Eliminar cliente (la función ya existe y fue añadida)
    exito = eliminar_cliente(id)

    if exito:
        console.print(f"[bold green]Cliente eliminado con éxito.[/bold green]")
    else:
        console.print("[bold red]Error al eliminar el cliente.[/bold red]")


@clientes.command(help="Exportar cliente a formato JSON")
@click.argument("id", type=int)
@click.option(
    "--clipboard", is_flag=True, help="Copiar al portapapeles en lugar de mostrar"
)
def exportar(id: int, clipboard: bool):
    """Comando para exportar un cliente a JSON."""
    # obtener_cliente devuelve objeto Cliente
    cliente = obtener_cliente(id)

    if not cliente:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    # exportar_cliente espera objeto o dict
    exito, contenido = exportar_cliente(cliente, "json")

    if exito:
        if clipboard:
            try:
                import pyperclip
                pyperclip.copy(contenido)
                console.print("[bold green]Cliente exportado a JSON y copiado al portapapeles.[/bold green]")
            except ImportError:
                 console.print("[bold yellow]La funcionalidad de portapapeles requiere la librería 'pyperclip'.[/bold yellow]")
                 console.print("[bold yellow]Instálala con: pip install pyperclip[/bold yellow]")
                 console.print("\nContenido JSON:")
                 console.print(contenido)
            except Exception as e:
                 console.print(f"[bold red]Error al copiar al portapapeles: {e}[/bold red]")
                 console.print("\nContenido JSON:")
                 console.print(contenido)

        else:
            console.print(contenido)
    else:
        console.print(f"[bold red]Error al exportar cliente: {contenido}[/bold red]")


if __name__ == "__main__":
    clientes()
