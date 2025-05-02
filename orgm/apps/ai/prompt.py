import typer
from typing import List, Optional
from rich.console import Console
import questionary
from orgm.apps.ai.generate import generate_text
from orgm.apps.ai.configs_select import ai_configs_select
import questionary
console = Console()


def ai_prompt(
    prompt: List[str] = typer.Argument(..., help="Texto que describe la solicitud a la IA"),
    config_name_opt: Optional[str] = typer.Option(
        None, "-c", "--config", help="Nombre de la configuración de IA a usar directamente."
    )
) -> None:
    """Genera texto usando el servicio de IA"""
    # Verificar si 'prompt' es una lista antes de unir
    if isinstance(prompt, list):
        prompt_text = " ".join(prompt).strip()
    else:
        # Si no es una lista, significa que no se proporcionaron argumentos
        prompt_text = questionary.text("Ingresa tu solicitud para la IA:").ask()

    # Añadir validación por si el usuario cancela la entrada de texto
    if not prompt_text:
        console.print("[bold yellow]No se ingresó ninguna solicitud. Operación cancelada.[/bold yellow]")
        return

    # Obtener configuraciones disponibles desde la API
    config_choices = ai_configs_select()

    # Verificar si se obtuvieron las configuraciones
    if config_choices is None:
        # El error ya se imprimió dentro de get_available_configs_from_api
        console.print("[bold red]No se pudieron obtener las configuraciones de IA desde la API.[/bold red]")
        return
    if not config_choices:
        console.print("[bold yellow]No hay configuraciones de IA disponibles en el servicio.[/bold yellow]")
        return

    config_name = None # Inicializar config_name

    # Usar la configuración de la opción si se proporciona y es válida

    print(config_name_opt == typer.Option)

    if type(config_name_opt) == str:
        if config_name_opt in config_choices:
            config_name = config_name_opt
        else:
            console.print(f"[bold red]Error: La configuración '{config_name_opt}' no existe.[/bold red]")
            console.print(f"Configuraciones disponibles: {', '.join(config_choices)}")
            return # Salir si la configuración proporcionada no es válida

    # Si no se proporcionó una configuración válida con -c, preguntar al usuario
    if config_name is None:
        # Asumiendo que la configuración por defecto se llama 'default'
        default_choice = "default" if "default" in config_choices else config_choices[0] if config_choices else None

        if default_choice is None:
            console.print("[bold red]No hay configuraciones disponibles para seleccionar.[/bold red]")
            return

        config_name = questionary.select(
            "Selecciona la configuración de IA a usar:",
            choices=config_choices,
            default=default_choice
        ).ask()

    # Si config_name sigue siendo None (el usuario canceló questionary)
    if config_name is None:
        console.print("[bold yellow]Operación cancelada.[/bold yellow]")
        return

    # Generar texto usando la configuración seleccionada o proporcionada
    resultado = generate_text(prompt_text, config_name)
    if resultado:
        # Mostrar la respuesta devuelta por la IA progresivamente para simular streaming
        console.print("[bold green]Respuesta IA:[/bold green] ", end="")
        for char in str(resultado):
            console.print(char, end="")
        console.print()

if __name__ == "__main__":
    ai_prompt()
    #ai_prompt(config_name_opt="terminal")