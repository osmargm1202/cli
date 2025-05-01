import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum  # Usar Enum en lugar de Literal
import questionary
import requests
import typer
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
from orgm.stuff.spinner import spinner
from orgm.apis.header import get_headers_json
from orgm.apis.rnc import buscar_rnc_cliente # Importar la función de búsqueda RNC

console = Console()

# Definir enum para tipo de factura
class TipoFactura(str, Enum):
    NCFC = "NCFC"
    NCF = "NCF"
    NCG = "NCG"
    NCRG = "NCRG"

# Variables globales que inicializaremos en cada función
POSTGREST_URL = None
headers = None

def initialize():
    """Inicializa las variables que anteriormente estaban a nivel de módulo"""
    global POSTGREST_URL, headers
    
    # Cargar variables de entorno
    load_dotenv(override=True)
    
    # Obtener URL de PostgREST
    POSTGREST_URL = os.getenv("POSTGREST_URL")
    if not POSTGREST_URL:
        console.print(
            "[bold yellow]Advertencia: POSTGREST_URL no está definida en las variables de entorno.[/bold yellow]"
        )
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    
    # Verificar si se obtuvieron las credenciales (opcional)
    if "CF-Access-Client-Id" not in headers:
        console.print(
            "[bold yellow]Advertencia: Credenciales de Cloudflare Access no encontradas o no configuradas.[/bold yellow]"
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
        cliente: Datos del cliente existente para modificar. None si es nuevo.

    Returns:
        Optional[Dict]: Diccionario con los datos del cliente o None si se cancela.
    """
    nombre_seleccionado = None
    numero_seleccionado = None

    if cliente is None: # Crear nuevo cliente
        buscar_api = questionary.confirm("¿Buscar cliente por RNC/Nombre en la API antes de crear?").ask()
        if buscar_api:
            while True: # Bucle de búsqueda
                termino_busqueda = questionary.text("Ingrese término de búsqueda (Nombre o RNC):").ask()
                if not termino_busqueda:
                    print("[yellow]Búsqueda cancelada. Ingresando datos manualmente.[/yellow]")
                    break # Salir del bucle y proceder manualmente

                with spinner(f"Buscando '{termino_busqueda}' en la API RNC..."):
                    resultados_api = buscar_rnc_cliente(termino_busqueda)

                if not resultados_api:
                    print("[yellow]No se encontraron resultados.[/yellow]")
                    reintentar = questionary.select(
                        "¿Qué desea hacer?",
                        choices=["Buscar de nuevo", "Continuar manualmente"]
                    ).ask()
                    if reintentar == "Continuar manualmente":
                        break
                    # Si elige "Buscar de nuevo", el bucle continúa
                else:
                    # Formatear resultados para questionary
                    opciones = []
                    for res in resultados_api:
                        # Asegurarse de que las claves existen y formatear
                        rnc = res.get('rnc', 'N/A')
                        razon = res.get('razon', 'N/A')
                        opciones.append(f"{rnc} - {razon}")
                    
                    opciones.extend(["Buscar de nuevo", "Continuar manualmente"])
                    
                    seleccion = questionary.select(
                        "Seleccione el cliente deseado:",
                        choices=opciones
                    ).ask()

                    if seleccion == "Continuar manualmente":
                        break
                    elif seleccion == "Buscar de nuevo":
                        continue # Volver a pedir término de búsqueda
                    else:
                        # Extraer RNC y Razón Social de la selección
                        try:
                            numero_seleccionado = seleccion.split(' - ')[0]
                            nombre_seleccionado = seleccion.split(' - ')[1]
                            print(f"[green]Cliente seleccionado:[/green] {nombre_seleccionado} (RNC: {numero_seleccionado})")
                            break # Salir del bucle con los datos seleccionados
                        except IndexError:
                            print("[red]Error al procesar la selección. Intentando de nuevo.[/red]")
                            continue # Algo salió mal, volver a buscar

    # Valores por defecto (usar los seleccionados si existen)
    defaults = {}
    if cliente: # Modificar cliente existente
        try:
            defaults = cliente.model_dump()
        except AttributeError:
             defaults = {} # Fallback
    else: # Crear nuevo cliente
        defaults = {
            "nombre": nombre_seleccionado or "",
            "numero": numero_seleccionado or "",
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
            "tipo_factura": TipoFactura.NCFC, # Usar Enum
        }

    # --- Formulario principal --- 
    nombre = questionary.text(
        "Nombre del cliente:", default=defaults.get("nombre", "")
    ).ask()
    if not nombre:
        return None # Cancelar si no hay nombre
    # ... resto de las preguntas del formulario ...

    nombre_comercial = questionary.text(
        "Nombre comercial:", default=defaults.get("nombre_comercial", "")
    ).ask()

    numero = questionary.text(
        "Número/NIF del cliente:", default=defaults.get("numero", "")
    ).ask()
    if not numero:
         return None # Cancelar si no hay número


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

    # Usar el Enum para el tipo de factura
    tipo_factura_str = questionary.select(
        "Tipo de factura:",
        choices=[e.value for e in TipoFactura],
        default=defaults.get("tipo_factura", TipoFactura.NCFC).value,
    ).ask()
    tipo_factura = TipoFactura(tipo_factura_str) if tipo_factura_str else TipoFactura.NCFC

    # Devolver un diccionario con los datos, usando None para campos vacíos opcionales
    return {
        "nombre": nombre,
        "nombre_comercial": nombre_comercial if nombre_comercial else None,
        "numero": numero,
        "correo": correo if correo else None,
        "direccion": direccion if direccion else None,
        "ciudad": ciudad if ciudad else None,
        "provincia": provincia if provincia else None,
        "telefono": telefono if telefono else None,
        "representante": representante if representante else None,
        "telefono_representante": telefono_representante if telefono_representante else None,
        "extension_representante": extension_representante if extension_representante else None,
        "celular_representante": celular_representante if celular_representante else None,
        "correo_representante": correo_representante if correo_representante else None,
        "tipo_factura": tipo_factura.value # Enviar el valor string a la API
    }

def eliminar_cliente(id: int) -> bool:
    """
    Elimina un cliente específico mediante una solicitud DELETE a PostgREST.

    Args:
        id (int): El ID del cliente a eliminar.

    Returns:
        bool: True si la eliminación fue exitosa, False en caso contrario.
    """
    # Asegurar que las variables estén inicializadas
    if POSTGREST_URL is None:
        initialize()
        if not POSTGREST_URL:
            console.print(
                "[bold red]No se puede continuar sin la URL de PostgREST[/bold red]"
            )
            return False
            
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
                "Volver al menú principal",
            ],
        ).ask()

        if accion == "Volver al menú principal":
            return "exit"
        
        elif accion == "Listar todos los clientes":
            with spinner("Listando clientes..."):
                clientes_list = obtener_clientes()
            mostrar_tabla_clientes(clientes_list)
        elif accion == "Buscar clientes":
            termino = questionary.text("Ingrese término de búsqueda:").ask()
            if termino:
                with spinner(f"Buscando clientes por '{termino}'..."):
                    clientes_list = buscar_clientes(termino)
                mostrar_tabla_clientes(clientes_list)
        elif accion == "Crear nuevo cliente":
            datos = formulario_cliente()
            if datos:
                with spinner("Creando nuevo cliente..."):
                    # Llamar a crear_cliente pasando el diccionario directamente
                    nuevo_cliente_obj = crear_cliente(datos)
                if nuevo_cliente_obj:
                    nombre_cliente = getattr(nuevo_cliente_obj, 'nombre', nuevo_cliente_obj.get('nombre', 'N/A'))
                    console.print(f"[bold green]Cliente creado: {nombre_cliente}[/bold green]")
                    mostrar_tabla_clientes([nuevo_cliente_obj])
                else:
                    console.print("[bold red]No se pudo crear el cliente.[/bold red]")

        elif accion == "Modificar cliente":
            id_cliente_str = questionary.text("ID del cliente a modificar:").ask()
            if id_cliente_str:
                try:
                    id_cliente = int(id_cliente_str)
                    with spinner(f"Obteniendo datos del cliente {id_cliente}..."):
                        cliente_obj = obtener_cliente(id_cliente)
                    if cliente_obj:
                        datos_actualizados = formulario_cliente(cliente_obj)
                        if datos_actualizados:
                            with spinner(f"Actualizando cliente {id_cliente}..."):
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
                    with spinner(f"Obteniendo detalles del cliente {id_cliente}..."):
                        cliente_obj = obtener_cliente(id_cliente)
                    if cliente_obj:
                        mostrar_detalle_cliente(cliente_obj)
                    else:
                        console.print(f"[bold red]Cliente con ID {id_cliente} no encontrado[/bold red]")
                except ValueError:
                    console.print("[bold red]ID inválido, debe ser un número.[/bold red]")


# Crear la aplicación Typer para clientes
app = typer.Typer(help="Gestión de clientes")

# Reemplazar comandos de click por typer
@app.command("list", help="Listar todos los clientes")
def listar():
    """Comando para listar todos los clientes."""
    with spinner("Listando clientes..."):
        lista_clientes = obtener_clientes()
    mostrar_tabla_clientes(lista_clientes)


@app.command("show", help="Mostrar detalles de un cliente")
def mostrar(id: int, formato_json: bool = typer.Option(False, "--json", help="Mostrar en formato JSON")):
    """Comando para mostrar detalles de un cliente."""
    with spinner(f"Obteniendo detalles del cliente {id}..."):
        cliente_obj = obtener_cliente(id)

    if not cliente_obj:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    if formato_json:
        contenido = formatear_cliente_json(cliente_obj)
        console.print(contenido)
    else:
        mostrar_detalle_cliente(cliente_obj)


@app.command("find", help="Buscar clientes")
def buscar(termino: str):
    """Comando para buscar clientes."""
    with spinner(f"Buscando clientes por '{termino}'..."):
        resultados = buscar_clientes(termino)
    mostrar_tabla_clientes(resultados)


@app.command("create", help="Crear un nuevo cliente")
def crear(
    nombre: str = typer.Option(..., help="Nombre del cliente", prompt=True),
    numero: str = typer.Option(..., help="Número/NIF del cliente", prompt=True),
    nombre_comercial: Optional[str] = typer.Option(None, help="Nombre comercial del cliente"),
    email: Optional[str] = typer.Option(None, help="Email del cliente"),
    telefono: Optional[str] = typer.Option(None, help="Teléfono del cliente"),
    direccion: Optional[str] = typer.Option(None, help="Dirección del cliente"),
    ciudad: Optional[str] = typer.Option(None, help="Ciudad del cliente"),
    provincia: Optional[str] = typer.Option(None, help="Provincia del cliente"),
    representante: Optional[str] = typer.Option(None, help="Nombre del representante"),
    telefono_representante: Optional[str] = typer.Option(None, help="Teléfono del representante"),
    extension_representante: Optional[str] = typer.Option(None, help="Extensión del representante"),
    celular_representante: Optional[str] = typer.Option(None, help="Celular del representante"),
    correo_representante: Optional[str] = typer.Option(None, help="Correo del representante"),
    tipo_factura: TipoFactura = typer.Option(TipoFactura.NCFC, help="Tipo de factura")
):
    """Comando para crear un nuevo cliente."""
    datos_cliente = {
        "nombre": nombre,
        "numero": numero,
        "correo": email,
        "telefono": telefono,
        "nombre_comercial": nombre_comercial,
        "direccion": direccion,
        "ciudad": ciudad,
        "provincia": provincia,
        "representante": representante,
        "telefono_representante": telefono_representante,
        "extension_representante": extension_representante,
        "celular_representante": celular_representante,
        "correo_representante": correo_representante,
        "tipo_factura": tipo_factura,
    }
    datos_cliente = {k: v for k, v in datos_cliente.items() if v is not None}

    with spinner("Creando cliente..."):
        cliente_obj = crear_cliente(**datos_cliente)

    if cliente_obj:
        id_cliente = getattr(cliente_obj, 'id', cliente_obj.get('id', 'N/A'))
        console.print(f"[bold green]Cliente creado con éxito. ID: {id_cliente}[/bold green]")
        mostrar_tabla_clientes([cliente_obj])
    else:
        console.print("[bold red]Error al crear el cliente.[/bold red]")


@app.command("edit", help="Actualizar un cliente existente")
def actualizar(
    id: int,
    nombre: Optional[str] = typer.Option(None, help="Nuevo nombre del cliente"),
    numero: Optional[str] = typer.Option(None, help="Nuevo Número/NIF del cliente"),
    nombre_comercial: Optional[str] = typer.Option(None, help="Nuevo nombre comercial"),
    correo: Optional[str] = typer.Option(None, help="Nuevo email del cliente"),
    direccion: Optional[str] = typer.Option(None, help="Nueva dirección"),
    ciudad: Optional[str] = typer.Option(None, help="Nueva ciudad"),
    provincia: Optional[str] = typer.Option(None, help="Nueva provincia"),
    telefono: Optional[str] = typer.Option(None, help="Nuevo teléfono del cliente"),
    representante: Optional[str] = typer.Option(None, help="Nuevo nombre del representante"),
    telefono_representante: Optional[str] = typer.Option(None, help="Nuevo teléfono del representante"),
    extension_representante: Optional[str] = typer.Option(None, help="Nueva extensión del representante"),
    celular_representante: Optional[str] = typer.Option(None, help="Nuevo celular del representante"),
    correo_representante: Optional[str] = typer.Option(None, help="Nuevo correo del representante"),
    tipo_factura: Optional[TipoFactura] = typer.Option(None, help="Nuevo tipo de factura")
):
    """Comando para actualizar un cliente existente."""
    with spinner(f"Verificando cliente {id}..."):
        cliente_existente = obtener_cliente(id)
    if not cliente_existente:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    # Recopilar todos los parámetros no None en un diccionario
    datos_actualizacion = {}
    if nombre is not None:
        datos_actualizacion["nombre"] = nombre
    if numero is not None:
        datos_actualizacion["numero"] = numero
    if nombre_comercial is not None:
        datos_actualizacion["nombre_comercial"] = nombre_comercial
    if correo is not None:
        datos_actualizacion["correo"] = correo
    if direccion is not None:
        datos_actualizacion["direccion"] = direccion
    if ciudad is not None:
        datos_actualizacion["ciudad"] = ciudad
    if provincia is not None:
        datos_actualizacion["provincia"] = provincia
    if telefono is not None:
        datos_actualizacion["telefono"] = telefono
    if representante is not None:
        datos_actualizacion["representante"] = representante
    if telefono_representante is not None:
        datos_actualizacion["telefono_representante"] = telefono_representante
    if extension_representante is not None:
        datos_actualizacion["extension_representante"] = extension_representante
    if celular_representante is not None:
        datos_actualizacion["celular_representante"] = celular_representante
    if correo_representante is not None:
        datos_actualizacion["correo_representante"] = correo_representante
    if tipo_factura is not None:
        datos_actualizacion["tipo_factura"] = tipo_factura

    if not datos_actualizacion:
        console.print("[yellow]No se especificaron campos para actualizar.[/yellow]")
        return

    with spinner(f"Actualizando cliente {id}..."):
        cliente_actualizado_dict = actualizar_cliente(id, datos_actualizacion)

    if cliente_actualizado_dict:
        console.print(f"[bold green]Cliente actualizado con éxito.[/bold green]")
        with spinner(f"Obteniendo datos actualizados del cliente {id}..."):
            cliente_obj = obtener_cliente(id)
        if cliente_obj:
            mostrar_tabla_clientes([cliente_obj])
        else:
            console.print("[yellow]No se pudo recuperar el cliente actualizado para mostrarlo.[/yellow]")
    else:
        console.print("[bold red]Error al actualizar el cliente (la API no devolvió datos).[/bold red]")


@app.command("delete", help="Eliminar un cliente")
def eliminar(
    id: int,
    confirmar: bool = typer.Option(False, "--confirmar", help="Confirmar eliminación sin preguntar")
):
    """Comando para eliminar un cliente."""
    with spinner(f"Verificando cliente {id}..."):
        cliente = obtener_cliente(id)
    if not cliente:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

    if not confirmar:
        nombre_cliente = getattr(cliente, 'nombre', f"ID {id}")
        console.print(
            f"[bold yellow]¿Está seguro de eliminar el cliente {nombre_cliente} (ID: {id})?[/bold yellow]"
        )
        confirmacion = typer.confirm("¿Confirmar eliminación?", default=False)
        if not confirmacion:
            console.print("[yellow]Operación cancelada.[/yellow]")
            return

    with spinner(f"Eliminando cliente {id}..."):
        exito = eliminar_cliente(id)

    if exito:
        console.print(f"[bold green]Cliente eliminado con éxito.[/bold green]")
    else:
        console.print("[bold red]Error al eliminar el cliente.[/bold red]")


@app.command("export", help="Exportar cliente a formato JSON")
def exportar(
    id: int,
    clipboard: bool = typer.Option(False, "--clipboard", help="Copiar al portapapeles en lugar de mostrar")
):
    """Comando para exportar un cliente a JSON."""
    with spinner(f"Obteniendo datos del cliente {id} para exportar..."):
        cliente = obtener_cliente(id)

    if not cliente:
        console.print(f"[bold red]Cliente con ID {id} no encontrado.[/bold red]")
        return

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


# Comando principal para el menú interactivo
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Gestión de clientes"""
    if ctx.invoked_subcommand is None:
        # Mostrar el menú interactivo
        try:
            menu_clientes()
        except Exception as e:
            console.print(f"[bold red]Error en el menú de clientes: {e}[/bold red]")


# Reemplazar la exportación del grupo click por la app de typer
clientes = app

if __name__ == "__main__":
    app()
