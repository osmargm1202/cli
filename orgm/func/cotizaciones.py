import typer
import questionary
from typing import Dict, Optional, List
from rich.console import Console
from rich.table import Table
from rich import print
from orgm.apis.divisa import obtener_tasa_divisa
from orgm.adm.servicios import obtener_servicios
from orgm.apis.ai import generate_project_description
import os, requests
from orgm.adm.clientes import buscar_clientes
from orgm.adm.cotizaciones import cotizaciones_por_cliente as adm_cotizaciones_por_cliente
from orgm.adm.proyectos import buscar_proyectos, Proyecto
from orgm.adm.db import Cotizacion
from orgm.stuff.spinner import spinner
from orgm.apis.header import get_headers_json
from datetime import datetime
from dotenv import load_dotenv

console = Console()

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
            "[bold yellow]Las consultas no incluirán autenticación de Cloudflare Access.[/bold yellow]"
        )


def obtener_cotizaciones() -> List[Dict]:
    """
    Obtiene todas las cotizaciones.
    
    Returns:
        List[Dict]: Lista de cotizaciones.
    """
    # Asegurar que las variables estén inicializadas
    if POSTGREST_URL is None:
        initialize()
        if not POSTGREST_URL:
            console.print(
                "[bold red]No se puede continuar sin la URL de PostgREST[/bold red]"
            )
            return []
            
    try:
        # Seleccionar todos los campos de cotizacion y campos específicos de cliente/proyecto
        select_query = "select=*,cliente(id,nombre),proyecto(id,nombre_proyecto)"
        # Ordenar por fecha descendente para mostrar las más recientes primero
        url = f"{POSTGREST_URL}/cotizacion?{select_query}&order=fecha.desc"
        with spinner("Obteniendo todas las cotizaciones..."):
            response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []


def obtener_cotizacion(id_cotizacion: int) -> Optional[Dict]:
    """
    Obtiene una cotización específica por su ID.
    
    Args:
        id_cotizacion (int): ID de la cotización a buscar.
        
    Returns:
        Optional[Dict]: Datos de la cotización o None si no se encuentra.
    """
    # Asegurar que las variables estén inicializadas
    if POSTGREST_URL is None:
        initialize()
        if not POSTGREST_URL:
            console.print(
                "[bold red]No se puede continuar sin la URL de PostgREST[/bold red]"
            )
            return None
            
    try:
        select_query = "select=*,cliente(id,nombre),proyecto(id,nombre_proyecto)"
        url = f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}&{select_query}"
        with spinner(f"Obteniendo cotización ID: {id_cotizacion}..."):
            response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result[0] if result else None
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None


def crear_cotizacion(datos: Dict) -> Optional[Dict]:
    """
    Crea una nueva cotización.
    
    Args:
        datos (Dict): Datos de la cotización a crear.
        
    Returns:
        Optional[Dict]: Cotización creada o None si falla.
    """
    # Asegurar que las variables estén inicializadas
    if POSTGREST_URL is None:
        initialize()
        if not POSTGREST_URL:
            console.print(
                "[bold red]No se puede continuar sin la URL de PostgREST[/bold red]"
            )
            return None
            
    try:
        # Asegurar que tenga fecha de creación
        if "fecha_creacion" not in datos:
            datos["fecha_creacion"] = datetime.now().isoformat()
            
        with spinner("Creando nueva cotización..."):
            response = requests.post(f"{POSTGREST_URL}/cotizacion", json=datos, headers=headers)
        response.raise_for_status()
        return response.json()[0] if response.json() else None
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return None


def actualizar_cotizacion(id_cotizacion: int, datos: Dict) -> bool:
    """
    Actualiza una cotización existente.
    
    Args:
        id_cotizacion (int): ID de la cotización a actualizar.
        datos (Dict): Nuevos datos para la cotización.
        
    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.
    """
    # Asegurar que las variables estén inicializadas
    if POSTGREST_URL is None:
        initialize()
        if not POSTGREST_URL:
            console.print(
                "[bold red]No se puede continuar sin la URL de PostgREST[/bold red]"
            )
            return False
            
    try:
        # Remover id si está en los datos para evitar conflictos
        if "id" in datos:
            del datos["id"]
            
        with spinner(f"Actualizando cotización ID: {id_cotizacion}..."):
            response = requests.patch(
                f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}", 
                json=datos, 
                headers=headers
            )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return False
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return False


def eliminar_cotizacion(id_cotizacion: int) -> bool:
    """
    Elimina una cotización.
    
    Args:
        id_cotizacion (int): ID de la cotización a eliminar.
        
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
            
    try:
        with spinner(f"Eliminando cotización ID: {id_cotizacion}..."):
            response = requests.delete(
                f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}", 
                headers=headers
            )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return False
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return False


def buscar_cotizaciones(termino: str) -> List[Dict]:
    """
    Busca cotizaciones por término en el nombre, descripción, etc.
    
    Args:
        termino (str): Término de búsqueda.
        
    Returns:
        List[Dict]: Lista de cotizaciones que coinciden con el término.
    """
    # Asegurar que las variables estén inicializadas
    if POSTGREST_URL is None:
        initialize()
        if not POSTGREST_URL:
            console.print(
                "[bold red]No se puede continuar sin la URL de PostgREST[/bold red]"
            )
            return []
            
    try:
        select_query = "select=*,cliente(id,nombre),proyecto(id,nombre_proyecto)"
        # Buscar en nombre_proyecto, descripcion, y nombre de cliente
        url = f"{POSTGREST_URL}/cotizacion?or=(descripcion.ilike.*{termino}*,cliente.nombre.ilike.*{termino}*,proyecto.nombre_proyecto.ilike.*{termino}*)&{select_query}"
        with spinner(f"Buscando cotizaciones con término: '{termino}'..."):
            response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []


def cotizaciones_por_cliente(id_cliente: int, limite: Optional[int] = None) -> List[Dict]:
    """
    Obtiene las cotizaciones de un cliente específico.
    
    Args:
        id_cliente (int): ID del cliente.
        limite (Optional[int]): Cantidad máxima de cotizaciones a retornar.
        
    Returns:
        List[Dict]: Lista de cotizaciones del cliente.
    """
    # Usamos la función del módulo adm en lugar de reimplementarla
    return adm_cotizaciones_por_cliente(id_cliente, limite)


def mostrar_tabla_cotizaciones(cotizaciones: List[Dict]) -> None:
    """
    Muestra una tabla con las cotizaciones.
    
    Args:
        cotizaciones (List[Dict]): Lista de cotizaciones para mostrar.
    """
    if not cotizaciones:
        console.print("[bold yellow]No se encontraron cotizaciones.[/bold yellow]")
        return
        
    tabla = Table(title="Cotizaciones", show_header=True)
    tabla.add_column("ID", style="dim")
    tabla.add_column("Número", style="green")
    tabla.add_column("Cliente", style="blue")
    tabla.add_column("Estado", style="magenta")
    tabla.add_column("Fecha", style="cyan")
    tabla.add_column("Total", style="yellow", justify="right")
    
    for cot in cotizaciones:
        # Formatear fecha
        fecha = cot.get("fecha_creacion", "")
        if fecha:
            try:
                fecha_obj = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
                fecha_form = fecha_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                fecha_form = fecha
        else:
            fecha_form = ""
            
        # Formatear total
        total = cot.get("total", 0)
        total_form = f"{total:,.2f} €" if total is not None else ""
        
        tabla.add_row(
            str(cot.get("id", "")),
            cot.get("numero", ""),
            cot.get("cliente_nombre", ""),
            cot.get("estado", ""),
            fecha_form,
            total_form
        )
    
    console.print(tabla)



def mostrar_cotizaciones(cotizaciones):
    """Muestra una tabla con las cotizaciones"""
    if not cotizaciones:
        print("[yellow]No se encontraron cotizaciones[/yellow]")
        return

    table = Table(title="Cotizaciones")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Cliente", style="green")
    table.add_column("Proyecto", style="green")
    table.add_column("Descripción", style="white", overflow="fold")
    table.add_column("Subtotal", style="magenta")
    table.add_column("ITBIS", style="magenta")
    table.add_column("Indirectos", style="magenta")
    table.add_column("Total", style="yellow")

    for c in cotizaciones:
        total = f"{c['moneda']} {c.get('total',0):,.2f}" if c.get('total') else "N/A"
        subtotal = f"{c['moneda']} {c.get('subtotal',0):,.2f}"
        itbis = f"{c.get('itbism',0):,.2f}"
        indirectos = f"{c.get('indirectos',0):,.2f}"
        table.add_row(
            str(c["id"]),
            f"{c['cliente']['id']} - {c['cliente']['nombre']}" if 'cliente' in c else str(c['id_cliente']),
            f"{c['proyecto']['id']} - {c['proyecto']['nombre_proyecto']}" if 'proyecto' in c else str(c['id_proyecto']),
            (c.get('descripcion','')[:60] + ('...' if c.get('descripcion') and len(c.get('descripcion'))>60 else '')),
            subtotal,
            itbis,
            indirectos,
            total,
        )

    console.print(table)


def _seleccionar_servicio(id_default: Optional[int] = None) -> int:
    with spinner("Obteniendo lista de servicios..."):
        servicios = obtener_servicios()
    # Manejar tanto diccionarios como objetos
    opciones = []
    for s in servicios:
        if isinstance(s, dict):
            # Si es un diccionario, usar .get()
            id_servicio = s.get("id", "")
            nombre_servicio = s.get("nombre", "") or s.get("concepto", "")
        else:
            # Si es un objeto, usar getattr()
            id_servicio = getattr(s, "id", "")
            nombre_servicio = getattr(s, "nombre", "") or getattr(s, "concepto", "")
        
        opciones.append(f"{id_servicio}: {nombre_servicio}")
    
    if not opciones:
        return id_default or 0
    
    if id_default:
        opciones_default = next((o for o in opciones if o.startswith(str(id_default))), opciones[0])
    else:
        opciones_default = opciones[0]
    
    opciones.append("Cancelar")
    sel = questionary.select("Seleccione servicio:", choices=opciones, default=opciones_default).ask()
    if sel == "Cancelar":
        return id_default or 0
    
    return int(sel.split(":")[0])


# Último cliente usado
_ultimo_cliente_id: Optional[int] = None


def _preguntar_cliente() -> Optional[int]:
    global _ultimo_cliente_id
    default_val = str(_ultimo_cliente_id) if _ultimo_cliente_id else ""
    cid_str = questionary.text("ID del cliente:", default=default_val).ask()
    if not cid_str:
        return None
    try:
        cid = int(cid_str)
    except ValueError:
        print("[bold red]ID inválido[/bold red]")
        return None

    # Mostrar últimas 10 cotizaciones de este cliente
    cotis = [c for c in obtener_cotizaciones() if c["id_cliente"] == cid]
    cotis.sort(key=lambda x: x.get('fecha', ''), reverse=True)
    mostrar_cotizaciones(cotis[:10])
    if len(cotis) > 10 and questionary.confirm("¿Mostrar más cotizaciones?", default=False).ask():
        mostrar_cotizaciones(cotis)

    _ultimo_cliente_id = cid
    return cid



def formulario_cotizacion(cotizacion=None) -> Dict:
    """Formulario para crear o actualizar una cotización"""
    es_nuevo = cotizacion is None

    # Verificar si cotizacion es un diccionario o un objeto y obtener valores por defecto
    defaults = {}
    if cotizacion:
        if isinstance(cotizacion, dict):
            # Si es un diccionario, usar .get()
            defaults = {
                "id_cliente": cotizacion.get("id_cliente", ""),
                "id_proyecto": cotizacion.get("id_proyecto", ""),
                "id_servicio": cotizacion.get("id_servicio", ""),
                "moneda": cotizacion.get("moneda", "RD$"),
                "descripcion": cotizacion.get("descripcion", ""),
                "estado": cotizacion.get("estado", "GENERADA"),
                "total": cotizacion.get("total", 0.0),
                "fecha": cotizacion.get("fecha", ""),
                "tasa_moneda": cotizacion.get("tasa_moneda", 1.0),
                "tiempo_entrega": cotizacion.get("tiempo_entrega", "3"),
                "avance": cotizacion.get("avance", "60"),
                "validez": cotizacion.get("validez", 30),
                "idioma": cotizacion.get("idioma", "ES"),
                "descuentop": cotizacion.get("descuentop", 0)
            }
        else:
            # Si es un objeto, usar getattr()
            defaults = {
                "id_cliente": getattr(cotizacion, "id_cliente", ""),
                "id_proyecto": getattr(cotizacion, "id_proyecto", ""),
                "id_servicio": getattr(cotizacion, "id_servicio", ""),
                "moneda": getattr(cotizacion, "moneda", "RD$"),
                "descripcion": getattr(cotizacion, "descripcion", ""),
                "estado": getattr(cotizacion, "estado", "GENERADA"),
                "total": getattr(cotizacion, "total", 0.0),
                "fecha": getattr(cotizacion, "fecha", ""),
                "tasa_moneda": getattr(cotizacion, "tasa_moneda", 1.0),
                "tiempo_entrega": getattr(cotizacion, "tiempo_entrega", "3"),
                "avance": getattr(cotizacion, "avance", "60"),
                "validez": getattr(cotizacion, "validez", 30),
                "idioma": getattr(cotizacion, "idioma", "ES"),
                "descuentop": getattr(cotizacion, "descuentop", 0)
            }
    else:
        # Valores predeterminados para nueva cotización
        defaults = {
            "id_cliente": "",
            "id_proyecto": "",
            "id_servicio": "",
            "moneda": "RD$",
            "descripcion": "",
            "estado": "GENERADA",
            "total": 0.0,
            "fecha": "",
            "tasa_moneda": 1.0,
            "tiempo_entrega": "3",
            "avance": "60",
            "validez": 30,
            "idioma": "ES",
            "descuentop": 0
        }

    cid = _preguntar_cliente() if es_nuevo else defaults["id_cliente"]
    if cid is None:
        return {}
    datos = {}
    datos["id_cliente"] = cid
    datos["id_servicio"] = _seleccionar_servicio(defaults["id_servicio"])
    datos["moneda"] = questionary.select(
        "Moneda:", choices=["RD$", "USD$", "EUR€"], default=defaults["moneda"]
    ).ask()

    # Fecha
    datos["fecha"] = questionary.text("Fecha (YYYY-MM-DD):", default=defaults["fecha"]).ask()

    # Tasa de cambio
    metodo_tasa = questionary.select(
        "¿Cómo desea obtener la tasa de cambio?",
        choices=["API", "Manual"],
        default="API",
    ).ask()
    if metodo_tasa == "API":
        with spinner("Obteniendo tasa de cambio USD->RD$..."):
            tasa = obtener_tasa_divisa("USD", "RD$", 1)
        datos["tasa_moneda"] = tasa or 1.0
    else:
        tasa_str = questionary.text("Tasa de cambio:", default=str(defaults["tasa_moneda"])).ask()
        try:
            datos["tasa_moneda"] = float(tasa_str)
        except ValueError:
            datos["tasa_moneda"] = 1.0


    metodo_desc = questionary.select(
        "¿Cómo desea establecer la descripción?",
        choices=["Manual", "Automática"],
        default="Manual" if defaults["descripcion"] else "Automática",
    ).ask()
    if metodo_desc == "Manual":
        datos["descripcion"] = questionary.text(
            "Descripción de la cotización:", default=defaults["descripcion"]
        ).ask()
    else:
        prompt = questionary.text("Prompt para generar descripción:").ask()
        if prompt:
            with spinner("Generando descripción con IA..."):
                desc = generate_project_description(prompt)
            datos["descripcion"] = desc or ""
        else:
            datos["descripcion"] = defaults["descripcion"]

    datos["estado"] = questionary.select(
        "Estado:", choices=["GENERADA", "ENVIADA", "ACEPTADA", "RECHAZADA"], default=defaults["estado"]
    ).ask()

    datos["tiempo_entrega"] = questionary.text("Tiempo de entrega:", default=defaults["tiempo_entrega"]).ask()
    datos["avance"] = questionary.text("Porcentaje de avance:", default=defaults["avance"]).ask()
    datos["validez"] = int(questionary.text("Días de validez:", default=str(defaults["validez"])).ask())
    datos["idioma"] = questionary.select(
        "Idioma:", choices=["ES", "EN"], default=defaults["idioma"]
    ).ask()

    # descuento porcentaje
    desc_p = questionary.text("Descuento (%):", default=str(defaults["descuentop"])).ask()
    try:
        datos["descuentop"] = float(desc_p)
    except ValueError:
        datos["descuentop"] = 0.0

    return datos


# Crear la aplicación Typer para cotizaciones
app = typer.Typer(help="Gestión de cotizaciones")

# Comando principal para el menú interactivo
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Gestión de cotizaciones"""
    if ctx.invoked_subcommand is None:
        menu_principal()


def menu_principal():
    while True:
        accion = questionary.select(
            "¿Qué desea hacer?",
            choices=[
                "Ver todas las cotizaciones",
                "Buscar cotizaciones (por Cliente o Proyecto)",
                "Crear nueva cotización",
                "Modificar cotización existente",
                "Eliminar cotización",
                "Ver detalles de una cotización",
                "Volver al menú principal",
            ],
        ).ask()

        if accion == "Volver al menú principal":
            return "exit"

        if accion == "Ver todas las cotizaciones":
            cotizaciones = obtener_cotizaciones()
            mostrar_cotizaciones(cotizaciones)
        elif accion == "Buscar cotizaciones (por Cliente o Proyecto)":
            tipo_busqueda = questionary.select(
                "¿Buscar por Cliente o Proyecto?",
                choices=["Cliente", "Proyecto", "Cancelar"]
            ).ask()

            if tipo_busqueda == "Cliente":
                termino = questionary.text("Nombre del cliente a buscar:").ask()
                if termino:
                    cliente_id = _seleccionar_cliente_por_nombre(termino)
                    if cliente_id:
                        _mostrar_cotis_cliente(cliente_id)
                        # Opción para ver/editar una cotización específica
                        id_text = questionary.text("ID de la cotización a ver/editar (dejar en blanco para continuar):").ask()
                        if id_text:
                            try:
                                cid = int(id_text)
                                cot = obtener_cotizacion(cid)
                            except ValueError:
                                cot = None
                            if cot:
                                mostrar_cotizacion_detalle(cot)
                                if questionary.confirm("¿Desea editar esta cotización?", default=False).ask():
                                    datos = formulario_cotizacion(cot)
                                    if datos:
                                        cot_id = getattr(cot, 'id', None) if not isinstance(cot, dict) else cot.get('id', None)
                                        if cot_id is not None:
                                            act = actualizar_cotizacion(cot_id, datos)
                                            if act:
                                                print("[bold green]Cotización actualizada[/bold green]")
                                        else:
                                            print("[bold red]No se pudo obtener el ID de la cotización[/bold red]")

            elif tipo_busqueda == "Proyecto":
                termino_proyecto = questionary.text("Nombre o término del proyecto a buscar:").ask()
                if termino_proyecto:
                    proyecto_id = _seleccionar_proyecto_por_nombre(termino_proyecto)
                    if proyecto_id:
                        _mostrar_cotis_proyecto(proyecto_id)
                        # Opción para ver/editar una cotización específica después de mostrar
                        id_text = questionary.text("ID de la cotización a ver/editar (dejar en blanco para continuar):").ask()
                        if id_text:
                            try:
                                cid = int(id_text)
                                # Validar que la cotización pertenece al proyecto buscado?
                                # Por ahora, se asume que el usuario introduce un ID válido de la lista mostrada
                                cot = obtener_cotizacion(cid)
                            except ValueError:
                                cot = None
                            if cot:
                                mostrar_cotizacion_detalle(cot)
                                if questionary.confirm("¿Desea editar esta cotización?", default=False).ask():
                                    datos = formulario_cotizacion(cot)
                                    if datos:
                                        cot_id = getattr(cot, 'id', None) if not isinstance(cot, dict) else cot.get('id', None)
                                        if cot_id is not None:
                                            act = actualizar_cotizacion(cot_id, datos)
                                            if act:
                                                print("[bold green]Cotización actualizada[/bold green]")
                                        else:
                                            print("[bold red]No se pudo obtener el ID de la cotización[/bold red]")
                    # Si proyecto_id es None, _seleccionar_proyecto_por_nombre ya mostró mensaje

            # Si tipo_busqueda es "Cancelar", no hace nada y vuelve al menú.

        elif accion == "Crear nueva cotización":
            datos = formulario_cotizacion()
            if datos:
                nueva = crear_cotizacion(datos)
                if nueva:
                    # Obtener el ID usando getattr para objetos o get para diccionarios
                    nueva_id = getattr(nueva, 'id', None) if not isinstance(nueva, dict) else nueva.get('id', None)
                    print(f"[bold green]Cotización creada: ID {nueva_id}[/bold green]")
        elif accion == "Modificar cotización existente":
            id_text = questionary.text("ID de la cotización a modificar:").ask()
            if not id_text:
                continue
            try:
                id_num = int(id_text)
            except ValueError:
                print("[bold red]ID inválido[/bold red]")
                continue
            cot = obtener_cotizacion(id_num)
            if not cot:
                print("[bold red]No se encontró la cotización[/bold red]")
                continue
            datos = formulario_cotizacion(cot)
            if datos:
                act = actualizar_cotizacion(id_num, datos)
                if act:
                    print("[bold green]Cotización actualizada correctamente[/bold green]")
        elif accion == "Eliminar cotización":
            id_text = questionary.text("ID de la cotización a eliminar:").ask()
            if not id_text:
                continue
            try:
                id_num = int(id_text)
            except ValueError:
                print("[bold red]ID inválido[/bold red]")
                continue
            cot = obtener_cotizacion(id_num)
            if not cot:
                print("[bold red]No se encontró la cotización[/bold red]")
                continue
            if questionary.confirm("¿Eliminar cotización?", default=False).ask():
                if eliminar_cotizacion(id_num):
                    print("[bold green]Cotización eliminada[/bold green]")
        elif accion == "Ver detalles de una cotización":
            id_text = questionary.text("ID de la cotización a ver:").ask()
            if not id_text:
                continue
            try:
                id_num = int(id_text)
            except ValueError:
                print("[bold red]ID inválido[/bold red]")
                continue
            cot = obtener_cotizacion(id_num)
            if not cot:
                print("[bold red]No se encontró la cotización[/bold red]")
                continue
            mostrar_cotizacion_detalle(cot)

# Reemplazar comandos de click por typer
@app.command("list")
def cmd_listar_cotizaciones():
    """Listar todas las cotizaciones"""
    cotizaciones = obtener_cotizaciones()
    mostrar_cotizaciones(cotizaciones)


@app.command("find")
def cmd_buscar_cotizaciones(termino: str):
    """Buscar cotizaciones por nombre de cliente"""
    cliente_id = _seleccionar_cliente_por_nombre(termino)
    if cliente_id:
        _mostrar_cotis_cliente(cliente_id)


@app.command("create")
def cmd_crear_cotizacion():
    """Crear una nueva cotización"""
    datos = formulario_cotizacion()
    if datos:
        nueva = crear_cotizacion(datos)
        if nueva:
            # Obtener el ID usando getattr para objetos o get para diccionarios
            nueva_id = getattr(nueva, 'id', None) if not isinstance(nueva, dict) else nueva.get('id', None)
            print(f"[bold green]Cotización creada: ID {nueva_id}[/bold green]")


@app.command("edit")
def cmd_modificar_cotizacion(id_cotizacion: int):
    """Modificar una cotización existente"""
    cot = obtener_cotizacion(id_cotizacion)
    if not cot:
        print(f"[bold red]No se encontró la cotización con ID {id_cotizacion}[/bold red]")
        return
    datos = formulario_cotizacion(cot)
    if datos:
        act = actualizar_cotizacion(id_cotizacion, datos)
        if act:
            print("[bold green]Cotización actualizada[/bold green]")


@app.command("delete")
def cmd_eliminar_cotizacion(id_cotizacion: int):
    """Eliminar una cotización"""
    cot = obtener_cotizacion(id_cotizacion)
    if not cot:
        print(f"[bold red]No se encontró la cotización con ID {id_cotizacion}[/bold red]")
        return
    if typer.confirm("¿Está seguro de eliminar esta cotización?", default=False):
        if eliminar_cotizacion(id_cotizacion):
            print("[bold green]Cotización eliminada correctamente[/bold green]")


@app.command("show")
def cmd_ver_cotizacion(id_cotizacion: int):
    """Ver detalles de una cotización"""
    cot = obtener_cotizacion(id_cotizacion)
    if not cot:
        print(f"[bold red]No se encontró la cotización con ID {id_cotizacion}[/bold red]")
        return
    mostrar_cotizacion_detalle(cot)


# Reemplazar la exportación del grupo click por la app de typer
cotizacion = app

# --- helper para seleccionar cliente ---
def _seleccionar_cliente_por_nombre(termino: str) -> Optional[int]:
    with spinner(f"Buscando clientes por '{termino}'..."):
        clientes = buscar_clientes(termino)
    if not clientes:
        print("[yellow]No se encontraron clientes[/yellow]")
        return None
    
    # Manejar tanto diccionarios como objetos
    opciones = []
    for c in clientes:
        if isinstance(c, dict):
            # Si es un diccionario, usar .get()
            id_cliente = c.get("id", "")
            nombre_cliente = c.get("nombre", "")
        else:
            # Si es un objeto, usar getattr()
            id_cliente = getattr(c, "id", "")
            nombre_cliente = getattr(c, "nombre", "")
        
        opciones.append(f"{id_cliente}: {nombre_cliente}")
    
    opciones.append("Cancelar")
    sel = questionary.select("Seleccione un cliente:", choices=opciones).ask()
    if sel == "Cancelar":
        return None
    
    return int(sel.split(":")[0])


def _mostrar_cotis_cliente(id_cliente: int):
    cotis = cotizaciones_por_cliente(id_cliente, 10)
    if not cotis:
        print("[yellow]No hay cotizaciones para este cliente[/yellow]")
        return
    mostrar_cotizaciones(cotis)
    # verificar si hay más de 10
    if len(cotis) == 10:
        # Hacer una consulta para contar total?
        mas = questionary.confirm("¿Mostrar más cotizaciones?", default=False).ask()
        if mas:
            cotis_all = cotizaciones_por_cliente(id_cliente, None)
            mostrar_cotizaciones(cotis_all)


def mostrar_cotizacion_detalle(cotizacion):
    """Muestra los datos completos de una cotización (modelo o dict)"""
    # Convert model to dict if needed
    if isinstance(cotizacion, Cotizacion):
        data = cotizacion.model_dump()
    else:
        data = cotizacion

    table = Table(title=f"Cotización ID: {data.get('id')}")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="green")

    for k, v in data.items():
        table.add_row(str(k), str(v))

    console.print(table)


def cotizaciones_por_proyecto(id_proyecto: int, limite: Optional[int] = None) -> List[Dict]:
    """
    Obtiene las cotizaciones relacionadas con un proyecto específico.
    
    Args:
        id_proyecto (int): ID del proyecto.
        limite (Optional[int]): Cantidad máxima de cotizaciones a retornar.
        
    Returns:
        List[Dict]: Lista de cotizaciones del proyecto.
    """
    # Asegurar que las variables estén inicializadas
    if POSTGREST_URL is None:
        initialize()
        if not POSTGREST_URL:
            console.print(
                "[bold red]No se puede continuar sin la URL de PostgREST[/bold red]"
            )
            return []
            
    try:
        select_query = "select=*,cliente(id,nombre),proyecto(id,nombre_proyecto)"
        url = f"{POSTGREST_URL}/cotizacion?id_proyecto=eq.{id_proyecto}&{select_query}"
        
        # Añadir límite si se especifica
        if limite:
            url += f"&limit={limite}"
            
        with spinner(f"Obteniendo cotizaciones del proyecto {id_proyecto}..."):
            response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Error en la solicitud HTTP: {e}[/bold red]")
        return []
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error en la conexión: {e}[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
        return []


def _mostrar_cotis_proyecto(id_proyecto: int):
    """Obtiene y muestra las cotizaciones para un ID de proyecto específico."""
    cotis = cotizaciones_por_proyecto(id_proyecto, 10)
    if not cotis:
        print("[yellow]No hay cotizaciones para este proyecto[/yellow]")
        return
    mostrar_cotizaciones(cotis)
    # verificar si hay más de 10
    if len(cotis) == 10:
        # Hacer una consulta para contar total? Mejor obtener todas si confirma
        mas = questionary.confirm("¿Mostrar más cotizaciones?", default=False).ask()
        if mas:
            cotis_all = cotizaciones_por_proyecto(id_proyecto, None) # Obtener todas
            mostrar_cotizaciones(cotis_all)


# --- helper para seleccionar proyecto ---
def _seleccionar_proyecto_por_nombre(termino: str) -> Optional[int]:
    """Busca proyectos por nombre y permite al usuario seleccionar uno."""
    with spinner(f"Buscando proyectos por '{termino}'..."):
        proyectos: List[Proyecto] = buscar_proyectos(termino)
    if not proyectos:
        print("[yellow]No se encontraron proyectos[/yellow]")
        return None
    
    # Manejar tanto diccionarios como objetos (aunque buscar_proyectos devuelve Proyecto)
    opciones = []
    for p in proyectos:
        if isinstance(p, Proyecto): # Verificar si es instancia de Proyecto
            id_proyecto = p.id
            nombre_proyecto = p.nombre_proyecto
            opciones.append(f"{id_proyecto}: {nombre_proyecto}")
        elif isinstance(p, dict): # Fallback por si acaso
            id_proyecto = p.get("id", "")
            nombre_proyecto = p.get("nombre_proyecto", "")
            opciones.append(f"{id_proyecto}: {nombre_proyecto}")
        # Ignorar otros tipos si los hubiera
    
    if not opciones:
         print("[yellow]No se encontraron proyectos válidos[/yellow]")
         return None

    opciones.append("Buscar de nuevo")
    opciones.append("Cancelar")

    while True:
        sel = questionary.select("Seleccione un proyecto:", choices=opciones).ask()
        
        if sel == "Cancelar":
            return None
        elif sel == "Buscar de nuevo":
            nuevo_termino = questionary.text("Nuevo término de búsqueda:").ask()
            if not nuevo_termino:
                return None # Cancelar si no ingresa nuevo término
            with spinner(f"Buscando proyectos por '{nuevo_termino}'..."):
                proyectos = buscar_proyectos(nuevo_termino)
            if not proyectos:
                print("[yellow]No se encontraron proyectos[/yellow]")
                # Podríamos preguntar si quiere intentar de nuevo o cancelar
                if not questionary.confirm("¿Intentar buscar de nuevo?", default=True).ask():
                    return None
                continue # Volver a pedir término
            # Actualizar opciones si se encontraron proyectos
            opciones = [f"{p.id}: {p.nombre_proyecto}" for p in proyectos if isinstance(p, Proyecto)]
            opciones.append("Buscar de nuevo")
            opciones.append("Cancelar")
            continue # Mostrar nueva lista
        else:
            # Seleccionó un proyecto
            try:
                return int(sel.split(":")[0])
            except (ValueError, IndexError):
                print("[red]Selección inválida[/red]")
                # Volver a mostrar la lista actual


if __name__ == "__main__":
    app() 