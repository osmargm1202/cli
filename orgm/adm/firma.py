# -*- coding: utf-8 -*-
from typing import Optional
from pathlib import Path
from rich import print

# Initialize variables as None at module level
FIRMA_URL = None
CF_ACCESS_CLIENT_ID = None
CF_ACCESS_CLIENT_SECRET = None

def initialize():
    """Initialize variables that were previously at module level"""
    global FIRMA_URL, CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET
    
    import os
    from dotenv import load_dotenv
    from orgm.apis.header import get_headers_json
    
    load_dotenv(override=True)
    
    # Obtener variables de entorno necesarias
    FIRMA_URL = os.getenv("FIRMA_URL")
    
    # Obtener headers usando la función centralizada
    headers = get_headers_json()
    if "CF-Access-Client-Id" in headers and "CF-Access-Client-Secret" in headers:
        CF_ACCESS_CLIENT_ID = headers["CF-Access-Client-Id"]
        CF_ACCESS_CLIENT_SECRET = headers["CF-Access-Client-Secret"]
    else:
        # Fallback al método anterior
        CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
        CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")
    
    if not all([FIRMA_URL, CF_ACCESS_CLIENT_ID, CF_ACCESS_CLIENT_SECRET]):
        print(
            "[bold red]Error: Se requieren las variables de entorno FIRMA_URL, CF_ACCESS_CLIENT_ID y CF_ACCESS_CLIENT_SECRET[/bold red]"
        )
        return False
    
    return True


def firmar_pdf(
    archivo_pdf: str, x1: int, y1: int, ancho: int, archivo_salida: Optional[str] = None
) -> Optional[str]:
    """
    Firma un archivo PDF usando el servicio protegido con Cloudflare Access.

    Args:
        archivo_pdf: Ruta al archivo PDF a firmar
        x1: Posición X donde colocar la firma
        y1: Posición Y donde colocar la firma
        ancho: Ancho de la firma
        archivo_salida: Nombre del archivo de salida (opcional)

    Returns:
        Ruta al archivo PDF firmado o None si ocurre un error
    """
    # Ensure initialization is done
    if FIRMA_URL is None:
        initialize()
    
    import requests
    
    try:
        # Verificar que el archivo exista
        pdf_path = Path(archivo_pdf)
        if not pdf_path.exists():
            print(f"[bold red]Error: El archivo {archivo_pdf} no existe[/bold red]")
            return None

        # Si no se especifica archivo de salida, usar el nombre del original con prefijo
        if not archivo_salida:
            archivo_salida = f"firmado_{pdf_path.name}"

        # URL del servicio de firma
        url = f"{FIRMA_URL}/firmar-pdf/"

        # Headers con autenticación de Cloudflare Access
        headers = {
            "accept": "application/pdf",
            "CF-Access-Client-Id": CF_ACCESS_CLIENT_ID,
            "CF-Access-Client-Secret": CF_ACCESS_CLIENT_SECRET,
        }

        # Datos del formulario
        files = {"file": (pdf_path.name, open(pdf_path, "rb"), "application/pdf")}
        data = {"x1": str(x1), "y1": str(y1), "ancho": str(ancho)}

        # Realizar la petición
        response = requests.post(url, headers=headers, files=files, data=data)

        # Verificar respuesta
        response.raise_for_status()

        # Guardar el archivo PDF firmado
        with open(archivo_salida, "wb") as f:
            f.write(response.content)

        print(
            f"[bold green]PDF firmado correctamente, guardado como {archivo_salida}[/bold green]"
        )
        return archivo_salida

    except Exception as e:
        print(f"[bold red]Error al firmar PDF: {e}[/bold red]")
        return None


def seleccionar_y_firmar_pdf(x1: int = 100, y1: int = 100, ancho: int = 200):
    """
    Abre un diálogo para seleccionar un archivo PDF, lo firma y guarda
    el resultado en la misma carpeta con el sufijo "signed".

    Args:
        x1: Posición X donde colocar la firma (default: 100)
        y1: Posición Y donde colocar la firma (default: 100)
        ancho: Ancho de la firma (default: 200)

    Returns:
        Ruta al archivo PDF firmado o None si ocurre un error
    """
    # Ensure initialization is done
    if FIRMA_URL is None:
        initialize()
        
    try:
        # Importar Kivy
        from kivy.app import App
        from kivy.lang import Builder
        from kivy.uix.boxlayout import BoxLayout
        import os


        # Definir la interfaz con Kivy Language
        kv_string = """
<FileChooserScreen>:
    orientation: 'vertical'
    spacing: 10
    padding: 10
    
    Label:
        text: 'Seleccione un archivo PDF para firmar'
        size_hint_y: None
        height: '40dp'
    
    FileChooserListView:
        id: file_chooser
        filters: ["*.pdf", "*.PDF"]
        path: app.get_start_dir()
        size_hint_y: 0.8
        
    BoxLayout:
        size_hint_y: None
        height: '50dp'
        spacing: 10
        
        Button:
            text: 'Cancelar'
            on_release: app.cancel()
            
        Button:
            text: 'Seleccionar'
            on_release: app.select(file_chooser.selection)
"""

        # Crear clase para la pantalla de selección
        class FileChooserScreen(BoxLayout):
            pass

        # Aplicación Kivy
        class PDFChooserApp(App):
            def __init__(self, **kwargs):
                super(PDFChooserApp, self).__init__(**kwargs)
                self.selected_file = None
                Builder.load_string(kv_string)

            def build(self):
                return FileChooserScreen()

            def get_start_dir(self):
                # Iniciar en el directorio de inicio del usuario
                return os.path.expanduser("~")

            def select(self, selection):
                if selection and len(selection) > 0:
                    self.selected_file = selection[0]
                self.stop()

            def cancel(self):
                self.selected_file = None
                self.stop()

        # Crear y ejecutar la aplicación
        app = PDFChooserApp(title="Seleccionar PDF")
        app.run()

        # Obtener el archivo seleccionado
        archivo_pdf = app.selected_file

        if not archivo_pdf:
            print(
                "[yellow]Operación cancelada: No se seleccionó ningún archivo[/yellow]"
            )
            return None

        # Crear el nombre del archivo de salida con sufijo "signed"
        pdf_path = Path(archivo_pdf)
        nombre_base = pdf_path.stem  # Obtiene el nombre sin extensión
        archivo_salida = pdf_path.parent / f"{nombre_base}_signed{pdf_path.suffix}"

        # Llamar a la función de firma
        return firmar_pdf(archivo_pdf, x1, y1, ancho, str(archivo_salida))

    except ImportError:
        print(
            "[bold red]Error: Se requiere el paquete kivy. Instale con pip install kivy[/bold red]"
        )
        return None
    except Exception as e:
        print(f"[bold red]Error al seleccionar o firmar PDF: {e}[/bold red]")
        return None


if __name__ == "__main__":
    seleccionar_y_firmar_pdf()
