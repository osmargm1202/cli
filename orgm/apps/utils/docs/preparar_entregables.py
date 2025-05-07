
import os
import shutil
from rich.console import Console
from rich.table import Table

console = Console() 


def copiar_entregables(datos, ruta_destino: str):
    """
    Verifica los archivos en el directorio de entregables PDF y los copia 
    a una carpeta de entrega organizada por revisión y disciplina.
    
    Args:
        datos (list): Lista de diccionarios con los datos de los documentos
        ruta_destino (str): Ruta base donde se crearán las carpetas de entrega
        
    Returns:
        dict: Diccionario con información de los documentos copiados por revisión
    """
    # Crear un diccionario para registrar los documentos copiados por revisión
    documentos_por_revision = {}
    
    for dato in datos:
        # Verificar que exista la clave necesaria para el directorio de entregables
        if 'op_dir_entregables_pdf' not in dato:
            continue
        
        # Obtener la revisión del documento (valor por defecto es "0" si no existe)
        revision = dato.get('revision', '0')
        
        # Obtener la disciplina del documento (valor por defecto es "SIN DISCIPLINA" si no existe)
        disciplina = dato.get('disciplina', 'SIN DISCIPLINA')
        
        # Nombre de la carpeta de destino para esta revisión
        carpeta_revision = os.path.join(ruta_destino, f"Entrega {revision}")
        
        # Nombre de la carpeta de disciplina dentro de la carpeta de revisión
        carpeta_disciplina = os.path.join(carpeta_revision, disciplina)
        
        # Ruta completa del archivo entregable
        ruta_entregable = os.path.join(dato['op_dir_entregables_pdf'], dato['nombre_pdf'])
        
        # Verificar si existe el archivo entregable
        if os.path.exists(ruta_entregable):
            # Crear la carpeta de disciplina dentro de la revisión si no existe
            os.makedirs(carpeta_disciplina, exist_ok=True)
            
            # Ruta de destino para la copia
            ruta_destino_archivo = os.path.join(carpeta_disciplina, dato['nombre_pdf'])
            
            try:
                # Copiar el archivo
                shutil.copy2(ruta_entregable, ruta_destino_archivo)
                
                # Registrar en el diccionario de documentos copiados
                if revision not in documentos_por_revision:
                    documentos_por_revision[revision] = {}
                
                if disciplina not in documentos_por_revision[revision]:
                    documentos_por_revision[revision][disciplina] = []
                
                documentos_por_revision[revision][disciplina].append({
                    'codigo': dato.get('codigo', ''),
                    'numero': dato.get('numero', ''),
                    'nombre': dato.get('nombre', ''),
                    'disciplina': disciplina,
                    'proyecto': dato.get('proyecto', ''),
                    'archivo': dato['nombre_pdf']
                })
                
                console.print(f"Archivo copiado: {dato['nombre_pdf']} -> Entrega {revision}/{disciplina}", style="green")
            except Exception as e:
                console.print(f"Error al copiar {dato['nombre_pdf']}: {str(e)}", style="bold red")
    
    # Mostrar resumen de archivos copiados por revisión y disciplina
    if documentos_por_revision:
        console.print("\n[bold blue]== RESUMEN DE ARCHIVOS COPIADOS POR REVISIÓN Y DISCIPLINA ==[/bold blue]\n")
        
        for revision, disciplinas in sorted(documentos_por_revision.items()):
            console.print(f"[bold cyan]Revisión: {revision}[/bold cyan]")
            
            total_revision = 0
            for disciplina, documentos in sorted(disciplinas.items()):
                table = Table(title=f"Disciplina: {disciplina}")
                table.add_column("Código", style="cyan")
                table.add_column("Número", style="yellow")
                table.add_column("Nombre", style="green")
                
                for documento in documentos:
                    table.add_row(
                        documento.get('codigo', ''),
                        documento.get('numero', ''),
                        documento.get('nombre', '')
                    )
                
                console.print(table)
                console.print(f"Total en disciplina {disciplina}: {len(documentos)}")
                total_revision += len(documentos)
            
            console.print(f"\n[bold green]Total de documentos copiados en revisión {revision}: {total_revision}[/bold green]\n")
            console.print(f"Ubicación: {os.path.join(ruta_destino, f'Entrega {revision}')}\n")
    else:
        console.print("No se encontraron archivos entregables para copiar.", style="bold yellow")
    
    return documentos_por_revision
