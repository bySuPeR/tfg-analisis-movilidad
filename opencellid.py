import os
import requests
import csv 
import math
import sys
from dotenv import load_dotenv
load_dotenv()

class EstacionBaseOpenCellID:
    """Constructor de estación base recogida en la API de OpenCellID"""
    def __init__(self, tipoRadio, cellID, longitud, latitud):
        self.tipoRadio = tipoRadio
        self.cellID = cellID
        self.longitud = longitud
        self.latitud = latitud

api_key = os.getenv("OPENCELLID_API_KEY")


def calcular_total_celdas(latitudMin,latitudMax,longitudMin,longitudMax):
    """Calcula el número total de celdas en las que se divide el mapa de la ciudad de estudio. Esto se debe a la limitación de la API de OpenCellID"""
    tamano_celda = 3500000
    total_celdas = 0
    latitud_actual = latitudMin
    while latitud_actual < latitudMax:
        longitud_actual = longitudMin
        while longitud_actual < longitudMax:
            total_celdas += 1
            longitud_actual += math.sqrt(tamano_celda) / (111000 * math.cos(latitud_actual * math.pi / 180))
        latitud_actual += math.sqrt(tamano_celda) / 111000
    return total_celdas


def leer_estaciones_base_csv(input_file,latitudMin,latitudMax,longitudMin,longitudMax):
    """Devuelve la lista de estaciones base de un archivo con extensión CSV"""
    estaciones_base = []
    with open(input_file, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                latitud = float(row[0])
                longitud = float(row[1])
                if latitud<latitudMax and latitud>latitudMin and longitud<longitudMax and longitud>longitudMin:
                    cellID = int(row[2])
                    tipoRadio = row[3]
                    estacion_base = EstacionBaseOpenCellID(tipoRadio, cellID, longitud, latitud)
                    print("Tipo: ", estacion_base.tipoRadio)
                    print("ID: ", estacion_base.cellID)
                    print("longitud: ", estacion_base.longitud)
                    print("latitud: ", estacion_base.latitud)
                    estaciones_base.append(estacion_base)
            except ValueError:
                continue
    return estaciones_base


def dividir_area(latitudMin, longitudMin, latitudMax, longitudMax, tamano_celda):
    """Divide el mapa de la ciudad de estudio en pequeñas celdas iguales. Esto se debe a la limitación de la API de OpenCellID"""
    latitud_actual = latitudMin
    while latitud_actual < latitudMax:
        longitud_actual = longitudMin
        while longitud_actual < longitudMax:
            lat_max_celda = min(latitud_actual + math.sqrt(tamano_celda) / 111000, latitudMax)
            lon_max_celda = min(longitud_actual + math.sqrt(tamano_celda) / (111000 * math.cos(latitud_actual * math.pi / 180)), longitudMax)
            print(latitud_actual, longitud_actual, lat_max_celda, lon_max_celda)
            yield latitud_actual, longitud_actual, lat_max_celda, lon_max_celda
            longitud_actual = lon_max_celda
        latitud_actual = lat_max_celda




def obtener_estaciones_base(url, params):
    """Método auxiliar que devuelve una lista parcial de estaciones base (sólo referente a la celda solicitada). Realiza una solicitud a la API de OpenCellID para obtenerlas"""
    estaciones_base = []
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.text.splitlines()
            for row in csv.reader(data):
                print(row)
                try:
                    latitud = float(row[0])
                    longitud = float(row[1])
                    cellID = int(row[5])
                    tipoRadio = row[10]
                    if tipoRadio in {"GSM", "LTE", "UMTS"}:
                        estacion_base = EstacionBaseOpenCellID(tipoRadio, cellID, longitud, latitud)
                        estaciones_base.append(estacion_base)
                except ValueError:
                    continue
        else:
            print(f"Error en la solicitud: {response.status_code}")

    except requests.RequestException as e:
        print(f"Error en la solicitud. Se ha agotado el número de solicitudes diarias: {e}")
        sys.exit(1)  # Termina el programa con código de error 1
    return estaciones_base

def escribir_estaciones_base_csv(url, output_file, total_celdas,latitudMin,latitudMax,longitudMin,longitudMax,tipo_antena):
    """Devuelve la lista de estaciones base al completo. Realiza las solicitudes necesarias a la API de OpenCellID para obtener todas."""
    global api_key
    tamano_celda = 3500000
    listaEstaciones = []
    if not os.path.exists('descargas'):
        ruta_completa = output_file
    else:
        ruta_completa = os.path.join('descargas', output_file)

    with open(ruta_completa, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        num_celda = 1
        print("Entra")
        for lat_min, lon_min, lat_max, lon_max in dividir_area(latitudMin, longitudMin, latitudMax, longitudMax, tamano_celda):
            print(f"Solicitando datos para la celda {num_celda}...de {total_celdas}")
            params = {
                "key": api_key,
                "BBOX": f"{lat_min},{lon_min},{lat_max},{lon_max}",
                "format": "csv"  
            }
            if tipo_antena.lower() != "todas":
                print("Entra Toda")
                params["radio"] = tipo_antena
            estaciones_base_celda = obtener_estaciones_base(url, params)
            for estacion_base in estaciones_base_celda:
                writer.writerow([estacion_base.latitud, estacion_base.longitud, estacion_base.cellID, estacion_base.tipoRadio])
                listaEstaciones.append(estacion_base)
            num_celda += 1
        print("Todas las solicitudes completadas.")
    return listaEstaciones








