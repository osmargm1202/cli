# -*- coding: utf-8 -*-
import questionary
from rich.console import Console
import typer
import sys

# Crear consola para salida con Rich
console = Console()

def ai_menu():
    """Menú interactivo para comandos relacionados con IA."""
    
    console.print("[bold blue]===== Menú Inteligencia Artificial =====[/bold blue]")
    
    opciones = [
        {"name": "💬 Enviar prompt a la IA", "value": "prompt"},
        {"name": "📋 Listar configuraciones de IA", "value": "configs"},
        {"name": "📤 Subir configuración", "value": "upload"},
        {"name": "✏️ Crear nueva configuración", "value": "create"},
        {"name": "🔄 Editar configuración existente", "value": "edit"},
        {"name": "⬅️ Volver al menú principal", "value": "volver"},
        {"name": "❌ Salir", "value": "exit"}
    ]
    
    try:
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in opciones],
            use_indicator=True
        ).ask()
        
        if seleccion is None:  # Usuario presionó Ctrl+C
            return "exit"
            
        # Obtener el valor asociado a la selección
        comando = next(opcion["value"] for opcion in opciones if opcion["name"] == seleccion)
        
        if comando == "exit":
            console.print("[yellow]Saliendo...[/yellow]")
            sys.exit(0)
        elif comando == "volver":
            from orgm.commands.menu import menu_principal
            return menu_principal()
        elif comando == "prompt":
            # Solicitar el prompt y la configuración
            prompt_text = questionary.text(
                "Ingrese su prompt para la IA:",
                multiline=True
            ).ask()
            
            if not prompt_text:
                console.print("[yellow]Operación cancelada: No se especificó un prompt[/yellow]")
                return ai_menu()
                
            # Mostrar las configuraciones disponibles
            from orgm.commands.ai import ai_configs
            console.print("\nConfiguraciones disponibles:")
            ai_configs()
            
            config_name = questionary.text(
                "Nombre de la configuración a usar (default para usar la predeterminada):",
                default="default"
            ).ask()
            
            # Ejecutar el comando de prompt
            from orgm.commands.ai import ai_prompt
            ai_prompt([prompt_text], config_name)
            
            return ai_menu()  # Volver al mismo menú después
            
        elif comando == "configs":
            # Listar configuraciones
            from orgm.commands.ai import ai_configs
            ai_configs()
            
            # Esperar a que el usuario presione Enter para continuar
            input("\nPresione Enter para continuar...")
            return ai_menu()
            
        elif comando == "upload":
            # Subir configuración
            from orgm.commands.ai import ai_config_upload
            ai_config_upload()
            
            # Esperar a que el usuario presione Enter para continuar
            input("\nPresione Enter para continuar...")
            return ai_menu()
            
        elif comando == "create":
            # Crear configuración
            from orgm.commands.ai import ai_config_create
            ai_config_create()
            
            # Esperar a que el usuario presione Enter para continuar
            input("\nPresione Enter para continuar...")
            return ai_menu()
            
        elif comando == "edit":
            # Editar configuración
            from orgm.commands.ai import ai_config_edit
            ai_config_edit()
            
            # Esperar a que el usuario presione Enter para continuar
            input("\nPresione Enter para continuar...")
            return ai_menu()
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"

if __name__ == "__main__":
    # Para pruebas
    ai_menu() 