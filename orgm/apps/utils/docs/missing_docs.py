import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from orgm.apps.utils.docs.leer_csv import leer_csv

console = Console(record=True)

def missing_documents(datos):
    """
    Revisa las carpetas de memorias (PDF y DOCX) y devuelve una lista de 
    documentos que no tienen archivos en alguna de las carpetas.
    
    Args:
        datos (list): Lista de diccionarios con los datos de los documentos
        
    Returns:
        list: Lista de diccionarios con los documentos que faltan
    """
    documentos_faltantes = []
    
    for dato in datos:
        # Verificar que existan las claves necesarias
        if 'op_dir_memorias_docx' not in dato or 'op_dir_memorias_pdf' not in dato:
            console.print(f"Error: Faltan claves en el dato {dato['codigo'] if 'codigo' in dato else 'desconocido'}", 
                         style="bold red")
            continue
        
        # Buscar archivos en las carpetas
        archivos_docx = [f for f in os.listdir(dato['op_dir_memorias_docx']) 
                        if f.endswith('.docx')] if os.path.exists(dato['op_dir_memorias_docx']) else []
        archivos_pdf = [f for f in os.listdir(dato['op_dir_memorias_pdf']) 
                       if f.endswith('.pdf')] if os.path.exists(dato['op_dir_memorias_pdf']) else []
        
        # Si no hay archivos en ninguna de las carpetas, agregar a la lista
        if not archivos_docx and not archivos_pdf:
            documentos_faltantes.append(dato)
    
    # Ordenar por disciplina y luego por número
    documentos_faltantes.sort(key=lambda x: (x.get('disciplina', ''), x.get('numero', '')))
    
    return documentos_faltantes

def mostrar_documentos_faltantes(datos, ruta_html: str):
    """
    Muestra una tabla con los documentos que faltan en las carpetas.
    
    Args:
        datos (list): Lista de diccionarios con los datos de los documentos
    
    Returns:
        list: Lista de documentos faltantes
    """
    documentos_faltantes = missing_documents(datos)
    
    if not documentos_faltantes:
        console.print("Todos los documentos tienen archivos en alguna de las carpetas", style="bold green")
        return []
    
    # Organizar documentos por disciplina
    documentos_por_disciplina = {}
    for doc in documentos_faltantes:
        disciplina = doc.get('disciplina', 'SIN DISCIPLINA')
        if disciplina not in documentos_por_disciplina:
            documentos_por_disciplina[disciplina] = []
        documentos_por_disciplina[disciplina].append(doc)
    
    # Para cada disciplina, ordenar por número
    for disciplina in documentos_por_disciplina:
        documentos_por_disciplina[disciplina].sort(key=lambda x: x.get('numero', ''))
    
    # Mostrar tabla por disciplina
    console.print("\n[bold blue]== DOCUMENTOS FALTANTES POR DISCIPLINA ==[/bold blue]\n")
    
    # Crear una consola específica para guardar el HTML

    for disciplina, documentos in sorted(documentos_por_disciplina.items()):
        table = Table(title=f"Disciplina: {disciplina}")
        table.add_column("Código", style="cyan")
        table.add_column("Número", style="yellow")
        table.add_column("Nombre", style="green")
        table.add_column("Proyecto", style="magenta")
        
        for documento in documentos:
            table.add_row(
                documento.get('codigo', ''),
                documento.get('numero', ''),
                documento.get('nombre', ''),
                documento.get('proyecto', '')
            )
        
        console.print(table)
        console.print("\n")
    
    # Guardar HTML usando el método save_html de Rich
    html_dir = str(os.path.join(ruta_html, "documentos_faltantes.html")).strip("'").strip('"')
    console.save_html(html_dir)
    # text_dir = str(os.path.join(ruta_html, "documentos_faltantes.text")).strip("'").strip('"')
    # console.save_text(text_dir)
    # svg_dir = str(os.path.join(ruta_html, "documentos_faltantes.svg")).strip("'").strip('"')
    # console.save_svg(svg_dir, theme="github-dark")
    
    console.print(f"El reporte HTML ha sido guardado como '{html_dir}'", style="bold blue")
    
    # Devolvemos la lista plana para su uso en otras funciones
    return documentos_faltantes



