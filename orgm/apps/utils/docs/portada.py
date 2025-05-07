import os
from docx import Document
from docxtpl import DocxTemplate
from docx.shared import Mm
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from jinja2 import Environment
from docxtpl import InlineImage
from rich.console import Console
from rich.progress import track
from orgm.apps.utils.docs.leer_csv import leer_csv
from orgm.apps.utils.docs.docx_pdf import convertir_docx_a_pdf
console = Console()

def directorios(datos: list[dict], temp_dir: str | None = None, output_dir: str | None = None):

    if not datos:
        console.print("No hay datos para procesar", style="bold red")
        return

    if not temp_dir:
        temp_dir = os.path.join(os.getcwd(), "orgm", "temp", "portada")
    else:
        temp_dir = temp_dir.strip().strip('"').strip("'")

    if not output_dir:
        output_dir = os.path.join(os.getcwd(), "orgm", "temp", "portada", "output")
    else:
        output_dir = output_dir.strip().strip('"').strip("'")

    for dato in track(datos, description="Generando directorios..."):
        dato['codigo'] = f"{dato['id_proyecto']}-{dato['id_subproyecto']}-{dato['id_disciplina']}-{dato['ano']}-{dato['numero']}"
        dato['nombre_docx'] = f"{dato['codigo']}-{dato['revision']}.docx"
        dato['nombre_pdf'] = f"{dato['codigo']}-{dato['revision']}.pdf"
        dato['op_dir_portadas_pdf'] = os.path.join(output_dir, dato['revision'], "portadas", "pdf")
        dato['op_dir_portadas_docx'] = os.path.join(output_dir, dato['revision'], "portadas", "docx")
        dato['op_dir_memorias_pdf'] = os.path.join(output_dir, dato['revision'], "memorias", "pdf", dato['codigo'])
        dato['op_dir_memorias_docx'] = os.path.join(output_dir, dato['revision'], "memorias", "docx", dato['codigo'])
        dato['op_dir_entregables_pdf'] = os.path.join(output_dir, dato['revision'], "entregables", "pdf", dato['codigo'])
        dato['op_dir_entregables_docx'] = os.path.join(output_dir, dato['revision'], "entregables", "docx", dato['codigo'])

        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(dato['op_dir_portadas_pdf'], exist_ok=True)
        os.makedirs(dato['op_dir_portadas_docx'], exist_ok=True)
        os.makedirs(dato['op_dir_memorias_pdf'], exist_ok=True)
        os.makedirs(dato['op_dir_memorias_docx'], exist_ok=True)
        os.makedirs(dato['op_dir_entregables_pdf'], exist_ok=True)
        os.makedirs(dato['op_dir_entregables_docx'], exist_ok=True)
        
    return datos, temp_dir, output_dir

def generar_portadas(datos=list[dict], temp_dir = str | None == None, output_dir = str | None == None, pdf: bool = False):

    datos, temp_dir, output_dir = directorios(datos, temp_dir, output_dir)


    imagen1 = os.path.join(temp_dir, "imagen1.png")
    logo1 = os.path.join(temp_dir, "logo1.png")
    logo2 = os.path.join(temp_dir, "logo2.png")

    docx_template = os.path.dirname(os.path.abspath(__file__))
    for parent in range(1, 4):
        docx_template = os.path.dirname(docx_template)
    docx_template = os.path.join(docx_template, "temp", "portada", "tpl_portada.docx")

    if not os.path.exists(docx_template):
        console.print(f"No se encontró el archivo {docx_template}", style="bold red")
        raise FileNotFoundError(f"No se encontró el archivo {docx_template}")


    for dato in track(datos, description="Generando portadas..."):

        file = DocxTemplate(docx_template)

        env = Environment(loader=file)

        context = {
            "PROYECTO": dato['proyecto'],
            "SUBPROYECTO": dato['subproyecto'],
            "DISCIPLINA": dato['disciplina'],
            "TITULO": dato['nombre'],
            "REVISION": dato['revision'],
            "CODIGO": dato['codigo'],
            "UBICACION": dato['ubicacion'],
            "PAIS": dato['pais'],
            "FECHA": dato['fecha'],
            "LOGO1": InlineImage(
                file, logo1, height=Mm(28)
            ),
            "LOGO2": InlineImage(
                file, logo2, height=Mm(4)
            ),
            "IMAGEN1": InlineImage(
                file, imagen1, height=Mm(80)
            )

        }
        file.render(context, env, autoescape=True)
        file.save(f"{dato['op_dir_portadas_docx']}/{dato['nombre_docx']}")
        if pdf:
            convertir_docx_a_pdf(f"{dato['op_dir_portadas_docx']}/{dato['nombre_docx']}", f"{dato['op_dir_portadas_pdf']}/{dato['nombre_pdf']}")


if __name__ == "__main__":
    temp_dir = '/home/osmar/Nextcloud/Proyectos/000 - DSEAT - SANTA CLARA/Memorias/portadas.csv'
    directorio = os.path.dirname(temp_dir)
    datos = leer_csv(temp_dir)
    generar_portadas(datos, directorio, directorio, pdf=True)
