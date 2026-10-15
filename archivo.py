import os
import shutil
import json
import zipfile

def obtener_ruta_archivo(tipo_archivo, extensiones_validas):
    """
    Devuelve la ruta y extensión del archivo proporcionado por el usuario que cumple los requisitos
    
    Parámetros:
    - tipo_archivo: Tipo del datos pedido por el sistema
    - extensiones_validas: Lista de extensiones permitidas
    
    Returns:
    - ruta: Ruta del archivo
    - extension: Extension del archivo
    """
    while True:
        ruta = input(f"Introduce la ruta del archivo {tipo_archivo}: ").strip()
        if os.path.isfile(ruta):
            extension = obtener_extension_archivo(ruta)
            if extension in extensiones_validas:
                return ruta, extension
            else:
                print(f"Archivo no válido. Por favor, introduce un archivo con una de las siguientes extensiones: {', '.join(extensiones_validas)}.")
        else:
            print("Ruta no válida. Por favor, introduce una ruta de archivo válida.")

def obtener_extension_archivo(ruta):
    """
    Devuelve la extensión de un archivo
    
    Parámetros:
    - ruta: Ruta del archivo

    """
    return os.path.splitext(ruta)[1][1:].lower()



def recrear_carpeta(carpeta):
    """
    Elimina y vuelve a crear vacía una carpeta existente del equipo
    
    Parámetros:
    - carpeta: Nombre de la carpeta a recrear
    
    """
    carpeta_absoluta = os.path.abspath(carpeta)
    try:
        # Se elimina la carpeta si existe
        shutil.rmtree(carpeta_absoluta)
        print(f"Carpeta '{carpeta}' eliminada correctamente.")
    except FileNotFoundError:
        print(f"Carpeta '{carpeta}' no encontrada.")
    
    # Se crea la carpeta vacía
    os.makedirs(carpeta)
    print(f"Carpeta '{carpeta}' creada vacía.")



def mostrar_opciones_predeterminadas():
    """
    Devuelve las opciones seleccionadas por el usuario entre dos opciones predeterminadas:
    - Gráficas
    - Información de simulación
    
    Retorna:
    - seleccionados: Opciones seleccionadas por el usuario
    """
    opciones = ["Gráficas", "Información de simulación"]
    print("Opciones disponibles:")
    for i, opcion in enumerate(opciones, start=1):
        print(f"{i}. {opcion}")

    seleccionados = []
    while True:
        seleccion = input("Seleccione las opciones por número separadas por coma (o 'listo' para finalizar): ").strip()
        if seleccion.lower() == 'listo':
            break
        numeros_seleccionados = [int(num.strip()) for num in seleccion.split(',') if num.strip().isdigit()]
        seleccionados.extend([opciones[num - 1] for num in numeros_seleccionados if 0 < num <= len(opciones)])
    return seleccionados

def mover_archivo(origen, destino):
    """
    Mueve los archivos de una carpeta a otra
    
    Parámetros:
    - origen: Origen del archivo
    - destino: Destino del archivo

    """
    shutil.move(origen, destino)
    print(f"El archivo ha sido movido de {origen} a {destino}.")



def descargar_archivos(seleccion, destino=None):
    """
    Crea y descarga un archivo ZIP con los archivos seleccionados.
    
    Parámetros:
    - seleccion: Lista de archivos a descargar.
    - destino: Ruta de destino donde se guardará el archivo ZIP (opcional).
    """
    lista = os.listdir('descargas')
    nombre_zip = "informe.zip"

    if destino and os.path.isdir(destino):
        ruta_zip = os.path.join(destino, nombre_zip)
    else:
        print("Ruta no válida, guardando en el escritorio...")
        ruta_zip = os.path.join(os.path.expanduser('~'), 'Desktop', nombre_zip)

    with zipfile.ZipFile(ruta_zip, 'w') as zipf:
        for archivo in seleccion:
            if archivo in lista:
                ruta_archivo = os.path.join('descargas', archivo)
                zipf.write(ruta_archivo, os.path.basename(ruta_archivo))

    print(f"Descarga lista en: {ruta_zip}")


def guardar_datos_en_archivo(datos, nombre_archivo='datosPrecarga.json'):
    """
    Devuelve la ruta y extensión del archivo proporcionado por el usuario que cumple los requisitos
    
    Parámetros:
    - tipo_archivo: Tipo del datos pedido por el sistema
    - extensiones_validas: Lista de extensiones permitidas
    
    Returns:
    - ruta: Ruta del archivo
    - extension: Extension del archivo
    """
    if 'precarga' in nombre_archivo.lower():
        carpeta_destino = 'precarga'
    else:
        carpeta_destino = 'descargas'
    if not os.path.exists(carpeta_destino):
        ruta_completa = nombre_archivo
    else:
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
    with open(ruta_completa, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo,ensure_ascii=False, indent=4)

def cargar_datos_desde_archivo(nombre_archivo='datosPrecarga.json'):
    """
    Devuelve la ruta y extensión del archivo proporcionado por el usuario que cumple los requisitos
    
    Parámetros:
    - tipo_archivo: Tipo del datos pedido por el sistema
    - extensiones_validas: Lista de extensiones permitidas
    
    Returns:
    - ruta: Ruta del archivo
    - extension: Extension del archivo
    """
    ruta_archivo = os.path.join('precarga', nombre_archivo)
    try:
        with open(ruta_archivo, 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return None