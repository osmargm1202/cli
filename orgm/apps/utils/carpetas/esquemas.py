# funcion para cargar esquemas de orgm/temp/carpetas/esquemas.json

import json
from rich import print
from dotenv import load_dotenv
import os
from orgm.apps.utils.carpetas.api import obtener_datos_de_cotizacion

load_dotenv()


def cargar_esquemas(tipo_proyecto: str):
    with open('orgm/temp/carpetas/esquemas.json', 'r') as archivo:
        return json.load(archivo)['tipos_proyecto'][tipo_proyecto]['carpetas']
    

def crear_carpeta(esquema: list, ruta: str):
    for carpeta in esquema:
        ruta_carpeta = os.path.join(ruta, carpeta)
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

def nombre_carpeta_proyecto(cotizacion: int):
    datos = obtener_datos_de_cotizacion(cotizacion)
    nombre_proyecto = f'{str(cotizacion).zfill(4)} - {datos['servicio']['nombre']} - {datos['proyecto']['nombre_proyecto']}'
    return nombre_proyecto


def crear_carpeta_proyecto():
    ruta_proyecto = os.getenv('CARPETA_PROYECTOS')
    carpetas = cargar_esquemas('Proyectos')

    crear_carpeta(carpetas, ruta_proyecto)


if __name__ == '__main__':

    # ruta_base = os.getenv('CARPETA_PROYECTOS')
    # crear_carpeta(cargar_esquemas('General'), ruta_base)
    print(nombre_carpeta_proyecto(533))