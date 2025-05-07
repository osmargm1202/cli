
import os
from docx import Document
from docxcompose.composer import Composer

from orgm.apps.utils.docs.ask_dir import seleccionar_carpeta


def unir_documentos_docx(docx_files, carpeta_destino, nombre_salida):
    master_doc = None
    for file_path in docx_files:
        master_doc = Document(file_path)
        break

    composer = Composer(master_doc)

    for file_path in docx_files:
        doc = Document(file_path)
        composer.append(doc)

    archivo_salida = os.path.join(carpeta_destino, nombre_salida)
    composer.save(archivo_salida)

    return archivo_salida

def unir_docx(nombre_salida):
    carpeta = seleccionar_carpeta()
    archivos_docx = [f for f in os.listdir(carpeta) if f.endswith(".docx")]
    archivos_completos = [os.path.join(carpeta, archivo) for archivo in archivos_docx]
    unir_documentos_docx(archivos_completos, carpeta, nombre_salida)


if __name__ == "__main__":
    print(unir_docx("01. COMPILADO.docx"))
