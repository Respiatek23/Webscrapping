#!/usr/bin/env python
# coding: utf-8
"""
Script para extraer enlaces de boletines del BORME (Boletín Oficial del Registro Mercantil)
Permite la extracción tanto de una fecha específica como de múltiples fechas desde un archivo.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os
import sys
from utils.Loger import Logger
def extraer_enlaces_borme(driver, fecha, logger,modo_escritura='w'):
    """
    Extrae y guarda enlaces de los boletines del BORME correspondientes a una fecha específica.
    Args:
        driver (selenium.webdriver): Instancia del controlador de Selenium para la navegación web.
        fecha (str): Fecha de búsqueda en formato "dd/mm/aaaa".
        logger (logging.Logger): Objeto de registro para registrar información sobre el proceso.
        modo_escritura (str, opcional): Modo de apertura del archivo de salida. Por defecto es 'w' 
            (sobrescribir el contenido), pero se puede usar 'a' para agregar enlaces.
    Returns:
        None: No devuelve ningún valor. Los enlaces extraídos se guardan en un archivo de texto.

    Logs:
        - Registra el inicio y finalización del proceso de descarga.
        - Informa si no se encuentra boletín para la fecha proporcionada.
        - Registra cualquier error inesperado durante la ejecución.

    Exceptions:
        - Captura y maneja `NoSuchElementException` si no hay boletín para la fecha indicada.
        - Captura cualquier otra excepción y registra el mensaje de error correspondiente.
    
    Archivo de salida:
        - ../data/outputs/links.txt: Archivo de texto donde se almacenan los enlaces extraídos.
    """
    URL_BASE = "https://www.boe.es/diario_borme/"
    RUTA_SALIDA = "../data/outputs/links.txt"
    try:
        # Navegación a la página y búsqueda por fecha
        driver.get(URL_BASE)
        campo_fecha = driver.find_element(By.ID, "fechaBORME")
        campo_fecha.send_keys(fecha)
        time.sleep(1)
        # Realizar búsqueda
        driver.find_elements(By.CLASS_NAME, "boton")[0].click()
        time.sleep(1)
        # Filtrar por Actos Inscritos
        driver.find_element("id", "dropDownSec").click()
        elementos_lista = driver.find_elements(By.TAG_NAME, "li")
        for elemento in elementos_lista:
            if elemento.text == "Actos inscritos":
                elemento.click()
                break
        time.sleep(1)
        # Extraer enlaces
        sumario = driver.find_element(By.CLASS_NAME, "sumario")
        elementos = sumario.find_elements(By.TAG_NAME, "li")
        enlaces = [elemento.find_element(By.TAG_NAME, "a").get_attribute("href") 
                  for elemento in elementos]
        # Guardar enlaces
        with open(RUTA_SALIDA, modo_escritura, encoding="utf-8") as archivo:
            for enlace in enlaces:
                archivo.write(f"{enlace}\n") 
        logger.info(f"Descarga completada de la fecha: {fecha}")    
    except NoSuchElementException:
        logger.info(f"No hay Boletín para la fecha: {fecha}")
    except Exception as e:
        logger.ino(f"Error inesperado procesando la fecha {fecha}: {str(e)}")
def procesar_borme(input_fecha):
        """
    Procesa boletines del BORME (Boletín Oficial del Registro Mercantil) para una o múltiples fechas.

    Funcionalidad principal:
    - Si `input_fecha` es un archivo, procesa todas las fechas que contiene, extrayendo los enlaces 
      del BORME para cada una de ellas.
    - Si `input_fecha` es una cadena con una única fecha, extrae los enlaces del BORME para esa fecha específica.

    Args:
        input_fecha (str): 
            - Ruta de un archivo que contiene múltiples fechas (una por línea).
            - O una fecha individual en formato "dd/mm/aaaa".

    Logs:
        - Registra el inicio del proceso, el progreso de la extracción de enlaces y cualquier error 
          durante la ejecución.

    Exceptions:
        - Registra cualquier error inesperado que ocurra durante la ejecución del proceso.

    Returns:
        None: No devuelve ningún valor. Los enlaces se guardan en un archivo de texto.
    """
    dir="../data/logs/Spyderlogs"
    logger_instance=Logger("Practica12",dir)
    logger=logger_instance.launch_logging()
    try:
        driver = webdriver.Chrome()
        if os.path.isfile(input_fecha):
            # Procesar archivo con múltiples fechas
            with open(input_fecha, "r", encoding="utf-8") as archivo:
                for i, linea in enumerate(archivo):
                    fecha = linea.strip()
                    modo = 'w' if i == 0 else 'a'
                    extraer_enlaces_borme(driver, fecha, logger,modo)
        else:
            # Procesar fecha individual
            extraer_enlaces_borme(driver, input_fecha, logger,'w')
    except Exception as e:
        logger.info(f"Error en la ejecución: {str(e)}")
    finally:
        driver.quit()
if __name__ == "__main__":
    arguments = sys.argv
    procesar_borme(arguments[-1])