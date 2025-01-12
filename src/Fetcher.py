#!/usr/bin/env python
# -*- coding: utf-8 
"""
Script para descargar archivos PDF del BORME a partir de una lista de enlaces.
"""
import requests
import os
from os import makedirs
from os.path import exists
from utils.Loger import Logger
def download_pdf(url, output_path,logger):
     """
    Descarga un archivo PDF desde una URL y lo guarda en una ruta especificada.

    Args:
        url (str): URL del archivo PDF a descargar.
        output_path (str): Ruta donde se guardará el archivo PDF descargado.
        logger (logging.Logger): Objeto de registro para registrar información sobre errores.

    Returns:
        bool: 
            - `True` si el archivo se descarga y guarda correctamente.
            - `False` si ocurre un error durante el proceso de descarga.

    Raises:
        requests.exceptions.RequestException: Si ocurre un error durante la solicitud HTTP 
        y no es manejado internamente.
    """
    try:
        response = requests.get(url.strip(), timeout=30)
        response.raise_for_status()
        with open(output_path, "wb") as file:
            file.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        logger.info(f"Error descargando {url}: {str(e)}")
        return False
def execute():
      """
    Ejecuta el proceso de descarga de archivos PDF desde una lista de enlaces y registra el progreso.
    Args:
        No recibe argumentos directamente, pero espera que los siguientes elementos estén 
        disponibles en las rutas definidas:
        - `../data/outputs/links.txt`: Archivo de texto que contiene las URLs a descargar.
        - `../data/outputs/PDF`: Directorio donde se guardarán los archivos descargados.
        - `../data/logs/Fetcherlogs`: Directorio donde se almacenarán los registros del proceso.

    Logs:
        - Registra el inicio y finalización del proceso de descarga.
        - Registra cada archivo descargado con su progreso.
        - Informa si el archivo de enlaces no se encuentra, si hay errores de E/S o cualquier 
          otro error inesperado.

    Exceptions:
        - Captura y maneja `FileNotFoundError` si el archivo de enlaces no se encuentra.
        - Captura y maneja `IOError` si ocurre un problema al leer el archivo de enlaces.
        - Captura cualquier otra excepción y registra el mensaje de error correspondiente.
    """
    dir="../data/logs/Fetcherlogs"
    logger_instance=Logger("Practica12",dir)
    logger=logger_instance.launch_logging()
    try:
        # Crear directorio de salida si no existe
        output_dir = "../data/outputs/PDF"
        if not exists(output_dir):
            makedirs(output_dir)
        # Leer y procesar enlaces
        with open("../data/outputs/links.txt", "r", encoding="utf-8") as archivo:
            enlaces = archivo.readlines()
            total = len(enlaces)
            logger.info(f"Iniciando descarga de {total} archivos")
            for i, url in enumerate(enlaces, 1):
                url = url.strip()
                if not url:
                    continue
                nombre_archivo = os.path.basename(url)
                ruta_salida = os.path.join(output_dir, nombre_archivo)
                if download_pdf(url, ruta_salida,logger):
                    logger.info(f"Descargado {nombre_archivo} ({i}/{total})")
        logger.info("Proceso de descarga completado")
    except FileNotFoundError:
        logger.info("El archivo de enlaces no se encuentra.")
    except IOError:
        logger.info("Error al leer el archivo de enlaces.")
    except Exception as e:
        logger.info(f"Error inesperado: {str(e)}")
if __name__ == "__main__":
    execute()