import typer
from rich.console import Console
import os
import questionary
from orgm.qstyle import custom_style_fancy


console = Console()

from orgm.apps.utils.docs.docx_pdf import docx_pdf
from orgm.apps.utils.docs.unir_docx import unir_docx
from orgm.apps.utils.docs.menu import menu
from orgm.apps.utils.docs.doc_list import generar_tabla_planos
from orgm.apps.utils.docs.missing_docs import mostrar_documentos_faltantes
from orgm.apps.utils.docs.existing_docs import mostrar_documentos_existentes
from orgm.apps.utils.docs.cargar_documentos import copiar_documento
from orgm.apps.utils.docs.preparar_entregables import copiar_entregables
from orgm.apps.utils.docs.leer_csv import leer_csv
from orgm.apps.utils.docs.portada import directorios
from orgm.apps.utils.docs.last_directory import guardar_ultimo_directorio, obtener_ultimo_directorio

app = typer.Typer(help="Comandos para interactuar con documentos")

app.command(name="pdf")(docx_pdf)
app.command(name="unir")(unir_docx)


def obtener_archivo_base(ruta_base: str | None = None):
    """
    Función para obtener el archivo base para los comandos.
    """
    if not ruta_base:
        ruta_base = obtener_ultimo_directorio()
    else:
        ruta_base = ruta_base.strip().strip('"').strip("'")
        guardar_ultimo_directorio(os.path.dirname(ruta_base))
    
    archivo_base = os.path.join(ruta_base, "portadas.csv")
    if not os.path.exists(archivo_base):
        console.print(f"No se encontró el archivo portadas.csv en {ruta_base}", style="bold red")
        return False

    console.print(f"Ruta CSV: {archivo_base}", style="bold green")
    return archivo_base


@app.command(name="listar")
def listar():
    """
    Imprimir lista de memorias o planos del proyecto.
    """
    archivo_base = obtener_archivo_base()
    if archivo_base:
        try:
            directorio = os.path.dirname(archivo_base)
            datos = leer_csv(archivo_base)
            if datos:
                generar_tabla_planos(datos, archivo_salida=f"{directorio}/lista_documentos.html")
            else:
                console.print("No se encontraron datos en el CSV.", style="bold red")
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")


@app.command(name="listar-f")
def listar_faltantes():
    """
    Mostrar documentos faltantes en el proyecto.
    """
    archivo_base = obtener_archivo_base()
    if archivo_base:
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


@app.command(name="listar-e")
def listar_existentes():
    """
    Mostrar documentos existentes en el proyecto.
    """
    archivo_base = obtener_archivo_base()
    if archivo_base:
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

@app.command(name="load")
def cargar_documentos():
    """
    Cargar documentos nuevos al proyecto.
    """
    archivo_base = obtener_archivo_base()
    if archivo_base:
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
                    console.print(documentos_por_disciplina)
                    for disciplina, docs in sorted(documentos_por_disciplina.items()):
                        # Agregar encabezado de disciplina como opción deshabilitada
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
                        ruta_archivo = ruta_archivo.strip().strip('"').strip("'")

                        if os.path.exists(ruta_archivo):
                            copiar_documento(documentos_faltantes, indice, ruta_archivo)
                        else:
                            console.print("El archivo no existe.", style="bold red")
                else:
                    console.print("No hay documentos faltantes.", style="bold green")
            else:
                console.print("No se encontraron datos en el CSV.", style="bold red")
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")


@app.command(name="dir")
def cambiar_directorio(directorio: str):
    """
    Cambiar el directorio de trabajo.
    """
    directorio = directorio.strip().strip('"').strip("'")
    if os.path.exists(directorio):
        guardar_ultimo_directorio(directorio)
    else:
        console.print(f"El directorio {directorio} no existe.", style="bold red")


@app.command(name="unir-portada")
def unir_con_portada():
    """
    Unir documentos con portada según el menú.
    """
    from orgm.apps.utils.docs.menu import imprimir_docx
    
    archivo_base = obtener_archivo_base()
    if archivo_base:
        try:
            directorio = os.path.dirname(archivo_base)
            datos = leer_csv(archivo_base)
            if datos:
                datos, temp_dir, output_dir = directorios(datos, temp_dir=directorio, output_dir=directorio)
                
                # Listar todos los códigos disponibles con un índice
                console.print("\n[bold blue]Documentos disponibles:[/bold blue]")
                for i, dato in enumerate(datos):
                    console.print(f"{i+1}. {dato.get('codigo', '')} - {dato.get('nombre', '')}")
                
                # Solicitar el índice del documento a procesar
                try:
                    indice_str = input("\nIngrese el número del documento a procesar (0 para todos): ")
                    indice = int(indice_str) - 1
                    
                    if indice == -1:  # Si ingresaron 0, procesar todos
                        for dato in datos:
                            imprimir_docx(dato)
                    elif 0 <= indice < len(datos):
                        dato = datos[indice]
                        imprimir_docx(dato)
                    else:
                        console.print("Índice inválido.", style="bold red")
                except ValueError:
                    console.print("Por favor, ingrese un número válido.", style="bold red")
            else:
                console.print("No se encontraron datos en el CSV.", style="bold red")
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")


@app.command(name="entrega")
def preparar_entrega(directorio_destino: str = None):
    """
    Preparar entrega copiando los documentos PDF de los entregables según su revisión.
    """
    archivo_base = obtener_archivo_base()
    if archivo_base:
        try:
            directorio = os.path.dirname(archivo_base)
            datos = leer_csv(archivo_base)
            if datos:
                datos, temp_dir, output_dir = directorios(datos, temp_dir=directorio, output_dir=directorio)
                
                # Si no se proporciona directorio de destino, usar el directorio actual
                if not directorio_destino:
                    directorio_destino = directorio
                else:
                    directorio_destino = directorio_destino.strip().strip('"').strip("'")
                    
                # Verificar que el directorio existe
                if not os.path.exists(directorio_destino):
                    os.makedirs(directorio_destino, exist_ok=True)
                    console.print(f"Creado directorio: {directorio_destino}", style="bold green")
                
                # Copiar los entregables
                copiar_entregables(datos, directorio_destino)
            else:
                console.print("No se encontraron datos en el CSV.", style="bold red")
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")


@app.callback(invoke_without_command=True)
def docs_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con documentos. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de documentos
        menu()
        


if __name__ == "__main__":
    app()
