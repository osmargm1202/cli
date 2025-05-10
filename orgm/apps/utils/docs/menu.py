import questionary
import os
from orgm.apps.utils.docs.portada import generar_portadas, directorios
from orgm.apps.utils.docs.leer_csv import leer_csv
from orgm.qstyle import custom_style_fancy
from orgm.apps.utils.docs.docx_pdf import convertir_docx_a_pdf
from orgm.apps.utils.docs.unir_docx import unir_documentos_docx
from orgm.apps.utils.docs.unir_pdf import unir_documentos_pdf
from orgm.apps.utils.docs.last_directory import guardar_ultimo_directorio, obtener_ultimo_directorio
from orgm.apps.utils.docs.doc_list import generar_tabla_planos
from orgm.apps.utils.docs.missing_docs import mostrar_documentos_faltantes
from orgm.apps.utils.docs.existing_docs import mostrar_documentos_existentes
from orgm.apps.utils.docs.cargar_documentos import copiar_documento
from orgm.apps.utils.docs.preparar_entregables import copiar_entregables
from rich.console import Console

console = Console()


def obtener_archivo_base(ruta_base: str | None = None):
    if not ruta_base:
        ruta_base = os.getcwd()
    else:
        ruta_base = ruta_base.strip().strip('"').strip("'")
    archivo_base = os.path.join(ruta_base, "portadas.csv")
    if not os.path.exists(archivo_base):
        ruta_csv = questionary.path(
            "No se encontró el archivo portadas.csv en el directorio actual. Por favor, ingrese la ruta del archivo:",
            style=custom_style_fancy
        ).ask()
        archivo_base = ruta_csv.strip().strip('"').strip("'")

    if archivo_base and os.path.exists(archivo_base):
        console.print(f"Ruta CSV: {archivo_base}", style="bold green")
        return archivo_base
    else:
        return False


def imprimir_docx(dato: dict):
    # Buscar archivos docx en el directorio de memorias
    archivos_docx = [f for f in os.listdir(dato['op_dir_memorias_docx']) if f.endswith('.docx')]


    if archivos_docx:
        if len(archivos_docx) > 1:
            archivos_completos = [os.path.join(dato['op_dir_memorias_docx'], archivo) for archivo in archivos_docx]
            archivo_unido = unir_documentos_docx(archivos_completos, dato['op_dir_memorias_docx'], dato['nombre_docx'])

            # Convertir el archivo unido a PDF
            ruta_pdf = os.path.join(dato['op_dir_memorias_pdf'], dato['nombre_pdf'])
            convertir_docx_a_pdf(archivo_unido, ruta_pdf)
            archivos_docx = [archivo_unido]
        for archivo in archivos_docx:
            ruta_docx = os.path.join(dato['op_dir_memorias_docx'], archivo)
            ruta_pdf = os.path.join(dato['op_dir_memorias_pdf'], dato['nombre_pdf'])
            console.print(ruta_docx, style="bold yellow dim")
            convertir_docx_a_pdf(ruta_docx, ruta_pdf)

        portadas_pdf = f'{dato['op_dir_portadas_pdf']}/{dato['nombre_pdf']}'
        archivos_pdf = [f'{dato['op_dir_memorias_pdf']}/{f}' for f in os.listdir(dato['op_dir_memorias_pdf']) if f.endswith('.pdf')]

        archivos_a_unir = []
        archivos_a_unir.append(portadas_pdf)
        archivos_a_unir.extend(archivos_pdf)

        console.print(archivos_a_unir, style="bold yellow")

        unir_documentos_pdf(archivos_a_unir, dato['op_dir_entregables_pdf'], dato['nombre_pdf'])

def menu():

    console.print("Bienvenido al menú de Documentos", style="bold blue italic")

    ultimo_directorio = obtener_ultimo_directorio()
    console.print(f"Último directorio: {ultimo_directorio}", style="bold yellow dim")
    
    opciones = [
        "Cargar documentos faltantes",
        "Reemplazar documentos existentes",
        "Imprimir lista de memorias",
        "Mostrar documentos faltantes",
        "Mostrar documentos existentes",
        "Unir documento con portada",
        "Preparar entrega",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        "Generar portadas desde CSV",
        "Cambiar directorio",
        "Salir"
    ]
    
    respuesta = questionary.select(
        "¿Qué desea hacer?",
        choices=opciones,
        style=custom_style_fancy
    ).ask()

    if respuesta == "Cambiar directorio":
        directorio = questionary.path(
            "Ingrese la ruta del directorio:",
            style=custom_style_fancy
        ).ask()
        guardar_ultimo_directorio(os.path.dirname(directorio.strip().strip('"').strip("'")))
        return menu()
    
    if respuesta == "Generar portadas desde CSV":
        archivo_base = obtener_archivo_base(ultimo_directorio)

        if archivo_base:
            if ultimo_directorio != os.path.dirname(archivo_base):
                guardar_ultimo_directorio(os.path.dirname(archivo_base))
            try:
                directorio = os.path.dirname(archivo_base)
                datos = leer_csv(archivo_base)
                if datos:
                    generar_pdf = questionary.confirm("¿Desea generar PDFs de las portadas?", style=custom_style_fancy).ask()
                    if generar_pdf:
                        generar_portadas(datos, temp_dir=directorio, output_dir=directorio, pdf=True)
                    else:
                        generar_portadas(datos, temp_dir=directorio, output_dir=directorio)
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
            return menu()
    elif respuesta == "Mostrar documentos faltantes":
        archivo_base = obtener_archivo_base(ultimo_directorio)
        
        if archivo_base:
            if ultimo_directorio != os.path.dirname(archivo_base):
                guardar_ultimo_directorio(os.path.dirname(archivo_base))
            try:
                directorio = os.path.dirname(archivo_base)
                datos = leer_csv(archivo_base)
                if datos:
                    datos, temp_dir, output_dir = directorios(datos, temp_dir=directorio, output_dir=directorio)
                    mostrar_documentos_faltantes(datos, ruta_html=directorio)
                else:
                    console.print("No se encontraron datos en el CSV.", style="bold red")
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
        return menu()
    
    elif respuesta == "Mostrar documentos existentes":
        archivo_base = obtener_archivo_base(ultimo_directorio)
        
        if archivo_base:
            if ultimo_directorio != os.path.dirname(archivo_base):
                guardar_ultimo_directorio(os.path.dirname(archivo_base))
            try:
                directorio = os.path.dirname(archivo_base)
                datos = leer_csv(archivo_base)
                if datos:
                    datos, temp_dir, output_dir = directorios(datos, temp_dir=directorio, output_dir=directorio)
                    mostrar_documentos_existentes(datos, ruta_html=directorio)
                else:
                    console.print("No se encontraron datos en el CSV.", style="bold red")
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
        return menu()
    
    elif respuesta == "Cargar documentos faltantes":
        archivo_base = obtener_archivo_base(ultimo_directorio)
        
        if archivo_base:
            if ultimo_directorio != os.path.dirname(archivo_base):
                guardar_ultimo_directorio(os.path.dirname(archivo_base))
            try:
                directorio = os.path.dirname(archivo_base)
                datos = leer_csv(archivo_base)
                if datos:
                    datos, temp_dir, output_dir = directorios(datos, temp_dir=directorio, output_dir=directorio)
                    documentos_faltantes = mostrar_documentos_faltantes(datos, ruta_html=directorio)
                    
                    if documentos_faltantes:
                        # Organizar por disciplina para la selección
                        documentos_por_disciplina = {}
                        for i, doc in enumerate(documentos_faltantes):
                            disciplina = doc.get('disciplina', 'SIN DISCIPLINA')
                            if disciplina not in documentos_por_disciplina:
                                documentos_por_disciplina[disciplina] = []
                            documentos_por_disciplina[disciplina].append((i, doc))
                        
                        # Crear lista de opciones para seleccionar documento, agrupadas por disciplina
                        opciones_documentos = []
                        for disciplina, docs in sorted(documentos_por_disciplina.items()):
                            # Agregar encabezado de disciplina como opción deshabilitada (no seleccionable)
                            opciones_documentos.append(questionary.Separator(f"-- {disciplina} --"))
                            
                            # Agregar documentos de esta disciplina
                            for i, doc in docs:
                                opciones_documentos.append(
                                    f"{i+1}. {doc.get('codigo', '')} - {doc.get('nombre', '')} ({doc.get('disciplina', '')})"
                                )
                        
                        documento_seleccionado = questionary.select(
                            "Seleccione el documento para cargar:",
                            choices=opciones_documentos,
                            style=custom_style_fancy
                        ).ask()
                        
                        if documento_seleccionado and not documento_seleccionado.startswith("--"):
                            # Obtener índice del documento seleccionado
                            indice = int(documento_seleccionado.split('.')[0]) - 1
                            
                            # Solicitar ruta del archivo a copiar
                            ruta_archivo = questionary.path(
                                "Ingrese la ruta del archivo a copiar:",
                                style=custom_style_fancy
                            ).ask()
                            
                            # Copiar archivo
                            copiar_documento(documentos_faltantes, indice, ruta_archivo)
                    else:
                        console.print("No hay documentos faltantes.", style="bold green")
                else:
                    console.print("No se encontraron datos en el CSV.", style="bold red")
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
        return menu()

    elif respuesta == "Reemplazar documentos existentes":
        archivo_base = obtener_archivo_base(ultimo_directorio)
        
        if archivo_base:
            if ultimo_directorio != os.path.dirname(archivo_base):
                guardar_ultimo_directorio(os.path.dirname(archivo_base))
            try:
                directorio = os.path.dirname(archivo_base)
                datos = leer_csv(archivo_base)
                if datos:
                    datos, temp_dir, output_dir = directorios(datos, temp_dir=directorio, output_dir=directorio)
                    documentos_existentes = mostrar_documentos_existentes(datos, ruta_html=directorio, solo_datos=True)
                    
                    if documentos_existentes:
                        # Organizar por disciplina para la selección
                        documentos_por_disciplina = {}
                        for i, doc in enumerate(documentos_existentes):
                            disciplina = doc.get('disciplina', 'SIN DISCIPLINA')
                            if disciplina not in documentos_por_disciplina:
                                documentos_por_disciplina[disciplina] = []
                            documentos_por_disciplina[disciplina].append((i, doc))
                        
                        # Crear lista de opciones para seleccionar documento, agrupadas por disciplina
                        opciones_documentos = []
                        for disciplina, docs in sorted(documentos_por_disciplina.items()):
                            # Agregar encabezado de disciplina como opción deshabilitada (no seleccionable)
                            opciones_documentos.append(questionary.Separator(f"-- {disciplina} --"))
                            
                            # Agregar documentos de esta disciplina
                            for i, doc in docs:
                                opciones_documentos.append(
                                    f"{i+1}. {doc.get('codigo', '')} - {doc.get('nombre', '')} ({doc.get('disciplina', '')})"
                                )
                        
                        documento_seleccionado = questionary.select(
                            "Seleccione el documento a reemplazar:",
                            choices=opciones_documentos,
                            style=custom_style_fancy
                        ).ask()
                        
                        if documento_seleccionado and not documento_seleccionado.startswith("--"):
                            # Obtener índice del documento seleccionado
                            indice = int(documento_seleccionado.split('.')[0]) - 1
                            
                            # Solicitar ruta del archivo a copiar
                            ruta_archivo = questionary.path(
                                "Ingrese la ruta del archivo de reemplazo:",
                                style=custom_style_fancy
                            ).ask()
                            
                            # Confirmar reemplazo
                            confirmar = questionary.confirm(
                                f"¿Está seguro de reemplazar el documento '{documentos_existentes[indice].get('nombre', '')}'?",
                                style=custom_style_fancy
                            ).ask()
                            
                            if confirmar:
                                # Copiar archivo (reemplazar)
                                copiar_documento(documentos_existentes, indice, ruta_archivo, reemplazar=True)
                                console.print("Documento reemplazado exitosamente.", style="bold green")

                                # Preguntar si desea reimprimir el documento
                                reimprimir = questionary.confirm(
                                    "¿Desea reimprimir el documento con la portada?",
                                    style=custom_style_fancy
                                ).ask()
                                
                                if reimprimir:
                                    try:
                                        # Obtener el documento seleccionado
                                        documento = documentos_existentes[indice]
                                        # Imprimir el documento con su portada
                                        imprimir_docx(documento)
                                        console.print("Documento reimpreso exitosamente.", style="bold green")
                                    except Exception as e:
                                        console.print(f"Error al reimprimir el documento: {e}", style="bold red")
                                
                    else:
                        console.print("No hay documentos existentes para reemplazar.", style="bold yellow")
                else:
                    console.print("No se encontraron datos en el CSV.", style="bold red")
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
        return menu()

    elif respuesta == "Imprimir lista de memorias":
        
        archivo_base = obtener_archivo_base(ultimo_directorio)
        if archivo_base:
            if ultimo_directorio != os.path.dirname(archivo_base):
                guardar_ultimo_directorio(os.path.dirname(archivo_base))
            try:
                datos = leer_csv(archivo_base)
                if datos:
                    # Preguntar si quiere imprimir todos los documentos
                    imprimir_todos = questionary.confirm(
                        "¿Desea imprimir tanto los documentos faltantes como los existentes?",
                        style=custom_style_fancy
                    ).ask()

                    if imprimir_todos:
                        # Generar tabla con todos los documentos
                        generar_tabla_planos(datos, archivo_salida=f"{ultimo_directorio}/lista_documentos.pdf")
                        # Mostrar documentos faltantes
                        mostrar_documentos_faltantes(datos, ruta_html=ultimo_directorio)
                        # Mostrar documentos existentes  
                        mostrar_documentos_existentes(datos, ruta_html=ultimo_directorio)
                    else:
                        # Solo generar la tabla normal
                        generar_tabla_planos(datos, archivo_salida=f"{ultimo_directorio}/lista_documentos.pdf")

                    return menu()
                else:
                    console.print("No se encontraron datos en el CSV.", style="bold red")
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
        return menu()

    elif respuesta == "Preparar entrega":
        archivo_base = obtener_archivo_base(ultimo_directorio)
        
        if archivo_base:
            if ultimo_directorio != os.path.dirname(archivo_base):
                guardar_ultimo_directorio(os.path.dirname(archivo_base))
            try:
                directorio = os.path.dirname(archivo_base)
                datos = leer_csv(archivo_base)
                if datos:
                    datos, temp_dir, output_dir = directorios(datos, temp_dir=directorio, output_dir=directorio)
                    
                    # Preguntar directorio de destino o usar el actual
                    usar_directorio_actual = questionary.confirm(
                        f"¿Desea usar el directorio actual para la entrega? ({directorio})",
                        style=custom_style_fancy
                    ).ask()
                    
                    if usar_directorio_actual:
                        ruta_destino = directorio
                    else:
                        ruta_destino = questionary.path(
                            "Ingrese la ruta para la entrega:",
                            style=custom_style_fancy
                        ).ask().strip().strip('"').strip("'")
                    
                    # Copiar los entregables
                    copiar_entregables(datos, ruta_destino)
                    console.print("Entregables copiados exitosamente.", style="bold green")
                    
                else:
                    console.print("No se encontraron datos en el CSV.", style="bold red")
                return menu()
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
        return menu()

    elif respuesta == "Unir documento con portada":
        archivo_base = obtener_archivo_base(ultimo_directorio)

        if archivo_base:
            if ultimo_directorio != os.path.dirname(archivo_base):
                guardar_ultimo_directorio(os.path.dirname(archivo_base))
            try:
                directorio = os.path.dirname(archivo_base)
                datos = leer_csv(archivo_base)
                if datos:
                    datos, temp_dir, output_dir = directorios(datos, temp_dir=directorio, output_dir=directorio)
                    # Crear lista de opciones con "Todos" como primera opción
                    opciones_codigos = ["Todos"]
                    opciones_codigos.extend([f"{dato['codigo']} - {dato['nombre']}" for dato in datos])
                    
                    # Preguntar al usuario qué documento procesar
                    codigos_seleccionados = questionary.checkbox(
                        "Seleccione los documentos a procesar:",
                        choices=opciones_codigos,
                        default="Todos",
                        style=custom_style_fancy

                    ).ask()
                    
                    # Filtrar datos según la selección
                    if "Todos" in codigos_seleccionados:
                        for dato in datos:
                            imprimir_docx(dato)
                    elif codigos_seleccionados:
                        for dato in datos:
                            if dato['codigo'] in codigos_seleccionados:
                                imprimir_docx(dato)
                    else:
                        return 'exit'
                    

            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
        return menu()
    else:
        return 'exit'
        
    return True

if __name__ == "__main__":
    menu()