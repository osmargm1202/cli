from rich.console import Console
import questionary
import subprocess
from orgm.apps.adm.cliente.find_clients import buscar_clientes
from orgm.apps.adm.cliente.get_client import obtener_cliente
from orgm.apps.adm.cliente.get_clients import obtener_clientes
from orgm.apps.adm.cliente.edit_client import actualizar_cliente
from orgm.apps.adm.cliente.form_client import formulario_cliente
from orgm.apps.adm.cliente.new_client import crear_cliente
from orgm.apps.adm.cliente.get_client import mostrar_detalle_cliente
from orgm.apps.adm.cliente.get_clients import mostrar_tabla_clientes
from orgm.stuff.spinner import spinner
from orgm.qstyle import custom_style_fancy

console = Console()


def menu():
    """Menú interactivo para comandos de cliente."""

    console.print("[bold blue]===== Menú de Cliente =====[/bold blue]")

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
        style=custom_style_fancy,
    ).ask()

    try:
        if accion == "Volver al menú principal":
            return "exit"
        elif accion == "client -h":
            subprocess.run(["orgm", "client", "-h"])
            return menu()
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
                    nombre_cliente = getattr(
                        nuevo_cliente_obj,
                        "nombre",
                        nuevo_cliente_obj.get("nombre", "N/A"),
                    )
                    console.print(
                        f"[bold green]Cliente creado: {nombre_cliente}[/bold green]"
                    )
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
                                cliente_actualizado = actualizar_cliente(
                                    id_cliente, datos_actualizados
                                )
                            if cliente_actualizado:
                                nombre_actualizado = getattr(
                                    cliente_actualizado, "nombre", "N/A"
                                )
                                console.print(
                                    f"[bold green]Cliente actualizado: {nombre_actualizado}[/bold green]"
                                )
                                mostrar_tabla_clientes([cliente_actualizado])
                            else:
                                console.print(
                                    "[bold red]No se pudo actualizar el cliente (la API no devolvió datos).[/bold red]"
                                )
                        else:
                            console.print("[yellow]Modificación cancelada.[/yellow]")
                    else:
                        console.print(
                            f"[bold red]Cliente con ID {id_cliente} no encontrado[/bold red]"
                        )
                except ValueError:
                    console.print(
                        "[bold red]ID inválido, debe ser un número.[/bold red]"
                    )
                except Exception as e:
                    console.print(
                        f"[bold red]Error inesperado al modificar cliente: {e}[/bold red]"
                    )
                    import traceback

                    traceback.print_exc()  # Para depuración

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
                        console.print(
                            f"[bold red]Cliente con ID {id_cliente} no encontrado[/bold red]"
                        )
                except ValueError:
                    console.print(
                        "[bold red]ID inválido, debe ser un número.[/bold red]"
                    )

    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"
