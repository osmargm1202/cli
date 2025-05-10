import os
import shutil
from rich.console import Console

console = Console()

def copiar_documento(datos, indice_documento, ruta_archivo, reemplazar=False):
    """
    Copia un archivo a la carpeta correspondiente (PDF o DOCX) y lo renombra.
    
    Args:
        datos (list): Lista de diccionarios con los datos de los documentos
        indice_documento (int): Índice del documento en la lista
        ruta_archivo (str): Ruta del archivo a copiar
        reemplazar (bool): Si es True, reemplazará el archivo si existe
        
    Returns:
        bool: True si se copió correctamente, False en caso contrario
    """
    try:
        if indice_documento < 0 or indice_documento >= len(datos):
            console.print("Índice de documento inválido", style="bold red")
            return False
        
        documento = datos[indice_documento]
        ruta_archivo = ruta_archivo.strip().strip('"').strip("'")
        
        if not os.path.exists(ruta_archivo):
            console.print(f"El archivo {ruta_archivo} no existe", style="bold red")
            return False
        
        # Determinar si es PDF o DOCX
        extension = os.path.splitext(ruta_archivo)[1].lower()
        
        if extension == '.pdf':
            carpeta_destino = documento['op_dir_memorias_pdf']
            nombre_destino = documento['nombre_pdf']
        elif extension == '.docx':
            carpeta_destino = documento['op_dir_memorias_docx']
            nombre_destino = documento['nombre_docx']
        else:
            console.print(f"Formato de archivo no soportado: {extension}", style="bold red")
            return False
        
        # Crear carpeta si no existe
        os.makedirs(carpeta_destino, exist_ok=True)
        
        # Ruta completa del archivo destino
        ruta_destino = os.path.join(carpeta_destino, nombre_destino)
        
        # Verificar si el archivo existe y si no estamos reemplazando
        if os.path.exists(ruta_destino) and not reemplazar:
            console.print(f"El archivo ya existe en: {ruta_destino}", style="bold red")
            confirmar = input(f"¿Desea reemplazarlo? (s/n): ").lower()
            if confirmar != 's':
                console.print("Operación cancelada", style="bold yellow")
                return False
        
        # Copiar archivo (reemplazándolo si existe)
        shutil.copy2(ruta_archivo, ruta_destino)
        
        if reemplazar and os.path.exists(ruta_destino):
            console.print(f"Archivo reemplazado exitosamente en: {ruta_destino}", style="bold green")
        else:
            console.print(f"Archivo copiado a: {ruta_destino}", style="bold green")
        return True
        
    except Exception as e:
        console.print(f"Error al copiar el archivo: {str(e)}", style="bold red")
        return False 