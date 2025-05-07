from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import Dict, Optional
from orgm.apps.adm.db import Cliente
from orgm.apps.adm.cliente.get_client import obtener_cliente
import typer
from orgm.stuff.spinner import spinner
from orgm.apps.adm.cliente.tipos import TipoFactura
from orgm.apps.adm.cliente.get_clients import mostrar_tabla_clientes

console = Console()


def actualizar_cliente(id_cliente: int, cliente_data: Dict) -> Optional[Cliente]:
    """Actualiza un cliente existente"""
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Cliente

    try:
        # Verificar que el cliente existe
        cliente_existente = obtener_cliente(id_cliente)
        if not cliente_existente:
            return None

        update_headers = headers.copy()
        update_headers["Prefer"] = "return=representation"

        response = requests.patch(
            f"{POSTGREST_URL}/cliente?id=eq.{id_cliente}",
            headers=update_headers,
            json=cliente_data,
            timeout=10,
        )
        response.raise_for_status()

        cliente_actualizado = Cliente.model_validate(response.json()[0])
        console.print(
            f"[bold green]Cliente actualizado correctamente: {cliente_actualizado.nombre}[/bold green]"
        )
        return cliente_actualizado
    except Exception as e:
        console.print(
            f"[bold red]Error al actualizar cliente {id_cliente}: {e}[/bold red]"
        )
        return None


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
    representante: Optional[str] = typer.Option(
        None, help="Nuevo nombre del representante"
    ),
    telefono_representante: Optional[str] = typer.Option(
        None, help="Nuevo teléfono del representante"
    ),
    extension_representante: Optional[str] = typer.Option(
        None, help="Nueva extensión del representante"
    ),
    celular_representante: Optional[str] = typer.Option(
        None, help="Nuevo celular del representante"
    ),
    correo_representante: Optional[str] = typer.Option(
        None, help="Nuevo correo del representante"
    ),
    tipo_factura: Optional[TipoFactura] = typer.Option(
        None, help="Nuevo tipo de factura"
    ),
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
        console.print("[bold green]Cliente actualizado con éxito.[/bold green]")
        with spinner(f"Obteniendo datos actualizados del cliente {id}..."):
            cliente_obj = obtener_cliente(id)
        if cliente_obj:
            mostrar_tabla_clientes([cliente_obj])
        else:
            console.print(
                "[yellow]No se pudo recuperar el cliente actualizado para mostrarlo.[/yellow]"
            )
    else:
        console.print(
            "[bold red]Error al actualizar el cliente (la API no devolvió datos).[/bold red]"
        )
