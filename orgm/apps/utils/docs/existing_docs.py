import os
from rich.console import Console
from rich.table import Table

console = Console(record=True)

def existing_documents(datos):
    """
    Revisa las carpetas de memorias (PDF y DOCX) y devuelve una lista de 
    documentos que tienen archivos en alguna de las carpetas.
    
    Args:
        datos (list): Lista de diccionarios con los datos de los documentos
        
    Returns:
        list: Lista de diccionarios con los documentos que existen
    """
    documentos_existentes = []
    
    for dato in datos:
        # Verificar que existan las claves necesarias
        if 'op_dir_memorias_docx' not in dato or 'op_dir_memorias_pdf' not in dato:
            continue
        
        # Buscar archivos en las carpetas
        archivos_docx = [f for f in os.listdir(dato['op_dir_memorias_docx']) 
                        if f.endswith('.docx')] if os.path.exists(dato['op_dir_memorias_docx']) else []
        archivos_pdf = [f for f in os.listdir(dato['op_dir_memorias_pdf']) 
                       if f.endswith('.pdf')] if os.path.exists(dato['op_dir_memorias_pdf']) else []
        
        # Si hay archivos en alguna de las carpetas, agregar a la lista
        if archivos_docx or archivos_pdf:
            # Agregar información sobre qué formatos están disponibles
            dato['tiene_docx'] = len(archivos_docx) > 0
            dato['tiene_pdf'] = len(archivos_pdf) > 0
            documentos_existentes.append(dato)
    
    # Ordenar por disciplina y luego por número
    documentos_existentes.sort(key=lambda x: (x.get('disciplina', ''), x.get('numero', '')))
    
    return documentos_existentes



def mostrar_documentos_existentes(datos, ruta_html: str, solo_datos: bool = False):
    """
    Muestra una tabla con los documentos que ya tienen archivos en las carpetas.
    
    Args:
        datos (list): Lista de diccionarios con los datos de los documentos
        ruta_html (str): Ruta donde guardar el archivo HTML con el reporte
        solo_datos (bool): Si es True, solo devuelve los datos sin mostrar la tabla
    
    Returns:
        list: Lista de documentos existentes
    """
    documentos_existentes = existing_documents(datos)
    
    if not documentos_existentes:
        if not solo_datos:
            console.print("No se encontraron documentos con archivos en las carpetas", style="bold red")
        return []
    
    if solo_datos:
        return documentos_existentes
    
    # Organizar documentos por disciplina
    documentos_por_disciplina = {}
    for doc in documentos_existentes:
        disciplina = doc.get('disciplina', 'SIN DISCIPLINA')
        if disciplina not in documentos_por_disciplina:
            documentos_por_disciplina[disciplina] = []
        documentos_por_disciplina[disciplina].append(doc)
    
    # Para cada disciplina, ordenar por número
    for disciplina in documentos_por_disciplina:
        documentos_por_disciplina[disciplina].sort(key=lambda x: x.get('numero', ''))
    
    # Mostrar tabla por disciplina
    console.print("\n[bold green]== DOCUMENTOS EXISTENTES POR DISCIPLINA ==[/bold green]\n")
    
    for disciplina, documentos in sorted(documentos_por_disciplina.items()):
        table = Table(title=f"Disciplina: {disciplina}")
        table.add_column("Código", style="cyan")
        table.add_column("Número", style="yellow")
        table.add_column("Nombre", style="green")
        table.add_column("Formato", style="magenta")
        table.add_column("Proyecto", style="blue")
        
        for documento in documentos:
            formatos = []
            if documento.get('tiene_docx', False):
                formatos.append("DOCX")
            if documento.get('tiene_pdf', False):
                formatos.append("PDF")
            
            formato_str = ", ".join(formatos)
            
            table.add_row(
                documento.get('codigo', ''),
                documento.get('numero', ''),
                documento.get('nombre', ''),
                formato_str,
                documento.get('proyecto', '')
            )
        
        console.print(table)
        console.print("\n")
    
    # Guardar HTML usando el método save_html de Rich
    html_dir = str(os.path.join(ruta_html, "documentos_existentes.html")).strip("'").strip('"')
    console.save_html(html_dir) 
    
    # text_dir = str(os.path.join(ruta_html, "documentos_existentes.text")).strip("'").strip('"')
    # console.save_text(text_dir)
    # svg_dir = str(os.path.join(ruta_html, "documentos_existentes.svg")).strip("'").strip('"')
    # console.save_svg(svg_dir)

    console.print(f"El reporte HTML ha sido guardado como '{html_dir}'", style="bold green")
    
    # Devolvemos la lista plana para su uso en otras funciones
    return documentos_existentes