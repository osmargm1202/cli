import subprocess
import os
import questionary
from orgm.qstyle import custom_style_fancy
from rich.console import Console

console = Console()

def convertir_docx_a_pdf(ruta_docx: str, ruta_salida: str | None = None) -> str | None:
    """
    Convierte un archivo DOCX a PDF usando LibreOffice en la terminal.

    Args:
        ruta_docx: La ruta al archivo DOCX de entrada.
        ruta_salida: Directorio opcional donde se guardará el PDF. 
                     Si no se especifica, el PDF se guarda en el mismo directorio que el DOCX.

    Returns:
        La ruta al archivo PDF generado, o None si la conversión falla.
    """

    if not ruta_docx:
        # busca el primer archivo con extension .docx en el directorio actual
        archivos_docx = [f for f in os.listdir(os.getcwd()) if f.endswith(".docx")]
        if archivos_docx:
            ruta_docx = archivos_docx[0]
        else:
            console.print("No se encontró ningún archivo DOCX en el directorio actual.")
            return None
    
    directorio_salida = os.path.dirname(ruta_docx)

    if ruta_salida:
        directorio_salida = os.path.dirname(ruta_salida)

    # console.print(directorio_salida, style="bold red")
        

    comando = [
        "soffice",
        "--headless",
        "--convert-to",
        "pdf",
        ruta_docx,
        "--outdir",
        directorio_salida
    ]

    try:
        proceso = subprocess.run(comando, capture_output=True, text=True, check=True)
        # Renombrar el archivo PDF generado al nombre especificado en ruta_salida
        if ruta_salida:
            nombre_pdf_generado = os.path.splitext(os.path.basename(ruta_docx))[0] + '.pdf'
            ruta_pdf_generado = os.path.join(directorio_salida, nombre_pdf_generado)
            
            if os.path.exists(ruta_pdf_generado) and ruta_pdf_generado != ruta_salida:
                os.rename(ruta_pdf_generado, ruta_salida)
        if proceso.stderr:
            console.print(f"Errores de LibreOffice: {proceso.stderr}")
        
        if os.path.exists(ruta_salida):
            console.print(f"Archivo PDF generado exitosamente en: {ruta_salida}")
            return ruta_salida


    except subprocess.CalledProcessError as e:
        console.print(f"Error al ejecutar LibreOffice:")
        console.print(f"Comando: {' '.join(e.cmd)}")
        console.print(f"Código de retorno: {e.returncode}")
        console.print(f"Salida: {e.output}")
        console.print(f"Error: {e.stderr}")
        return None
    except FileNotFoundError:
        console.print("Error: El comando 'soffice' (LibreOffice) no fue encontrado. Asegúrate de que LibreOffice esté instalado y en el PATH del sistema.")
        return None


def solicitar_datos_conversion():
    """
    Solicita al usuario los datos necesarios para la conversión de DOCX a PDF mediante questionary
    
    Returns:
        tuple: (ruta_docx, directorio_salida)
    """

    
    ruta_docx = questionary.path(
        "Seleccione el archivo DOCX a convertir:",
        validate=lambda text: text.endswith('.docx'),
        style=custom_style_fancy,
    ).ask()

    usar_mismo_dir = questionary.confirm(
        "¿Desea guardar el PDF en el mismo directorio del DOCX?",
        default=True,
        style=custom_style_fancy
    ).ask()

    directorio_salida = None
    if not usar_mismo_dir:
        directorio_salida = questionary.path(
            "Seleccione el directorio donde guardar el PDF:",
            only_directories=True,
            style=custom_style_fancy
        ).ask()

    return ruta_docx, directorio_salida


def docx_pdf():
    ruta_docx, directorio_salida = solicitar_datos_conversion()
    pdf_generado = convertir_docx_a_pdf(ruta_docx, directorio_salida)
    return pdf_generado
