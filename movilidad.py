import csv
import folium
import math
import os
from datetime import datetime
import pandas as pd
import requests
import polyline
import rutasValhalla
from geopy.distance import geodesic
from folium import plugins
import pandas as pd
from datetime import timedelta 
from requests.exceptions import ConnectionError, Timeout
from dotenv import load_dotenv
import sys
load_dotenv()
rutas_json = {}

class Humano:
    """Constructor de humano"""
    def __init__(self, idHumano,tiempo, latitud, longitud, señalHumano):
        self.idHumano = idHumano
        self.tiempo = tiempo
        self.latitud = latitud
        self.longitud = longitud
        self.señalHumano = señalHumano

class Taxi:
    """Constructor de taxi"""
    def __init__(self, señalTaxi, idTaxi, dia, hora, latitud, longitud):
        self.señalTaxi = señalTaxi
        self.idTaxi = idTaxi
        self.dia = dia
        self.hora= hora
        self.latitud = float(latitud)
        self.longitud = float(longitud)
        




token = os.getenv("MAPBOX_ACCESS_TOKEN")
listaTaxis = []


##################HUMANOS##################


def leer_datos_desde_txt(archivoMovilidad, latitud_ref, longitud_ref, id_prefix):
    """Devuelve la lista de humanos leídos de un archivo con extensión TXT"""
    global rutas_json
    rutas_json.clear()
    datos = []
    i = 1
    with open(archivoMovilidad, 'r') as file:
        for line in file:
            try:
                parts = line.split()
                tiempo = float(parts[0])
                coord_x_metros = float(parts[1])
                coord_y_metros = float(parts[2])

                # Convertir coordenadas de metros a grados decimales
                latitud_decimal = latitud_ref + (coord_x_metros / 111111)
                longitud_decimal = longitud_ref + (coord_y_metros / (111111 * math.cos(latitud_ref * math.pi / 180)))

                datos.append(Humano(f"{id_prefix}{i}", tiempo, latitud_decimal, longitud_decimal, i))
                i += 1
            except ValueError:
                continue
    return datos



def leer_datos_desde_csv(archivoMovilidad):
    """Devuelve la lista de humanos leídos de un archivo con extensión CSV"""
    datos = []
    i=1
    with open(archivoMovilidad, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                id_str = row[0]
                tiempo = float(row[1])
                latitud = float(row[2])
                longitud = float(row[3])

                datos.append(Humano(id_str, tiempo, latitud, longitud, i))
                i += 1
            except ValueError:
                continue
    return datos



def guardar_datos_en_csv(datos):
    """Construye un nuevo archivo CSV para guardar la lista de señales humanas en el formato correcto."""
    nombre_archivo = 'datosHumanos.csv'
    if not os.path.exists('descargas'):
        ruta_completa = nombre_archivo
    else:
        ruta_completa = os.path.join('descargas', nombre_archivo)
    with open(ruta_completa, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Tiempo', 'Latitud', 'Longitud'])  # Agregar un encabezado con el ID
        for humano in datos:
            # Se convierte cada objeto Humano en una lista o tupla con los datos a escribir en el CSV
            data_row = [humano.idHumano, humano.tiempo, humano.latitud, humano.longitud, humano.señalHumano]
            writer.writerow(data_row)




##################TAXIS##################

def leerArchivoTaxi(diaMin,diaMax, horaMin, horaMax, nombreArchivo):
    """Devuelve la lista de taxis leídos de un archivo con extensión CSV"""
    listaTaxis = []
    i = 1
    horaFiltroMax = horaMax
    horaFiltroMin = horaMin
    horaFiltroTimeMax = datetime.strptime(horaFiltroMax, "%H:%M:%S").time()
    horaFiltroTimeMin = datetime.strptime(horaFiltroMin, "%H:%M:%S").time()
    diaFiltroMin = diaMin
    diaFiltroMax=diaMax

    with open(nombreArchivo, 'r') as archivo:
        reader = csv.reader(archivo)
        lineas = list(reader)
        if lineas:
            lineas = lineas[1:]
        lineas_ordenadas = ordenar_lineas_por_fecha_hora(lineas, diaMin,diaMax, horaMin, horaMax)
        total_lineas = len(lineas_ordenadas)
        inicio = 0
        fin = total_lineas - 1
        # Si no hay líneas ordenadas, la lista estará vacía
        if total_lineas == 0:
            print("Error: No se encontraron taxis en el intervalo de tiempo especificado.")
            sys.exit(0)
        inicio, dia, horaTaxi = busquedaBinaria(lineas_ordenadas, inicio, fin, diaFiltroMin, horaFiltroTimeMin)
        inicio = ajusteInicio(lineas_ordenadas, inicio, dia, horaTaxi)  # necesario al encontrar taxis con el mismo día y hora

        for linea in lineas_ordenadas[inicio:]:
            try:
                idTaxi = linea[0]
                dia = linea[1]
                hora = linea[2]
                latitud = linea[3]
                longitud = linea[4]

                fecha_dia_hora = f"{dia} {hora}"
                horaTaxi = datetime.strptime(hora, "%H:%M:%S").time()
                if diaFiltroMin <= dia <= diaFiltroMax and horaFiltroTimeMin <= horaTaxi <= horaFiltroTimeMax:
                    señalTaxi = i
                    taxi = Taxi(señalTaxi, idTaxi, dia, hora, latitud, longitud)
                    listaTaxis.append(taxi)
                    i += 1
                elif horaTaxi > horaFiltroTimeMax:
                    break
            except ValueError:
                continue

    print(f"Número total de taxis encontrados: {len(listaTaxis)}")
    return listaTaxis

def ordenar_lineas_por_fecha_hora(lineas, diaMin,diaMax, horaMin, horaMax):
    """Ordena las líneas del archivo CSV por los parámetros fecha y hora"""
    def extraer_fecha_hora(linea):
        """Combina la fecha y la hora de una línea concreta del archivo"""
        try:
            fecha = linea[1]
            hora = linea[2]
            # Convertir fecha y hora a datetime para validación
            fecha_datetime = datetime.strptime(fecha, "%Y-%m-%d").date()
            fecha_min_date = datetime.strptime(diaMin, "%Y-%m-%d").date()
            fecha_max_date = datetime.strptime(diaMax, "%Y-%m-%d").date()

            hora_datetime = datetime.strptime(hora, "%H:%M:%S").time()

            # Convertir horaMin y horaMax a objetos time
            hora_min_time = datetime.strptime(horaMin, "%H:%M:%S").time()
            hora_max_time = datetime.strptime(horaMax, "%H:%M:%S").time()

            if fecha_min_date <= fecha_datetime <= fecha_max_date and hora_min_time <= hora_datetime <= hora_max_time:
                return datetime.combine(fecha_datetime, hora_datetime)
        except (IndexError, ValueError) as e:
            print(f"Error al procesar la línea: {linea}. Error: {e}")
            return None

    lineas_validas = [linea for linea in lineas if extraer_fecha_hora(linea) is not None]
    print(len(lineas_validas))
    return sorted(lineas_validas, key=extraer_fecha_hora)

def busquedaBinaria(lineas, inicio, fin, diaFiltro, horaFiltroTimeMin):
    """Realiza una búsqueda binaria para encontrar el inicio del intervalo de estudio en el archivo ordenado de los taxis."""
    while inicio <= fin:
        medio = (inicio + fin) // 2
        partes = lineas[medio]
        print(partes)
        fecha = partes[1]
        print(fecha)
        hora = partes[2]
        print(hora)
        horaTaxi = datetime.strptime(hora, "%H:%M:%S").time()
        print(f"Medio: {medio}, Dia: {fecha}, Hora Taxi: {horaTaxi}, Hora Filtro Min: {horaFiltroTimeMin}")
        if fecha < diaFiltro:
            inicio = medio + 1
        elif fecha > diaFiltro:
            fin = medio - 1
        elif horaTaxi < horaFiltroTimeMin:
            inicio = medio + 1
        elif horaTaxi > horaFiltroTimeMin:
            fin = medio - 1
        else:
            inicio = medio
            break
    return inicio, fecha, horaTaxi

def ajusteInicio(lineas, inicio, diaFiltro, horaFiltroTimeMin):
    """Realiza un pequeño ajuste necesario de la búsqueda binaria. Es necesario en caso de haber señales de taxi recogidos a la misma fecha y hora. """
    while inicio > 0:
        partes = lineas[inicio]
        fecha = partes[1]
        hora = partes[2]
        horaTaxi = datetime.strptime(hora, "%H:%M:%S").time()
        print(f"Inicio: {inicio}, Dia: {fecha}, Hora Taxi: {horaTaxi}, Hora Filtro Min: {horaFiltroTimeMin}")
        if fecha == diaFiltro and horaTaxi == horaFiltroTimeMin:
            inicio -= 1
        else:
            break
    return inicio + 1


def guardarTaxisProcesados(listaTaxis):
    """Construye un nuevo archivo CSV para guardar la lista de señales de taxis en el formato correcto."""
    nombre_archivo = 'taxis.csv'
    if not os.path.exists('descargas'):
        ruta_completa = nombre_archivo
    else:
        ruta_completa = os.path.join('descargas', nombre_archivo)
    
    with open(ruta_completa, 'w', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow(['SenalTaxi','idTaxi', 'dia', 'hora', 'latitud', 'longitud'])
    # Escribe los datos de los objetos Taxi en el archivo CSV
        for taxi in listaTaxis:
            escritor_csv.writerow([taxi.señalTaxi, taxi.idTaxi, taxi.dia, taxi.hora, taxi.latitud, taxi.longitud])







def procesarTaxis():
    """Devuelve la lista de estaciones leídas de un archivo con extensión CSV"""
    with open("taxis.csv", 'r') as archivo:
        lector_csv = csv.reader(archivo)
        next(lector_csv)
    
        for fila in lector_csv:
            # Convertir valores de la fila a tipos adecuados
            señalTaxi = int(fila[0])
            idTaxi = int(fila[1])
            dia = fila[2]
            hora = fila[3]
            latitud = float(fila[4])
            longitud = float(fila[5])
            

        # Crear una instancia de la clase Taxi y agregarla a la lista
            taxi=Taxi(señalTaxi, idTaxi, dia, hora, latitud, longitud)
            listaTaxis.append(taxi)
    return listaTaxis


def crearRutasTaxis(listaTaxis,umbral_segundos=40):
    """
    Divide las rutas de los taxis basado en un umbral de tiempo de inactividad.
    
    Parametros:
    - taxis: lista de diccionarios con las señales de los taxis.
    - umbral_segundos: tiempo de inactividad en segundos para dividir las rutas.
    
    Returns:
    - rutas: diccionario con las rutas de cada taxi.
    """
    datos = [(taxi.señalTaxi, taxi.idTaxi, taxi.dia, taxi.hora, taxi.latitud, taxi.longitud) for taxi in listaTaxis]
    df = pd.DataFrame(datos, columns=['señalTaxi', 'idTaxi', 'dia', 'hora', 'latitud', 'longitud'])
    # Se convierte la columna 'dia' y 'hora' en un solo datetime
    df['datetime'] = pd.to_datetime(df['dia'] + ' ' + df['hora'])
    # Se ordena por ID y datetime
    df = df.sort_values(by=['idTaxi', 'datetime'])
    # Se define un umbral de tiempo de inactividad para dividir rutas (por ejemplo, 40 segundos)
    umbral_tiempo = timedelta(seconds=umbral_segundos)

    rutas = {}

    for taxi_id, grupo in df.groupby('idTaxi'):
        ruta_actual = []
        rutas[taxi_id] = []
        tiempo_anterior = None

        for idx, row in grupo.iterrows():
            if tiempo_anterior is not None:
                # Se calcula la diferencia de tiempo
                diferencia_tiempo = row['datetime'] - tiempo_anterior
                
                # Si la diferencia de tiempo es mayor que el umbral, se inicia una nueva ruta
                if diferencia_tiempo > umbral_tiempo:
                    rutas[taxi_id].append(ruta_actual)
                    ruta_actual = []
            
            # Se agrega el punto actual a la ruta
            ruta_actual.append((row['latitud'], row['longitud']))
            
            # Se actualiza el tiempo anterior
            tiempo_anterior = row['datetime']
        
        # Se agrega la última ruta
        if ruta_actual:
            rutas[taxi_id].append(ruta_actual)

        global rutas_json
        carretera_numero = 1

        for taxi_id, rutas_taxi in rutas.items():
            for ruta in rutas_taxi:
                rutas_json[f'Carretera {carretera_numero}'] = {
                    "Cantidad de puntos reales": len(ruta),
                    "Puntos reales": ruta,
                    "Cantidad de puntos calculados Valhalla": 0,
                    "Puntos calculados Valhalla": [],
                    "Cantidad de puntos ruta calculada": 0,
                    "Puntos de la ruta calculada": []
                }
                carretera_numero += 1
        
    return rutas

def colocarRutas(rutas, mapa, modo):

    """
    Coloca las rutas seguidas por los taxi en una nueva capa de información en el mapa de Folium
    
    Parámetros:
    - rutas: Rutas de los taxis / trazas de humanos estudiadas
    - mapa: Mapa de Folium al que se le va a añadir la nueva capa de información
    - modo: Entero que recoge el tipo de movilidad estudiada.
    
    Returns:
    - mapa: Mapa de folium con la nueva capa añadida
    - rutas_json: Diccionario creado con información sobre las rutas
    """
    rutasMapa = folium.FeatureGroup(name='Rutas Movilidad', show=False)
    carretera_numero = 1
    for id , lista_rutas in rutas.items():
        if modo==1:
            print(f'Taxi ID: {id}')
        elif modo==2:
            print(f'Humano ID: {id}')
            # Si es humano, lista_rutas es una sola ruta
            lista_rutas = [lista_rutas]

        for i, ruta in enumerate(lista_rutas):
            print(f'  Procesando Ruta {i+1}')
            
            points_dataset = [(lon, lat) for lat, lon in ruta]
            df_trip = pd.DataFrame(points_dataset, columns=['lon', 'lat'])

            meili_request_body = rutasValhalla.crear_solicitud_meli_desde_puntos(df_trip, modo)
            headers = {'Content-type': 'application/json'}
            trace_url = "http://localhost:8002/trace_attributes"
            try:
                # Se envía la solicitud a Valhalla y se obtiene la respuesta
                r = requests.post(trace_url, data=str(meili_request_body), headers=headers, timeout=10)
                r.raise_for_status()  # Se lanza una excepción si la solicitud no tuvo éxito (HTTP Error)
                response_text = r.json()
            
                if 'shape' in response_text:
                    # Se decodifica la polilínea de la respuesta
                    matched_points = polyline.decode(response_text['shape'], 6)

                    # Se crea un DataFrame con los puntos coincidentes
                    matched_df = pd.DataFrame(matched_points, columns=["lat", "lon"])

                    final_route_coords = []

                    for i in range(len(matched_df) - 1):
                        point1 = (matched_df.loc[i, 'lat'], matched_df.loc[i, 'lon'])
                        point2 = (matched_df.loc[i + 1, 'lat'], matched_df.loc[i + 1, 'lon'])
                        distance = geodesic(point1, point2).meters
                        if distance <= 100:
                            final_route_coords.append(point1)
                        else:
                            best_route = rutasValhalla.obtener_mejor_ruta_mapbox(point1, point2, token, modo)
                            if best_route:
                                final_route_coords.extend(best_route)

                    # se añade el último punto
                    final_route_coords.append((matched_df.iloc[-1]['lat'], matched_df.iloc[-1]['lon']))

                    # Se la ruta calculada al mapa de Folium
                    plugins.AntPath(locations=final_route_coords, color='red', delay=1000, dash_array=[50, 100]).add_to(rutasMapa)


                    global rutas_json
                    ruta_info = rutas_json[f'Carretera {carretera_numero}']
                    ruta_info["Cantidad de puntos calculados Valhalla"] = len(matched_points)
                    ruta_info["Puntos calculados Valhalla"] = matched_points
                    ruta_info["Cantidad de puntos ruta calculada"] = len(final_route_coords)
                    ruta_info["Puntos de la ruta calculada"] = final_route_coords
                    carretera_numero += 1 
                else:
                    print("La respuesta no contiene la clave 'shape'")


            except ConnectionError:
                print(f"No se pudo establecer una conexión con el servidor Valhalla en {trace_url}.")
                return mapa, None  # No continuar si falla la conexión

            except Timeout:
                print("La solicitud a Valhalla ha excedido el tiempo de espera.")
                return mapa, None  # No continuar si falla por timeout
            except ValueError:
                print("No hay ruta posible")
    rutasMapa.add_to(mapa)
    return mapa, rutas_json




def crearRutasHumanos(listaHumanos):
    """
    Crea rutas para cada humano basado en sus datos de tiempo, latitud y longitud.
    
    Parámetros:
    - listaHumanos: lista de objetos Humano con los datos correspondientes.
    
    Returns:
    - rutas: diccionario con la ruta de cada humano.
    """
    # Se convierte la lista de objetos Humano a un DataFrame

    datos = [(humano.idHumano, humano.tiempo, humano.latitud, humano.longitud, humano.señalHumano) for humano in listaHumanos]
    df = pd.DataFrame(datos, columns=['idHumano', 'tiempo', 'latitud', 'longitud', 'señalHumano'])

    # Se convierte la columna 'tiempo' a datetime
    df['datetime'] = pd.to_datetime(df['tiempo'], unit='s', origin='unix')

    # Se ordena por ID y datetime
    df = df.sort_values(by=['idHumano', 'datetime'])

    # Se crea un diccionario para almacenar las rutas
    rutas = {}

    for idHumano, grupo in df.groupby('idHumano'):
        ruta = []
        for idx, row in grupo.iterrows():
            ruta.append((row['latitud'], row['longitud']))

        # Si la ruta tiene puntos, se añade al diccionario
        if ruta:
            rutas[idHumano] = ruta

    global rutas_json
    carretera_numero = 1

    for idHumano, ruta in rutas.items():
        rutas_json[f'Carretera {carretera_numero}'] = {
            "Cantidad de puntos reales": len(ruta),
            "Puntos reales": ruta,
            "Cantidad de puntos calculados Valhalla": 0,
            "Puntos calculados Valhalla": [],
            "Cantidad de puntos ruta calculada": 0,
            "Puntos de la ruta calculada": []
        }
        carretera_numero += 1
    
    return rutas
