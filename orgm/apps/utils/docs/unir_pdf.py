import os
from PyPDF2 import PdfMerger
from orgm.apps.utils.docs.ask_dir import seleccionar_carpeta


def unir_documentos_pdf(pdf_files, carpeta_destino, nombre_salida):
    merger = PdfMerger()
    

    for pdf_path in pdf_files:
        merger.append(pdf_path)
    
    archivo_salida = os.path.join(carpeta_destino, nombre_salida)
    merger.write(archivo_salida)
    merger.close()
    
    return archivo_salida

def unir_pdf(nombre_salida):
    carpeta = seleccionar_carpeta()
    archivos_pdf = [f for f in os.listdir(carpeta) if f.endswith(".pdf")]
    archivos_completos = [os.path.join(carpeta, archivo) for archivo in archivos_pdf]
    unir_documentos_pdf(archivos_completos, carpeta, nombre_salida)


if __name__ == "__main__":
    print(unir_pdf("01. COMPILADO.pdf"))
