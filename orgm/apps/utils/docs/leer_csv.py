from rich.console import Console

console = Console() 

def leer_csv(archivo_csv):
    """
    Lee un archivo CSV y retorna una lista de diccionarios con los campos del proyecto
    
    Args:
        archivo_csv (str): Ruta al archivo CSV
        
    Returns:
        list: Lista de diccionarios con los campos:
            - proyecto: Nombre del proyecto
            - subproyecto: Nombre del subproyecto 
            - disciplina: Disciplina del proyecto
            - id_proyecto: ID del proyecto
            - id_subproyecto: ID del subproyecto
            - id_disciplina: ID de la disciplina
            - ano: Año del proyecto
            - numero: Número del proyecto
            - nombre: Nombre del documento
            - revision: Número de revisión
    """
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            
        resultado = []
        for linea in lineas:
            valores = [valor.strip() for valor in linea.split(',')]
            if lineas.index(linea) == 0:
                continue
            if len(valores) >= 10:
                proyecto = {
                    'proyecto': valores[0].upper(),
                    'subproyecto': valores[1].upper(), 
                    'disciplina': valores[2].upper(),
                    'id_proyecto': valores[3].upper(),
                    'id_subproyecto': valores[4].upper(),
                    'id_disciplina': valores[5].upper(),
                    'ano': valores[6],
                    'numero': valores[7].zfill(2),
                    'nombre': valores[8].upper(),
                    'revision': valores[9].zfill(2),
                    'fecha': valores[10],
                    'ubicacion': valores[11].upper(),
                    'pais': valores[12].upper(),
                }
                resultado.append(proyecto)
            
        return resultado
        
    except FileNotFoundError:
        console.print("El archivo no existe", style="bold red")
        return []
    except Exception as e:
        console.print(f"Error al leer el archivo: {str(e)}", style="bold red")
        return []


if __name__ == "__main__":
    datos = leer_csv("datos.csv")
    for dato in datos:
        print(dato)
        break