#!/usr/bin/env python
# coding: utf-8
from pypdf import PdfReader
import os
import jsonlines
import pathlib
import json
from os.path import exists, join
from os import makedirs
from utils.Loger import Logger
# Función para guardar los datos en un archivo JSON Lines
def save_nested_to_jsonlines(data, filename,logger):
    """Entra la lista con la informacion del pdf, en cada jsonlines se guarda un pdf
    """
    output_dir =  "../data/outputs/jsonlines"
    file_path = output_dir+"/"+f"{filename}.json"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                json_line = json.dumps(item, ensure_ascii=False)
                f.write(json_line + '\n')
    except Exception as e:
        logger.info(f"Error al guardar el archivo {filename}: {e}")
# Función para transformar los párrafos a diccionarios
def extraer_datos_constitucion(parrafo):
    """
    Extrae información estructurada de un párrafo relacionado con la constitución de una entidad.

    La función toma como entrada un párrafo de texto y devuelve un diccionario con 
    los siguientes campos:
    
    - "Id": código de la entidad.
    - "nombre": nombre de la entidad.
    - "Acto legal": tipo de acto legal relacionado con la constitución.
    - "Comienzo de operaciones": fecha o detalle del inicio de las operaciones.
    - "Domicilio": dirección de la entidad.
    - "Capital" (opcional): monto del capital, si está presente.
    - Otros campos: extrae también el campo correspondiente a "Objetivo social" o 
      cualquier otra clave que aparezca antes de "Domicilio".
      
    Args:
        parrafo (str): Párrafo de texto que contiene la información de la constitución.
    Returns:
        dict: Diccionario con la información extraída.
    Raises:
        ValueError: Si ocurre algún error durante el procesamiento del párrafo.
    """
    try:
        dicc = {}
        # Dividir el párrafo en secciones
        titulo, d = parrafo.split("Comienzo de operaciones:", 1)
        codigo, nombre = titulo.split("-", 1)
        nombre, acto_legal = nombre.split("\n", 1)
        
        dicc["Id"] = codigo.strip()
        dicc["nombre"] = nombre.strip()
        dicc["Acto legal"] = acto_legal.strip()

        # Procesar 'Comienzo de operaciones' y demás secciones
        operaciones, d = d.split(". ", 1)
        dicc["Comienzo de operaciones"] = operaciones.strip()

        d = d.replace("\n", "").strip()
        objetivo_social, d = d.split("Domicilio:", 1)
        key, value = objetivo_social.split(":", 1)
        dicc[key.strip()] = value.strip()

        domicilio, d = d.split("Capital", 1)
        dicc["Domicilio"] = domicilio.strip()
        try:
            c=d.split(",",1)[0]
            dicc["Capital"] = c.strip()
        except Exception as e:
            pass
        return dicc
    except Exception as e:
        raise ValueError(f"Error al procesar 'Constitución': {e}")
def extraer_datos_extincion(parrafo):
        """
    Extrae información estructurada de un párrafo relacionado con la extinción de una entidad.

    La función toma como entrada un párrafo de texto y devuelve un diccionario con 
    los siguientes campos:
    
    - "Id": código de la entidad.
    - "nombre": nombre de la entidad.
    - "Actolegal": siempre se establece con el valor "Extinción".
    - "Disolución" (opcional): fecha o detalle de la disolución, si está presente en el párrafo.

    Args:
        parrafo (str): Párrafo de texto que contiene la información de la extinción.
    Returns:
        dict: Diccionario con la información extraída.
    Raises:
        ValueError: Si ocurre algún error durante el procesamiento del párrafo.
    """
    try:
        dicc = {}
        r, d = parrafo.split("\n", 1)
        codigo, nombre = r.split("-", 1)

        dicc["Id"] = codigo.strip()
        dicc["nombre"] = nombre.strip()
        dicc["Actolegal"] = "Extinción"

        if "Disolución" in d:
            d = d.split("Disolución.", 1)[1]
            disolucion = d.split(".", 1)[0]
            dicc["Disolución"] = disolucion.strip()

        return dicc
    except Exception as e:
        raise ValueError(f"Error al procesar 'Extinción': {e}")

def parrafos_to_dict(parrafos, logger):
    """
    Convierte párrafos de texto del Boletín Oficial en diccionarios estructurados,
    procesando específicamente entradas de constitución y extinción de empresas.
    
    Esta función procesa cada párrafo y determina si contiene información sobre:
    - Constitución de nuevas empresas
    - Extinción de empresas existentes
    
    Args:
        parrafos (list): Lista de strings, cada uno conteniendo un párrafo del Boletín
                        Oficial que describe una constitución o extinción de empresa
        logger (Logger): Instancia del logger para registro de eventos y errores
        
    Returns:
        list: Lista de diccionarios, donde cada diccionario contiene la información
              estructurada de una constitución o extinción de empresa
              
    Raises:
        Exception: Captura y registra errores específicos durante el procesamiento
                  de cada párrafo, permitiendo continuar con el resto
    """
    lista = []
    for p in parrafos:
        if "Constitución" in p:
            try:
                dicc = extraer_datos_constitucion(p)
                lista.append(dicc)
            except Exception as e:
                logger.info(f"Error al procesar Constitución: {e}")
                continue
        elif "Extinción" in p:
            try:
                dicc = extraer_datos_extincion(p)
                lista.append(dicc)
            except Exception as e:
                logger.info(f"Error al procesar Extinción: {e}")
                continue
    return lista
# Función para leer el PDF y extraer los párrafos
def read_pdf(path, nombre, logger):
    """
    Lee y procesa un archivo PDF del Boletín Oficial, extrayendo y limpiando su contenido.

    Esta función realiza las siguientes operaciones:
    1. Lee el archivo PDF especificado
    2. Extrae el texto de todas las páginas
    3. Limpia el contenido eliminando cabeceras y líneas no deseadas
    4. Divide el texto en párrafos basándose en códigos numéricos
    5. Convierte los párrafos en diccionarios
    6. Guarda los resultados en formato jsonlines
    
    Args:
        path (str): Ruta del directorio donde se encuentra el archivo PDF
        nombre (str): Nombre del archivo PDF a procesar
        logger (Logger): Instancia del logger para registro de eventos
    Returns:
        None
    Raises:
        FileNotFoundError: Si el archivo PDF no existe en la ruta especificada
        PdfReadError: Si hay problemas al leer el archivo PDF
        Exception: Para otros errores durante el procesamiento

    """
    try:
        pdf_path = join(path, nombre)
        reader = PdfReader(pdf_path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        full_text="\n".join(text)
        # Limpiar y filtrar las líneas
        lines=full_text.split("\n")
        cleaned_lines = [
            line.strip() for line in lines if line.strip() and not line.startswith("BOLETÍN OFICIAL")
            and not line.startswith("Núm.") and not line.startswith("cv")
            and not line.startswith("Verificable en https://www.boe.es") and not line.startswith("https")]
        cleaned_lines = cleaned_lines[4:]  # Elimino las cabeceras
        cleaned_texto = "\n".join(cleaned_lines)  # Reagrupo las líneas
        # Dividir en párrafos
        parrafos = []
        num = int(cleaned_texto[0:6])  # Divido en base a los códigos
        while str(num) in cleaned_texto:
            cleaned_texto = cleaned_texto.split(str(num))
            parrafos.append(str(num) + cleaned_texto[0])
            cleaned_texto = cleaned_texto[1]
            num += 1
        # Transformar los párrafos en diccionarios
        lista = parrafos_to_dict(parrafos,logger)
        save_nested_to_jsonlines(lista, nombre,logger)
    except Exception as e:
        logger.info(f"Error al leer el PDF {nombre}: {e}")
# Función principal para ejecutar el proceso en todos los archivos PDF
def run():
    """Aqui se define el logger y se recojen todos los pdfs de la carpeta"""
    dir="../data/logs/Crawlerlogs"
    logger_instance=Logger("Practica12",dir)
    logger=logger_instance.launch_logging()
    ruta = "../data/outputs/PDF"
    archivos = os.listdir(ruta)
    for i in archivos:
        if i.endswith(".pdf") and not i.endswith("99.pdf"):  # Asegurarse de que sea un archivo PDF
            read_pdf(ruta, i,logger)
    logger.info("Proceso completado con éxito")
if __name__ == "__main__":
    run()
