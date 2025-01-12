#!/usr/bin/env python
# coding: utf-8
import json
import csv
from datetime import datetime
import os
from utils.Loger import Logger
def clean_datos(lista_datos,logger):
    """
    Procesa y limpia una lista de datos de empresas, normalizando caracteres especiales
    y estructurando la información en un formato consistente.

    Args:
        lista_datos (list): Lista de diccionarios con información de empresas.

    Returns:
        list: Lista de diccionarios con los datos procesados y estructurados.
        
    Raises:
        ValueError: Si la lista de entrada está vacía o no es válida
        TypeError: Si los datos no tienen el formato esperado
    """
    if not lista_datos or not isinstance(lista_datos, list):
        raise ValueError("La lista de datos está vacía o no es válida")
    new_lista = []
    for indice, datos in enumerate(lista_datos):
        try:
            if not isinstance(datos, dict):
                logger.warning(f"Elemento {indice} no es un diccionario, se omite")
                continue
            new_dict = {}
            for clave, valor in datos.items():
                try:
                    if not isinstance(valor, str):
                        logger.warning(f"Valor no string en clave {clave}, se convierte a string")
                        valor = str(valor)
                    # Limpieza de caracteres especiales
                    clave = clave.replace("Ã³", "ó")
                    valor = valor.replace("Ã³", "ó")
                    valor = valor.replace("Ã'", "Ñ")
                    valor = valor.replace("Ã\xad", "í")
                    valor = valor.replace("Ãº", "ú")
                    valor = valor.replace(",", "")
                    # Procesamiento de fecha de operaciones
                    if clave == "Comienzo de operaciones":
                        try:
                            valor = datetime.strptime(valor, '%d.%m.%y').date()
                            new_dict["ComienzoDeOperaciones"] = valor
                        except ValueError as e:
                            logger.error(f"Error al procesar fecha de operaciones: {e}")
                            new_dict["ComienzoDeOperaciones"] = None

                    # Procesamiento de capital
                    elif clave == "Capital":
                        try:
                            valor = valor.split(":", 1)[1]
                            valor = int(valor.replace(".", ""))
                            new_dict["CapitalSocial"] = valor
                        except (ValueError, IndexError) as e:
                            logger.error(f"Error al procesar capital: {e}")
                            new_dict["CapitalSocial"] = None
                    # Procesamiento de nombre y tipo de sociedad
                    elif clave == 'nombre':
                        new_dict["Nombre"] = valor
                        if "SL." in valor:
                            new_dict["TipoDeSociedad"] = "Sociedad Limitada"
                        elif "SA." in valor:
                            new_dict["TipoDeSociedad"] = "Sociedad Anonima"
                        else:
                            new_dict["TipoDeSociedad"] = "No especificado"
                    # Procesamiento de domicilio
                    elif clave == "Domicilio":
                        try:
                            new_dict["DomicilioCompleto"] = valor
                            via = "No especificada"
                            # Separar ciudad
                            try:
                                [valor, ciudad] = valor.split("(", 1)
                                ciudad = ciudad.replace(")", "")
                                new_dict["Ciudad"] = ciudad.lower()
                            except ValueError:
                                logger.warning("No se pudo extraer la ciudad del domicilio")
                                new_dict["Ciudad"] = None
                            # Identificar tipo de vía
                            if valor[0:2] == "C/":
                                via = "Calle"
                                valor = valor.replace("C/", "")
                            elif valor[0:5] == "PLAZA":
                                via = "Plaza"
                            elif valor[0:4] == "CTRA":
                                via = "Carretera"
                            elif valor[0:4] == "AVDA":
                                via = "Avenida"
                            elif valor[0:5] == "PASEO":
                                via = "Paseo"
                            new_dict["Tipodevia"] = via
                            # Extraer número y nombre de vía
                            palabras = valor.split(" ")
                            nombre_via = ""
                            numero = None
                            for palabra in palabras:
                                if palabra.isdigit():
                                    numero = int(palabra)
                                    break
                                else:
                                    nombre_via += palabra + " "
                            new_dict["Numero"] = numero
                            new_dict["Nombredevia"] = nombre_via.lower().strip()
                        except Exception as e:
                            logger.error(f"Error al procesar domicilio: {e}")
                            new_dict["DomicilioCompleto"] = valor
                            new_dict["Ciudad"] = None
                            new_dict["Tipodevia"] = None
                            new_dict["Numero"] = None
                            new_dict["Nombredevia"] = None
                except Exception as e:
                    logger.error(f"Error al procesar clave {clave}: {e}")
                    continue
            new_lista.append(new_dict)
        except Exception as e:
            logger.error(f"Error al procesar registro {indice}: {e}")
            continue
    return new_lista
def list_to_csv(nombre_archivo, datos,logger):
    """
    Convierte una lista de diccionarios a un archivo CSV.
    
    Args:
        nombre_archivo (str): Nombre del archivo a crear
        datos (list): Lista de diccionarios con los datos a escribir
        
    Raises:
        ValueError: Si los datos de entrada no son válidos
        OSError: Si hay problemas con la escritura del archivo
    """
    try:
        # Validación de parámetros de entrada
        if not nombre_archivo:
            raise ValueError("El nombre del archivo no puede estar vacío")
        if not datos or not isinstance(datos, list):
            raise ValueError("Los datos deben ser una lista no vacía")
            
        campos = ["Nombre", "TipoDeSociedad", "ComienzoDeOperaciones", 
                 'DomicilioCompleto', 'Ciudad', 'Tipodevia', 'Numero', 
                 'Nombredevia', 'CapitalSocial']
        path = "../data/outputs/csv/"
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logger.error(f"Error al crear el directorio {path}: {e}")
            raise
        archivo_path = os.path.join(path, f"{nombre_archivo}.csv")
        try:
            with open(archivo_path, mode="w", newline="", encoding='utf-8') as archivo:
                escritor = csv.DictWriter(archivo, fieldnames=campos)
                try:
                    escritor.writeheader()
                    for i, fila in enumerate(datos, 1):
                        try:
                            fila_procesada = {campo: fila.get(campo, 'None') for campo in campos}
                            escritor.writerow(fila_procesada)
                        except Exception as e:
                            logger.error(f"Error procesando fila {i}: {e}")
                            continue
                    # Registro de estadísticas
                    logger.info(f"Archivo {archivo_path} creado exitosamente")
                except csv.Error as e:
                    logger.error(f"Error escribiendo CSV: {e}")
                    raise
        except PermissionError:
            logger.error(f"Error de permisos al escribir en {archivo_path}")
            raise
        except OSError as e:
            logger.error(f"Error de E/S escribiendo archivo {archivo_path}: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Error general en list_to_csv: {e}")
        raise
def run():
    """
    Procesa archivos jsonlines de un directorio, limpia los datos y los convierte a CSV.
    Incluye manejo de errores para operaciones de archivos y procesamiento de datos.
    """
    dir="../data/logs/Wranglerlogs"
    logger_instance=Logger("Practica12",dir)
    logger=logger_instance.launch_logging()
    try:
        ruta = "../data/outputs/jsonlines"
        # Verificar si el directorio existe
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"El directorio {ruta} no existe")
        # Listar archivos del directorio
        try:
            archivos = os.listdir(ruta)
            if not archivos:
                logger.error(f"Advertencia: No se encontraron archivos en {ruta}")
                return
        except PermissionError as e:
            logger.error(f"Error de permisos al acceder al directorio: {e}")
            return
        # Procesar cada archivo
        for a in archivos:
            lista_datos = []
            archivo_path = os.path.join(ruta, a)
            try:
                with open(archivo_path, 'r', encoding='utf-8') as archivo:
                    for num_linea, linea in enumerate(archivo, 1):
                        try:
                            datos = json.loads(linea.strip())
                            lista_datos.append(datos)
                        except json.JSONDecodeError as e:
                            logger.error(f"Error al decodificar JSON en archivo {a}, línea {num_linea}: {e}")
                            continue
                        except Exception as e:
                            logger.error(f"Error inesperado procesando línea {num_linea} en {a}: {e}")
                            continue
                # Procesar datos solo si se cargaron correctamente
                if lista_datos:
                    try:
                        new_lista = clean_datos(lista_datos,logger)
                        list_to_csv(a, new_lista,logger)
                    except Exception as e:
                        logger.error(f"Error al procesar datos del archivo {a}: {e}")
                else:
                    logger.error(f"No se pudieron cargar datos del archivo {a}")
                    
            except FileNotFoundError:
                logger.error(f"No se encontró el archivo: {archivo_path}")
            except PermissionError:
                logger.error(f"Error de permisos al acceder al archivo: {archivo_path}")
            except Exception as e:
                logger.error(f"Error inesperado al procesar el archivo {a}: {e}")
    except Exception as e:
        logger.error(f"Error general en la ejecución: {e}")
if __name__ == "__main__":
    run()