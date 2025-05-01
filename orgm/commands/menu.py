# -*- coding: utf-8 -*-
import questionary
from rich.console import Console
import typer
import os
import subprocess
from pathlib import Path

# Importar el módulo de búsqueda de RNC
from orgm.apps.rnc_app import rnc_app

# Crear consola para salida con Rich
console = Console()

def menu_principal():
    """Muestra un menú interactivo para los comandos principales de orgm."""
    console.print("[bold blue]===== ORGM CLI - Menú Principal =====[/bold blue]")
    
    # Definimos las categorías de comandos disponibles

    main_opciones = [
        {"name": "🧩 Administración", "value": "adm"},
        {"name": "🧮 Cálculos", "value": "calc"},
        {"name": "🔑 Confituracion", "value": "cfg"},
        {"name": "🔍 Utilidades", "value": "util"},
        {"name": "❓ Ayuda", "value": "help"},
        {"name": "❌ Salir", "value": "exit"}

    ]

    administracion = [
        {"name": "🧩 Clientes", "value": "client"},
        {"name": "📋 Proyectos", "value": "project"},
        {"name": "💰 Cotizaciones", "value": "quotation"},
        {"name": "💰 Presupuestos", "value": "presupuesto"},
        {"name": "💵 Pagos", "value": "payment"},
        {"name": "💰 Facturas de Venta", "value": "factura_venta"},
        {"name": "💰 Facturas de Compra", "value": "factura_compra"},
        {"name": "💰 Facturas de Compras a Personas", "value": "cfactura_compra_persona"},
        {"name": "💰 Facturas de Compras Menores", "value": "cfactura_compra_menor"},
        {"name": "🧾 Comprobantes", "value": "comprobante"},
        {"name": "👤 Personas Fisicas", "value": "persona_fisica"},
        {"name": "🏢 Proveedores", "value": "proveedor"},
        {"name": "🏢 Empleados", "value": "empleado"},
        {"name": "🔄 Volver al menú principal", "value": "main-menu"},
        
    ]

    calculos = [
        {"name": "🧮 Calculo de Breaker", "value": "breaker"},
        {"name": "🧮 Calculo de Cable", "value": "cable"},
        {"name": "🧮 Calculo de Sistema de Puesta a Tierra", "value": "spt"},
        {"name": "🔄 Volver al menú principal", "value": "main-menu"},
    ]

    configuracion = [
        {"name": "🔑 Variables de entorno", "value": "env"},
        {"name": "🔄 Volver al menú principal", "value": "main-menu"},
    ]
    

    utilidades = [
        {"name": "🐳 Docker", "value": "docker"},
        {"name": "📄 Operaciones PDF", "value": "pdf"},
        {"name": "🔍 Buscar empresa", "value": "find-company"},
        {"name": "💱 Tasa de divisa", "value": "currency-rate"},
        {"name": "🔄 Actualizar", "value": "update"},
        {"name": "⚙️ Verificar URLs", "value": "check"},
        {"name": "🤖 Inteligencia Artificial", "value": "ai"},
        {"name": "🔄 Volver al menú principal", "value": "main-menu"},
    ]

    seleccion = questionary.select(
                "Seleccione una opción:",
                choices=[opcion["name"] for opcion in main_opciones],
                use_indicator=True,
                use_shortcuts=True
            ).ask()
    
    if seleccion is None:  # Usuario presionó Ctrl+C
        return "exit"
    
    comando = next(opcion["value"] for opcion in main_opciones if opcion["name"] == seleccion)
    
    if comando == "exit":
        console.print("[yellow]Saliendo...[/yellow]")
        return "exit"
    elif comando == "help":
        # Mostrar el contenido del archivo comandos.md
        mostrar_ayuda()
        return menu_principal()
    
    elif comando == "adm":
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in administracion],
            use_indicator=True,
            use_shortcuts=True
        ).ask()

        comando = next(opcion["value"] for opcion in administracion if opcion["name"] == seleccion)

    elif comando == "calc":
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in calculos],
            use_indicator=True,
            use_shortcuts=True
        ).ask()

        comando = next(opcion["value"] for opcion in calculos if opcion["name"] == seleccion)

    elif comando == "cfg":
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in configuracion],
            use_indicator=True,
            use_shortcuts=True
        ).ask() 

        comando = next(opcion["value"] for opcion in configuracion if opcion["name"] == seleccion)

    elif comando == "util":
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in utilidades],
            use_indicator=True,
            use_shortcuts=True
        ).ask()

        comando = next(opcion["value"] for opcion in utilidades if opcion["name"] == seleccion)

    if comando == "main-menu":
        
        return menu_principal()

    # Para comandos directos, ejecutar el comando y volver al menú
    print(f"Ejecutando comando: {comando}")
    try:
        # Usar subprocess.run en lugar de typer.run para ejecutar el comando como string
        result = subprocess.run(f"orgm {comando}", shell=True, check=True)
        if result.returncode != 0:
            console.print("[bold red]El comando falló con un código de error.[/bold red]")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error al ejecutar el comando: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error inesperado: {e}[/bold red]")
    return menu_principal()


def mostrar_ayuda():
    """Muestra el contenido del archivo comandos.md"""
    try:
        # Obtener la ruta del script actual
        script_dir = Path(__file__).parent
        # Construir la ruta al archivo comandos.md (está en el directorio principal de orgm)
        orgm_dir = script_dir.parent # Subir un nivel desde 'commands' a 'orgm'
        comandos_path = orgm_dir / "comandos.md"
        
        # Leer y mostrar el archivo
        with open(comandos_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        console.print(contenido)
    except Exception as e:
        console.print(f"[bold red]Error al mostrar la ayuda: {e}[/bold red]")

if __name__ == "__main__":
    # Para pruebas
    resultado = menu_principal()
    console.print(f"Seleccionado: {resultado}") 