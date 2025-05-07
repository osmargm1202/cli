from orgm.stuff.initialize_postgrest import initialize
from rich.console import Console
from typing import Dict, Optional
from orgm.apps.adm.db import Cliente
from orgm.apps.adm.cliente.max_id import obtener_id_maximo
import typer
from orgm.apps.adm.cliente.tipos import TipoFactura
from orgm.apps.adm.cliente.get_clients import mostrar_tabla_clientes
from orgm.stuff.spinner import spinner

console = Console()


def crear_cliente(cliente_data: Dict) -> Optional[Cliente]:
    """Crea un nuevo cliente"""
    # Asegurar que las variables estén inicializadas
    POSTGREST_URL, headers = initialize()

    import requests
    from orgm.apps.adm.db import Cliente

    try:
        # Validar datos mínimos requeridos
        if not cliente_data.get("nombre"):
            console.print(
                "[bold red]Error: El nombre del cliente es obligatorio[/bold red]"
            )
            return None

        # Asignar ID si no está definido
        if "id" not in cliente_data:
            cliente_data["id"] = obtener_id_maximo()

        response = requests.post(
            f"{POSTGREST_URL}/cliente", headers=headers, json=cliente_data, timeout=10
        )
        response.raise_for_status()

        nuevo_cliente = Cliente.model_validate(response.json()[0])
        console.print(
            f"[bold green]Cliente creado correctamente con ID: {nuevo_cliente.id}[/bold green]"
        )
        return nuevo_cliente
    except Exception as e:
        console.print(f"[bold red]Error al crear cliente: {e}[/bold red]")
        return None


def crear(
    nombre: str = typer.Option(..., help="Nombre del cliente", prompt=True),
    numero: str = typer.Option(..., help="Número/NIF del cliente", prompt=True),
    nombre_comercial: Optional[str] = typer.Option(
        None, help="Nombre comercial del cliente"
    ),
    email: Optional[str] = typer.Option(None, help="Email del cliente"),
    telefono: Optional[str] = typer.Option(None, help="Teléfono del cliente"),
    direccion: Optional[str] = typer.Option(None, help="Dirección del cliente"),
    ciudad: Optional[str] = typer.Option(None, help="Ciudad del cliente"),
    provincia: Optional[str] = typer.Option(None, help="Provincia del cliente"),
    representante: Optional[str] = typer.Option(None, help="Nombre del representante"),
    telefono_representante: Optional[str] = typer.Option(
        None, help="Teléfono del representante"
    ),
    extension_representante: Optional[str] = typer.Option(
        None, help="Extensión del representante"
    ),
    celular_representante: Optional[str] = typer.Option(
        None, help="Celular del representante"
    ),
    correo_representante: Optional[str] = typer.Option(
        None, help="Correo del representante"
    ),
    tipo_factura: TipoFactura = typer.Option(TipoFactura.NCFC, help="Tipo de factura"),
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
        id_cliente = getattr(cliente_obj, "id", cliente_obj.get("id", "N/A"))
        console.print(
            f"[bold green]Cliente creado con éxito. ID: {id_cliente}[/bold green]"
        )
        mostrar_tabla_clientes([cliente_obj])
    else:
        console.print("[bold red]Error al crear el cliente.[/bold red]")
