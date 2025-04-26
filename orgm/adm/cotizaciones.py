# -*- coding: utf-8 -*-
# NUEVO ARCHIVO: orgm/adm/cotizaciones.py
# Funciones para acceder a PostgREST relacionadas con las cotizaciones

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

import requests
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from orgm.adm.db import Cotizacion

console = Console()
load_dotenv(override=True)

# Obtener la URL de PostgREST desde las variables de entorno
POSTGREST_URL = os.getenv("POSTGREST_URL")
if not POSTGREST_URL:
    console.print(
        "[bold red]Error: POSTGREST_URL no está definida en las variables de entorno[/bold red]"
    )
    exit(1)

# Obtener credenciales de Cloudflare Access
CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

if not all([CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET]):
    console.print(
        "[bold yellow]Advertencia: CF_ACCESS_CLIENT_ID o CF_ACCESS_CLIENT_SECRET no están definidas en las variables de entorno.[/bold yellow]"
    )
    console.print(
        "[bold yellow]Las consultas no incluirán autenticación de Cloudflare Access.[/bold yellow]"
    )

# Configuración de los headers para PostgREST
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Prefer": "return=representation",
}

# Agregar headers de Cloudflare Access si están disponibles
if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
    headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
    headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET


def obtener_cotizaciones() -> List[Dict]:
    """
    Obtiene todas las cotizaciones.
    
    Returns:
        List[Dict]: Lista de cotizaciones.
    """
    try:
        response = requests.get(f"{POSTGREST_URL}/cotizacion", headers=headers)
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
    try:
        response = requests.get(
            f"{POSTGREST_URL}/cotizacion?id=eq.{id_cotizacion}", headers=headers
        )
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
    try:
        # Asegurar que tenga fecha de creación
        if "fecha_creacion" not in datos:
            datos["fecha_creacion"] = datetime.now().isoformat()
            
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
    try:
        # Remover id si está en los datos para evitar conflictos
        if "id" in datos:
            del datos["id"]
            
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
    try:
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
    Busca cotizaciones que coincidan con el término de búsqueda.
    
    Args:
        termino (str): Término de búsqueda.
        
    Returns:
        List[Dict]: Lista de cotizaciones que coinciden con la búsqueda.
    """
    try:
        # Buscar en varios campos
        query = f"?or=(numero.ilike.*{termino}*,descripcion.ilike.*{termino}*)"
        response = requests.get(f"{POSTGREST_URL}/cotizacion{query}", headers=headers)
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
        limite (Optional[int]): Límite de resultados a devolver.
        
    Returns:
        List[Dict]: Lista de cotizaciones del cliente.
    """
    try:
        # Construir la URL con el ID del cliente
        url = f"{POSTGREST_URL}/cotizacion?id_cliente=eq.{id_cliente}"
        
        # Agregar límite si se especifica
        if limite is not None:
            url += f"&limit={limite}"
            
        # Ordenar por fecha de creación descendente
        url += "&order=fecha.desc"
        
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


# # Comandos CLI
# @click.group(help="Gestión de cotizaciones")
# def cotizaciones():
#     pass


# @cotizaciones.command(help="Listar todas las cotizaciones")
# def listar():
#     """Listar todas las cotizaciones."""
#     cotizaciones_list = obtener_cotizaciones()
#     mostrar_tabla_cotizaciones(cotizaciones_list)
    

# @cotizaciones.command(help="Mostrar detalles de una cotización")
# @click.argument("id", type=int)
# @click.option("--json", is_flag=True, help="Mostrar en formato JSON")
# def mostrar(id: int, json: bool):
#     """Mostrar detalles de una cotización específica."""
#     cotizacion = obtener_cotizacion(id)
    
#     if not cotizacion:
#         console.print(f"[bold red]No se encontró la cotización con ID {id}[/bold red]")
#         return
        
#     if json:
#         console.print(json.dumps(cotizacion, indent=2))
#     else:
#         # Mostrar detalles en formato tabla
#         tabla = Table(title=f"Detalles de Cotización #{id}", show_header=True)
#         tabla.add_column("Campo", style="green")
#         tabla.add_column("Valor", style="yellow")
        
#         # Añadir filas con los datos
#         for campo, valor in cotizacion.items():
#             # Formatear fechas
#             if campo.startswith("fecha_") and valor:
#                 try:
#                     fecha_obj = datetime.fromisoformat(valor.replace("Z", "+00:00"))
#                     valor = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
#                 except (ValueError, TypeError):
#                     pass
                    
#             # Formatear valores monetarios
#             if campo in ["total", "subtotal", "impuestos"]:
#                 if valor is not None:
#                     valor = f"{valor:,.2f} €"
                    
#             tabla.add_row(campo, str(valor) if valor is not None else "")
            
#         console.print(tabla)


# @cotizaciones.command(help="Buscar cotizaciones")
# @click.argument("termino")
# def buscar(termino: str):
#     """Buscar cotizaciones que coincidan con el término."""
#     resultados = buscar_cotizaciones(termino)
#     mostrar_tabla_cotizaciones(resultados)


# @cotizaciones.command(help="Crear una nueva cotización")
# @click.option("--cliente-id", required=True, type=int, help="ID del cliente")
# @click.option("--numero", required=True, help="Número de cotización")
# @click.option("--descripcion", required=True, help="Descripción de la cotización")
# @click.option("--total", type=float, default=0.0, help="Total de la cotización")
# def crear(cliente_id: int, numero: str, descripcion: str, total: float):
#     """Crear una nueva cotización."""
#     datos = {
#         "cliente_id": cliente_id,
#         "numero": numero,
#         "descripcion": descripcion,
#         "total": total,
#         "estado": "PENDIENTE",
#         "fecha_creacion": datetime.now().isoformat()
#     }
    
#     cotizacion = crear_cotizacion(datos)
    
#     if cotizacion:
#         console.print(f"[bold green]Cotización creada con éxito. ID: {cotizacion.get('id')}[/bold green]")
#         mostrar_tabla_cotizaciones([cotizacion])
#     else:
#         console.print("[bold red]Error al crear la cotización.[/bold red]")


# @cotizaciones.command(help="Actualizar una cotización existente")
# @click.argument("id", type=int)
# @click.option("--cliente-id", type=int, help="ID del cliente")
# @click.option("--numero", help="Número de cotización")
# @click.option("--descripcion", help="Descripción de la cotización")
# @click.option("--estado", help="Estado de la cotización")
# @click.option("--total", type=float, help="Total de la cotización")
# def actualizar(id: int, cliente_id: Optional[int], numero: Optional[str], 
#               descripcion: Optional[str], estado: Optional[str], total: Optional[float]):
#     """Actualizar una cotización existente."""
#     # Verificar que la cotización existe
#     cotizacion_existente = obtener_cotizacion(id)
#     if not cotizacion_existente:
#         console.print(f"[bold red]No se encontró la cotización con ID {id}[/bold red]")
#         return
        
#     # Construir datos a actualizar
#     datos = {}
#     if cliente_id is not None:
#         datos["cliente_id"] = cliente_id
#     if numero is not None:
#         datos["numero"] = numero
#     if descripcion is not None:
#         datos["descripcion"] = descripcion
#     if estado is not None:
#         datos["estado"] = estado
#     if total is not None:
#         datos["total"] = total
        
#     # Si no hay datos para actualizar
#     if not datos:
#         console.print("[yellow]No se especificaron datos para actualizar.[/yellow]")
#         return
        
#     # Actualizar cotización
#     exito = actualizar_cotizacion(id, datos)
    
#     if exito:
#         console.print(f"[bold green]Cotización actualizada con éxito.[/bold green]")
#         # Mostrar cotización actualizada
#         cotizacion_actualizada = obtener_cotizacion(id)
#         if cotizacion_actualizada:
#             mostrar_tabla_cotizaciones([cotizacion_actualizada])
#     else:
#         console.print("[bold red]Error al actualizar la cotización.[/bold red]")


# @cotizaciones.command(help="Eliminar una cotización")
# @click.argument("id", type=int)
# @click.option("--confirmar", is_flag=True, help="Confirmar eliminación sin preguntar")
# def eliminar(id: int, confirmar: bool):
#     """Eliminar una cotización."""
#     # Verificar que la cotización existe
#     cotizacion = obtener_cotizacion(id)
#     if not cotizacion:
#         console.print(f"[bold red]No se encontró la cotización con ID {id}[/bold red]")
#         return
        
#     # Confirmar eliminación
#     if not confirmar:
#         console.print(f"[bold yellow]¿Está seguro de eliminar la cotización #{cotizacion.get('numero')} (ID: {id})?[/bold yellow]")
#         confirmacion = click.confirm("¿Confirmar eliminación?", default=False)
#         if not confirmacion:
#             console.print("[yellow]Operación cancelada.[/yellow]")
#             return
            
#     # Eliminar cotización
#     exito = eliminar_cotizacion(id)
    
#     if exito:
#         console.print(f"[bold green]Cotización eliminada con éxito.[/bold green]")
#     else:
#         console.print("[bold red]Error al eliminar la cotización.[/bold red]")


# if __name__ == "__main__":
#     cotizaciones()
