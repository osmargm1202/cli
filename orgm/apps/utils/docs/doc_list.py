
from orgm.apps.utils.docs.leer_csv import leer_csv
import sys
import os


from rich.console import Console

console = Console()

# pdfmetrics.registerFont(TTFont('Roboto', '/usr/share/fonts/TTF/Roboto-Regular.ttf'))

def dividir_texto(texto, max_caracteres=30):
    palabras = texto.split()
    lineas = []
    linea_actual = ''
    for palabra in palabras:
        if len(linea_actual) + len(palabra) + 1 <= max_caracteres:
            if linea_actual:
                linea_actual += ' '
            linea_actual += palabra
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)
    return '<br/>'.join(lineas)

def generar_tabla_planos(datos, archivo_salida="lista_planos.html"):
    from rich.console import Console
    from rich.table import Table

    console = Console(record=True)
    
    # Crear la tabla
    table = Table(title="LISTA DE PLANOS / MEMORIAS", show_header=True, header_style="bold white on black")
    
    # Agregar columnas
    table.add_column("N°", justify="center", style="dim", width=8)
    table.add_column("CÓDIGO", justify="left", width=20)
    table.add_column("NOMBRE", justify="left", width=30)
    table.add_column("REVISIÓN", justify="center", style="bold blue", width=10)
    table.add_column("FECHA", justify="center", width=12)
    table.add_column("DISCIPLINA", justify="center", width=12)
    # Agregar filas
    for i, dato in enumerate(datos, 1):
        codigo = f"{dato['id_proyecto']}-{dato['id_subproyecto']}-{dato['id_disciplina']}-{dato['ano']}-{dato['numero']}"
        table.add_row(
            str(i),
            codigo,
            dividir_texto(dato['nombre'], 30).replace('<br/>', '\n'),
            dato['revision'],
            dato['fecha'],
            dato['disciplina']
        )

    # Guardar como HTML
    console.print(table)
    console.print(f"HTML generado: {archivo_salida}", style="bold green")
    console.save_html(archivo_salida)


def main():
    if len(sys.argv) > 1:
        archivo_csv = sys.argv[1]
    else:
        archivo_csv = input("Ruta del archivo CSV: ").strip()
    if not os.path.exists(archivo_csv):
        console.print("No se encontró el archivo CSV.", style="bold red")
        return
    datos = leer_csv(archivo_csv)
    if not datos:
        console.print("No se encontraron datos en el CSV.", style="bold red")
        return
    generar_tabla_planos(datos)

if __name__ == "__main__":
    main()
