El createvenv.py sirve para crear el entorno virtual con el requirements
en caso de perder el entorno virtual.

El proyecto tiene 5 ejecutables:
1. El Spyder que tiene como entrada una fecha o un fichero de texto y a la salida crea una lista de links que guarda en data/outputs/links.txt.
2. El Fetcher que no tiene ninguna entrada, lee los links del .txt creado por el spyder y guarda los .pdf en la carpeta data/outputs/PDF/.
3. El Crawler tampoco tiene entradas y su función es iterar por cada PDF y recopilar la informacion que le hemos especificado de cada uno y guardarlo
como .jsonl, crea un .jsonl por cada fichero y lo guarda con el nombre del pdf. Los .jsonl se guardan en data/outputs/jsonlines/.
4.El Wrangler tampoco tiene entradas, su función es reconvertir los jsonlines creados por el Crawler en ficheros csv, los guarda en data/outputs/csv/ .
5. El Main, es el que usaremos para conectar con el resto de ejecutables, y no llamarlos directamente.