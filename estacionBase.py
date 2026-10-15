import gzip #libreria para usar archivos .gz
import csv
import os
from geopy.distance import geodesic

estaciones_por_tipo = {}
listaEstaciones = []

class EstacionBase:
    """Constructor de estación base """
    def __init__(self, tipoRadio, mcc, mnc, lac, cellID, unit, longitud, latitud, rango, samples, changeables, created, updated, averageSignal):
        self.tipoRadio = tipoRadio
        self.mcc = mcc
        self.mnc = mnc
        self.lac = lac
        self.cellID = cellID
        self.unit = unit
        self.longitud = longitud
        self.latitud = latitud
        self.rango = rango
        self.samples = samples
        self.changeables = changeables
        self.created = created
        self.updated = updated
        self.averageSignal = averageSignal


def leerArchivoEstacionesBases(tipo_antena, nombreArchivo,longitudMax,longitudMin,latitudMax,latitudMin):

    estaciones_por_tipo.clear()
    listaEstaciones.clear()
    """Devuelve la lista de estaciones leídas de un archivo con extensión GZ"""

    ruta_al_archivo_gz = nombreArchivo
    bandera=False
    
    with gzip.open(ruta_al_archivo_gz, 'rt', encoding='utf-8') as archivo:

        for linea in archivo:
            try:
                partes = linea.strip().split(',')
                
                tipoRadio = partes[0]
                mcc = int(partes[1])
                mnc = int(partes[2])
                lac = int(partes[3])
                cellID = int(partes[4])
                unit = int(partes[5])

                longitudStr = partes[6]
                longitud = float(longitudStr)
                    
                latitudStr = partes[7]
                latitud = float(latitudStr)
                    
                rango = int(partes[8])
                samples = int(partes[9])
                changeables = int(partes[10])
                created = partes[11]
                updated = partes[12]
                averageSignal = int(partes[13])
                # FILTRADO DE ESTACIONES BASE #
                estacion_base = filtrarEstaciones(tipo_antena, longitudMax, longitudMin, latitudMax, latitudMin, tipoRadio, mcc, mnc, lac, cellID, unit, longitud, latitud, rango, samples, changeables, created, updated, averageSignal)
                if estacion_base:
                    listaEstaciones.append(estacion_base)
            except ValueError:
                continue
    return listaEstaciones

def guardarEstacionesProcesadas(listaEstaciones):
    """Construye un nuevo archivo CSV para guardar la lista de estaciones en el formato correcto."""
    nombre_archivo = 'estacionesBases.csv'
    if not os.path.exists('descargas'):
        ruta_completa = nombre_archivo
    else:
        ruta_completa = os.path.join('descargas', nombre_archivo)
    with open(ruta_completa, 'w', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
    # Escribe los datos de los objetos Estacion Base en el archivo CSV
        for estacion in listaEstaciones:
            escritor_csv.writerow([estacion.tipoRadio,estacion.mcc, estacion.mnc, estacion.lac, estacion.cellID, estacion.unit,estacion.longitud,estacion.latitud,estacion.rango,estacion.samples,estacion.changeables,estacion.created,estacion.updated,estacion.averageSignal])







def procesarEstaciones(nombreArchivo,tipo_antena,longitudMax,longitudMin,latitudMax,latitudMin):
    """Devuelve la lista de estaciones leídas de un archivo con extensión CSV"""
    with open(nombreArchivo, 'r') as archivo:
        lector_csv = csv.reader(archivo)
        for fila in lector_csv:
            # Convertir valores de la fila a tipos adecuados
            try:
                tipoRadio = fila[0]
                mcc = int(fila[1])
                mnc = int(fila[2])
                lac = int(fila[3])
                cellID = int(fila[4])
                unit = int(fila[5])
                longitud = float(fila[6])
                latitud = float(fila[7])
                rango = int(fila[8])
                samples = int(fila[9])
                changeables = int(fila[10])
                created = int(fila[11])
                updated = int(fila[12])
                averageSignal = int(fila[13])
                # FILTRADO DE ESTACIONES BASE #
                estacion_base = filtrarEstaciones(tipo_antena, longitudMax, longitudMin, latitudMax, latitudMin, tipoRadio, mcc, mnc, lac, cellID, unit, longitud, latitud, rango, samples, changeables, created, updated, averageSignal)
                if estacion_base:
                    listaEstaciones.append(estacion_base)
            except ValueError:
                continue
    return listaEstaciones



def filtrarEstaciones(tipo_antena, longitudMax, longitudMin, latitudMax, latitudMin, tipoRadio, mcc, mnc, lac, cellID, unit, longitud, latitud, rango, samples, changeables, created, updated, averageSignal):
    """Filtra las estaciones base que son adecuadas para el estudio"""
    if tipo_antena.lower() == "todas" or tipoRadio.lower() == tipo_antena.lower():
        if latitud < latitudMax and latitud > latitudMin and longitud < longitudMax and longitud > longitudMin:
            return EstacionBase(tipoRadio, mcc, mnc, lac, cellID, unit, longitud, latitud, rango, samples, changeables, created, updated, averageSignal)
    return None

def obtener_estacion_por_id_y_cercania(estacion_id,lat_punto, lon_punto,listaEstaciones):
    """Devuelve la estacion más cercana a una coordenada dada por parametros. Método útil en caso de haber varias estaciones base con el mismo ID."""
    estacion_con_mismo_id = [estacion for estacion in listaEstaciones if estacion.cellID == estacion_id]

    if not estacion_con_mismo_id:
        return None  # No se encontraron antenas con el ID dado

    estacion_mas_cercana = estacion_con_mismo_id[0]
    distancia_minima = geodesic((lat_punto, lon_punto), (estacion_mas_cercana.latitud, estacion_mas_cercana.longitud)).meters

    for estacion in estacion_con_mismo_id[1:]:
        distancia = geodesic((lat_punto, lon_punto), (estacion.latitud, estacion.longitud)).meters
        if distancia < distancia_minima:
            estacion_mas_cercana = estacion
            distancia_minima = distancia
            print("Nueva antena mas cercana: ", estacion_mas_cercana)
    print("Antena mas cercana: ", estacion_mas_cercana)
    return estacion_mas_cercana